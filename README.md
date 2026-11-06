# EaglerCraft-DECOMP

VIBE Client / EaglerCraft 26.3 web wrapper and reverse-engineering workspace.

## GitHub Pages

The site is deployed with GitHub Actions from the `main` branch. The page entry point is `index.html`.

## Add the client

For automatic loading, place the user's legally obtained client build in the repository root with this exact filename:

```
26.3-wasm.html
```

The supplied build is a large single-file HTML bundle. If it is too large for the browser upload interface, publish it as a GitHub Release asset or another static host, then paste its direct HTTPS URL into **MOD MENU → CLIENT**. You can also use **Open 26.3-wasm.html** to load a local copy for the current browser session.

## Mod menu

Press **Right Shift** to open or close the menu. Current tools are visual/page-level modifiers: Fullbright (brightness filter), Color boost, Crosshair, and screen zoom. They do not modify server state or game mechanics.

## Reverse-engineering notes

The supplied HTML is a compiled WebAssembly/TeaVM build with embedded Brotli-compressed modules and EPK resource bundles. It is not the original Java source tree. Static inspection and WASM disassembly can expose module structure and low-level operations, but cannot reliably restore original Java class names, comments, or project structure without source maps, symbols, or intermediate build artifacts.

This repository keeps the page wrapper separate from the bundled client. The original client file is not rewritten by the wrapper.
