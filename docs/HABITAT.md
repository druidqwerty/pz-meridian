# Continuity: an underground town, not sixteen identical laboratories

This pass changes **native map content only**. No quests, pass cards, door locks,
power-restoration systems, special enemies or new runtime mechanics were added.
The existing infected B1/B2 floors and zombie-free surface rules are unchanged.

## Wing layout

Each table entry is one 256-tile native cell; both underground floors belong to
the same institution. The rows run north to south, columns west to east.

| Cells (y) | x188 | x189 | x190 | x191 |
|---|---|---|---|---|
| 4 | Reception hospital | Recovery/staff | Research | Isolation |
| 5 | Public reception | School/community | Family homes | Water/domestic services |
| 6 | Cargo/food stores | Residents/shared kitchens | Residents/recreation | Power distribution |
| 7 | Repair/emergency crews | Records/administration | Communications/directorate | Reserve shelter |

Residential cells contain bedrooms, kitchens, living rooms and ordinary domestic
facilities, not automatic laboratories on their lower floor. School/community
rooms include classroom furniture, a nursery, library, changing lockers and open
exercise/assembly areas. Utility and management wings use workbenches, storage,
laundry, sinks, filing cabinets and communications desks. These are ordinary
vanilla props; utility appliances do not imply a simulated infrastructure system.

Hall/living floors use six verified vanilla material palettes: white/grey/dark
grey/purple tile and two wood treatments. This marks the wing architecturally
without adding fake text signs or custom art. Functional-room tile remains where
appropriate. The sixteen `wing` entries and room furnishing roles are recorded in
the build manifest, separately from real vanilla loot-distribution room names.

## Twelve different ways in

Every entrance still uses the original physical stair at local `(128..130,128)`.
The surface approach/landing reference is local `(127,128)`. Add the cell origin
`(cellX*256,cellY*256)` to obtain world coordinates. Nothing teleports the player.

| Cell | Entrance role | Leads into |
|---|---|---|
| 188,4 | Medical reception | Hospital/triage |
| 189,4 | Hospital staff | Recovery rooms and staff facilities |
| 190,4 | Research | Research rooms, records and staff facilities |
| 191,4 | Isolation emergency | Isolation/observation wing |
| 188,5 | Public arrival | Reception and public services |
| 191,5 | Water-service | Water/domestic-service rooms |
| 188,6 | Cargo receiving | Storage, kitchens and workshop |
| 191,6 | Power-service | Distribution and repair rooms |
| 188,7 | Repair crews | Maintenance and emergency accommodation |
| 189,7 | Records/administration | Records and offices |
| 190,7 | Communications | Communications/directorate |
| 191,7 | Reserve evacuation | Reserve accommodation and stores |

The surface pavilions now have receiving-area props appropriate to their use:
medical supplies, freight crates, filing/communications or waiting furniture.
Their broad centre, south doors and stair approaches remain clear. All twelve
roles have English/Russian metadata names. This does **not** claim that new
localized text signs are displayed on the ground. Three isolated annexes remain
research facilities rather than duplicating the main town's entrance scheme.

## Real alternate routes

The original six-wide north/south and east/west cross-cell galleries, steel fire
doors, salvage barriers and both stair coordinates are preserved. A new four-wide
service ring at local bounds `(12,12)..(243,243)` connects all four gallery arms.
Internal column aisles connect room blocks to it. Every small room has a second
physical side door; larger halls have separated side doors. These loops let an
explorer avoid the centre without solving a new scripted puzzle.

## Evidence and limits

`tests/test_habitat.py` checks all sixteen built cells against installed B42
sprite metadata and loot-distribution room names; it verifies ordinary domestic
and technical furnishing, all twelve entrance identities and the original native
stairs. A separate physical collision/door graph removes the central junction and
checks that the service ring still joins all four arms. A third check verifies
two real room exits and original seam/stair reachability. Existing architecture,
codec and obstacle tests also pass after this change.

These are **structural tests**, not proof of real player traversal, all camera
angles or multiplayer behavior. Final live evidence belongs in [QA](QA.md).

## По-русски

Убежище разделено на шестнадцать функциональных частей: приёмный госпиталь,
реабилитация, исследования и изоляция, общественный центр, школа и детские
комнаты, семейное жильё, бытовые службы, склады, отдых, ремонт, архив и связь.
Назначение сохраняется на обоих этажах. Добавлены обычные прачечные, душевые,
мастерские и общественные помещения — без механики восстановления узлов.

Двенадцать поверхностных входов получили разные роли и обстановку приёмных.
Физические лестницы остались на прежних местах. Четырёхтайловое служебное кольцо
и дополнительные двери дают обход центрального перекрёстка; основные галереи,
металлические двери и проходимые лестничные площадки сохранены. Заражённое
подземелье и безопасная поверхность остаются разными зонами.
