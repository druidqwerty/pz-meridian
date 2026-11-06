# Meridian: The Long Way Home — 0.3.0-alpha.1

## English

GitHub-only architectural diversity, park & parking overhaul alpha for Project Zomboid **42.21**.
Start a **NEW Sandbox world on Meridian**; existing saves are not migrated.

### What changed

- **100 distinct variants per building type (3,900 total cataloged variants across 39 building kinds and 12 architectural classes)**:
  - **Private country houses & cottages (`cottage`, `house`, `ranch`, `duplex`, `rowhouse`, `farm`)**: warm clapboard, timber, log and brick facades, wooden/white casement windows, L-shaped garden courts, picket/wooden fences, lawns, flowerbeds, shade trees, patio seating and roadside mailboxes.
  - **Apartment blocks (`apartment`, `midrise`, `motel`)**: multi-storey brownstone, brick and stucco massing, U-court/L-wing silhouettes, landscaped residential courtyards with hedges, benches, lamps and waste bins.
  - **High-rise towers (`residentialtower`, `officetower`, `officeblock`)**: 6–13 storey towers with stepped ground podiums, upper-floor setbacks and roof terraces, commercial stone/curtain-wall facades, metal-framed window bays and stone plazas.
  - **Commercial & retail (`shop`, `generalstore`, `stripmall`, `diner`, `fuel`, `gas`, `laundry`)**: storefront masonry and painted commercial facades, 25+ varied brand signs (Zippee, Greene's, Barg-N-Clothes, Diner Neon, Seahorse Coffee, Spiffo's, Bakery, Hair Studio, Pharmacy, Laundromat, Fossoil, etc.), tiled forecourts and cafe seating.
  - **Gun shops (`gunshop`)**: fortified dark masonry and bunker concrete, metal security windows with barricades, steel doors, Hunting/Army signage, chain-link security cages, sandbag barriers and ammo crates.
  - **Police stations (`police`)**: civic stone/brick precincts, `POLICE` facade signs, steel security doors, chain-link fenced motor-pool/impound yards, traffic cones, armories and dispatch offices.
  - **Fire stations (`firestation`)**: firehouse red brick, three-part metal apparatus bay doors, concrete apparatus aprons, fire standpipes/hydrants, traffic cones, `EMERGENCY` signage and crew dormitories.
  - **Military camps & checkpoints (`military`, `barracks`, `camp`, `checkpoint`, `gatehouse`, `guardhut`, `relay`)**: military concrete/corrugated/timber walls, perimeter chain-link and security fencing, sandbag defensive parapets, olive supply crates and drums, and `Army Property` / `Restricted Area` signage.
  - **Shopping malls (`bigboxmall`)**: two-storey `96×72` commercial gallerias with multi-brand signage, department/sports/grocery anchors, food courts and >20,000-tile striped parking aprons.
  - **Medical, civic & industrial classes (`hospital`, `clinic`, `school`, `civic`, `library`, `museum`, `warehouse`, `workshop`, `depot`, etc.)**: clinical white masonry, classical brick/stone with arched/white windows, and industrial corrugated bays with fenced cargo yards.
- **Expanded parks and parking lots**:
  - **2,613 park zones** across towns and Meridian city: full-block neighborhood parks on open plots, pocket parks, ornamental hedge borders, paved cross-promenades, paired park benches, shade trees, flowerbeds, planters and park lamps.
  - **697 building-side striped parking lots** plus 4 regional mall parking aprons (**264,411 total parking squares**) with painted white stall dividers and outdoor lighting.
  - All 16 cells of Meridian city now feature cell-specific urban mixes (**1,049 unique `(kind, variant)` building pairs** placed in the world).

### Verification and limitations

The version-specific [QA ledger](https://github.com/druidqwerty/pz-meridian/blob/main/docs/QA.md)
records static audit (`2,387` cells, `25,199` rooms, `12,025` accepted zoned room plans, `0` unknown sprites) and live B42.21 game verification (`546` unique compiled sprites checked in `IsoSpriteManager`, `0` missing/textureless, `0` Lua/resource errors, plus save-reload persistence).
Multiplayer, full-route driving and a fivefold driving-time ratio remain uncertified. Optional Viewpoint's underground ceiling/terrain bands remain a known limitation.
No Steam or Boosty publication is authorized for this map.

[Bunker entrance guide](https://github.com/druidqwerty/pz-meridian/blob/main/docs/BUNKER-ACCESS.md):
west gate → east to X48256 → north to south door **48259,1424**;
upper stair landing **48255,1408**.

Created with AI assistance. Original code/geometry: MIT; retained source notices
are documented in ATTRIBUTION.md. Game artwork is not included.

Copyright © 2026 druidqwerty. Project Zomboid belongs to The Indie Stone.

## Русский

Альфа **0.3.0-alpha.1** для PZ **42.21**, публикация только на GitHub.
Нужна **новая игра Sandbox на карте Meridian**. Старые сохранения не переносятся.

- **По 100 уникальных вариантов каждого типа зданий (3 900 вариантов по 39 типам и 12 архитектурным классам, 1 049 уникальных пар тип+вариант в мире)**:
  - **Частные загородные дома и коттеджи (`cottage`, `house`, `ranch`, `duplex`, `rowhouse`, `farm`)**: деревянный сайдинг, брус, сруб и кирпич, деревянные и белые рамы окон, Г-образные дворики, штакетник и деревянные заборы, газоны, клумбы, садовые деревья, уличные кресла и почтовые ящики у входа.
  - **Многоквартирные жилые дома (`apartment`, `midrise`, `motel`)**: многоэтажная кирпичная и штукатурная кладка, П-образные и Г-образные корпуса, благоустроенные жилые дворы с живой изгородью, скамейками, фонарями и баками.
  - **Высотки (`residentialtower`, `officetower`, `officeblock`)**: башни 6–13 этажей с выделенным стилобатом и уступами верхних этажей, каменными и коммерческими фасадами, металлическими оконными переплётами и мощёными площадями.
  - **Коммерческие здания (`shop`, `generalstore`, `stripmall`, `diner`, `fuel`, `gas`, `laundry`)**: витринные фасады, более 25 вариантов вывесок брендов (Zippee, Greene's, Barg-N-Clothes, Diner Neon, Seahorse Coffee, Spiffo's, Bakery, Hair Studio, Pharmacy, Laundromat, Fossoil и др.), уличные столики и мощёные подходы.
  - **Оружейные магазины (`gunshop`)**: укреплённая тёмная кладка, металлические окна с решётками/баррикадами, стальные двери, вывески Hunting/Army, огороженный сеткой спецдвор, брустверы из мешков с песком и армейские ящики.
  - **Полицейские участки (`police`)**: каменно-кирпичные фасады, вывеска `POLICE`, стальные двери, закрытая автостоянка/спецдвор с высокой сеткой, дорожные конусы, оружейные и диспетчерские.
  - **Пожарные части (`firestation`)**: краснокирпичные фасады, широкие 3-секционные металлические ворота боксов, бетонная площадка выезда, пожарные гидранты/стендеры, конусы, вывеска `EMERGENCY` и казармы расчёта.
  - **Военные лагеря и КПП (`military`, `barracks`, `camp`, `checkpoint`, `gatehouse`, `guardhut`, `relay`)**: периметр из высокой сетки, оборонительные позиции из мешков с песком, зелёные армейские ящики и бочки, стальные двери и предупреждающие щиты `Army Property` / `Restricted Area`.
  - **Торговые центры (`bigboxmall`)**: двухэтажные галереи `96×72` с фирменными вывесками, универмагами, фуд-кортом и размеченными парковками свыше 20 000 клеток.
- **Парковые зоны и парковки**:
  - **2 613 парковых зон** в городах и мегаполисе Meridian: квартальные городские парки на свободных участках, скверы, живые изгороди, мощёные аллеи, парные скамейки, деревья, клумбы, вазоны и парковые фонари.
  - **697 размеченных придомовых и городских парковок** у коммерческих, жилых, полицейских, пожарных и общественных зданий + 4 крупных паркинга у ТЦ (**264 411 парковочных клеток** суммарно).

Статический аудит и живая проверка в B42.21 (`546` спрайтов без пропусков и ошибок, проверка освещения, лестниц, проходов и перезагрузки сохранения) записаны в `docs/QA.md`. Без публикации в Steam/Boosty.

Вход в бункер: от западных ворот на восток до X48256, затем на север к двери
**48259,1424**; верхняя лестничная площадка **48255,1408**.

Создано с помощью ИИ. Оригинальные исходники и геометрия — MIT;
сторонние уведомления сохранены. Игровые изображения не распространяются.

Copyright © 2026 druidqwerty. Project Zomboid принадлежит The Indie Stone.
