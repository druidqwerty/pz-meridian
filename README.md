# Meridian: The Long Way Home — B42.21

[![Support development](docs/banner.png)](https://boosty.to/lrgpp)

Support independent mods / Поддержать разработку модов.

**An original standalone expedition map.** Leave Last Light in the southwest,
follow the supply road through abandoned communities and classified installations,
and reach the walled city of Meridian in the northeast. Its streets are empty of
infected. The two-storey Continuity habitat beneath them is not.

![Original route plan](docs/route-map.png)

## Test build

- 128.256 km principal road; 49.152 × 49.152 km world envelope, native scale.
- Six civilian districts, six military/research districts, roadside service stops,
  and the largest, walled final city. The hinterland uses vanilla B42 wilderness.
- Original furnished buildings using vanilla sprites and loot room definitions.
- Four surface entrances to the main refuge; connected galleries, living quarters,
  medical wards, laboratories and supply caches on floors −1 and −2.
- Additional underground research annexes. Thirteen bilingual archive fragments.
- Working fuelled starting SUV with a key; actual fuel pumps along the route.
- Native zombie density rises toward the northeast. The city surface is cleared
  independently of its underground infestation, including incoming wanderers.

The route is **about 4.90× a geometric vanilla road-path proxy**. That is not a
verified fivefold driving-time benchmark. Off-road shortcuts remain possible.
This is an alpha for gameplay/art feedback, not a claimed hand-polished final map.

## Play

1. Extract the ZIP so `Zomboid/mods/MeridianLongWayHome` contains `42` and `common`.
2. Enable **Meridian: The Long Way Home** in Mods.
3. Start a **new Sandbox world**, select the **Meridian** map/start region.
4. Spawn in Last Light. The SUV is on the nearby main road at (640, 48640).
   Follow the road east. Fuel stops are roughly 4.5 km apart.
5. Right-click near district archives to read the recovered records. Look for
   hidden metal lockers in ordinary buildings and sealed underground stores.

Do not add this map to an existing save or mix it with another map replacing the
same cells. Existing saves are not migrated. Normal sandbox zombie population
settings still apply; disabling all zombies also disables custom bunker hordes.

## Viewpoint

Optional, **not a required dependency**. Install Viewpoint and its ZombieBuddy
dependency separately; their files are not included. Target: Viewpoint 0.1.6.1 /
PZ 42.21. No replacement camera or custom depth textures are used. See
[QA evidence and limits](docs/QA.md) for the actual tested modes and remaining
limitations. Multiplayer is not yet certified.

## Development

Python 3.10+; `pip install -r requirements.txt`, then `python tools/generate.py`.
Run `python tools/audit.py` against the installed game and `python -m unittest
discover -s tests -v` (tests also need `requirements-dev.txt`). Generated native maps are distributed as release ZIPs, not
committed game assets. Read [MODLOG](MODLOG.md), [architecture](docs/ARCHITECTURE.md)
and [runtime](RUNTIME.md). Created with AI assistance. Original geometry and code;
no Real USA building or third-party mod asset was copied.

GitHub-only prerelease. No Steam or Boosty publication is authorized for this map.

## Русский

**Новая карта-путешествие, не Россия и не копия реальной местности.** Старт —
юго-западный Ласт-Лайт. Дорога ведёт через заброшенные поселения к всё более
закрытым военным объектам и городу Меридиан на северо-востоке.

Наверху, внутри стен, зомби нет. Под городом — два заражённых этажа убежища
«Непрерывность»: тоннели, жильё, лаборатории и склады. По документам эвакуация
оказалась частью заранее подготовленного эксперимента; один заражённый разрушил
план идеальной безопасности. Дополнительные тайные комплексы скрыты по маршруту.

Установка: включить мод и начать **новую игру Sandbox на карте Meridian**.
Внедорожник с ключом и полным баком ждёт у стартового посёлка на главной дороге.
Далее — топливные станции примерно через 4,5 км. Документы открываются правой
кнопкой рядом с архивами районов. Мебель и лут соответствуют назначению комнат.

Главная дорога — 128 км, примерно в 4,9 раза длиннее расчётного ванильного
автомобильного маршрута. Пятикратное время поездки ещё не замерено. Это тестовая
альфа: баланс, оформление и отдельные маршруты требуют игрового отзыва.
Viewpoint необязателен; результаты проверки — в QA. Существующие сохранения не
трогаются. Публикация пока только на GitHub, без Steam и Boosty.

Copyright © 2026 druidqwerty. Original Meridian code and geometry: MIT.
Project Zomboid artwork and game belong to The Indie Stone; not included.
Авторское право © 2026 druidqwerty. Исходный код и геометрия Meridian: MIT.
Графика и игра Project Zomboid принадлежат The Indie Stone и не включены.
