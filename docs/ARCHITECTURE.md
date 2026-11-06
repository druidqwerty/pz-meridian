# Meridian native architecture

**Historical alpha.1 baseline.** The catalogue, dimensions, repeated four-room
layout and test timings below describe the previous build, not 0.2.0. Current
architecture is documented in [URBANISM](URBANISM.md),
[furniture and lighting](FURNITURE_LIGHTING.md), [public realm](PUBLIC_REALM.md)
and the versioned [QA ledger](QA.md). Native format/stair principles still apply.

Original fiction and layouts; no Real Russia content, copied Real USA
buildings, extracted artwork, or custom tile dependencies.

## Surface catalogue

`tools/architecture.py` exposes `build_structure(tiles, rooms, buildings,
x, y, kind, seed=0)`. Input geometry is cell-local (`0..255`). It supports
house, cottage, apartment, shop, fuel/gas, military, barracks, lab, hospital,
clinic, civic, school, warehouse, and police. Normal footprints are 16x14 to
30x28, plus a two-tile sheltered entrance apron. South-facing entrances open
into a five-deep lobby, with a three-wide axial circulation hall. Four named
rooms have actual partition walls and doors, not just room metadata.

- Timber, stone and two brick facade variants; rhythmically spaced windows.
- Different footprints, one to three floors, sheltered entrance canopies.
- Residential timber flooring; white tiled service rooms; genuine ceilings.
- Furniture matches room function, with complete paired beds and medical beds,
  kitchens, plumbing, office desks, classroom seating and storage.
- `tools/furnishing.py` adds role-specific activity clusters: bedside cabinets
  and lamps, televisions, radios, kitchen appliances, computer desks, phones,
  microscopes, medical carts/bloodbags, showers/medicine cabinets, supply crates,
  plants, table flowers and bins. Residential seating/drawers vary by seed.
- Lobby ends have seating and furnishings while the axial path, entrance and
  stair flights stay clear. Some alcoves and facade edges have wood/metal crate
  barricades, using vanilla `IsMoveAble` + `CanScrap` + material definitions.
- Some ground-floor windows have genuine two/three-plank barricades, authored
  with vanilla `MOBarricade.lua` trigger sprites. That loader converts the frames
  into `IsoBarricade` objects; they are not decorative wood pasted over windows.
  The south-side trigger lies one square north of its north-edge window. Main
  entrances and interior circulation doors are never boarded shut.
- Vanilla `Distributions.lua` room names govern normal room/container loot.
- Every seventh seed places a guaranteed metal-container cache in a room.
- `spawn`, `entrance`, `rect`, `caches`, and `barricades` are local; the generator
  promotes them to absolute world coordinates. Both point lists use `[x,y,z]`.

## Continuity habitat

`tools/bunker.py` exposes `build_bunker(tiles, rooms, buildings, cx, cy, config)`.
`config` contains inclusive `minCX`, `maxCX`, `minCY`, `maxCY` native cell
bounds. Outside these bounds it returns empty entrance/cache lists.

Both levels (-1 and -2) have linked six-wide full-cell axial galleries, a
24x24 central lobby, and four large wings. Wings alternate furnished smaller
compartments with 96x96 large halls or laboratory spaces. The roles include
residential dormitories, kitchens, hospitals, military storage, laboratories,
and medical supplies. Furniture is repeated in separated bays with clear
aisles, rather than left only along a distant outer wall.

All adjacent cells share open tunnel seams. External seams are sealed. Each
cell has an actual stair flight between -2 and -1. The twelve perimeter cells
also have masonry surface entrance pavilions, with a physical stair flight
down from the surface. A one-cell configuration produces one entrance.

Reserve surface local rectangle `[120,120,24,24]` plus its east/south walls
at coordinate144. Call bunker generation after terrain and surface buildings:
it removes the three upper-floor squares over each surface stair. Perimeter
entrances land at absolute `cx*256+127, cy*256+128, 0` and their lower approach
is `cx*256+131, cy*256+128, -1`. The -2 -> -1 flight is at local y136.

Returned `entrances` and `caches` use absolute coordinates. Caches are dicts
`{x,y,z,kind}` and always refer to an emitted metal container. `area`, `levels`,
`stairs`, and `tunnelAxes` are diagnostic metadata. Each cell's underground
rooms form one BuildingDef; each entrance pavilion forms a second BuildingDef.

The former unfurnished large public halls now use the same separated furniture
bays as the living/medical wings. The `hall` furnishing role provides rest areas,
tables, radio points, shelving and plant clusters without filling circulation.

## Verification

Executed on installed Project Zomboid42.21 metadata, 2026-11-06:

```
python -m unittest discover -s projects/pz-meridian/tests -p test_architecture.py -v
Ran 3 tests in 2.084s — OK
```

These are independent structural acceptance checks, not claimed gameplay proof:

1. Every building kind, seeds0/1/7: all sprites exist in installed native tile
   definitions; all room names exist in vanilla distributions; every room on
   every floor is traversable through openable doors; stair geometry has
   complete bottom/middle/top parts, floor holes and upper landings.
2. Corner and interior bunker cells: all rooms are connected to the lobby,
   all four seam approaches are reachable, stair approaches are clear, room
   rectangles do not overlap, cache containers exist, and surface holes are cut.
3. Full native LOTHeader/LOTPack write/read preserves tiles and negative-level
   room data exactly.

Sprite properties are read directly from local `media/*.tiles.txt`; game
definitions are never bundled. Roofs use a verified vanilla flat-roof floor,
not speculative pitched geometry. Rendering, multiplayer, light brightness,
vehicle access, and loot rolls still require the parent's in-game playtest.

## Enrichment acceptance (2026-11-06)

The later map-only expedition pass adds `content_catalog.py` programmes,
`themed_rooms.py` ordinary-life scenes, `expedition*.py` compound geography,
`habitat.py` wing identities and `story_scenes.py` physical archive/convoy props.
Native room names retain actual vanilla loot distributions (including laundry
and gym); furniture themes are separate from those names. The generator writes
`build/content-summary.json` and an authored coordinate guide, and rejects any
missing planned compound building. See EXPEDITION.md/HABITAT.md for scope.

`tests/test_furnishing.py` adds three independent local-data acceptance checks:

1. Every added furnishing exists, is moveable, and is a complete single-square
   sprite (no missing parts of sprite-grid objects). Wood/metal barrier crates
   expose real salvage material and collision properties; the wooden crate uses
   vanilla Hammer pickup/placement.
2. All authored wooden window frames map to registered vanilla `MOBarricade`
   handlers and an actual adjacent window, across every building kind and six
   seeds. The principal entrance remains unboarded.
3. Every room function, including public halls, receives multiple furnishing
   types; buildings vary by seed while their rooms remain reachable.

These tests pass against the installed B42.21 metadata. They do not replace the
separate live-game pickup/unbarricade and appearance checks in `docs/QA.md`.
