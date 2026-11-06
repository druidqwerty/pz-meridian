# Area-aware interior QA — 0.2.1-alpha.1

Static/prepared and actual-game evidence remain separate. The first candidate
below is **not accepted for release**: its underground population checks failed.
The untouched failed reports and screenshots are retained.

## Prepared/static coverage

- `static-audit.json` and `static-checks.json`: parent-run native/static gates.
- `density-checklist.json`: actual compiled RoomDefs matched by world rectangle,
  level and native loot role; 13,944 accepted zoned rooms, 8,062 fitted compact
  rooms and sixteen deliberate circulation rooms. This is not live evidence.
- `density-targets.json`: seven historically labelled functional-room samples,
  two authored night-switch checks and two ordinary staircase traversals.

## First actual-game run — failed, retained

`20261106-152839-433264`; wrapper and native result **FAIL**. Bound product:
4,796 files, tree SHA-256
`744d2fa695c22d4eaff072befe2513ba7c15666d890b0964f64ed4254dece47b`.

- Seven ten-tile ordinary `ISWalkToTimedAction` aisle walks passed: office,
  nursery, retail, commercial kitchen, storage, B1 public kitchen and B1 dormitory.
  The original target labels called the nursery "School classroom" and the
  commercial kitchen "Public dining"; these names are not proof of those purposes.
- Tower z0→1 and public bunker z0→-1 ordinary stair traversals passed.
- Native authored switches changed observed nighttime illumination with the
  diagnostic torch off: office delta 0.400000006; B1 kitchen 0.235294104.
- Runtime registry checked all 184 compiled sprite names: zero missing or
  textureless sprites, seven valid native seasonal proxies, no registry mutation.
- Zero Lua errors and zero unknown map-resource errors; six retained stock
  font/Piano startup diagnostics. This is not a warning-free-log claim.
- **Both selected B1 room centres had zero nearby below-ground zombies.** These
  are real failed population assertions, not relabeled successes. Other evidence
  (including 72 below-ground zombies under the classroom) does not erase them.
- An isolated test save was created; no user save or settings were opened.

Files: `pre-final-failed-report.txt`, `pre-final-failed-receipt.json`,
`pre-final-failed-screenshot-index.json` and 29 corresponding actual PNGs.

The parent visually inspected the office workstation/filing groups, B1 preparation
counter zones, complete dorm bed/locker/nightstand groups and their clear aisles.
Native field-of-view occludes the far sides: these frames certify sampled views,
not every tile or all camera angles. No full-route driving or multiplayer claim.

## Read-only population diagnosis — not release acceptance

`20261106-153757-558389` reloaded an isolated copy of that failed test save with
the **same unchanged product bytes**. Persisted token/position/floor passed.
The diagnostic wrapper's PASS means its observation tour completed; it does
**not** assert that either empty B1 centre is sufficiently infected.

At each exact centre the private wrapper sampled at 0/15/30/60 seconds using
ordinary native simulation. It never called spawn/queue/process helpers,
changed time speed, removed zombies or changed sandbox population settings.

| At t15, t30 and t60 | B1 kitchen | B1 dormitory |
| --- | ---: | ---: |
| Global loaded zombie count | 0 | 0 |
| Same-level / nearby-60 zombie count | 0 / 0 | 0 / 0 |
| Nearby persisted seeded buckets | 0 | 0 |
| Loaded floor squares, 14–60 tile annulus | 9,318 | 9,122 |
| Eligible free interior floor squares in that annulus | 6,587 | 6,296 |

Process bunker-spawn count remained 36 and total persisted seeded buckets 76.
Thus the 1,600 global zombie cap and lack of free floor do not explain these
empty samples. The observation supports investigating queued-job starvation;
it does not by itself expose the private queue or prove a particular repair.
At diagnostic reload the old public entrance had 52 below-ground zombies.

Files: `pre-final-population-diagnostic-report.txt`, matching receipt/index and
five actual PNGs. `population-diagnostic-wrapper.py` and its target JSON preserve
the exact private observation source in the GitHub source repository (the playable
ZIP excludes diagnostic drivers); run the wrapper from project `build/`
with the normal `tools/playtest.py` CLI, never install it in the product.

No new accepted fresh-run or release binding is claimed in this section.

## Repaired frozen candidate — final fresh native PASS

`20261106-154258-021984`; wrapper and native report **PASS**. The runtime
scheduler now prunes unloaded jobs, prioritizes three nearby loaded safe jobs
plus one oldest eligible job, and retains temporarily blocked loaded jobs for
retry. The original spawn exclusion and 1,600 loaded-zombie cap are unchanged.
Geometry was not rebuilt for this repair.

Final bound product: **4,796 files**, tree SHA-256
`c3f2943fba4181fb70ee805324dd1675d5064ca8e5792632f92fecfee8d49435`.
The isolated launch copy exactly matches the frozen source. The old failed
candidate above has a different hash and remains historical evidence only.

The same eleven original targets and infected assertions ran without extended
settling delays, forced spawns, queue calls or population changes:

- All seven ten-tile ordinary aisle walks passed, with actual floors and RoomDefs.
- At the original approximately twelve-second post-teleport samples, the B1
  kitchen had **103 nearby below-ground zombies** and the B1 dormitory **74**;
  both original infected assertions passed. These are local samples, not a claim
  that every underground tile has zombies or proof of combat balance.
- Tower z0→1 and public bunker z0→-1 genuine ordinary walking-action stairs passed.
- Both authored native night switches passed: brightness deltas **0.400000006**
  and **0.235294104**, diagnostic torch off, authored switch state restored.
- Bound surface samples inside the sanctuary contained zero surface zombies;
  outside-city infection and underground populations were not removed.
- All 184 compiled sprite names registered, zero missing/textureless sprites,
  seven verified native seasonal proxies; registry lookup did not mutate it.
- Zero Lua and unknown map-resource errors. Six stock font/Piano startup
  diagnostics remain recorded, not silently suppressed.

Files: `final-report.txt`, `final-receipt.json`, `final-screenshot-index.json`
and **29 actual final PNGs**. Diagnostic teleports between sites are not walking
route evidence; only the explicitly queued aisle/stair actions prove traversal.
The visible kitchen preparation islands and complete dorm bed/locker/nightstand
groups have clear aisles and actual nearby zombies. Native field-of-view still
occludes the far side of these large rooms; whole-room visual certification,
all angles, driving-time ratios, full-route driving and multiplayer are not claimed.

Parent inspection caught a coverage-label error: the original "School classroom"
target actually selected furnishing purpose **nursery**, and "Public dining"
actually selected **restaurantkitchen**. Native loot names alone were insufficient:
nursery intentionally uses classroom loot, while public dining may use hall loot.
Original target JSON, checklist and raw reports remain immutable historical data.
Those two original successful walks prove nursery/kitchen access, not actual
classroom student workstations or dining seating. Future preparation now requires
the actual furnishing `purpose` as well as the native `lootRole`; a regression
rejects both semantic mismatches. Correct programme coverage is supplemental.

## Exact final-world isolated reload — PASS

`20261106-155013-062068`; wrapper and native result **PASS**. Persisted token,
exact position **48259.5,1408.5,-1** and physical floor passed. The reload had
439 nearby below-ground zombies. All 4,796 files match the same final hash.
Sprite/Lua/map-resource gates passed again; six stock startup diagnostics remain.

Files: `reload-report.txt`, `reload-receipt.json`,
`reload-screenshot-index.json` and `reload-reload.png`.
No user save, profile, options or unrelated mod was opened or changed. These
checks use a fresh isolated world and its own copied save, not migration of an
existing world. Packaging/public release binding is a separate parent-owned gate.

## Purpose-corrected narrow coverage supplement — PASS

`20261106-155309-686353`; wrapper and native result **PASS** on a new isolated
copy of the successful final fresh save. Product bytes are unchanged: all 4,796
files match final tree `c3f2943fba4181fb70ee805324dd1675d5064ca8e5792632f92fecfee8d49435`.
This is a two-target coverage supplement, not another full fresh certification.

| Actual furnishing purpose | Native loot role | World rectangle | Ordinary aisle |
| --- | --- | --- | --- |
| classroom | classroom | 600,48737,15,10 at z0 | ten tiles, PASS |
| dining | hall | 5144,29244,23,32 at z0 | ten tiles, PASS |

Both actual RoomDefs/floors passed, followed by real queued `ISWalkToTimedAction`
aisle traversal. Actual frames show student desk/chair groups in the classroom
and dining tables/chairs plus refreshment surfaces in the public dining hall.
The supplement fills the two semantic coverage gaps; the original nursery and
commercial-kitchen labels/reports have not been rewritten. Four focused target
tests now pass, including rejection of the wrong purposes despite compatible
native loot names.

Persisted reload token/position/floor, all 184 sprites, zero Lua and unknown
map-resource errors passed again; six stock startup diagnostics remain.
Files: `supplemental-report.txt`, `supplemental-receipt.json`,
`supplemental-screenshot-index.json`, **seven actual PNGs**,
`supplemental-density-targets.json` and `supplemental-density-checklist.json`.
Native field-of-view still occludes the far side; no all-room/all-angle claim.
