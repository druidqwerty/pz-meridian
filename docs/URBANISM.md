# Urban rebuilding / Переработка застройки

## English

This pass replaces the single four-room template used for almost every building.
Native rooms, physical walls, doors, floors and actual westward stair flights are
generated from different programmes rather than changing a label over one plan.

| Programme | Physical differences |
|---|---|
| Cottage/house | Compact entrance hall; asymmetric kitchen/living and bedroom/bath wings |
| Ranch | Larger one-storey L-plan with an actual open rear court |
| Duplex | Two-storey paired domestic suites; eight rooms off circulation per floor |
| Row house | Narrow three-storey plan; bedrooms replace ground-floor living uses upstairs |
| Guard hut | Small single sentry room, not a four-room mini-house |
| Garage/depot/fire station | Deep service bay; a complete native three-part metal garage door and clear north approach |
| Strip mall | Three independent shop units, each with its own west-side public door and paved common arcade |
| School | Multiple classroom bands, library, staff office and bathrooms |
| Police/checkpoint/barracks | Secure supplies, work/communications rooms, accommodation and bathrooms |
| Clinic/lab/hospital | Consultation/ward or laboratory bands, medical storage and staff areas |
| Office tower | Retail/public ground floor and subdivided work floors above |
| Residential tower | Public ground floor and two domestic suites on upper floors |
| Gun shop | Native `gunstore` and `gunstorestorage` loot rooms, counters and actual gun racks |
| Large shopping centre | 96×72-tile, two-storey footprint; cross-concourse, anchor retail, fashion/sports units, food seating, kitchen, service corridor, staff/storage/bathrooms |

Meridian's four city districts retain their different services. Civic and council
blocks have the densest skyline; residential blocks mix towers with smaller homes;
utilities keep depots, waterworks and repair facilities between taller buildings.
The compiled city contains 140 six-plus-storey buildings out of 248 buildings
(eight planned lots are reserved for existing roads). Residential towers have
9–11 occupied storeys and office towers 11–13;
their real floor counts vary deterministically, not only their metadata labels.
The large shopping centres use dedicated sites, not the ordinary 64-tile city lots.

Native room loot remains selected by the game's existing room names. Furniture
themes are separate. Every enclosed generated room receives a native type-7 electrical
room-light object, a wall switch and visible wall fixtures; availability of mains
power still follows the game's ordinary electricity rules.

The graphics remain vanilla sprite references. The shopping centre uses complete
four-part native fashion and sports wall signs. There is no claim that an unknown
external reference image, custom neon shop logo or extracted game art is shipped.
The internet references and implemented motifs are recorded in the companion
reference document prepared for this pass.

## Русский

Один общий четырёхкомнатный шаблон заменён разными настоящими планировками.
У ранчо появился открытый двор и Г-образный контур; у гаражей — глубокий рабочий
бокс с трёхсекционными гаражными воротами. Небольшая сторожка состоит из одного
служебного помещения, а не из уменьшенного типового дома. Торговый ряд получил
три самостоятельных входа и общую мощёную галерею. Школы, полиция, медицинские
здания и военные постройки отличаются не только названием, но и комнатами.

В собранном Meridian 140 из 248 зданий имеют не менее шести этажей
(восемь плановых участков оставлены под существующие дороги).
Жилые башни имеют 9–11 обитаемых этажей, офисные — 11–13. На первом этаже
сохраняются общественные и торговые помещения; выше находятся квартиры либо
офисы. Между высотными зданиями остаются небольшие дома и городские службы.

Большой торговый центр занимает 96×72 клетки и два этажа: проходная центральная
галерея, крупные и небольшие магазины, спортивный отдел, зона питания, кухня,
склады, служебные помещения и санузлы. Торговые центры размещаются на отдельных
площадках. Оружейный магазин использует настоящие игровые категории добычи и
оружейные стеллажи. Над отделами ТЦ установлены целые составные вывески игры.

В комнатах предусмотрены настоящие цепи освещения, выключатели и настенные
светильники. Электричество подчиняется обычным правилам игры, а не включается
скрытым бесконечным источником питания.

## Verification scope

The architectural native-property tests cover every building kind with several
seeds: all occupied floors and rooms are reachable, furniture sprite names exist,
every stair flight has the correct three parts and upper floor opening, and
RoomDefs do not overlap. Separate tests check public storefront access, complete
garage doors, open service approaches, actual city floor counts, mall circulation,
native gun-shop room distributions and room-light metadata. These are static
native-property checks; the release QA ledger records the separate live-game run.

Copyright © 2026 druidqwerty and Meridian contributors. Original generator and
documentation: MIT. Project Zomboid sprite names refer to the owner's game;
no game art is redistributed.
