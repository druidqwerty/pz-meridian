# Realizable American town and city references

Research for the owner's November 6 visual correction request. References were
retrieved on 2026-11-06; they guide original layouts, not copied game buildings.
This document is a design/acceptance brief, **not evidence of implementation**.
Only ordinary vanilla B42 map sprites, physical floors, doors and stairs are in
scope. No downloaded photographs, game artwork or third-party map assets ship.

## Fetched references and concrete translations

| Reference | Useful observed principle | Native-map translation | Do not claim |
|---|---|---|---|
| [NPS: Pullman history and culture](https://www.nps.gov/pull/learn/historyculture/index.htm) | A planned industrial community combines works, administration, hotel, church, park and housing, rather than only housing. | Give an industrial settlement a repair/depot yard, administration, workers' homes, lodging and a small public building; distinguish service courts from residential lots. | A faithful reconstruction of Pullman or its ornate administration tower. |
| [American Main Street](https://en.wikipedia.org/wiki/Main_Street) | The primary small-town retail street concentrates shops, services and social activity. | Cluster several small shopfronts and a diner around a walkable main street; give larger school/police buildings their own lots behind/alongside it. | Every business is a trading NPC or active economy. |
| [Shotgun house](https://en.wikipedia.org/wiki/Shotgun_house) | A narrow frontage and rooms arranged one behind another create a visibly different domestic plan from a square house. | Use narrow small dwellings, deeper lots, different room sequences and a clear front-to-back route; mix with wider ranch houses and duplexes. | Historical authenticity, or calling every long rectangular house a shotgun house. |
| [Strip mall](https://en.wikipedia.org/wiki/Strip_mall) | Several independently entered shops share a frontage and pedestrian path, with parking in front; small centres mix grocery, laundry and food/services. | A low shopping row with separate doors, storage/service rooms and a shared open apron. This is deliberately different from an isolated square grocery. | A functional parking simulation, guaranteed vehicles, or a giant indoor mall. |
| [Downtown Louisville](https://en.wikipedia.org/wiki/Downtown_Louisville) | A street grid contains civic, medical and retail areas, old narrow two-to-four-storey buildings and a concentrated taller skyline. | Keep a varied low/mid-rise street layer under groups of accessible apartment/office towers; reserve identifiable medical, civic and industrial blocks instead of repeating one tower. | A copy of Louisville, its exact skyline or real-world skyscraper heights. |
| [Police station facilities](https://en.wikipedia.org/wiki/Police_station) | Reception, staff workspace, lockers, secure storage and vehicle access serve different functions; stations are not ordinary homes. | A public front office, separated staff rooms and storage, with a service-side yard. Use verified native room distributions rather than fake loot labels. | Working detention, police NPCs, scripted law enforcement or a new armoury system. |

The source pages above were fetched successfully over HTTPS. Two guessed NPS
article URLs returned 404 and were discarded; they are not cited as references.

## Route-level composition

The visual progression should be measured along the long principal road, not
just by world X/Y. A site near the end of a winding road may be geographically
close to an earlier site, without belonging to the same architectural stage.

1. **Last Light / early rural towns:** mostly one/two-storey houses with genuinely
   different footprints, small garages, shops and civic buildings. A police
   station and school should be recognizable by their own plan and scale.
2. **Agrarian and industrial stretches:** farm/service courts, workshops,
   warehouses, small retail and occasional larger lodging/administration.
3. **Later regional centres:** a visible share of mid-rise apartments/offices,
   mixed with small houses and public/service buildings, not a uniform skyline.
4. **Restricted approaches:** checkpoints, watch/guard huts, barracks and supply
   courts remain legible; larger administration/lab blocks need not be houses.
5. **Meridian:** many taller blocks grouped into recognizable districts, with
   lower street-front shops, schools, police/medical premises and service yards.
   The exact floor cap must remain within the verified native codec and tested
   renderer/stair limits. A tower is not accepted merely because `levels` is high.

## Interiors and fortification acceptance

- Every furniture arrangement must have an intentional viewing/working direction:
  seating toward tables/TVs, complete bed pairs with usable sides, appliances
  against a wall with their usable face toward the room. Verify the actual
  vanilla `Facing` and grid properties, not sprite-number arithmetic.
- The large unused portions of ordinary rooms should become activity clusters,
  smaller rooms or useful circulation. One flowerpot does not furnish a hall.
- Each real room needs native switch/light metadata and visible appropriate
  fittings. Verify at night with the diagnostic torch off, then toggle a native
  room switch; a light sprite by itself is not proof of illumination.
- The wall needs an actual wide cross-section and a taller continuous silhouette,
  not several coincident wall sprites. Gate depth, approach lanes, corner joints,
  walkways and a safe accessible stair must be checked physically.
- Representative cities should be compared from an isometric overview as well
  as close interiors. First-person camera assertions alone do not prove variety.

## Map-content portions of the earlier development plan

The original full proposal is not assumed to be fully implemented. Existing
project records [EXPEDITION](EXPEDITION.md), [HABITAT](HABITAT.md) and the generated
[coordinate guide](EXPEDITION-LOCATIONS.md) preserve the accepted map-only scope:

| Plan family | Map-only interpretation to preserve and improve |
|---|---|
| Seven road chapters | Early town, farmland, industry, reservoir, forest plateau, restricted territory and final Meridian should look and play spatially different. |
| Main/regional/service roads | Keep the long principal road; detours return locally and compound spurs do not shortcut distant chapters. |
| Landmark compounds | Dam, postal distribution centre, test homes, sanatorium, evacuation terminal, archive, relay, quarry repairs, water intake and construction museum need function-specific layouts. |
| Roadside rhythm | Motels, veterinary practice, chapel, salvage, weigh/truck stops, visitor centre, campground, rest area, maintenance depot and registration camp break up the journey. |
| Expedition bases | Physically usable garages, farmstead/service houses and observation/forest posts; no auto-claim or new resupply system. |
| Environmental story | Existing archives, convoy traces and abandoned possessions; no quest journal, pass-card progression, radio or special-enemy mechanics. |
| Underground town | Distinct domestic, medical, school, utility, storage and administrative wings; several physical routes and entrance roles. |

The current request adds a stronger city/skyline requirement and explicitly
rejects the old repeated four-room building as adequate visual differentiation.
Earlier published counts describe the previous alpha, not acceptance of this pass.

## Verification boundary

`tools/urban_targets.py` prepares representative live visits and a separate
acceptance checklist from the new manifest. That is test preparation only.
Root/integrator owns actual screenshots, night-light toggles, stair traversal,
wall inspection, regression results and the final installation/release decision.

### Private oracle interface

- Run `python tools/urban_targets.py` after the new full generation. The previous
  alpha's manifest is useful only to check that missing features produce warnings.
- `stairTests` accepts cell-local or absolute `start`/`end` (`from`/`to` also
  accepted). The top occupied-floor visit uses the final stair landing rather
  than guessing that a ground-floor plan repeats unchanged at the top.
- Building `lighting` entries select `kind: switch`, not a point-light lamp.
  `playtest.py` consumes a target `lighting: {x,y,z,sprite}` through the test-only
  `lighting_probe.py`; both stay outside product Lua and release installation.
- The probe verifies the exact native switch and its room registration, turns
  off the private diagnostic torch, sets the private world to 23:00, holds an ON
  frame for eight seconds and an OFF frame for eight seconds, captures each, then
  restores switch state, time and torch. Exception cleanup also restores them.
- It records actual square brightness and requires a positive ON/OFF difference.
  A mere successful switch toggle cannot pass `native_illumination_observed`.
  Native switch registration is checked with exposed getters; public Java fields
  such as `roomLights` are not Lua properties and are deliberately not accessed.
  Screenshots still require review.
- Optional target `zoom` uses the vanilla isometric zoom controls. Standard visits
  hold the screenshot before teleporting onward, avoiding asynchronous captures
  of the next target. All diagnostic changes are confined to an isolated cache.
- No lights, bulbs, generators or power are created by this oracle. It cannot
  repair a broken product while supposedly testing it.

### Native sprite registry, not just text metadata

`sprite_probe.py` reads every used name from the actual bound LOTHeaders and
checks `IsoSpriteManager.instance:getNamedMap():containsKey(name)`. It never calls
`getSprite(name)` as an existence test: B42 creates a placeholder for absent names.
A synthetic missing-name control remains absent and registry size is unchanged.

Textureless ordinary sprites fail. Native trees are a narrow semantic exception:
the sprite must have native `IsoObjectType.tree` type and a `tree` size in 1..8.
The engine's `CellLoader` explicitly handles this branch before its ordinary
texture rejection. `NatureTrees`/`ErosionObj` subsequently replace these proxies
with seasonal-stage artwork. Such proxies are listed separately, not described
as missing art or removed merely to satisfy an overstrict test.
