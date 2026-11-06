# Meridian: The Long Way Home — 0.2.1-alpha.1

## English

GitHub-only large-interior furnishing alpha for Project Zomboid **42.21**.
Start a **NEW Sandbox world on Meridian**; existing saves are not migrated.

### What changed

- Large rooms receive one purpose-led plan: workstations, teaching areas,
  retail shelves, preparation benches, storage and seating form activity zones
  with clear circulation.
- Shelter rooms are planned once, instead of repeating complete kitchens or
  bedrooms in every small bay. Public kitchens have one main appliance line,
  distributed preparation and pantry zones. Sleeping facilities explicitly use
  dormitory layouts. Native loot room categories are preserved.
- Fixed facing and use-space conflicts in reusable groups, including cabinets
  blocked by packing crates and opposing preparation surfaces.
- Generation checks furnishing density, oversized empty patches, connected floor
  and approaches. Unresolved large plans stop generation; small fitted rooms and
  dedicated corridors remain explicit separate policies, not density-audited.
- Fixed bunker horde queue starvation: unloaded old areas no longer delay
  newly visited rooms behind stale jobs. Persistent first-visit population,
  player safety distance and normal sandbox zombie switches are retained.
- Reusable improvements remain in PZ Map Tools; Meridian vendors pure hash-bound
  MIT planner source for reproducible builds without a sibling checkout.

The road, districts, towers, shopping centres, lighting, sanctuary surface,
infected underground and existing gameplay remain. No new quests, NPCs,
power-restoration rules or mandatory dependencies are added.

### Verification and limitations

The version-specific [QA ledger](https://github.com/druidqwerty/pz-meridian/blob/main/docs/QA.md)
records exact static and live-game evidence and its limits. Sampling rooms is
not visual hand-polishing of every interior. Multiplayer, full-route driving
and a fivefold driving-time ratio remain uncertified. Optional Viewpoint's
underground ceiling/terrain bands remain a known limitation.
No Steam or Boosty publication is authorized for this map.

[Bunker entrance guide](https://github.com/druidqwerty/pz-meridian/blob/main/docs/BUNKER-ACCESS.md):
west gate → east to X48256 → north to south door **48259,1424**;
upper stair landing **48255,1408**.

Created with AI assistance. Original code/geometry: MIT; retained source notices
are documented in ATTRIBUTION.md. Game artwork is not included.

Copyright © 2026 druidqwerty. Project Zomboid belongs to The Indie Stone.

## Русский

Альфа **0.2.1-alpha.1** для PZ **42.21**, публикация только на GitHub.
Нужна **новая игра Sandbox на карте Meridian**. Старые сохранения не переносятся.

- Большие комнаты получают единый план по назначению: рабочие места,
  учебные зоны, торговые стеллажи, подготовка продуктов, хранение и отдых
  связаны проходами, а не заполнены случайной мебелью.
- Подземные помещения планируются целиком. Вместо повторения полной кухни
  в каждом отсеке — одна основная линия техники, зоны подготовки и кладовые.
  Спальные помещения используют общественные схемы размещения;
  игровые категории комнат для добычи сохранены.
- В инструменте карт исправлены поворот мебели и подходы: ящики не занимают
  место перед шкафами, рабочие поверхности не перекрывают доступ друг к другу.
- Генератор проверяет плотность, крупные пустоты, связность пола и подходы.
  Неудачный большой план останавливает сборку. Малые комнаты и выделенные
  коридоры остаются отдельными явными политиками.
- Исправлена очередь заселения бункера: старые выгруженные зоны больше
  не задерживают заражённых в новых комнатах. Безопасная дистанция появления,
  постоянство заселения и настройки зомби сохранены.
- Универсальный планировщик сохранён в PZ Map Tools; Meridian содержит его
  чистые MIT-исходники с контрольными суммами без зависимости от соседнего проекта.

Дорога, районы, высотки, ТЦ, освещение, безопасная поверхность города,
заражённое подземелье и прежние механики сохранены. Новых квестов, NPC,
обязательных модов или запуска электростанций нет.

Точные проверки и границы доказательств — в QA. Выборочная проверка не означает
ручную полировку всех помещений. Мультиплеер, полный автопробег и пятикратное
время поездки не сертифицированы; известные подземные полосы потолка/поверхности
Viewpoint остаются. Без публикации Steam/Boosty.

Вход в бункер: от западных ворот на восток до X48256, затем на север к двери
**48259,1424**; верхняя лестничная площадка **48255,1408**. Схема — по ссылке выше.

Создано с помощью ИИ. Оригинальные исходники и геометрия — MIT;
сторонние уведомления сохранены. Игровые изображения не распространяются.

Copyright © 2026 druidqwerty. Project Zomboid принадлежит The Indie Stone.
