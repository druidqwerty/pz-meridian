# Meridian: The Long Way Home

## Goal / authorization
Original fictional PZ B42.21 standalone journey map. SW spawn -> NE walled,
zombie-free surface city; infected underground government refuge beneath.
User requests installation for testing, GitHub only. NO Steam/Boosty publication.
Retired Real Russia remains retired; only reusable native codecs are reused.

## Contract
- Mod ID MeridianLongWayHome; map Meridian; version 0.1.0-alpha.1.
- World tiles 0..49151 both axes, cell size 256, tile nominal 1 metre.
- Spawn southwestern corner; city x48128..49151,y1024..2047.
- Original 128.256km road planning baseline (~5x installed vanilla diagonal,
  NOT a verified driving-time ratio). Avoid misleading geographic-scale claims.
- Bunker cells 188..191,4..7, z=-1/-2; shafts in four corners at local128,128.
- Native map data only + Lua API. Vanilla sprites, no custom tiles/dependency.

## Work owners / file state
- Parent: tools/world.py, generate.py, atlas.py, audit.py; build/install/release.
- architecture agent: tools/architecture.py,bunker.py; rooms, furniture, stairs.
- runtime agent: mod/42/media/lua and sandbox options; safety, story, seeding.
- QA agent: tools/playtest.py; isolated fresh/reload/Viewpoint smoke.
- Native codec copied from pz-map-tools with original MIT notice retained.

## Current checkpoint
- DONE geometry/native build: 2,299 cell pairs, 720 surface structures, 746 native
  BuildingDefs, 5,872 RoomDefs, 615,985,630 native bytes. Every cell decoded with
  exact tile equality. Metadata part0 370,814 bytes (<9MB conservative budget).
- DONE architecture/bunker/landscaping: verified native sprites, functional loot
  rooms, 4 main shafts, 3 classified annexes, connected negative levels, parklets.
- DONE runtime/story/car/supplies; 9 meaningful regression tests pass.
- DONE native atlas oracle: 2,199 atlas cells / 4,355 features / 0 invalid ranges,
  0 zero-index geometries; maximum3,642 indices/cell (signed-short limit32,767).
- Initial actual-game fresh test PASS: spawn walking, doors, loot, ordinary
  wilderness, final surface0zombies+72below, both underground floors inhabited,
  save created. Menu had vanilla WorldMapVisited sentinel error: product scoped
  Meridian preview fix added, final Viewpoint fresh/reload pending.
- Balance: early-town density reduced after initial real-game count was excessive.
- Next: final Viewpoint/native gameplay gates, install new folder, GitHub prerelease.

## Gotchas
Sparse authored cells rely on native B42 wilderness. Final safe-zone cleanup must
check z>=0: never remove bunker zombies. Actual gameplay evidence is required;
static checks alone are not rendering/vehicle/stair compatibility proof.

## Runtime file checkpoint
- DONE: shared/10_Core policy/config adapter; server/20_Sanctuary z>=0-only fence;
  server/30_Bunkers persistent first-visit underground horde buckets;
  server/40_Supplies one-shot secret cache fill; server/50_Starter repaired SUV;
  client/60_Archives optional context documents; all settings and 13 texts EN/RU.
- Five Lua simulation tests pass: floor boundary/authority, disabled-population
  respect and no duplicate seeding, no duplicate cache fill, one SUV/fuel/key,
  syntax and translation parity. See RUNTIME.md for API source evidence.
- Runtime awaits native game QA, generated 00_Config.lua/site coordinates.
- First native QA found PZ42.21 vector spawn-menu exploration-fog initialization
  crash (uninitialized mainmenu MetaGrid). Added client/65_MapPreview.lua scoped
  ONLY selected Meridian pregame widget; keeps actual ingame fog and othermaps
  untouched. Own4-layer preview + original vanilla zoom/render; all9 tests pass.
