# Meridian game oracle

## Environment inspected 2026-11-06

- Project Zomboid B42.21: `G:/Steam/steamapps/common/ProjectZomboid`.
- Runtime: `jre64/bin/java.exe` in that install.
- Javac: `C:/Users/druid/.openclaw/workspace/_ext/jdk/jdk-25.0.4.1+1/bin/javac.exe`.
- Python: `../pz-map-tools/.venv/Scripts/python.exe`.
- Viewpoint Workshop `3809306528`, version `0.1.6.1`; `mods/Viewpoint/common/mod.info`.
- Its required ZombieBuddy loader: Workshop `3619862853`.
- Real USA reference: Workshop `3829712469`, `mods/RealUSA/42/mod.info`.

These are local dependencies, not redistributable product files. The test runner
uses the neutral native-game/optional-camera helpers preserved in `pz-map-tools`.
It does not modify those helpers, installed game files, user options or saves.

## What the runner proves

`tools/playtest.py` creates a new `build/playtest/<timestamp>/cache` for every run.
It privately copies the candidate mod, enables it and a test-only driver, uses real
menu callbacks to start a new world, and accepts the loading prompt through a
reflection-only Java helper. No mouse or keyboard input is generated.

Fresh checks: world and spawn selection, real floor/room/loot/door/stair counts,
a two-tile ordinary pathfinding action, optional streamed target inspection,
optional first/third/isometric Viewpoint camera changes, native atlas open/load,
optional genuine staircase pathfinding and starter-SUV fuel/key/seat/engine checks,
and save creation. A fully charged vanilla flashlight is equipped only in the
diagnostic cache, not in the shipped product or any user save.
Reload checks compare the persisted test token and exact final position.

Targets are a JSON array, for example:

```json
[{"name":"meridian_surface","x":100,"y":100,"z":0,"safeSurface":true},
 {"name":"meridian_bunker","x":100,"y":100,"z":-1,"room":true,"infected":true}]
```

Coordinates above are examples, not actual map coordinates. `safeSurface` checks
zombies within 60 tiles of the target and `infected` checks loaded below-ground
zombies there. This is not a proof that every surface tile in the city is safe.
A target may request `walkTo: {x, y, z}` to queue ordinary pathfinding to a different
level; only a PASS on `<name>_stair_traversal` proves that particular staircase was
traversed. A `vehicle: true` target locates the nearby SUV, checks fuel/key, enters
the actual driver seat and starts/stops its engine; it does not drive it.

Screenshots require human/model visual inspection; camera API state alone is not
proof that the art renders well. Teleports are diagnostics, not walking/driving
route evidence or proof that stairs are traversable.

## Commands from workspace

```powershell
projects/pz-map-tools/.venv/Scripts/python.exe projects/pz-meridian/tools/playtest.py --mod projects/pz-meridian/mod --targets projects/pz-meridian/build/test-targets.json
projects/pz-map-tools/.venv/Scripts/python.exe projects/pz-meridian/tools/playtest.py --mod projects/pz-meridian/mod --targets projects/pz-meridian/build/test-targets.json --viewpoint
projects/pz-map-tools/.venv/Scripts/python.exe projects/pz-meridian/tools/playtest.py --resume projects/pz-meridian/build/playtest/<fresh-run>
```

Use `--prepare-only` to inspect the generated launch and driver without launching.
`--timeout` defaults to 600 seconds; parent wrapper must remain alive while JVM is
running because Windows execution tools use a kill-on-close Job Object. The runner
supervises the exact process it created and terminates that process after a result
or timeout. It never kills a process by name. No test-driver files enter the mod.

## Five-times vanilla travel target

The installed vanilla `media/maps/Muldraugh, KY` has **4,065 native cells**.
Cell-coordinate bounds are `(0,0)..(77,62)`, an enclosing rectangle of
**19,968 × 16,128 tiles** (256 tiles/cell). Its bounding diagonal is approximately
**25,668 tiles**. Five such diagonals are approximately **128,339 tiles**.
This is an exact file-based extent measurement plus a geometric estimate, **not**
a measured road route or driving-time benchmark. Vanilla wilderness edges do not
all contain roads. Comparing driving times requires fixed vehicle, route endpoints,
road speeds, fuel rules, game-time speed and interruption policy. A new-map route
can be designed against this 128 km geometric proxy, but must not be advertised as
verified 5× vanilla driving time before paired full driving measurements exist.

### Native-road proxy

A second measurement uses the **installed native `worldmap.xml.bin`**, not the
older 300-cell XML alongside it. Primary/secondary/tertiary polygons were rasterized
at four tiles/pixel; 14 line features used an eight-tile width. An eight-neighbour
shortest path within the largest connected road component runs from southwest
extreme `(944,14816)` to northeast extreme `(15600,2464)` and measures approximately
**26,170 tiles**. The planned Meridian road is **128,256 tiles**, or **4.90×** this
native-road geometric proxy. Rasterization and unrestricted polygon-edge driving
are approximations. This is **not measured driving time**. Machine-readable
measurement: `build/vanilla-road-baseline.json`.

## Verification status

Runner Python syntax and all three embedded Lua chunks compiled successfully.
Initial baseline run `build/playtest/20261106-043948-059258` passed the driver
checks (floor/room/loot/walking, safe surface with preserved infected underground,
both negative levels, remote native wilderness, saving). Its log audit separately
found a vanilla spawn-preview `WorldMapVisited.setBounds` negative-array exception.
This initial run is **not error-clean atlas acceptance**. A scoped product preview
fix and final fresh/Viewpoint/reload tests are pending. The runner now fails on
any `dumping Lua stack trace` or `ERROR: Lua` log entry, independently of driver
PASS, so the preview issue cannot silently pass the final oracle.
