# VIBE Client — Eaglercraft 26.3 workspace

This repository contains the VIBE GitHub Pages wrapper and a first-pass reverse-engineering inventory for the supplied Eaglercraft 26.3 single-file build.

## Repository layout

- index.html — VIBE wrapper and visual mod menu.
- .github/workflows/pages.yml — GitHub Pages deployment workflow.
- tools/inspect_eagler.py — metadata-only WASM/EPK inspector.
- requirements.txt — Python dependency for the inspector.
- decomp/REVERSE_ENGINEERING.md — findings from the supplied HTML.
- decomp/analysis.json — machine-readable module/package report.
- decomp/resources.html — browser-based image, texture, JSON, NBT and shader explorer with PNG-only, all-assets, and sound ZIP export.
- decomp/VIBE_ENGINE_BRIDGE.md — client API contract and the recovered movement-hook targets.

## Add the game client

The original 26.3 client HTML is not committed here. To auto-load it from Pages, add your authorized client build to the repository root using this exact filename:

26.3-wasm.html

The page can also load a local HTML file for the current browser session or a hosted direct HTTPS URL from MOD MENU → CLIENT.

## Mod menu

Press Right Shift to open or close the menu. Current controls include visual/page-level effects (Fullbright, Color Boost, Crosshair, and Zoom) plus a HACKS tab. Fly, Noclip, Speed and No Fall controls call the VIBE Engine Bridge contract. They stay disabled until the loaded game build exposes that API; the supplied WASM build does not currently export player-control methods. The menu does not pretend that a request succeeded when no engine hook exists.

## Reverse-engineering status

The input contains TeaVM/WebAssembly GC modules and EPK resource packages, not the original Java source tree. The report documents recovered module metadata and Java namespace identifiers. The Resource Explorer can read the original HTML locally, preview PNG assets, inspect JSON and metadata, and export the embedded assets and sound packages as ZIP files. It is not a complete Java decompilation: method bodies, comments, original source layout, and symbol-to-method mappings have not been recovered.


## Import separated binary resources

The ZIP packages are prepared separately for upload because GitHub's browser uploader cannot accept the entire audio collection as one file. See `assets/packages/README.md` for the five filenames and the one-click extraction workflow. After adding the five ZIPs to `assets/packages/`, run **Actions → Import Eaglercraft Resource Packages** to generate the individual files under `assets/images/`, `assets/json/`, `assets/data/`, and `assets/audio/`.
