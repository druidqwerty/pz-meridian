# Meridian game oracle

## Environment inspected 2026-11-06

- Project Zomboid B42.21: `G:/Steam/steamapps/common/ProjectZomboid`.
- Runtime: `jre64/bin/java.exe` in that install.
- Javac: local JDK 25.0.4 compiler (`bin/javac.exe`; override with `--javac`).
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
zombies within 60 tiles of the target **and inside the actual sanctuary bounds**;
the general `surface` count also includes nearby infected outside the city walls.
`infected` checks loaded below-ground zombies there. This is not a proof that
every surface tile in the city is safe.
A target may request `walkTo: {x, y, z}` to queue ordinary pathfinding to a different
level; only a PASS on `<name>_stair_traversal` proves that particular staircase was
traversed. A `vehicle: true` target locates the nearby SUV, checks fuel/key, enters
the actual driver seat and starts/stops its engine; it does not drive it.

Added-content targets may request `metalDoor: {x,y,z,sprite}` to verify the native
`IsoDoor` and toggle it without changing lock state; `salvage: {x,y,z,sprite}`
queues the vanilla `ISMoveablesAction` in scrap mode. The player target must be
adjacent. Filled containers are first emptied with ordinary queued
`ISInventoryTransferAction` actions; there is no direct inventory clear. The probe
supplies only the normal material-specific tools to its private inventory, checks
`canScrapObject`, adjacency/action validity and disabled movables cheats, then
checks that the queued action removed the exact original object. No direct object
deletion, forced success, skill alteration or instant-action cheat is used.
`unbarricade: {x,y,z,sprite}` instead addresses the actual window/door, verifies a
native `IsoBarricade` exists on the player's side, supplies an ordinary crowbar or
blowtorch, and queues `ISUnbarricadeAction` to remove one plank/metal barrier.
Map screenshots include a regional overview and street zoom, not a whole-world fit.

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

## Native-game verification ledger

### Initial baseline

`build/playtest/20261106-043948-059258`: ordinary spawn walking, physical rooms,
loot, safe city surface, preserved infected B1/B2 and remote native forest passed.
A separate log audit found the vanilla pre-game vector-preview negative-array
exception; a narrowly scoped product preview fix was added before the final run.

### Frozen candidate with Viewpoint

`build/playtest/20261106-045129-812755`:

- Both real pathfinding descents passed: surface→B1 and B1→B2.
- Sixteen first/third-person camera assertions passed at eight representative sites.
- Physical doors, spawn walking, loot, both infected underground levels and remote
  generated wilderness passed. Surface samples contained zero zombies while hundreds
  of below-ground zombies remained present.
- Preview initialization and all gameplay were Lua-error-clean.
- Save created successfully. `candidate-bind.json` binds all4,619mod files to the
  launch copy; the source/copy SHA-256 trees matched exactly.
- Overall driver result **FAIL**, solely because the first direct-entry engine-start
  attempt did not reach Running. This is retained without relabeling it PASS.

`build/playtest/20261106-045701-832212` reloaded that saved world:

- Persisted token, position and floor passed before focused follow-up gameplay.
- Starter SUV persisted; actual key, fuel and driver seat passed.
- Engine quality100 and battery charge1 were observed. After ordinary diagnostic
  entry completion (clearing the player movement-block flag), the engine genuinely
  reached **Running**; engine/state checks passed. No car parts were modified.
- Overall recheck **PASS**, Lua-error-clean. No full driving test is claimed.

### Visual issues found by inspection, not hidden by API assertions

- The native paper-map data loaded, but the overview image was blank beige.
  Data-loaded API checks alone are not visual atlas acceptance.
- B1 first-person views exposed bright sky strips along ceiling edges. Viewpoint's
  native `RoofLevels.covers` requires a flat-roof marker or FLOOR+ROOM, whereas the
  exterior grass/road layer above a bunker supplies FLOOR only.
- City facade/canopy/windows/pavement rendered coherently in first and third person;
  the underground medical bay showed actual beds, cabinets and zombies with the
  diagnostic flashlight. A car close-up had test-flashlight glare, not missing art.

The two visual issues required an after-fix focused test; completion and remaining
ceiling limits are recorded below. BEFORE screenshots, raw driver
reports, exact source binding and a screenshot index are exported to
`docs/test-results/2026-11-06-initial/`.

### Oracle-only failures retained for audit

- `20261106-044611-390516`: indexed `getCell():getVehicles()` as a list. B42 returns
  a Java Set; fixed by scanning loaded squares' `getVehicleContainer()`.
- `20261106-044827-716783`: passed `haveThisKeyId()` result to `tryStartEngine`.
  Native API returns a Key object, not boolean; fixed with explicit `~= nil`.
- `20261106-045032-287374`: canceled before gameplay when parent began the final
  entrance-count rebuild. No test claim is made for that intermediate snapshot.

All failed/canceled runs remain in the private build directory. No existing user
saves, settings, mods or game files were changed by the oracle.

## Enrichment interaction completion (before broad expansion)

- `20261106-051328-703427` was interrupted during road salvage. Its retained
  partial log proves ordinary crowbar removal of a real window plank (2 to 1),
  but is not an overall PASS or save/reload claim.
- `20261106-051844-707713` proved genuine roadblock scrap, steel `IsoDoor` toggle,
  both physical stair descents and safe-surface/infected-basement samples. Its
  overall FAIL is retained: the probe tried to scrap a filled tunnel crate.
- `20261106-052458-192513` reloaded that save, passed token/position, moved four
  crate items with normal `ISInventoryTransferAction`, then genuinely scrapped
  the crate. Overall PASS; completed runs have no Lua stack traces.
- No direct object deletion, inventory clear, skill alteration or movables cheat.
  The saved diagnostic player remains god/ghost; this is not a combat test.
- This evidence binds the earlier 4,620-file tree, not the later expanded world.
  See [content receipts](test-results/2026-11-06-content/README.md).

## Final native-content expansion

Frozen product: **2,381 native cells / 4,784 files**, tree SHA-256
`581a21c7d438c314c428496984b0d8dd1ff7100a38db0acbe7172752f12055a0`.
**27** structural/simulation regressions and the native static audit pass.
They are distinct from these actual-game tests:

### Fresh changed-site run: `20261106-053010-285473`

- Six representative sites loaded with physical floors, RoomDefs, native doors,
  containers and loot: dam waterworks, postal hall, city utility waterworks,
  residential house, B1 school classroom and B2 residential laundry.
- All twelve first/third-person camera assertions passed. Inspected actual frames
  show coherent surface interiors, school tables/chairs, washers/carts and infected
  below ground. These views do not certify every room's visual finish.
- Both genuine staircase descents and a 16-tile ordinary pathfinding walk along
  the new service ring passed. Teleports between test sites are not traversal proof.
- Nonblank atlas vectors visibly show regional roads/water and city street blocks.
  A one-second screenshot hold fixes oracle readback races; overview is regional,
  not a full-world fit. Exploration fog was true before a private diagnostic reveal.
- Overall **FAIL retained** solely for two near-edge population assertions whose
  old 60-tile radius included infected OUTSIDE the sanctuary. No Lua errors.

### Narrow reload/recheck: `20261106-053547-819680`

- Overall **PASS**, Lua-error-clean. Persisted token, position and floor passed.
- Both identical boundary samples had **zero inside-city surface zombies** with
  bounds-aware counting. Outside-city surface populations 116/110 and below-ground
  populations 726/660 were retained, not erased to satisfy the test.
- A real 20-tile walk on a new regional detour passed, followed by camera/atlas
  checks and another save. This is not the complete detour or a vehicle-route test.
- Reload-copy SHA-256 matches all 4,784 bound final-product files. Product geometry
  and Lua were unchanged by the boundary-count and screenshot-oracle corrections.

### Remaining Viewpoint ceiling finish

Opaque ceiling coverage improves the old bright open-sky leak, but final school
frames still show thin bright ceiling-edge seams and overlapping underside bands.
The earlier medical hall also shows a conspicuous green surface-texture strip.
The B2 laundry ceiling is opaque; flawless first-person ceilings are **not** claimed.
Viewpoint's flat-roof coverage and solid-floor material gathering are separate:
preserved native surface terrain can still supply a visible grass/floor underside.
No proven data-only correction preserving that surface is claimed.

Actual screenshots, unchanged failed reports, final reload PASS and sanitized
binding receipts: [expansion evidence](test-results/2026-11-06-expansion/README.md).
No full-route driving, driving-time ratio, long-term balance, every entrance,
all camera angles or multiplayer certification is implied.
