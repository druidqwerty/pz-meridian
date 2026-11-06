# Streets, commercial forecourts and navigation

## Pedestrian continuity

Every inhabited site gets two-wide paved sidewalks following its real asphalt
roads, including towns, service compounds, military/research sites and Meridian.
They extend to native cell coordinates0 and255; the previous six-square blank
margin no longer breaks pavements between adjoining cells. Native roads are
left drivable and unchanged. Crossings use the ordinary road surface.

Door aprons connect to these sidewalks with obstacle-aware cardinal paths,
instead of drawing an L that might run through another building. Paths clear
ordinary vegetation only, never walls, furniture, doors or existing road props.
Paved paths and the city's entrance-pavilion reserves remain free of garden
trees, benches and planters.

## Large commercial sites

Dedicated mall cells use broad concrete parking rectangles and separate tiled
front plazas. The site plan declares actual CELL-local `parking` and `plazas`
rectangles. The hardscape decorator respects the mall/adjacent shops, native
asphalt access aisles, water and the actual shaft reservation, when present.

Native white line overlays mark parking banks with seven-square bays and
eight-square drive aisles. Clear perimeter circulation is retained. Native
powered lamp posts line the perimeter, not the drive aisles. Floors and white
paint are walkable; lamp posts and signs retain their normal native physics.
There is no scripted parking/traffic simulation.

## Visible building identity

Complete vanilla sign groups identify police, medical buildings, educational
facilities, stores, fuel stops, diners, laundries, books, hunting supplies and
military/restricted buildings. The native mall sign is lit. Homes are not
given inappropriate commercial signs. These are existing PZ sign designs, not
custom city names or newly generated billboard art.

Facade lettering is mounted as a complete group on a supporting south wall,
never by deleting a door. Street-name/STOP posts stand behind the sidewalk,
not in vehicle lanes. Bunker pavilions can use the same `place_building_sign`
API after their native walls are built, and separate wayfinding connects the
surface approach to the real stair.

## Verification boundary

`tests/test_public_realm.py` checks cell-seam continuity, vegetation clearance,
road/building preservation, obstacle-avoiding paths, more than20,000 concrete
squares in the representative mall lot, real drive aisles and complete native
sign `SpriteGridPos` groups. All four tests pass. Existing four-district road
access/convoy tests also pass. Night appearance and actual commercial-site
screenshots remain the responsibility of the current live QA documented in
[QA.md](QA.md); static tests alone do not certify visual polish.

## Reusable tooling

`public_geometry.py` contains sprite-independent dilation, obstacle-aware
pedestrian routing and parking-bank geometry. `building_signs.py` and
`public_realm.py` add the native sign and hardscape adapters. They can be reused
for future fictional maps without preserving or reviving any retired setting.
