# Entrance pavilions: useful contents and physical wayfinding

This is native map content, not a new HUD marker, quest or teleport system.
The player-facing approach and all entrance coordinates are in
[BUNKER-ACCESS](BUNKER-ACCESS.md). The route illustration is not a game screenshot.

## Inspection findings

The sixteen underground wings already separate medical care, recovery, research,
isolation, reception, school/community, family living, water/domestic services,
logistics, shared kitchens, recreation, power, maintenance, administration,
communications and reserve accommodation. Their two floors intentionally keep
their respective institutional identities instead of turning every basement
into the same laboratory. This pass does not add another unexplained institution.

The entrance pavilions were the obvious weak point: only three props stood in a
24x24 hall, the actual descent was not distinguished from an empty floor opening,
and the medicine cabinet in medical pavilions had no supporting wall. An entrance
guide is also needed because an isometric screenshot's screen directions are
not north/east map directions.

## Native additions

`tools/bunker_wayfinding.py` decorates the already constructed pavilion:

- A contrasting two-tile floor-finish strip leads from the south-door approach
  to the **west** upper stair landing. It replaces only an existing floor finish;
  it never adds a floor across the three-square stair opening.
- Two original vanilla illuminated EXIT signs have real solid north-wall
  support, one on the surface and one in the B1 return zone. They display the
  game's EXIT art, not custom text or a fictional directional arrow.
- Two separated side alcoves receive reception/waiting, medical, work/storage,
  archive or communications clusters according to that entrance's actual role.
  The same facing-aware, transactional furniture placer used in buildings keeps
  whole sofas/beds together and leaves the central door/stair route clear.
- The exact legacy floating medicine cabinet is moved onto a real north wall;
  unrelated furniture and all native door/switch metadata are preserved.
- Exterior restricted-area signage belongs to the separate native public-realm
  sign helper; it is not duplicated here.

The helper returns absolute coordinates and observed counts under `wayfinding`.
It is idempotent: repeating it does not accumulate extra furniture or change
floors back and forth. No user save, installed game art or runtime Lua is touched.

## Verification

Executed `test_bunker_wayfinding.py` on 2026-11-06 using installed B42 metadata:
one parameterized test across **all twelve main entrance cells**, PASS (15.1s).
It checks existing native sprite names, unchanged square keys, unchanged surface
and deep stair holes/parts, door-to-upper-landing collision reachability, the B1
route to the deeper upper landing, furnishings and repeat-decoration stability.

These are structural checks. They do not certify final appearance or substitute
for a real traversal and screenshot review. `bunker_access_guide.py` also emits
`build/test-bunker-entrances.json`: twelve ordinary `ISWalkToTimedAction` descent
targets for the isolated oracle. Current executed game evidence belongs in
[QA](QA.md); a prepared target file is not a claim that those visits happened.
