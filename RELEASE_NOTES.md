# Meridian: The Long Way Home — 0.2.0-alpha.1

## English

GitHub-only urban/interior rebuilding alpha for Project Zomboid **42.21**.
Start a **NEW Sandbox world on Meridian**; old saves are not migrated.

### What changed

- Replaced the near-universal four-room building with 53 building programmes:
  compact homes, L-plan ranches, duplexes, row houses, garages, sentry huts,
  schools, police/fire stations, shops, workshops and classified facilities.
- Small towns have different building mixes, sizes and setbacks. Regional
  centres grow taller along the route. Meridian contains **248 surface buildings,
  including 140 with at least six occupied storeys**; towers reach 13 storeys.
  Every occupied floor has real rooms and native physical stairs.
- Four separate **96×72-tile, two-storey shopping centres** contain anchor shops,
  smaller units, food seating, kitchens and service rooms. Their broad concrete
  parking lots have native markings and open drive aisles; forecourts use tile.
- **13 small gun shops** use native gun-store loot distributions and gun racks.
  Building-specific vanilla signs and setback road signs add visual identity.
- Corrected furniture facing, complete bed/sofa groups, usable seats, supported
  appliances and denser activity clusters. Compact homes no longer have a giant
  empty five-tile-deep lobby.
- Real native room-light metadata, wall switches and visible powered fixtures
  above and below ground. Ordinary electricity shutoff/generator/bulb rules apply.
- Two-wide sidewalks continue to native-cell seams. Building approaches use a
  collision-aware route instead of a broken line through a neighbouring building.
- Rebuilt the city wall as a **13-tile-deep, eight-storey fortification**, with
  an upper walkway, actual stair access and a 21-tile-wide, four-storey-clear gate.
- Bunker pavilions have more role-specific furnishings, backed signs and contrasting
  floor guidance to their real stairs. [Entrance guide](https://github.com/druidqwerty/pz-meridian/blob/main/docs/BUNKER-ACCESS.md):
  west gate → east to X48256 → north to south door **48259,1424**;
  upper stair landing **48255,1408**, lower approach **48259,1408,-1**.

### Inventory and verification boundary

**2,387 native cell pairs; 1,188 surface structures; 25,423 native rooms.**
The original 128.256km road, seven chapters, six regional detours, ten landmark
compounds, twelve stop types, seven possible bases, sixteen underground wings,
twelve main bunker entrances, thirteen archives and existing gameplay remain.
This is map content, not new quests, NPCs, working trade or power-restoration rules.

Static/native gates and separate live-game results are recorded in the
[QA ledger](https://github.com/druidqwerty/pz-meridian/blob/main/docs/QA.md).
Native tile/room data is decoded and round-tripped during compilation. No game
artwork, other mods or private test drivers are bundled. Pure validated recipes
were also retained in the reusable pz-map-tools repository; no retired map revived.

### Known limitations

This is an alpha, not hand-polished final art. Multiplayer and full-route driving
or a fivefold travel-time ratio are not certified. Viewpoint remains optional;
terrain-texture bands near some underground ceiling edges are still a known
camera limitation. Reference motifs are original native adaptations, not copies
of Louisville, Pullman or downloaded map assets. New world required.

Created with AI assistance. Original code/geometry MIT; format references and
third-party notices are in ATTRIBUTION.md and CODEC-LICENSE.txt.
No Steam or Boosty publication is authorized for this map.

## Русский

Альфа **0.2.0-alpha.1** для PZ **42.21**, публикация только на GitHub.
Нужна **новая игра Sandbox на карте Meridian**. Старые сохранения не переносятся.

- Вместо одного четырёхкомнатного шаблона — 53 программы зданий: компактные
  дома, ранчо с двором, дуплексы, таунхаусы, гаражи, сторожки, школы, полиция,
  пожарные станции, торговые ряды и ведомственные объекты.
- Разные составы городков и нарастание этажности к финалу. В Meridian **248 зданий,
  из них 140 — от шести обитаемых этажей**. Высотки достигают 13 этажей;
  внутри есть настоящие помещения и лестницы.
- Четыре крупных двухэтажных ТЦ 96×72 клетки, большие бетонные парковки с
  разметкой и проездами, плиточные площади; 13 небольших оружейных магазинов.
- Тематические игровые вывески, дорожные знаки, связные тротуары и подходы,
  которые обходят здания и доходят до границ клеток карты.
- Исправлен поворот мебели; кровати и диваны ставятся целиком. Добавлены
  функциональные группы мебели вместо пустых залов и одиночных предметов.
- Настоящие комнатные выключатели и светильники. Электричество работает по
  обычным правилам игры, без скрытого бесконечного питания.
- Объёмная стена: **13 клеток толщины, 8 этажей высоты**, верхний проход,
  лестница и ворота шириной 21 клетку с четырёхэтажным просветом.
- Входные павильоны бункера стали заметнее и подробнее обставлены; добавлены
  указатели и контрастная дорожка к лестнице. Ближайший общественный вход:
  от западных ворот на восток до X48256, затем на север к двери **48259,1424**;
  верхняя площадка **48255,1408**, нижний подход **48259,1408,-1**.

Итог: **2 387 пар нативных клеток, 1 188 наземных зданий, 25 423 помещения**.
Главная дорога и прежнее экспедиционное наполнение сохранены; новых игровых
систем, NPC, торговли, квестового журнала и запуска электростанций нет.

Точные результаты автоматических и игровых проверок находятся в QA.
Мультиплеер, полный автопробег и пятикратное время поездки не сертифицированы.
Полосы текстуры поверхности у некоторых подземных потолков Viewpoint остаются
известным ограничением. Это тестовая альфа, не завершённая ручная полировка.
Исходники созданы с помощью ИИ; рабочие универсальные решения сохранены отдельно
в pz-map-tools, без восстановления старой карты. Без публикации Steam/Boosty.

Copyright © 2026 druidqwerty. Original Meridian code and geometry: MIT.
Project Zomboid artwork and game belong to The Indie Stone; not included.
Авторское право © 2026 druidqwerty. Исходный код и геометрия Meridian: MIT.
Графика и игра Project Zomboid принадлежат The Indie Stone и не включены.
