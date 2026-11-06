# Expedition content pass — map geography only

This pass takes the map-content portions of the owner's development brief.
It adds no quest journal, access-card system, radio system, generator simulation,
special vehicle rules, new items, victory screen or random-event controller.
All new rooms, doors, roads, furniture and outdoor supplies are ordinary native
map data. The previous principal road, starting SUV and sanctuary boundary remain.

## Seven road chapters

The chapters follow distance along the existing128.256km main road, not a straight
southwest/northeast coordinate gradient. The names are geographical themes, not
seven gated missions. Existing settlements are retained.

| Chapter | Route distance | Map identity |
|---|---:|---|
| Last Light / Ласт-Лайт | 0–10.3km | Start town, expedition garage and motel |
| Agrarian Valley / Аграрная долина | 10.3–30.8km | Farmstead, veterinary rooms and chapel |
| Industrial Belt / Промышленный пояс | 30.8–50.0km | Mail sorting, repair yards, quarry stores and weigh station |
| Reservoir Country / Большое водохранилище | 50.0–70.5km | Dam impoundment, visitor stop, campground and utility house |
| Forest Plateau / Лесное плато | 70.5–89.8km | Remote archive, relay, sanatorium and forest base |
| Restricted Territory / Закрытая территория | 89.8–120.6km | Test homes, terminals, registration camp and observation post |
| Meridian / Меридиан | 120.6–128.3km | Water intake, final approach and a home within the city |

These themes do not create elevated terrain. The quarry is a native dirt/material
yard and workshop complex, not a new excavated-height terrain feature. The dam
uses an authored impoundment and flat embankment/causeway rather than a custom
animated or elevated hydroelectric model.

## Three connected road classes

- The original primary road remains128,256tiles long and is not shortened.
- Six regional detours return to the same principal-road segment. Each bypasses
  only1,024tiles of main road; the detour itself is longer. They do not join distant
  chapters or erase the long journey.
- Twenty-eight compound service spurs lead to dry independent sites. Twenty-five
  also have a second local exit returning to the main road256tiles from the first.
  The three single-entry compounds still have broad native cross lanes and yards.
- The native atlas includes primary, secondary and service-road geometries.
  These are map roads, not a route-selection menu or a new navigation mechanic.

Static tests check dry building footprints, service-road joins, retained road
clearance and ordinary pedestrian reachability of every landmark entrance.
These are not substitutes for a complete live driving run in multiple vehicles.

## Ten landmark compounds

Coordinates below are compound-centre junctions, not teleport destinations or
guaranteed room spawn points. The distinct compounds use several original native
buildings around different courtyard/loading arrangements.

| Landmark / Объект | Centre x,y | Physical composition |
|---|---|---|
| Sluice Seven Dam / Дамба «Шлюз-7» | 14976,29312 | Utility halls, stores, office, repair rooms, water impoundment and broad embankment |
| Dead Letter Distribution Centre / Почтовый центр | 2944,35968 | Sorting/storage halls, staff rooms and crate/locker loading bands |
| Instrumented Residential Block / Испытательный квартал | 25728,10368 | Four identical homes, observation laboratory and separate supply yard |
| Still Pines Sanatorium / Санаторий «Тихие сосны» | 22656,19584 | Residential/treatment blocks, laundry, service laboratory and planted court |
| Unopened Evacuation Terminal / Терминал эвакуации | 41344,10624 | Two boarding buildings, control post, treatment rooms and staged building supplies |
| Regional Records Archive / Региональный архив | 28288,25472 | Reading rooms, records storage, administration and records-loading apron |
| Crown Relay Station / Ретранслятор «Корона» | 27520,19840 | Communications building, stores, workshop and staff homes |
| Breakwater Quarry Repair Base / Карьерная база | 3456,29312 | Material yards, separate workshops, depot and administration |
| Meridian Water Intake / Водозабор Meridian | 43392,1152 | Twin utility buildings, equipment/service yards and checkpoint |
| Museum of Regional Construction / Музей строительства | 40576,4224 | Exhibition/public rooms, library, offices, garden and maintenance display yard |

Quarry machinery, dam power and relay communications are environmental scenery,
not newly controllable systems. Room furniture uses the building's function;
loot remains governed by native room distributions and existing sandbox rules.

## Twelve differentiated roadside stops

| Stop / Остановка | Centre x,y |
|---|---|
| Red Lantern Motel / Мотель «Красный фонарь» | 7552,48256 |
| Valley Veterinary Practice / Ветеринарный пункт | 13696,47488 |
| Roadside Memorial Chapel / Придорожная часовня | 13952,38784 |
| Spare Mile Salvage / Авторазборка | 5760,38784 |
| Northbound Weigh Station / Весовая станция | 2944,32640 |
| Freight Rest Truck Stop / Стоянка дальнобойщиков | 8576,29312 |
| Lakeside Visitor Centre / Туристический центр | 18816,29312 |
| Reservoir Campground / Кемпинг | 25216,29312 |
| Forest Rest Area / Лесная площадка отдыха | 28288,22912 |
| Plateau Road Maintenance Depot / Дорожное депо | 22656,17024 |
| Sector Bus Interchange / Автобусный терминал | 32128,10368 |
| Final Registration Camp / Распределительный лагерь | 40576,6784 |

Campgrounds use native shelters, kitchens, bedrooms, picnic benches and storage,
not custom tents with a separate camping system. A salvage yard supplies the
setting/workspaces; this pass does not add vehicle-spawning scripts.

## Seven potential expedition bases

No base is automatically claimed or made zombie-free. The player can use the
ordinary game's habitation, storage, carpentry and vehicle mechanics.

| Base / База | Centre x,y | Trade-off |
|---|---|---|
| Last Light Expedition Garage / Стартовый гараж | 896,48256 | Repair/storage rooms near the beginning; separate from the starting SUV |
| Alder Expedition Farmstead / Фермерская усадьба | 13696,42368 | Domestic rooms and broad rural yard, off the main road |
| Industrial Road Depot / Дорожное депо | 2944,30080 | Workshop/storage first, little civilian shopping |
| Reservoir Staff House / Дом персонала | 22144,29312 | Overnight rooms alongside utility/storage buildings |
| Forest Expedition Station / Лесная станция | 25472,19840 | Remote shelter and service yard between forest stops |
| Former Observation Post / Наблюдательный пост | 35456,10368 | Restricted-zone supply yard and several approaches |
| Meridian Expedition Home / Дом в Meridian | Existing city residence | Select an ordinary house inside the established safe surface boundary |

The seventh base reuses the existing city residence stock instead of placing an
overlapping second compound over authored city blocks. None of these places adds
new guaranteed working water/power or a scripted resupply loop.

## Verification boundary

`tests/test_expedition.py` checks28new compounds, the seven chapter assignment,
ten distinct landmark layouts and physical setpieces, native sprite existence,
dry building footprints, connected three-class roads, unchanged main-road length,
unmodified road tiles after decoration and every landmark entrance's reachability.
The final build/live-game run and release evidence are owned by the integrator
and recorded in `QA.md`. This source-level content note does not certify those
later checks or claim the original long-form campaign proposal is fully polished.
