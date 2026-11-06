#!/usr/bin/env python3
"""Metadata-only inspector for the Eaglercraft 26.3 single-file HTML build.

Reads inline Brotli/WASM and EPK data in memory. Writes only analysis.json and
wasm-symbols.csv; it never writes executable binaries, textures, or sound files.
Requires Python 3.10+ and the brotli package.
"""
from __future__ import annotations

import argparse
import base64
import csv
import json
import re
import sys
import zlib
from collections import Counter
from pathlib import Path

try:
    import brotli
except ImportError as exc:
    raise SystemExit("Install requirements with: python -m pip install -r requirements.txt") from exc

PAYLOADS = {
    "main": "eag-inline-wasm-br",
    "mesh": "eag-inline-mesh-wasm-br",
    "server": "eag-inline-server-wasm-br",
    "assets": "eag-inline-assets",
    "sounds": "eag-inline-sounds",
}
PREFIXES = (b"net.minecraft.", b"net.lax1dude.eaglercraft.", b"com.mojang.", b"org.teavm.")


def uleb(data: bytes, pos: int) -> tuple[int, int]:
    value = shift = 0
    while True:
        if pos >= len(data) or shift > 35:
            raise ValueError("Invalid or truncated unsigned LEB128")
        byte = data[pos]
        pos += 1
        value |= (byte & 127) << shift
        if byte < 128:
            return value, pos
        shift += 7


def wasm_name(data: bytes, pos: int) -> tuple[str, int]:
    size, pos = uleb(data, pos)
    end = pos + size
    if end > len(data):
        raise ValueError("Truncated WebAssembly name")
    return data[pos:end].decode("utf-8", "replace"), end


def inline_payload(html: str, payload_id: str) -> bytes:
    pattern = re.compile(
        r"<script\b(?=[^>]*\bid=[\"']" + re.escape(payload_id)
        + r"[\"'])[^>]*>(.*?)</script\s*>",
        re.I | re.S,
    )
    match = pattern.search(html)
    if not match:
        raise ValueError("Inline payload missing: " + payload_id)
    return base64.b64decode(re.sub(r"\s+", "", match.group(1)), validate=True)


def parse_imports(section: bytes) -> Counter[str]:
    count, pos = uleb(section, 0)
    grouped: Counter[str] = Counter()
    for _ in range(count):
        module, pos = wasm_name(section, pos)
        _name, pos = wasm_name(section, pos)
        kind = section[pos]
        pos += 1
        if kind == 0:
            _, pos = uleb(section, pos)
        elif kind == 1:
            pos += 1
            flags, pos = uleb(section, pos)
            _, pos = uleb(section, pos)
            if flags & 1:
                _, pos = uleb(section, pos)
        elif kind == 2:
            flags, pos = uleb(section, pos)
            _, pos = uleb(section, pos)
            if flags & 1:
                _, pos = uleb(section, pos)
        elif kind == 3:
            pos += 2
        elif kind == 4:
            pos += 1
            _, pos = uleb(section, pos)
        else:
            raise ValueError("Unknown WebAssembly import kind: " + str(kind))
        grouped[module] += 1
    return grouped


def parse_exports(section: bytes) -> list[dict]:
    count, pos = uleb(section, 0)
    labels = ("function", "table", "memory", "global", "tag")
    rows = []
    for _ in range(count):
        name, pos = wasm_name(section, pos)
        kind = section[pos]
        pos += 1
        index, pos = uleb(section, pos)
        rows.append({"name": name, "kind": labels[kind] if kind < len(labels) else str(kind), "index": index})
    return rows


def inspect_wasm(role: str, compressed: bytes) -> tuple[dict, list[str]]:
    wasm = brotli.decompress(compressed)
    pos = 8
    if wasm[:8] != b"\0asm\1\0\0\0":
        raise ValueError("Not a WebAssembly v1 module: " + role)
    counts: Counter[int] = Counter()
    sizes: dict[str, int] = {}
    imports: Counter[str] = Counter()
    exports: list[dict] = []
    custom: dict[str, object] = {}
    defined = 0
    while pos < len(wasm):
        section_id = wasm[pos]
        size, body = uleb(wasm, pos + 1)
        end = body + size
        if end > len(wasm):
            raise ValueError("Truncated WebAssembly section")
        payload = wasm[body:end]
        counts[section_id] += 1
        sizes[str(section_id)] = len(payload)
        if section_id == 2:
            imports = parse_imports(payload)
        elif section_id == 3:
            defined, _ = uleb(payload, 0)
        elif section_id == 7:
            exports = parse_exports(payload)
        elif section_id == 0:
            n, cursor = uleb(payload, 0)
            name = payload[cursor:cursor + n].decode("utf-8", "replace")
            raw = payload[cursor + n:]
            try:
                custom[name] = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                custom[name] = {"payload_bytes": len(raw)}
        pos = end

    symbols: set[str] = set()
    for prefix in PREFIXES:
        for match in re.finditer(re.escape(prefix), wasm):
            start = match.start()
            if start == 0:
                continue
            length = wasm[start - 1]
            if len(prefix) <= length <= 240:
                try:
                    candidate = wasm[start:start + length].decode("ascii")
                except UnicodeDecodeError:
                    continue
                if candidate.startswith(prefix.decode("ascii")) and re.fullmatch(r"[A-Za-z0-9_.$/]+", candidate):
                    symbols.add(candidate)

    return ({
        "name": role,
        "compressed_bytes": len(compressed),
        "wasm_bytes": len(wasm),
        "defined_functions": defined,
        "import_count": sum(imports.values()),
        "imports_by_module": dict(sorted(imports.items())),
        "exports": exports,
        "custom_sections": custom,
        "section_counts": {str(k): v for k, v in sorted(counts.items())},
        "section_payload_bytes": sizes,
        "namespace_symbol_count": len(symbols),
    }, sorted(symbols))


def inspect_epk(role: str, payload: bytes) -> dict:
    header = payload.find(b"#  world name:")
    marker = payload.find(b"\n\n", header)
    start = payload.find(b"\x1f\x8b", marker + 2)
    if header < 0 or marker < 0 or start < 0:
        raise ValueError("EPK header or gzip stream missing: " + role)
    archive = zlib.decompress(payload[start:], 31)
    pos = archive.find(b">FILE")
    if pos < 0:
        raise ValueError("EPK file table missing: " + role)
    counts: Counter[str] = Counter()
    byte_counts: Counter[str] = Counter()
    file_count = 0
    while archive[pos:pos + 5] == b">FILE":
        pos += 5
        name_len = archive[pos]
        pos += 1
        end_name = pos + name_len
        path = archive[pos:end_name].decode("utf-8", "replace")
        pos = end_name
        size = int.from_bytes(archive[pos:pos + 4], "big")
        pos += 4 + size
        if pos > len(archive):
            raise ValueError("EPK entry exceeds archive: " + path)
        ext = Path(path).suffix.lower().lstrip(".") or "(none)"
        counts[ext] += 1
        byte_counts[ext] += size
        file_count += 1
    return {
        "name": role,
        "compressed_payload_bytes": len(payload),
        "unpacked_archive_bytes": len(archive),
        "file_count": file_count,
        "extensions": dict(sorted(counts.items())),
        "bytes_by_extension": dict(sorted(byte_counts.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path, help="Eaglercraft single-file HTML")
    parser.add_argument("--out", type=Path, default=Path("decomp-output"))
    args = parser.parse_args()
    if not args.html.is_file():
        parser.error("Input file does not exist: " + str(args.html))
    html = args.html.read_text(encoding="utf-8", errors="replace")
    report = {"input": args.html.name, "input_bytes": args.html.stat().st_size, "modules": {}, "resource_packages": {}}
    rows: list[tuple[str, str]] = []
    for role in ("main", "mesh", "server"):
        result, symbols = inspect_wasm(role, inline_payload(html, PAYLOADS[role]))
        report["modules"][role] = result
        rows.extend((role, symbol) for symbol in symbols)
    for role in ("assets", "sounds"):
        report["resource_packages"][role] = inspect_epk(role, inline_payload(html, PAYLOADS[role]))

    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out / "wasm-symbols.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(("module", "namespace_symbol"))
        writer.writerows(rows)
    (args.out / "analysis.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print("Metadata written to", args.out.resolve())
    return 0


if __name__ == "__main__":
    sys.exit(main())
