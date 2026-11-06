"""Private read-only sampling wrapper; never part of the shipped mod."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
import playtest

PROBE = r'''
local populationProbe
local function populationSample(data,label,elapsed)
 local p=getPlayer(); local cell=getCell(); local zs=cell:getZombieList()
 local global,samez,near=zs:size(),0,0
 for n=0,zs:size()-1 do
  local a=zs:get(n)
  if math.floor(a:getZ())==data.z then
   samez=samez+1
   if math.abs(a:getX()-data.x)<60 and math.abs(a:getY()-data.y)<60 then near=near+1 end
  end
 end
 local state=ModData.get("MeridianLongWayHome")
 local total,localSeeded=0,0
 for key,value in pairs(state and state.seeded or {}) do
  if value then
   total=total+1
   local site,bx,by,zz=string.match(key,"^([^:]+):(%-?%d+):(%-?%d+):(%-?%d+)$")
   if zz and tonumber(zz)==data.z and math.abs(tonumber(bx)*8+3.5-data.x)<60
     and math.abs(tonumber(by)*8+3.5-data.y)<60 then localSeeded=localSeeded+1 end
  end
 end
 local eligible,loaded=0,0
 local site=Meridian.bunkerAt(data.x,data.y,data.z)
 for x=data.x-60,data.x+60 do for y=data.y-60,data.y+60 do
  local radius=(x-data.x)^2+(y-data.y)^2
  if radius>=196 and radius<=3600 then
   local q=cell:getGridSquare(x,y,data.z)
   if q then
    loaded=loaded+1
    if Meridian.contains(site,x,y) and q:getRoom() and q:TreatAsSolidFloor()
      and not q:HasStairs() and q:isFree(false) then eligible=eligible+1 end
   end
  end
 end end
 local prefix=label.."_population_t"..elapsed
 MeridianTest.record(prefix.."_elapsed_ms",getTimestampMs()-populationProbe.started)
 MeridianTest.record(prefix.."_global",global)
 MeridianTest.record(prefix.."_same_z",samez)
 MeridianTest.record(prefix.."_near_60",near)
 MeridianTest.record(prefix.."_process_bunker_spawned",Meridian.bunkerSpawned or 0)
 MeridianTest.record(prefix.."_seeded_total",total)
 MeridianTest.record(prefix.."_seeded_near_60",localSeeded)
 MeridianTest.record(prefix.."_loaded_annulus_14_60",loaded)
 MeridianTest.record(prefix.."_free_floor_annulus_14_60",eligible)
end
local function beginPopulation(data)
 if data.populationDiagnostics then
  populationProbe={data=data,started=getTimestampMs(),next=1,intervals={0,15,30,60}}
  MeridianTest.record(data.name.."_diagnostic_kind","read_only_no_queue_spawn_or_time_mutation")
 end
end
local function updatePopulation()
 if not populationProbe then return end
 local s=populationProbe; local elapsed=s.intervals[s.next]
 if elapsed and getTimestampMs()-s.started>=elapsed*1000 then
  populationSample(s.data,s.data.name,elapsed); s.next=s.next+1
 end
end
'''

world=playtest.WORLD
for marker in ('local function tick()','\n updateIsoZoom()\n',
               '  MeridianTest.record("target_teleport",target.name)',
               '  phase=3; due=getTimestampMs()+12000'):
    assert world.count(marker)==1, marker
world=world.replace('local function tick()',PROBE+'\nlocal function tick()',1)
world=world.replace('\n updateIsoZoom()\n','\n updateIsoZoom()\n updatePopulation()\n',1)
world=world.replace('  MeridianTest.record("target_teleport",target.name)',
    '  MeridianTest.record("target_teleport",target.name)\n  beginPopulation(target)',1)
world=world.replace('  phase=3; due=getTimestampMs()+12000',
    '  phase=3; due=getTimestampMs()+(target.populationDiagnostics and 61000 or 12000)',1)
playtest.WORLD=world
playtest.main()
