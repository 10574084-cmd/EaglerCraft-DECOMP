# VIBE Client — Eaglercraft 26.3 workspace

This repository contains the VIBE GitHub Pages wrapper and a first-pass reverse-engineering inventory for the supplied Eaglercraft 26.3 single-file build.

## Repository layout

- index.html — VIBE wrapper and visual mod menu.
- .github/workflows/pages.yml — GitHub Pages deployment workflow.
- tools/inspect_eagler.py — metadata-only WASM/EPK inspector.
- requirements.txt — Python dependency for the inspector.
- decomp/REVERSE_ENGINEERING.md — findings from the supplied HTML.
- decomp/analysis.json — machine-readable module/package report.

## Add the game client

The original 26.3 client HTML is not committed here. To auto-load it from Pages, add your authorized client build to the repository root using this exact filename:

26.3-wasm.html

The page can also load a local HTML file for the current browser session or a hosted direct HTTPS URL from MOD MENU → CLIENT.

## Mod menu

Press Right Shift to open or close the menu. Current controls are visual/page-level effects: Fullbright, Color Boost, Crosshair, and Zoom. These do not change server state, inventory, movement, or game mechanics.

## Reverse-engineering status

The input contains TeaVM/WebAssembly GC modules and EPK resource packages, not the original Java source tree. The report documents recovered module metadata and Java namespace identifiers. It is not a complete Java decompilation: method bodies, comments, original source layout, and symbol-to-method mappings have not been recovered.
