# Eaglercraft 26.3 u1 — reverse-engineering report

This report analyzes the user-provided 26.3-wasm.html single-file build. It records binary metadata and retained namespace identifiers; it does not reconstruct or redistribute Java source, executable payloads, textures, or sounds.

## Build identification

- HTML title: Eaglercraft 26.3 u1
- Input size: 68,220,124 bytes (about 65.1 MiB)
- Runtime: TeaVM / WebAssembly GC
- Inline decompressor: Brotli decoder compiled to WebAssembly
- Runtime modules: main, mesh, and server
- Resource packages: assets.epk and sounds.epk

## WebAssembly module inventory

| Module | Brotli bytes | Decoded WASM bytes | Defined functions | Imports | Namespace identifiers |
|---|---:|---:|---:|---:|---:|
| main | 14,718,870 | 108,704,404 | 186,330 | 99 | 9,319 |
| mesh | 2,299,226 | 18,150,375 | 31,641 | 57 | 2,666 |
| server | 7,792,628 | 44,116,692 | 165,921 | 72 | 7,317 |

The sets overlap: there are 19,302 module/symbol rows and 10,201 unique identifiers across all three modules.

## Import groups

| Module | teavmJso | teavmMath | teavm | wasm:js-string | Other |
|---|---:|---:|---:|---:|---:|
| main | 67 | 13 | 7 | 7 | 5 |
| mesh | 30 | 9 | 6 | 7 | 5 |
| server | 43 | 11 | 6 | 7 | 5 |

The other imports are from teavmDate, teavmConsole, and teavmAsync. All modules contain TeaVM custom sections teavm.memoryRequirements and teavm.imports. No WebAssembly name, DWARF, or source-map custom section was found.

## Recovered identifiers

The compiled modules retain length-prefixed Java package/type strings. Examples include:

- net.minecraft.client.player.LocalPlayer
- net.minecraft.client.multiplayer.ClientLevel
- net.minecraft.client.renderer.LevelRenderer
- net.minecraft.world.entity.Entity
- net.lax1dude.eaglercraft.v1_8.internal.PlatformInput$VKeyEvent
- net.lax1dude.eaglercraft.v1_8.internal.PlatformWebRTC$LANPeer
- net.lax1dude.eaglercraft.v1_8.internal.teavm.ClientMain$2

The mesh module contains MeshMainClass. The server module contains ServerMainClass, WorkerIntegratedServerHost, EaglerIntegratedServerWorker26, and IPC packet identifiers.

These names are useful for navigating further analysis. They are not a mapping from every WASM function index to its original Java method.

## Resource package inventory

| Package | Unpacked bytes | Files | Inventory |
|---|---:|---:|---|
| assets.epk | 20,558,206 | 21,500 | 15,704 JSON; 3,973 PNG; 1,511 NBT; 213 MCMeta; 90 shader files; other metadata |
| sounds.epk | 34,809,347 | 4,779 | 4,779 OGG files |

The assets.epk header identifies eagler-26.3; sounds.epk identifies eagler-26.2. This metadata difference alone does not prove incompatibility.

## What was and was not recovered

**Recovered:** module boundaries, WASM section sizes, imports/exports, TeaVM memory requirements, retained namespace/type identifiers, and resource package counts.

**Not recovered:** original Java files, comments, exact project layout, or complete Java method bodies. The WASM code section still needs instruction-level disassembly and analysis. The supplied build has no debug/source-map metadata that directly maps those instructions to Java files.

## Re-run the inspection

Use Python 3.10+:

```bash
python -m pip install -r requirements.txt
python tools/inspect_eagler.py 26.3-wasm.html --out decomp-output
```

The script writes analysis.json and wasm-symbols.csv only. It does not export executable binaries or resource payloads.

## Next milestones

1. Disassemble the WebAssembly GC function bodies in all three modules.
2. Group functions around retained Java type identifiers and runtime entry points.
3. Trace the JavaScript-to-WASM bridge and document confirmed extension points for VIBE.
4. Add game-state mods only after a stable in-client bridge is confirmed. Current Fullbright, Color Boost, Crosshair, and Zoom controls are wrapper-level visual effects, not game-logic patches.
