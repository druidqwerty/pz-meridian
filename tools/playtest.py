"""Private, supervised PZ B42 game oracle. Never installed in the product.

No keyboard/mouse input; all saves/options and optional Java approvals are run-local.
Requires the user's installed game and reusable pz-map-tools alongside this project.
"""
from __future__ import annotations
import argparse
import hashlib
from datetime import datetime
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
REUSABLE = ROOT.parent / 'pz-map-tools/tools'
sys.path.insert(0, str(REUSABLE))
from game_smoke import DEFAULT_GAME, DEFAULT_JAVAC, options, compile_prompt_helper
from gameplay_probe import CONTENT
from lighting_probe import CONTENT as LIGHTING_CONTENT
from sprite_probe import CONTENT as SPRITE_CONTENT

MENU = r'''
local step,due=0,nil
local function tick()
 if not due or getTimestampMs()<due then return end
 if MeridianTestConfig.resume then
  due=nil
  MainScreen.continueLatestSave(MeridianTestConfig.mode,MeridianTestConfig.saveName)
  return
 end
 if step==0 then
  ActiveMods.getById("currentGame"):copyFrom(ActiveMods.getById("default"))
  local solo=MainScreen.instance.soloScreen
  solo:setVisible(true); solo:onItemClick(solo.panels[1],0,0); solo:clickPlay()
 elseif step==1 then
  local ui,found=WorldSelect.instance,false
  for index,row in ipairs(ui.listbox.items) do
   local dirs=row.item.mapDirs
   for n=0,dirs:size()-1 do
    if dirs:get(n)==MeridianTestConfig.folder then
     ui.listbox.selected=index; ui:onSelectWorld(); found=true
    end
   end
  end
  assert(found,"New world absent from world selection")
  MeridianTest.record("world_selection",true); takeScreenshot()
 elseif step==2 then
  WorldSelect.instance:clickNext()
  local ui,found=MapSpawnSelect.instance,false
  for index,row in ipairs(ui.listbox.items) do
   if row.item.dir==MeridianTestConfig.folder then ui.listbox.selected=index; found=true end
  end
  assert(found,"New map absent from spawn selection")
  ui.textEntry:setText("MeridianPrivateOracle")
  MeridianTest.record("spawn_selection",true); takeScreenshot()
 elseif step==3 then
  MapSpawnSelect.instance:clickNext()
  local region=MapSpawnSelect.instance.selectedRegion
  local primary
  for _,points in pairs(region.points) do
   for _,point in ipairs(points) do
    if point.posX==MeridianTestConfig.x and point.posY==MeridianTestConfig.y then primary=point end
   end
  end
  assert(primary,"Published starting point missing")
  for profession,_ in pairs(region.points) do region.points[profession]={primary} end
 elseif step==4 then
  MainScreen.instance.charCreationProfession:onOptionMouseDown({internal="NEXT"},0,0)
 elseif step==5 then
  MainScreen.instance.charCreationMain:onOptionMouseDown({internal="NEXT"},0,0)
 else return end
 step=step+1; due=getTimestampMs()+2000
end
Events.OnMainMenuEnter.Add(function()
 if due then return end
 getCore():setOptionShowSurvivalGuide(false)
 due=getTimestampMs()+4000
 Events.OnFETick.Add(function() MeridianTest.run(tick) end)
end)
'''

CORE = r'''
require "MeridianTest/Config"
MeridianTest={records={},failed=false,done=false}
function MeridianTest.record(key,value)
 local s=key.."="..tostring(value)
 print("[MeridianTest] "..s); table.insert(MeridianTest.records,s)
end
function MeridianTest.check(key,value)
 MeridianTest.record(key,value and "PASS" or "FAIL")
 if not value then MeridianTest.failed=true end
end
function MeridianTest.finish()
 if MeridianTest.done then return end
 MeridianTest.record("result",MeridianTest.failed and "FAIL" or "PASS")
 local f=getFileWriter("meridian-playtest.txt",true,false)
 f:write(table.concat(MeridianTest.records,"\n").."\n"); f:close()
 MeridianTest.done=true
end
function MeridianTest.run(fn)
 if MeridianTest.done then return end
 local ok,err=pcall(fn)
 if not ok then
  MeridianTest.record("exception",err); MeridianTest.failed=true
  if MeridianTest.restoreLighting then pcall(MeridianTest.restoreLighting,"exception_cleanup") end
  MeridianTest.finish()
 end
end
require "MeridianTest/Menu"
'''

WORLD = r'''
require "TimedActions/WalkToTimedAction"
local phase,due,index,startX,startY,target=0,0,0,nil,nil,nil
local testCar
local function shot(name) MeridianTest.record("screenshot",name); takeScreenshot() end
local isoZoomGoal,isoZoomDue,isoZoomSteps=nil,0,0
local function updateIsoZoom()
 if not isoZoomGoal or getTimestampMs()<isoZoomDue then return end
 local core=getCore(); local current=core:getZoom(0)
 if math.abs(current-isoZoomGoal)<0.04 or isoZoomSteps>=12 then isoZoomGoal=nil; return end
 local direction=current<isoZoomGoal and 1 or -1
 local nextZoom=core:getNextZoom(0,direction)
 if nextZoom==current or math.abs(nextZoom-isoZoomGoal)>math.abs(current-isoZoomGoal)+0.02 then
  isoZoomGoal=nil; return
 end
 core:doZoomScroll(0,direction); isoZoomSteps=isoZoomSteps+1
 isoZoomDue=getTimestampMs()+450
end
local function inspectPoint(label,expected)
 local p=getPlayer(); local sq=p:getSquare()
 MeridianTest.record(label.."_position",p:getX()..","..p:getY()..","..p:getZ())
 MeridianTest.check(label.."_floor",sq and sq:getFloor()~=nil)
 if expected.room then MeridianTest.check(label.."_room",sq and sq:getRoom()~=nil) end
 local counts={containers=0,items=0,doors=0,stairs=0,zombies=0,surface=0,below=0,safeSurface=0}
 local availableDoor
 local x,y,z=math.floor(p:getX()),math.floor(p:getY()),math.floor(p:getZ())
 for xx=x-35,x+35 do for yy=y-35,y+35 do
  local s=getCell():getGridSquare(xx,yy,z)
  if s then
   if s:has(IsoObjectType.stairsTW) or s:has(IsoObjectType.stairsTN) then counts.stairs=counts.stairs+1 end
   for n=0,s:getObjects():size()-1 do
    local o=s:getObjects():get(n)
    if instanceof(o,"IsoDoor") then
     counts.doors=counts.doors+1
     if not o:isLocked() and not o:isBarricaded() then availableDoor=o end
    end
    local c=o:getContainer()
    if c then counts.containers=counts.containers+1; counts.items=counts.items+c:getItems():size() end
   end
  end
 end end
 local zombies=getCell():getZombieList()
 for n=0,zombies:size()-1 do
  local a=zombies:get(n)
  if math.abs(a:getX()-x)<60 and math.abs(a:getY()-y)<60 then
   counts.zombies=counts.zombies+1
   if a:getZ()>=0 then counts.surface=counts.surface+1 else counts.below=counts.below+1 end
   if Meridian.isSafeSurface(a:getX(),a:getY(),a:getZ()) then counts.safeSurface=counts.safeSurface+1 end
  end
 end
 for k,v in pairs(counts) do MeridianTest.record(label.."_"..k,v) end
 if label=="spawn" then
  MeridianTest.check("spawn_containers",counts.containers>0)
  MeridianTest.check("spawn_loot",counts.items>0)
  MeridianTest.check("spawn_doors",counts.doors>0)
  if availableDoor then
   local was=availableDoor:IsOpen(); availableDoor:ToggleDoor(p)
   MeridianTest.check("spawn_door_opens",availableDoor:IsOpen()~=was)
   if availableDoor:IsOpen()~=was then availableDoor:ToggleDoor(p) end
  end
 end
 if expected.safeSurface then
  MeridianTest.check(label.."_sample_inside_sanctuary",Meridian.isSafeSurface(x,y,z))
  MeridianTest.check(label.."_no_surface_zombies",counts.safeSurface==0)
 end
 if expected.infected then MeridianTest.check(label.."_infected",counts.below>0) end
 shot(label)
end
local function tick()
 updateIsoZoom()
 if getTimestampMs()<due then return end
 local p=getPlayer()
 if phase==0 then
  if MeridianTestConfig.resume then
   local d=p:getModData()
   MeridianTest.check("reload_token",d.MeridianTestToken==MeridianTestConfig.token)
   MeridianTest.check("reload_position",d.MeridianTestX and math.abs(p:getX()-d.MeridianTestX)<1 and math.abs(p:getY()-d.MeridianTestY)<1 and math.abs(p:getZ()-d.MeridianTestZ)<0.1)
   inspectPoint("reload",{})
   if MeridianTestConfig.resumeTour then phase=2 else MeridianTest.finish() end
   return
  end
  inspectPoint("spawn",{room=true})
  MeridianTest.check("spawn_position",math.abs(p:getX()-MeridianTestConfig.x)<4 and math.abs(p:getY()-MeridianTestConfig.y)<4)
  local sq=p:getSquare(); startX,startY=p:getX(),p:getY()
  for _,d in ipairs({{2,0},{0,2},{-2,0},{0,-2}}) do
   local s=getCell():getGridSquare(math.floor(startX)+d[1],math.floor(startY)+d[2],0)
   if s and s:getRoom()==sq:getRoom() and s:isFree(false) then ISTimedActionQueue.add(ISWalkToTimedAction:new(p,s)); break end
  end
  phase=1; due=getTimestampMs()+10000
 elseif phase==1 then
  MeridianTest.check("spawn_walk",(p:getX()-startX)^2+(p:getY()-startY)^2>1)
  phase=2
 elseif phase==2 then
  index=index+1; target=MeridianTestConfig.targets[index]
  if not target then phase=8; return end
  if MeridianTestConfig.viewpoint and target.noViewpoint and not RRViewpointProbe.select("isometric") then
   index=index-1; due=getTimestampMs()+500; return
  end
  if target.zoom then
   getCore():setAutoZoom(0,false)
   isoZoomGoal=math.max(getCore():getMinZoom(),math.min(getCore():getMaxZoom(),target.zoom))
   isoZoomSteps=0; isoZoomDue=0
  end
  p:teleportTo(target.x+0.5,target.y+0.5,target.z or 0)
  MeridianTest.record("target_teleport",target.name)
  phase=3; due=getTimestampMs()+12000
 elseif phase==3 then
  inspectPoint(target.name,target)
  MeridianTest.record(target.name.."_isometric_zoom",getCore():getZoom(0))
  if target.metalDoor then inspectMetalDoor(target.metalDoor,target.name) end
  if target.lighting then
   if beginLighting(target.lighting,target.name) then phase=21; due=getTimestampMs()+8000
   else phase=2; due=getTimestampMs()+1000 end
  elseif target.unbarricade then
   if beginUnbarricade(target.unbarricade,target.name) then phase=17; due=getTimestampMs()+25000
   else phase=2 end
  elseif target.salvage then
   if beginSalvageUnload(target.salvage,target.name) then phase=18; due=getTimestampMs()+2000
   elseif beginSalvage(target.salvage,target.name) then phase=15; due=getTimestampMs()+70000
   else phase=2 end
  elseif target.vehicle then
   testCar=nil
   for xx=target.x-15,target.x+15 do
    for yy=target.y-15,target.y+15 do
     local square=getCell():getGridSquare(xx,yy,0)
     local car=square and square:getVehicleContainer()
     if car then testCar=car; break end
    end
    if testCar then break end
   end
   MeridianTest.check("starter_vehicle_present",testCar~=nil)
   assert(testCar,"Starter SUV not loaded near expected road position")
   MeridianTest.record("starter_vehicle_script",testCar:getScriptName())
   local tank=testCar:getPartById("GasTank")
   MeridianTest.check("starter_vehicle_fuel",tank and tank:getContainerContentAmount()>1)
   local haveKey=p:getInventory():haveThisKeyId(testCar:getKeyId())~=nil
   MeridianTest.check("starter_vehicle_key",haveKey)
   ISTimedActionQueue.clear(p)
   testCar:enter(0,p); testCar:setCharacterPosition(p,0,"inside")
   MeridianTest.check("starter_vehicle_enter",p:getVehicle()==testCar)
   MeridianTest.record("starter_lab_blocked_before",p:isBlockMovement())
   MeridianTest.record("starter_engine_quality",testCar:getEngineQuality())
   MeridianTest.record("starter_battery_charge",testCar:getBatteryCharge())
   MeridianTest.record("starter_engine_state_before",testCar:getEngineState())
   -- Direct diagnostic entry has no timed-action completion to clear this flag.
   -- Match normal completed entry; do not alter any car part or engine state.
   p:setBlockMovement(false)
   testCar:tryStartEngine(haveKey)
   phase=12; due=getTimestampMs()+8000
  elseif target.walkTo then
   local d=target.walkTo
   local dest=getCell():getGridSquare(d.x,d.y,d.z)
   MeridianTest.check(target.name.."_stair_destination_loaded",dest and dest:getFloor()~=nil)
   assert(dest,"Stair destination not loaded")
   ISTimedActionQueue.clear(p)
   ISTimedActionQueue.add(ISWalkToTimedAction:new(p,dest))
   MeridianTest.record(target.name.."_action","real_ISWalkToTimedAction_no_teleport")
   phase=11; due=getTimestampMs()+20000
  elseif MeridianTestConfig.viewpoint and not target.noViewpoint then phase=4
  else phase=2; due=getTimestampMs()+1500 end
 elseif phase==21 then
  lightingOnFrame(target.name)
  phase=22; due=getTimestampMs()+1500
 elseif phase==22 then
  lightingSwitchOff(target.name)
  phase=23; due=getTimestampMs()+8000
 elseif phase==23 then
  lightingOffFrame(target.name)
  phase=24; due=getTimestampMs()+1500
 elseif phase==24 then
  restoreLighting(target.name)
  if MeridianTestConfig.viewpoint and not target.noViewpoint then phase=4 else phase=2 end
 elseif phase==18 then
  local ready=salvageUnloadReady(target.name)
  if ready==true then
   if beginSalvage(target.salvage,target.name) then phase=15; due=getTimestampMs()+70000 else phase=2 end
  elseif ready==false then phase=2 else due=getTimestampMs()+2000 end
 elseif phase==17 then
  finishUnbarricade(target.name)
  shot(target.name.."_after_unbarricade")
  if MeridianTestConfig.viewpoint and not target.noViewpoint then phase=4 else phase=2 end
 elseif phase==15 then
  finishSalvage(target.name)
  shot(target.name.."_after_salvage")
  if MeridianTestConfig.viewpoint and not target.noViewpoint then phase=4 else phase=2 end
 elseif phase==12 then
  MeridianTest.check("starter_vehicle_engine",testCar:isEngineRunning())
  shot("starter_engine_running")
  MeridianTest.record("starter_engine_state_after",testCar:getEngineState())
  testCar:shutOff(); testCar:exit(p); testCar:setCharacterPosition(p,0,"outside")
  p:setBlockMovement(false); ISTimedActionQueue.clear(p)
  testCar=nil
  if MeridianTestConfig.viewpoint and not target.noViewpoint then phase=4 else phase=2 end
 elseif phase==11 then
  local d=target.walkTo
  MeridianTest.record(target.name.."_walk_result",p:getX()..","..p:getY()..","..p:getZ())
  MeridianTest.check(target.name.."_"..(target.walkLabel or "stair_traversal"),math.abs(p:getZ()-d.z)<0.1 and math.abs(p:getX()-d.x)<1.5 and math.abs(p:getY()-d.y)<1.5)
  shot(target.name.."_after_stairs")
  if MeridianTestConfig.viewpoint and not target.noViewpoint then phase=4 else phase=2 end
 elseif phase==4 then
  if not RRViewpointProbe.select("first") then return end
  RRViewpointProbe.aim(target.yaw or -math.pi/4,target.pitch or -0.08)
  phase=5; due=getTimestampMs()+3500
 elseif phase==5 then
  MeridianTest.check(target.name.."_first_camera",RRViewpointProbe.mode()=="first"); shot(target.name.."_first")
  phase=6; due=getTimestampMs()+1000
 elseif phase==6 then
  if not RRViewpointProbe.select("third") then return end
  RRViewpointProbe.aim(target.yaw or -math.pi/4,target.pitch or -0.08)
  phase=7; due=getTimestampMs()+3500
 elseif phase==7 then
  MeridianTest.check(target.name.."_third_camera",RRViewpointProbe.mode()=="third"); shot(target.name.."_third")
  phase=9; due=getTimestampMs()+1000
 elseif phase==9 then
  if not RRViewpointProbe.select("isometric") then return end
  phase=2
 elseif phase==8 then
  ISWorldMap.ShowWorldMap(0)
  local map=ISWorldMap_instance
  MeridianTest.check("atlas_opens",map~=nil)
  assert(map,"Native paper map did not open")
  MeridianTest.record("atlas_hide_unvisited_before_diagnostic_override",map.mapAPI:getBoolean("HideUnvisited"))
  map:setHideUnvisitedAreas(false)
  map.mapAPI:setBoolean("Isometric",false)
  map.mapAPI:resetView()
  MeridianTest.record("atlas_image_pyramid",map.mapAPI:getBoolean("ImagePyramid"))
  MeridianTest.record("atlas_features",map.mapAPI:getBoolean("Features"))
  phase=13; due=getTimestampMs()+6000
 elseif phase==13 then
  local map=ISWorldMap_instance
  MeridianTest.check("atlas_loaded",map and map.mapAPI:isDataLoaded() and map.mapAPI:getDataCount()>0)
  shot("native_atlas_overview")
  phase=19; due=getTimestampMs()+1000
 elseif phase==19 then
  local map=ISWorldMap_instance
  local city=Meridian.Config.safeCity
  map.mapAPI:centerOn((city.x1+city.x2)/2,(city.y1+city.y2)/2)
  map.mapAPI:setZoom(14)
  phase=16; due=getTimestampMs()+5000
 elseif phase==16 then
  shot("native_atlas_street_zoom")
  phase=20; due=getTimestampMs()+1000
 elseif phase==20 then
  ISWorldMap_instance:close(); setGameSpeed(1)
  phase=14
 elseif phase==14 then
  local d=p:getModData()
  d.MeridianTestToken=MeridianTestConfig.token
  d.MeridianTestX=p:getX(); d.MeridianTestY=p:getY(); d.MeridianTestZ=p:getZ()
  save(true); MeridianTest.record("save_requested",true)
  phase=10; due=getTimestampMs()+5000
 elseif phase==10 then MeridianTest.finish() end
end
Events.OnGameStart.Add(function()
 MeridianTest.record("game_started",MeridianTestConfig.folder)
 MeridianTest.run(function() inspectSpriteRegistry(MeridianTestConfig.spriteNames) end)
 local p=getPlayer(); p:setGodMod(true); p:setGhostMode(true)
 MeridianTest.check("lab_protection",p:isGodMod() and p:isGhostMode())
 -- Diagnostic light only; never added to the shipped product or user saves.
 local torch=p:getInventory():AddItem("Base.Torch")
 assert(torch,"Vanilla diagnostic flashlight unavailable")
 torch:setUsedDelta(1); torch:setActivated(true); p:setPrimaryHandItem(torch)
 MeridianTest.check("diagnostic_flashlight",torch:isActivated())
 getGameTime():setTimeOfDay(12); setGameSpeed(1)
 due=getTimestampMs()+8000
 Events.OnTickEvenPaused.Add(function()
  local debug=UIManager.getDebugConsole(); if debug then debug:setVisible(false) end
  if SurvivalGuide and SurvivalGuide.instance then SurvivalGuide.instance:onClose() end
  local panel=getPlayerInfoPanel(0); if panel then panel:setVisible(false) end
  MeridianTest.run(tick)
 end)
end)
'''


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')


def tree_binding(folder):
    """Bind the launch copy to product bytes; path+size+SHA-256, not timestamps."""
    result={}
    for path in sorted(folder.rglob('*')):
        if path.is_file():
            result[path.relative_to(folder).as_posix()]={
                'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    return result


def native_sprite_names(folder):
    """Names from the actual isolated compiled product, not stale source metadata."""
    from map_binary import _Reader
    names=set()
    for file in folder.rglob('*.lotheader'):
        header=_Reader(file.read_bytes())
        if header.take(4)!=b'LOTH' or header.uint()!=1:
            raise ValueError(f'Invalid native header: {file.name}')
        names.update(header.line() for _ in range(header.count()))
    return sorted(names)


def classify_resource_errors(log):
    """Keep exact observed stock startup-font failures distinct from map failures."""
    stock_root=re.escape(DEFAULT_GAME.as_posix()+'/media/')
    baseline_font=re.compile(r'^ERROR: General\s+f:0 at AngelCodeFont\.parseFnt\s+> '
        r'AngelCodeFont failed to load page 0 texture '+stock_root+
        r'(?:mainfont_0\.png|mainfont2_0\.png|fonts/zomboidDialogue\.bmfc_0\.png)$')
    baseline_piano=re.compile(r'^ERROR: General\s+f:0 at CraftRecipeComponentScript\.getIconTexture> '
        r'CraftRecipeComponentScript: Recipe Piano missing UiConfigScript - falling back to '
        r'SpriteConfigScript first world object face for recipe icon\.$')
    errors=[];known=[]
    for line in log.splitlines():
        lower=line.lower()
        if 'missing tile ' in lower or ('texture' in lower and 'error:' in lower and
                any(word in lower for word in ('missing','not found','failed'))):
            known_line=baseline_font.fullmatch(line.replace('\\','/')) or baseline_piano.fullmatch(line)
            (known if known_line else errors).append(line)
    return errors,known


def lua(value):
    if value is True: return 'true'
    if value is False: return 'false'
    if value is None: return 'nil'
    if isinstance(value, str): return json.dumps(value, ensure_ascii=True)
    if isinstance(value, (int, float)): return str(value)
    if isinstance(value, list): return '{' + ','.join(lua(v) for v in value) + '}'
    return '{' + ','.join('['+lua(k)+']='+lua(v) for k,v in value.items()) + '}'


def prepare(args):
    run=ROOT/'build/playtest'/datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    run.mkdir(parents=True, exist_ok=False)
    cache=run/'cache'
    if args.resume:
        prior=json.loads((args.resume/'run.json').read_text(encoding='utf-8'))
        old=Path(prior['cache'])
        saves=list((old/'Saves').glob('*/*/map_ver.bin'))
        if len(saves)!=1: raise ValueError('Reload requires one isolated saved world')
        shutil.copytree(old,cache,ignore=shutil.ignore_patterns('console.txt','Logs','Screenshots','meridian-playtest.txt'))
        cfg=prior['config']
        cfg.update(resume=True,saveName=saves[0].parent.name,mode=saves[0].parent.parent.name)
        if args.resume_targets:
            cfg.update(resumeTour=True,targets=json.loads(args.resume_targets.read_text(encoding='utf-8')))
        cmd=[c.replace(str(old),str(cache)) for c in prior['command']]
        # Keep prior run's immutable java-agent jars, but new run-local settings/cache.
    else:
        mod=args.mod.resolve()
        info=(mod/'42/mod.info').read_text(encoding='utf-8')
        mod_id=re.search(r'^id\s*=\s*(.+)$',info,re.M).group(1).strip()
        maps=list(mod.glob('*/media/maps/*/map.info'))
        if len(maps)!=1: raise ValueError('Expected one map.info across version/common folders')
        point_text=(maps[0].parent/'spawnpoints.lua').read_text(encoding='utf-8')
        match=re.search(r'posX\s*=\s*(\d+)\s*,\s*posY\s*=\s*(\d+)\s*,\s*posZ\s*=\s*(-?\d+)',point_text)
        if not match: raise ValueError('Need native absolute spawnpoint')
        x,y,z=map(int,match.groups())
        shutil.copytree(mod,cache/'mods'/mod_id)
        source_tree=tree_binding(mod)
        launch_tree=tree_binding(cache/'mods'/mod_id)
        if source_tree!=launch_tree: raise ValueError('Candidate launch-copy SHA-256 mismatch')
        write(run/'candidate-bind.json',json.dumps(dict(
            source=str(mod),copy=str(cache/'mods'/mod_id),files=len(source_tree),
            treeSHA256=hashlib.sha256(json.dumps(source_tree,sort_keys=True).encode()).hexdigest(),
            equal=True,entries=source_tree),indent=2))
        (cache/'mods/MeridianPrivateOracle/common').mkdir(parents=True)
        write(cache/'mods/MeridianPrivateOracle/42/mod.info','name=Meridian Private Oracle\nid=MeridianPrivateOracle\nversionMin=42.21\n')
        dependencies=[]; extra=[]
        if args.viewpoint:
            from viewpoint_smoke import prepare as viewpoint_prepare
            steam=Path('G:/Steam/steamapps/workshop/content/108600')
            receipt=viewpoint_prepare(run,steam/'3809306528/mods/Viewpoint',steam/'3619862853/mods/ZombieBuddy',args.javac)
            for dep in receipt['junctions']: shutil.copytree(dep['source'],cache/'mods'/dep['name'])
            extra=receipt['java_args']; dependencies=receipt['enable_before_map']
            probe_dir=cache/'mods/MeridianPrivateOracle/42/media/lua/client/MeridianTest'
            probe_dir.mkdir(parents=True,exist_ok=True)
            shutil.copy2(receipt['test_driver_lua'],probe_dir/'ViewpointProbe.lua')
        write(cache/'mods/default.txt','VERSION = 1,\nmods\n{\n'+''.join(' mod = '+m+',\n' for m in dependencies+[mod_id,'MeridianPrivateOracle'])+'}\nmaps\n{\n}\n')
        write(cache/'mods/reset-mods-42_00.txt','Explicit isolated oracle selection.\n')
        write(cache/'options.ini',options())
        cfg=dict(folder=maps[0].parent.name,x=x,y=y,z=z,token=run.name,viewpoint=args.viewpoint,
                 targets=json.loads(args.targets.read_text(encoding='utf-8')) if args.targets else [])
        jar=compile_prompt_helper(run,args.javac)
        cmd=[str(args.game/'jre64/bin/java.exe'),*extra,f'-javaagent:{jar}','-Djava.awt.headless=true',
             '--enable-native-access=ALL-UNNAMED','--add-exports=java.base/jdk.internal.misc=ALL-UNNAMED',
             '-XX:-CreateCoredumpOnCrash','-XX:-OmitStackTraceInFastThrow','-XX:+UseZGC','-Xmx8192m',
             '-Dzomboid.steam=0','-Djava.library.path=./win64/;./','-cp','./;projectzomboid.jar',
             'zombie.gameStates.MainScreenState',f'-cachedir={cache}','-nosteam','-debug']
    driver=cache/'mods/MeridianPrivateOracle/42/media/lua/client/MeridianTest'
    cfg['spriteNames']=native_sprite_names(cache/'mods')
    write(driver/'Config.lua','MeridianTestConfig='+lua(cfg)+'\n')
    write(driver/'Menu.lua',MENU)
    write(driver/'Core.lua',CORE)
    probes=CONTENT+'\n'+LIGHTING_CONTENT+'\n'+SPRITE_CONTENT+'\nlocal function tick()'
    write(driver/'World.lua',WORLD.replace('local function tick()',probes,1))
    if cfg.get('viewpoint'):
        write(driver/'ZZ_LoadProbe.lua','require "MeridianTest/ViewpointProbe"\n')
    meta=dict(run=str(run),cache=str(cache),command=cmd,config=cfg,game=str(args.game),status='prepared')
    write(run/'run.json',json.dumps(meta,indent=2))
    return run,meta


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mod',type=Path,default=ROOT/'mod')
    p.add_argument('--game',type=Path,default=DEFAULT_GAME)
    p.add_argument('--javac',type=Path,default=DEFAULT_JAVAC)
    p.add_argument('--targets',type=Path)
    p.add_argument('--viewpoint',action='store_true')
    p.add_argument('--resume',type=Path)
    p.add_argument('--resume-targets',type=Path)
    p.add_argument('--prepare-only',action='store_true')
    p.add_argument('--timeout',type=int,default=600)
    args=p.parse_args()
    run,meta=prepare(args)
    print(json.dumps({'run':str(run),'status':'prepared'}),flush=True)
    if args.prepare_only: return
    report=Path(meta['cache'])/'Lua/meridian-playtest.txt'
    with (run/'client.stdout.log').open('wb') as stream:
        child=subprocess.Popen(meta['command'],cwd=args.game,stdout=stream,stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP|subprocess.CREATE_NO_WINDOW)
        meta.update(pid=child.pid,status='running')
        write(run/'run.json',json.dumps(meta,indent=2))
        deadline=time.monotonic()+args.timeout
        try:
            while child.poll() is None and time.monotonic()<deadline and not report.exists(): time.sleep(1)
            if report.exists():
                time.sleep(3)
                text=report.read_text(encoding='utf-8')
                print(text,flush=True)
                meta['status']='passed' if 'result=PASS' in text else 'failed'
                console=Path(meta['cache'])/'console.txt'
                log=console.read_text(encoding='utf-8',errors='replace') if console.exists() else ''
                errors=[line for line in log.splitlines() if 'dumping Lua stack trace' in line or 'ERROR: Lua' in line]
                meta['lua_error_lines']=errors
                resource_errors,known_resource_warnings=classify_resource_errors(log)
                meta['runtime_resource_errors']=resource_errors
                meta['known_stock_startup_resource_warnings']=known_resource_warnings
                if resource_errors:
                    meta['status']='failed-native-resource-log'
                    print('Native resource gate: '+json.dumps(resource_errors),flush=True)
                if errors:
                    meta['status']='failed-lua-log'
                    print('Lua log gate: '+json.dumps(errors),flush=True)
            else:
                meta['status']='timeout' if child.poll() is None else 'exited-without-report'
                print('No result: '+meta['status'],flush=True)
        finally:
            if child.poll() is None:
                child.terminate()
                try: child.wait(15)
                except subprocess.TimeoutExpired: child.kill(); child.wait(5)
            write(run/'run.json',json.dumps(meta,indent=2))
    shots=sorted((Path(meta['cache'])/'Screenshots').glob('*.png'))
    print(json.dumps({'run':str(run),'status':meta['status'],'screenshots':[str(s) for s in shots]}),flush=True)
    if meta['status']!='passed': raise SystemExit(1)


if __name__=='__main__': main()
