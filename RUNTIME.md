# Meridian runtime contract and audit

## Generated input

`mod/42/media/lua/shared/Meridian/00_Config.lua` (build-owned) defines:

```lua
Meridian = Meridian or {}
Meridian.Config = {
  modId="MeridianLongWayHome",
  world={minX=0,minY=0,maxX=49151,maxY=49151},
  safeCity={x1=48128,y1=1024,x2=49151,y2=2047},
  bunkers={{id="final",x1=48128,y1=1024,x2=49151,y2=2047,
    minZ=-2,maxZ=-1,zombiesPerBucket=3}},
  starterVehicle={x=640,y=48640,z=0,script="Base.SUV"},
  caches={{x=100,y=200,z=-1,kind="food"}},
  storySites={{id="departure",x=536,y=48664,z=0,textKey="UI_Meridian_Story1"}},
}
```

`caches` must identify the exact square of an actual loot container. Kinds:
`food`, `medical`, `tools`, `armory`. Vanilla room/container loot is retained.
Room-name aliases are supported (`armystorage`/`policestorage` -> armory;
`medicalstorage`/`laboratory`/`hospitalroom` -> medical;
`bedroom`/`kitchen` -> food). A food reserve holds 16 items, medical 10,
tools 9, armory 12 (including six ammunition boxes), in addition to native loot.
Archives 1..13 progressively disclose the planned evacuation experiment and
the infected admission to Meridian's refuge. They are readable through a
right-click option when within eight tiles of their site, on the same floor.

## Rules

- Native surface population density in the safe-city rectangle must be zero.
  `20_Sanctuary.lua` additionally removes zombies at **z >= 0 only**, including
  zombies entering from outside. It never suppresses negative-floor infection.
  `OnZombieUpdate` handles newly active zombies; a backwards loaded-list sweep
  runs at game start and every in-game minute. This is a runtime protected zone,
  not an impenetrable boundary: entrants are removed on their update.
- `30_Bunkers.lua` seeds loaded, interior, solid, free, non-stair bunker floor
  squares. Once per site/8x8 bucket/floor for the lifetime of that save. Four
  buckets per 60 ticks at most; loaded population cap 1,600. Three zombies per
  bucket by default. Never spawns within fourteen tiles of a same-floor player.
  Failed/blocked buckets remain eligible on subsequent square loads.
- Bunker scripted spawns respect `Zombies=6` (None),
  `ZombieConfig.PopulationMultiplier=0`, and live `BunkerHordes=false`.
  Disabling does not erase existing zombies. No on-revisit scripted respawn.
- `40_Supplies.lua` adds a sealed cache's supplies once on `OnFillContainer`.
  Guard on native object's saved mod data prevents refilling. Item types are
  checked through `getScriptManager():FindItem` before being added.
- `50_Starter.lua` creates one repaired, fuelled vanilla SUV per world and gives
  its key to the triggering player. Starts on `OnNewGame`; retries while the
  road streams in and after reload/nearby arrival. Never refills/replaces a lost
  vehicle. Does not clear or change the player's other inventory. MP creation
  is server-authoritative but actual MP synchronization remains unverified.
- All three optional gameplay switches are Sandbox settings, EN/RU translated,
  read live with safe defaults. No duplicate ModOptions, no camera/UI settings.
- Wilderness population beyond authored cell headers remains native B42 biome
  generation. Northeast density progression is authored on road/settlement cells;
  no hidden runtime horde injection into arbitrary wilderness or other maps.

## API preflight evidence (installed PZ 42.21)

Paths below are relative to `G:/Steam/steamapps/common/ProjectZomboid/media/lua`.

| API | Installed source evidence |
|---|---|
| `IsoZombie:removeFromWorld/removeFromSquare` | `client/DebugUIs/DebugContextMenu.lua:605` |
| `Events.OnZombieUpdate` | Installed A-Life `Combat/ALifeHordeRelations.lua:3022`; also documented Java event in B42 skill |
| `Events.LoadGridsquare` | `client/DebugUIs/DebugScenarios.lua:101` |
| `addZombiesInOutfit(x,y,z,count,nil,50)` | `client/Tutorial/Steps.lua:830` and debug horde UI `ISSpawnHordeUI.lua:276` |
| `square:isFree(false)` | Installed A-Life `World` spawn policies; native debug tools |
| `square:HasStairs()` | `server/RainBarrel/BuildingObjects/RainCollectorBarrel.lua:66` |
| `ModData.getOrCreate` | `server/Foraging/forageServer.lua:26` |
| `getOnlinePlayers/getNumActivePlayers/getSpecificPlayer` | `server/XpSystem/XpUpdate.lua:294` |
| `Events.OnFillContainer(room,type,container)` | `server/Items/LootLog.lua:34` |
| Item names | `server/Items/ProceduralDistributions.lua` (Bandage:58, WaterBottle:2419, TinnedBeans:596, Hammer:904, NailsBox:7957, Pistol:1084, Bullets9mmBox:977) |
| Native room loot names | `server/Items/Distributions.lua`: armystorage3852, bedroom4887, hall9652, hospitalroom9835, laboratory10856 (Chemistry/ScienceMisc/TestingLab), medicalstorage11620. No global distributions replaced. |
| `addVehicleDebug`, `repair`, `createVehicleKey` | `client/DebugUIs/Scenarios/Trailer3Scenario_Roadtrip.lua:85`; server `Vehicles/ProfessionVehicles.lua:26` |
| `part:setContainerContentAmount(capacity)` | `server/Vehicles/Vehicles.lua:221` |
| `ISModalRichText:new` | `client/OptionScreens/CharacterCreationProfession.lua:522`; constructor `client/ISUI/ISModalRichText.lua:162` |

## Viewpoint

Installed Workshop item **3809306528**, Viewpoint **0.1.6.1**, requires PZ
**42.21** and ZombieBuddy **>=2.3.0** (`common/mod.info`). The map has no hard
Viewpoint dependency, no bundled JAR, no copied camera code, no shader/model
pack overrides, and no camera event interception. Native walls, doors, windows,
stairs, floors and furniture use vanilla sprite names. The optional Viewpoint
environment is detected for logging only. Actual rendering, stair traversal,
aiming and save/reload compatibility require the independent native game QA.

## Automated policy checks

### PZ42.21 native preview fix

First native launch exposed `NegativeArraySizeException -127246320` from
`MapSpawnSelectImage.prerender -> MapUtils.initDefaultStyleV1 ->
UIWorldMapV1.setUnvisitedRGBA -> WorldMapVisited.getInstance/setBounds`.
`javap` confirms this initializer reads the main-menu MetaGrid's uninitialized
sentinel bounds, even when independent atlas bounds are valid.

`client/Meridian/65_MapPreview.lua` initializes an original four-layer vector
style **only for Meridian's selected, pre-game spawn-preview widget** and then
delegates vanilla initial zoom/render. It does not call exploration-fog APIs,
change `MapUtils`, touch MetaGrid/global visited state, or change the in-game
map's fog. Scope regression covers Meridian, other maps and in-game selector.
Native reruns are complete: preview initialization is error-clean and the atlas
renders nonblank vectors. Exact failed/passed runs and visually inspected frames
are recorded in [QA](docs/QA.md); those receipts, not this API contract, define
the rendering and traversal claims.

```powershell
python -m unittest discover -s projects/pz-meridian/tests -p test_runtime.py -v
```

Five tests: safe-zone floor/edge/client authority; No Zombies and persistent
bunker seeding; no-repeat supplies; one vehicle/fuel/key; all Lua syntax and
EN/RU key parity. Passing simulation does **not** prove in-game render or APIs.
