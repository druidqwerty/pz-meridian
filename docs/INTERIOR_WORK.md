# Interior revision work journal — 2026-11-06

## Completed files

- `tools/furniture_orientation.py`: 62 curated native-facing/grid sprite names;
  verified independently against installed B42 metadata. North-wall appliances
  face south, south-wall storage north, complete sofa/bed grids in all used views.
- `tools/interior_layouts.py`: transactional furniture groups, blocked door and
  stair approaches, useful kitchen/bedroom/living/public/storage furnishings.
- `tools/interior_scenes.py`: laundry, workshop, utilities, nursery, gym, assembly.
- `tools/furnishing.py`: compatible `furnish_room(...,base=None,blocked=())` entry.
- `tools/room_lighting.py`: idempotent native type7 circuit, backed wall switch,
  spaced native luminous wall fixtures; no custom runtime lighting behavior.
- `tests/test_interiors.py`:3/3 PASS against native property and codec oracles.
- `docs/FURNITURE_LIGHTING.md`: accurate user-facing changes and technical sources.

## Integration and evidence

- Architecture owner integrated furniture helper and per-room lighting after
  geometry, aggregating `rec.lighting`. Root integrated bunker illumination.
- `test_architecture.py`:3/3 PASS after these integrations, including all current
  building kinds at three seeds, native stairs and connected bunker RoomDefs.
- Existing tests for native furnishings/complete singleton props passed. A
  temporary barricade-count failure was caused by architecture work in flight;
  that owner reinstated native window plank frames.
- Actual night room-circuit ON/OFF proof is delegated to root/live QA. Do not
  call bytecode/property acceptance an in-game lighting pass.

## Gotchas

- `RoomDef.objects` serialization needs CELL-local coordinates, not offsets
  relative to the room. Loader applies cell offset then subtracts room origin.
- Non-RGB wall switches control `IsoRoom` lights. RGB lamps are independent
  bulb-bearing point-light objects, and `getLights()` on the room switch alone
  is not proof that the room's ambient light exists.
- Python runtime with dependencies is `../pz-map-tools/.venv/Scripts/python.exe`.
- Changing a physical switch without adding type7 metadata leaves room-light
  availability dependent on loaded switch chunks; alpha.1 had empty objects.

## Next step

Parent performs final full regression/build/live night-switch screenshots,
checks furnished rooms and updates QA/release based on observed results.

## Additional owner steering — public realm

- Reworked `landscape.py` to make two-wide sidewalks across0/255 cellseams for
  ALL inhabited sites. Real asphalt unchanged; trees yield only to walking
  surfaces. BFS connections avoid entire building masks. Actual reserveShaft
  flag replaces the old unconditional centre reserve that broke town curbs.
- New `public_geometry.py`: reusable mask dilation/exterior routing/parkingbanks.
- New `building_signs.py`:complete native purpose-specific facade sign groups.
- New `public_realm.py`:site.parking/plazas CELL-local rectangle schema,
  hardscape/aisle-preserving concrete, white parking lines, off-lane posts,
  actual perimeter light posts and facade identity.
- New `test_public_realm.py`:4/4PASS native signs/clearances/parkingcontinuity;
  `test_content.py`:3/3PASS including four district street reachability.
- Fixed test oracle regex to admit real hyphenated native sprite names; old
  \w-only parser silently ignored `signs_one-off_*` sheets. Product audit's
  native-name parser already handled these correctly.
- Root owns actual site plan, manifest stats and final live night/parking QA.
- Architecture owner coordinates reusable helper export to pz-map-tools only
  after parent validation; no retired map generation or installation authorized.
