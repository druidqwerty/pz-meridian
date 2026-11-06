# Independent prerelease review — 2026-11-06

Scope: native builder/architecture/bunkers/landscaping, shipped Lua runtime,
installer, README/runtime/QA claims. Review did not alter runtime/map files.
This snapshot predates the final Viewpoint, real-stair and reload results.

## Result

No additional critical map/runtime coordinate or sanctuary-floor blocker was
found. GitHub **prerelease** is appropriate only with the actual final QA results
and unresolved playtest limits accurately recorded. This is not certification of
fivefold driving time, full vehicle-route traversal, or multiplayer.

### Findings and safe fixes

1. **QA publication text is stale.** `docs/QA.md` still ends with “No game launch
   has been performed yet”, despite the completed first native game run reported
   by the parent. Replace this section before release with actual run IDs, checks,
   screenshots reviewed, and remaining failures/unknowns. Do not count camera API
   mode changes as visual proof or teleports as stair/road traversal proof.

2. **Archive discovery needs a player-facing location guide.** The current
   generated config correctly relocates all thirteen archives into real building
   lobbies, but the mechanic is only an eight-tile right-click context trigger:
   there is no visible archive object, sign, map label or proximity prompt. The
   README's “near district archives” gives no way to identify those lobbies.
   Safe minimal fix: document each district/building and exact coordinates or
   provide an optional spoiler guide. Better follow-up: physical native archive
   props or discoverable map annotations. Some narrative cache hints are flavor,
   not guaranteed matches to the procedural cache-placement rule; avoid claiming
   they are a tested puzzle chain.

3. **Static metadata estimate understates the effective save grid.**
   `tools/audit.py` calculates `24 + 8*192*192 + 10*rooms + 23*buildings`.
   PZ's default WorldGen envelope is typically `[-250..250]`, so the safer estimate
   is `24 + 8*501*501 + 10*rooms + 23*buildings`. With 5,872 rooms and 746
   BuildingDefs this is **2,083,910 bytes**, still comfortably under the 9 MB gate.
   Fix the estimate/label; this does not require rebuilding the native map.

4. **Documented clean test setup lacks a dependency.** `tests/test_runtime.py`
   imports `lupa`, but `requirements.txt` lists only numpy, Pillow and shapely.
   The README's `pip install -r requirements.txt` followed by unittest will fail
   on a clean Python environment. Add `lupa` to a documented developer/test
   requirements file or the existing requirements. Shipped in-game Lua does not
   depend on Python or lupa.

## Direct independent checks

Parent follow-up: archive guide is now `docs/ARCHIVES.md`; developer setup uses
`requirements-dev.txt` including lupa; metadata audit uses the actual 501×501
saved-world envelope, and installer now compares SHA-256 for every file.
Final QA evidence below is maintained separately in `docs/QA.md`.

- All **13 archive coordinates** decoded from generated `00_Config.lua` resolve
  to authored native floors and `hall` RoomDefs. The earlier route-centre archive
  mismatch is fixed in the current `generate.finish` code and generated config.
- All **185 cache coordinates** are unique and contain the actual emitted
  `furniture_storage_02_0` container sprite. No missing container was found.
- Starting SUV square `(640,48640,0)` decodes to genuine asphalt.
- Fuel pump `location_shop_fossoil_01_14` exists in installed B42 definitions,
  has native `fuelAmount=20000`, and is not merely a decorative sign. This audit
  alone does not prove player refuelling/electric-power interaction.
- Sanctuary checks use inclusive final-city bounds and **z>=0 only**. Bunker
  identification rejects nonnegative floors. No code path removes negative-z
  zombies through sanctuary enforcement.
- Bunker creation is first-visit, per-8x8-bucket/floor and persisted. Live loaded
  population cap is 1,600. Player exclusion radius14 and retry-on-future-load
  behavior are disclosed in RUNTIME.md; no duplicate replay seeding was introduced.
- Cache filling preserves vanilla contents, validates item scripts and marks each
  parent object to prevent duplicate fills. Starter SUV uses persisted one-shot
  state and does not respawn destroyed/lost cars.
- Installer targets only the resolved `Zomboid/mods/MeridianLongWayHome` folder,
  keeps an existing copy under project install backups, and does not edit saves
  or user profiles. The parent corrected installation verification to SHA-256
  for every file; final packaging/install receipts retain checksum evidence.
- Known pavilion/crossroad obstruction is not a new finding: the central shaft
  pavilion occupies the local128 crossroads in corner/annex cells; those sites
  need the already acknowledged local detour. The principal city road at y1536
  does not cross a corner-cell shaft.
- No Steam/Boosty publisher exists in this project. Existing support-banner links
  are not a new publication. GitHub publication remains the parent's authorized
  final step; no external publication was performed by this review.

## Archive coordinates (generated snapshot)

All are ground-floor building lobbies; use as an optional spoiler appendix.

| Fragment | District | x | y |
|---|---|---:|---:|
| 1 | Last Light | 544 | 48676 |
| 2 | Alder Crossing | 8869 | 48684 |
| 3 | Bellwether | 14113 | 41638 |
| 4 | Stillwater | 3749 | 39212 |
| 5 | Mercy Junction | 7268 | 29736 |
| 6 | Northline | 20068 | 29736 |
| 7 | Warden Pass | 28775 | 26672 |
| 8 | Station 6 | 24935 | 20272 |
| 9 | White Relay | 23143 | 11824 |
| 10 | Hush Array | 30823 | 10800 |
| 11 | Gatehouse Nine | 38503 | 10800 |
| 12 | Continuity Annex | 41063 | 4144 |
| 13 | Meridian | 48679 | 1520 |

## Enrichment integration review (after original snapshot)

An independent read-only check decoded representative native cells and compared
manifest metadata after the furniture/obstacles integration. It confirmed:

- 150,465 furniture/decor sprite instances (includes paired furniture parts).
- 59 checkpoint anchors, 797 unique roadside salvage objects and no objects in
  the declared five-tile route passage.
- 3,070 authored building-barrier squares, including real plank triggers and
  movable/scrappable crate groups; 494 tunnel salvage objects.
- Native steel-door sprites and roof underlays present in decoded bunker data.
- The cache count increased from the historical185 above to186 after furnishing
  formerly empty large halls; release notes corrected to the new count.

A further source review found that ordinary colorblind preference changes rebuild
V3 atlas style in vanilla. The Meridian vector fallback now wraps that style
boundary, scoped to the actual ISWorldMap widget in a Meridian world. It does not
apply to other worlds, loot maps or the spawn selector; exploration fog remains
untouched. Repeated restyles and cross-world isolation have a regression test.
Actual gameplay and visual evidence are reported separately in QA.md; the above
are structural/source checks, not substitutes for interaction or rendering proof.

## Final expansion publication review

A second independent read-only review checked the final README, release notes,
QA ledger, evidence, notices and Markdown links. It found no blocking publication
contradictions, secrets or private user paths in the publication material.
The 27-test receipt and static audit agree: 2,381 native pairs, 832 surface
structures, 866 total BuildingDefs and 6,270 rooms. Fresh-run FAIL and narrow
reload PASS remain separate, with matching final 4,784-file SHA-256 bindings.

The only packaging-link defect was README's relative MODLOG link, since the
working journal is not bundled. It now points to the source repository.
Earlier counts and findings above are historical snapshots, not final totals.
See [QA](QA.md) for completed game checks and remaining Viewpoint ceiling limits.
