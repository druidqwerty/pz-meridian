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

## Urban/interior revision — 0.2.0-alpha.1

Frozen final candidate: **2,387 native cell pairs / 4,796 mod files**,
tree SHA-256 `bce864b2bd7c0892a2351f69bb42f6697a8a64c8db91b274e71b9de52f0e7339`.
It contains 1,188 surface structures, 25,423 RoomDefs and 1,234 BuildingDefs;
25,411 native room-light circuits exclude twelve deliberately open-air crowns.
Meridian has 248 surface buildings, including 140 with six or more occupied
storeys (maximum thirteen); four large shopping centres and thirteen gun shops
are present across the map. Static counts are not visual acceptance of every room.

The completed static/native suite contains 48 passing checks, including the
twelve-entrance parameterized wayfinding and compiled southeast-perimeter checks.
The final architecture and interior regressions were also rechecked after the
supported-lamp fix. These checks do not replace the actual-game evidence below.

### Final fresh native run — 20261106-142304-247195

Overall wrapper and native report **PASS**, eleven targets in an isolated new
world with the final north/west-wall-supported fixtures. Real authored switches
were toggled at night in cottage, tower and B1 kitchen rooms with the diagnostic
torch off: measured brightness deltas **0.396078 / 0.301961 / 0.301961**.
The test creates no room lights, bulbs or electrical power.

Four actual ordinary walking-action stair traversals passed: tower z0→1 and
z11→12, fortification z7→8 and public bunker z0→-1. Teleports between test
locations are not traversal proof. Bound surface population samples were empty;
the underground remained infected. Native doors, floors, rooms and loot loaded.

The exact compiled sprite set contains 181 names: read-only runtime-registry
inspection found zero missing sprites, zero invalid textureless sprites and
seven valid native seasonal tree proxies. The negative control and unchanged
registry size passed. No Lua errors or unknown map-resource errors were found;
six actual startup font/Piano fallback diagnostics remain in the receipt.
This does not claim a warning-free log or a fresh unmodded baseline for this run.

### Isolated save/reload — 20261106-142928-051777

Wrapper and native result **PASS**: persisted token, exact position/floor and
physical floor loaded from the saved test world. All 4,796 reloaded mod files
match the final bound candidate. Sprite, Lua and map-resource gates passed again.
No user save or existing world was opened or migrated; new geometry requires a
**new Sandbox world**. This is not long-term save or multiplayer certification.

The root reviewer inspected actual final cottage/tower/B1 night pairs, complete
bed, upper tower stairs, parking and fortification walkway. Supported fixtures
and brightness changes are visible. The wall frame proves the local walkway,
not a panoramic skyline; the upper bunker-shaft frame is partly occluded, while
the after-descent frame shows the player and physical B1 stairs. Full entrance
pavilion visual coverage is not claimed. Viewpoint underground terrain/ceiling
bands, full-route driving, the proposed travel-time ratio and multiplayer remain
outside this acceptance boundary.

See [urban evidence](test-results/2026-11-06-urban/README.md) for untouched failed
pre-final reports, final/reload receipts and actual screenshots. Those failed
runs were not relabeled as proof of the final candidate.


## Area-aware interiors — 0.2.1-alpha.1

This version changes furnishing geometry; the earlier 0.2.0 live run is historical,
not proof of these bytes. The initial 4,796-file candidate tree SHA-256 was
`744d2fa695c22d4eaff072befe2513ba7c15666d890b0964f64ed4254dece47b`;
its retained failed run found underground population queue starvation. The final
post-fix runtime is bound separately below.

### Compilation and static gates

All 2,387 native cell pairs are compiled, decoded and round-tripped. The world
retains 1,188 surface structures, 25,423 native rooms, 1,234 BuildingDefs and the
128.256km principal road. There are 639,745 furnishing sprite instances; that
instance count is not an occupied-floor-area measurement. No unknown native
sprites were found; all sixteen sanctuary cells retain zero surface density.

The manifest contains 22,022 reports for actual furnished rectangles:
13,944 zoned, 8,062 compact and sixteen circulation rectangles. Every zoned
plan passes final density, maximum-empty-square and connected-floor/approach
gates. The separate release audit rechecks footprint counts, density arithmetic,
empty-square limits and strict boolean acceptance. Compact/circulation reports
remain explicitly `accepted:null, densityAudited:false`, not density passes.
RoomDef coverage is broader than furnishing-report coverage: connecting halls
and open-air areas are not all furnished or density-certified.

The 57-check broad Meridian discovery passes, followed by final eight-area and
three-native-architecture reruns after the cache fix, three reviewer native
interior checks and five audit negative controls. Reusable Map Tools passes
sixteen furnishing and ten urban checks. Its historical 471-test discovery
retains one failure/four errors/ten skips for unavailable retired geography,
receipts and optional compiler fixtures; no retired product was restored.
See the machine-readable [static receipts](test-results/2026-11-06-density/static-checks.json)
and [compiled audit](test-results/2026-11-06-density/static-audit.json).

The installed Meridian copy has a recoverable backup of the previous version;
all 4,796 copied files are SHA-256 verified. User saves, profiles and unrelated
mods are untouched. Changes require a new Sandbox world, not an old-save upgrade.

### Retained failed candidate and read-only population diagnosis

Fresh run `20261106-152839-433264` failed only the selected B1 kitchen/dormitory
infestation assertions. Seven real aisle walks, two real stairs and two native
night-light toggles passed, but those results did not erase the failed population
samples. Its 29 actual PNGs and unchanged report remain `pre-final-failed-*`.

Read-only diagnostic reload `20261106-153757-558389` observed the same product:
both room centres stayed at zero loaded/nearby zombies at 15/30/60 seconds,
with 6,587/6,296 eligible free interior squares respectively. The global
1,600-zombie cap was not reached. This was an observation-tour PASS, not release
acceptance. Five further PNGs, report and exact private probe source are retained.

Source analysis and a regression reproduced FIFO starvation behind unloaded
buckets. The repaired runtime prioritizes three nearby loaded jobs plus one
oldest eligible job per 60 ticks, still inspecting at most four full buckets.
Stale anchors are pruned, including admission to a saturated queue; temporary
protected/blocked/capped jobs retry while loaded instead of being lost after
three attempts. Player safety distance, authority, sandbox switches, population
cap and once-per-save seeding remain. Ten queue regressions and the five existing
runtime checks pass. Geometry was not rebuilt for this runtime-only repair.

See [all density evidence](test-results/2026-11-06-density/README.md) for exact
failed/diagnostic receipts and the separately bound final results below.

### Repaired fresh run and exact isolated reload

Final product tree: **4,796 files**, SHA-256
`c3f2943fba4181fb70ee805324dd1675d5064ca8e5792632f92fecfee8d49435`.

Fresh `20261106-154258-021984`: native and wrapper **PASS** with the same
eleven target definitions and original sample timing as the failed candidate.
All seven ordinary ten-tile aisle walks, tower z0→1 and public bunker z0→-1
ordinary stair traversals pass. The formerly empty kitchen/dormitory samples
now contain **103 / 74 nearby below-ground zombies** after about twelve seconds;
same-floor infected are also visible in the selected actual PNGs. No test
queue/spawn helper or population deletion was used to obtain this result.

Authored native switches at night, with the diagnostic torch off, produce
brightness deltas **0.400000006 / 0.235294104** in office/B1 kitchen views.
All 184 compiled sprite names resolve: zero missing or invalid textureless
sprites, seven valid seasonal proxies; registry size and negative control pass.
Zero Lua and unknown map-resource errors; six known stock font/Piano startup
diagnostics are retained rather than called a warning-free log.

Reload `20261106-155013-062068`: native and wrapper **PASS** for saved token,
exact position/floor and physical floor. All 4,796 source/reloaded files match
the final tree; 439 nearby below-ground zombies remain. This is an isolated
test-world reload, not long-term save or multiplayer certification.

The root reviewer inspected final prep/storage zones, complete bed/locker/
nightstand groups, retail activity clusters and both native night ON/OFF pairs.
Clear local aisles and visible light changes are shown. Native field of view
occludes far sides; these images do not certify every room tile or all angles.
Original target labels are retained verbatim: the native classroom sample's
actual programme is nursery, and the surface dining-labelled sample is a public
kitchen. The exact purposes are in the checklist; they are not falsely claimed
as classroom/dining-seating visual coverage.

All reports, 29 fresh frames and the reload frame are in the
[density evidence](test-results/2026-11-06-density/README.md). Existing Viewpoint
ceiling/terrain bands, full-route driving/time ratio, combat balance and
multiplayer remain outside this acceptance boundary.

### Actual-purpose coverage supplement

Supplemental isolated reload-tour `20261106-155309-686353` passes native and
wrapper gates with the same final product bytes. It adds only the two genuine
programmes missing from the original semantic selection: `classroom` at
[600,48737,15,10] and `dining` at [5144,29244,23,32]. Both ordinary ten-tile
aisle walks pass, as do reload token/position/floor, sprite and Lua/resource
gates. This is new narrow coverage, not a relabeled repeat of the original run.

The root inspected both actual programme PNGs: complete student desk/chair
groups and dining table/chair plus refreshments groups flank open circulation.
Seven supplemental PNGs are retained. Future target preparation now filters
actual furnishing purpose as well as native loot names; four target-safety tests
including the semantic-selection regression pass. Original target JSON, labels
and reports remain immutable. These samples still do not certify every classroom
or dining room's visual finish, combat, multiplayer or the complete journey.

## 0.3.0-alpha.1 architectural diversity, parks and parking overhaul

- **3,900 cataloged building variants (100 distinct variants per building kind across 39 kinds and 12 architectural archetypes)**:
  Every single one of the 3,900 variants passed static B42.21 sprite definition + `.pack` texture verification, stair flight/landing checks, room reachability from entrance/stairs, native type-7 room lighting checks, and area-scaled room furnishing acceptance.
- **Compiled world (`2,387` cell pairs, `1,188` surface structures, `1,234` `BuildingDef`s, `25,199` `RoomDef`s, `707,386,945` native bytes)**:
  - **1,049 unique `(kind, variant)` building pairs** placed across the world.
  - **2,613 park zones** (full-block neighborhood parks on open plots, pocket parks, and residential garden yards).
  - **697 building-side striped parking lots** plus 4 regional shopping centre aprons (**264,411 total parking squares**).
  - Static audit (`tools/audit.py`) PASS: `0` unknown sprites, `21,816` furnishing reports (`12,025` zoned rooms 100% accepted, `9,775` compact, `16` circulation), `metadataPart0` `2,288,404` bytes (`< 9 MB`).
- **Live B42.21 game verification (`20261106-232550-798823`) and isolated save-reload (`20261106-233323-696224`)**:
  - `sprite_registry_checked=546`, `sprite_registry_missing_count=0`, `sprite_registry_textureless_count=0`, `sprite_registry_seasonal_tree_proxy_count=7` (`all_native_sprites_registered=PASS`, `native_sprite_textures_or_verified_tree_proxy=PASS`).
  - All 11 compiled-room density, aisle traversal, night switch ON/OFF (`0.898039 -> 0.662745`, `delta=0.235294`), tower stair (`z0 -> z1`), and public bunker descent (`z0 -> z-1`) targets PASS (`0` Lua errors, `0` runtime resource errors, 29 screenshots).
  - Reload `20261106-233323-696224` PASS: `reload_token=PASS`, `reload_position=PASS` (`48259.5,1408.5,-1`), `402` below-ground zombies retained, `0` surface zombies in sanctuary.

