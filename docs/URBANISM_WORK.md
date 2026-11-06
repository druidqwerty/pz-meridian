# Urban architecture work journal — 2026-11-06

## Scope

Owner rejected repeated empty house plans. Replace genuine geometry, not labels;
add compact homes, different service buildings and a metropolitan final skyline.
Later steering adds large shopping centres and gun shops.

## Files completed

- `tools/building_layouts.py`: 53-kind programme routing, compact domestic hall,
  L-plan ranch court, variable-room service, education, medical, residential and
  office programmes. Doors chosen on actual circulation adjacency.
- `tools/mall_layout.py`: original96×72two-storey mall, cross-concourse, service
  corridor, independently accessible retail, food/kitchen and staff rooms.
- `tools/architecture.py`: footprint-derived exterior walls/roof, physical native
  stair flights, floor-dependent layouts, furniture reserved by actual doors,
  real room circuits/switches/fixtures via furniture agent helper. Preserves
  ordinary window barricades and dedicated archive desks. Native three-part
  garage doors and separate strip-mall storefronts; complete native mall signs.
- `tools/content_catalog.py`: new kinds/dimensions and high-rise-majority city
  programme. Four district names and important waterworks/home stock retained.
- `tests/test_urban_buildings.py`: six acceptance checks described below.
- `docs/URBANISM.md`: bilingual implementation and verification scope.

## Verified independently of full compile

Interpreter: `../pz-map-tools/.venv/Scripts/python.exe` (default system Python
does not have Shapely; no duplicate environment or runtime modification made).

- `test_architecture.py`: 3PASS; all53kinds and three seeds checked for existing
  sprites, reachable RoomDefs, native stairs, upper holes and cache containers.
- `test_furnishing.py`: 3PASS after restoring retained native boarded windows.
- `test_content.py`: 3PASS; city stock, street access, archives and convoy props.
- `test_urban_buildings.py`: 6PASS; real high-rise majority; actual ranch court;
  compact cottage circulation; complete garage-door triplet and clear bay;
  separate public strip-mall storefronts; both mall storeys reachable, separate
  native programmes and type7 light metadata; gunstore/gunstorestorage + gunracks.

## Interfaces handed to parent

- `build_structure` signature unchanged. Return `rect`/`spawn` unchanged.
- `lighting` contains cell-local dict coordinates from the lighting helper.
- `stairTests` contains cell-local `{'from':[x,y,z], 'to':[x,y,z]}` flights.
- Parent promotes lighting/stair coordinates in generator records.
- `city_program` keeps 16 lots/cell, all normal kinds fit <36×36 footprints.
- `bigboxmall`96×72×2 is dedicated-site-only, not selected for city grid lots.

## Remaining owner

Parent owns full build/install, live-game proof, release docs/counts and packaging.
Do not call this static work in-game verified until that parent QA is complete.
