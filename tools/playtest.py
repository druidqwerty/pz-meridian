"""Private, supervised PZ B42 game oracle. Never installed in the product.

No keyboard/mouse input; all saves/options and optional Java approvals are run-local.
Requires the user's installed game and reusable pz-map-tools alongside this project.
"""
from __future__ import annotations
import argparse
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
 if not ok then MeridianTest.record("exception",err); MeridianTest.failed=true; MeridianTest.finish() end
end
require "MeridianTest/Menu"
'''

WORLD = r'''
require "TimedActions/WalkToTimedAction"
local phase,due,index,startX,startY,target=0,0,0,nil,nil,nil
local testCar
local function shot(name) MeridianTest.record("screenshot",name); takeScreenshot() end
local function inspectPoint(label,expected)
 local p=getPlayer(); local sq=p:getSquare()
 MeridianTest.record(label.."_position",p:getX()..","..p:getY()..","..p:getZ())
 MeridianTest.check(label.."_floor",sq and sq:getFloor()~=nil)
 if expected.room then MeridianTest.check(label.."_room",sq and sq:getRoom()~=nil) end
 local counts={containers=0,items=0,doors=0,stairs=0,zombies=0,surface=0,below=0}
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
 if expected.safeSurface then MeridianTest.check(label.."_no_surface_zombies",counts.surface==0) end
 if expected.infected then MeridianTest.check(label.."_infected",counts.below>0) end
 shot(label)
end
local function tick()
 if getTimestampMs()<due then return end
 local p=getPlayer()
 if phase==0 then
  if MeridianTestConfig.resume then
   local d=p:getModData()
   MeridianTest.check("reload_token",d.MeridianTestToken==MeridianTestConfig.token)
   MeridianTest.check("reload_position",d.MeridianTestX and math.abs(p:getX()-d.MeridianTestX)<1 and math.abs(p:getY()-d.MeridianTestY)<1 and math.abs(p:getZ()-d.MeridianTestZ)<0.1)
   inspectPoint("reload",{}); MeridianTest.finish(); return
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
  p:teleportTo(target.x+0.5,target.y+0.5,target.z or 0)
  MeridianTest.record("target_teleport",target.name)
  phase=3; due=getTimestampMs()+12000
 elseif phase==3 then
  inspectPoint(target.name,target)
  if target.vehicle then
   testCar=nil
   local list=getCell():getVehicles()
   for n=0,list:size()-1 do
    local car=list:get(n)
    if (car:getX()-target.x)^2+(car:getY()-target.y)^2<400 then testCar=car; break end
   end
   MeridianTest.check("starter_vehicle_present",testCar~=nil)
   assert(testCar,"Starter SUV not loaded near expected road position")
   MeridianTest.record("starter_vehicle_script",testCar:getScriptName())
   local tank=testCar:getPartById("GasTank")
   MeridianTest.check("starter_vehicle_fuel",tank and tank:getContainerContentAmount()>1)
   local haveKey=p:getInventory():haveThisKeyId(testCar:getKeyId())
   MeridianTest.check("starter_vehicle_key",haveKey)
   testCar:enter(0,p); testCar:setCharacterPosition(p,0,"inside")
   MeridianTest.check("starter_vehicle_enter",p:getVehicle()==testCar)
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
  elseif MeridianTestConfig.viewpoint then phase=4 else phase=2 end
 elseif phase==12 then
  MeridianTest.check("starter_vehicle_engine",testCar:isEngineRunning())
  shot("starter_engine_running")
  testCar:shutOff(); testCar:exit(p); testCar:setCharacterPosition(p,0,"outside")
  testCar=nil
  if MeridianTestConfig.viewpoint then phase=4 else phase=2 end
 elseif phase==11 then
  local d=target.walkTo
  MeridianTest.record(target.name.."_walk_result",p:getX()..","..p:getY()..","..p:getZ())
  MeridianTest.check(target.name.."_stair_traversal",math.abs(p:getZ()-d.z)<0.1 and math.abs(p:getX()-d.x)<1.5 and math.abs(p:getY()-d.y)<1.5)
  shot(target.name.."_after_stairs")
  if MeridianTestConfig.viewpoint then phase=4 else phase=2 end
 elseif phase==4 then
  if not RRViewpointProbe.select("first") then return end
  RRViewpointProbe.aim(-math.pi/4,-0.08)
  phase=5; due=getTimestampMs()+3500
 elseif phase==5 then
  MeridianTest.check(target.name.."_first_camera",RRViewpointProbe.mode()=="first"); shot(target.name.."_first")
  phase=6
 elseif phase==6 then
  if not RRViewpointProbe.select("third") then return end
  RRViewpointProbe.aim(-math.pi/4,-0.08)
  phase=7; due=getTimestampMs()+3500
 elseif phase==7 then
  MeridianTest.check(target.name.."_third_camera",RRViewpointProbe.mode()=="third"); shot(target.name.."_third")
  phase=9
 elseif phase==9 then
  if not RRViewpointProbe.select("isometric") then return end
  phase=2
 elseif phase==8 then
  ISWorldMap.ShowWorldMap(0)
  local map=ISWorldMap_instance
  MeridianTest.check("atlas_opens",map~=nil)
  assert(map,"Native paper map did not open")
  map:setHideUnvisitedAreas(false)
  map.mapAPI:setBoolean("Isometric",false)
  map.mapAPI:resetView()
  phase=13; due=getTimestampMs()+6000
 elseif phase==13 then
  local map=ISWorldMap_instance
  MeridianTest.check("atlas_loaded",map and map.mapAPI:isDataLoaded() and map.mapAPI:getDataCount()>0)
  shot("native_atlas_overview")
  map:close(); setGameSpeed(1)
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
    write(driver/'Config.lua','MeridianTestConfig='+lua(cfg)+'\n')
    write(driver/'Menu.lua',MENU)
    write(driver/'Core.lua',CORE)
    write(driver/'World.lua',WORLD)
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
