# VIBE Engine Bridge — API contract

The HACKS panel does not write directly into WebAssembly memory. The supplied Eaglercraft 26.3 build is compiled with TeaVM/WebAssembly GC and its public module exports do not include a Java player object or movement methods.

To activate the HACKS panel, the **game source build** must expose this API in the game page's own JavaScript realm:

```js
window.__VIBE_ENGINE__ = {
  apiVersion: 1,

  // Return true when applied, false when rejected, or a Promise of either.
  setHack(name, enabled) {
    // Implement in the Java/TeaVM game source.
  },

  // Optional. Called when the Fly speed slider changes.
  setFlySpeed(value) {
    // Apply the chosen speed to the local player ability state.
  }
};
```

Supported `setHack` names:

- `fly`
- `noclip`
- `speed`
- `noFall`

The page checks for this API before enabling its controls. The API must be exposed **inside the game iframe**, not on the outer GitHub Pages window.

## Candidate targets recovered from the compiled build

The main WASM binary retains these strings:

- `net.minecraft.client.player.LocalPlayer`
- `net.minecraft.world.entity.Entity`
- `PlayerAbilities`
- `getAbilities`
- `noPhysics`, `setNoPhysics`, `isNoPhysics`
- `mayfly`, `canFly`, `isFlying`
- `setFlying`, `setFlyingSpeed`, `flyingSpeed`
- `walkSpeed`, `walkingSpeed`, `flySpeed`

These are retained names, not recovered method implementations. Verify their exact signatures and timing in the Java source before wiring them into the client tick loop.

## Recommended implementation responsibilities

1. Keep all player-state changes in the game Java/TeaVM source where the live `LocalPlayer` and `PlayerAbilities` instances exist.
2. Implement Fly and Noclip as local client toggles and clearly label that multiplayer servers may correct or reject movement.
3. Preserve and restore prior player values when a toggle is disabled or the player/world changes.
4. Expose only the four named operations and the optional flight-speed setter through the versioned bridge.
5. Return `false` or throw a useful error when there is no player, the world is not ready, or the operation is unavailable.

## Why the current compiled HTML is not enough

The page's TeaVM bootstrap stores the runtime in `window.__tv`, but the WASM export list contains `main`, TeaVM exception/string helpers, wrapper helpers, and `teavm.memory`. It does not export a live player object, `setNoPhysics`, `setFlying`, or an equivalent mod API. A browser overlay cannot call those Java methods merely because their names remain in a binary string table.

A source tree or a build that already includes a documented JavaScript bridge is required to complete the engine-side implementation.
