"""Policy regression checks; these do not replace native gameplay tests."""
from pathlib import Path
import json
import unittest
from lupa import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
LUA = ROOT / 'mod/42/media/lua'


class Runtime(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute('''
            Events=setmetatable({}, {__index=function(t,k)
                local e={Add=function() end};rawset(t,k,e);return e end})
            SandboxVars={Zombies=3,ZombieConfig={PopulationMultiplier=1}}
            client=false
            function isClient() return client end
            function isServer() return false end
            function getNumActivePlayers() return 0 end
            saved={}
            ModData={getOrCreate=function() return saved end}
            function zombie(x,y,z)
                return {getX=function() return x end,getY=function() return y end,
                getZ=function() return z end,
                removeFromWorld=function(s) s.removed=true end,
                removeFromSquare=function(s) s.detached=true end}
            end
            function square(x,y,z)
                return {getX=function() return x end,getY=function() return y end,
                getZ=function() return z end,getRoom=function() return {} end,
                TreatAsSolidFloor=function() return true end,
                HasStairs=function() return false end,isFree=function() return true end,
                getVehicleContainer=function() return nil end}
            end
            emptyList={size=function() return 0 end}
            cell={getZombieList=function() return emptyList end,
                getGridSquare=function(s,x,y,z) return square(x,y,z) end}
            function getCell() return cell end
            spawnCalls=0
            function addZombiesInOutfit(x,y,z,count)
                spawnCalls=spawnCalls+1
                return {size=function() return count end}
            end
            function getScriptManager() return {FindItem=function(s,t) return {} end} end
            IsoDirections={N=0}
        ''')
        self.load('shared/Meridian/10_Core.lua')
        self.lua.execute('''
            Meridian.Config={world={minX=0,minY=0,maxX=49151,maxY=49151},
              safeCity={x1=48128,y1=1024,x2=49151,y2=2047},
              bunkers={{id="final",x1=48128,y1=1024,x2=49151,y2=2047,minZ=-2,maxZ=-1}},
              starterVehicle={x=640,y=48640,z=0,script="Base.SUV"},
              caches={{x=10,y=20,z=-1,kind="food"}}}
        ''')

    def load(self, relative):
        self.lua.execute((LUA / relative).read_text(encoding='utf-8-sig'))

    def check(self, source):
        self.lua.execute(source)

    def test_surface_and_bunker_boundary(self):
        self.load('server/Meridian/20_Sanctuary.lua')
        self.check('''
            local a=zombie(48128,1024,0); Meridian.enforceSanctuary(a); assert(a.removed and a.detached)
            local b=zombie(49151,2047,3); Meridian.enforceSanctuary(b); assert(b.removed)
            local c=zombie(48640,1536,-1); Meridian.enforceSanctuary(c); assert(not c.removed)
            local d=zombie(48127,1024,0); Meridian.enforceSanctuary(d); assert(not d.removed)
            client=true
            local e=zombie(48640,1536,0); Meridian.enforceSanctuary(e); assert(not e.removed)
        ''')

    def test_bunker_persistent_and_zombie_disable(self):
        self.load('server/Meridian/30_Bunkers.lua')
        self.check('''
            local sq=square(48640,1536,-1)
            SandboxVars.Zombies=6;Meridian.queueBunkerSquare(sq)
            for i=1,60 do Meridian.processBunkerQueue() end
            assert(spawnCalls==0)
            SandboxVars.Zombies=3;SandboxVars.ZombieConfig.PopulationMultiplier=0
            Meridian.queueBunkerSquare(sq)
            for i=1,60 do Meridian.processBunkerQueue() end
            assert(spawnCalls==0)
            SandboxVars.ZombieConfig.PopulationMultiplier=1
            Meridian.queueBunkerSquare(sq)
            for i=1,60 do Meridian.processBunkerQueue() end
            assert(spawnCalls==1 and Meridian.bunkerSpawned==3)
            Meridian.queueBunkerSquare(sq)
            for i=1,60 do Meridian.processBunkerQueue() end
            assert(spawnCalls==1)
            Meridian.queueBunkerSquare(square(48640,1536,0))
            for i=1,60 do Meridian.processBunkerQueue() end
            assert(spawnCalls==1)
        ''')

    def test_supplies_not_repeatable(self):
        self.load('server/Meridian/40_Supplies.lua')
        self.check('''
            local data={};local sq=square(10,20,-1);local items={}
            local parent={getSquare=function() return sq end,getModData=function() return data end}
            local container={getParent=function() return parent end,
                AddItem=function(s,t) items[#items+1]=t end}
            Meridian.fillSupplies("storage","crate",container)
            assert(#items==16 and data.MeridianCacheFilled)
            Meridian.fillSupplies("storage","crate",container);assert(#items==16)
            Meridian.Config.caches[1].kind="armystorage";data.MeridianCacheFilled=nil
            Meridian.fillSupplies("armystorage","crate",container)
            assert(#items==28 and items[23]=="Base.Pistol")
        ''')

    def test_starter_vehicle_one_per_world(self):
        self.load('server/Meridian/50_Starter.lua')
        self.check('''
            local created=0;local keys=0;local fuel=0;local repaired=false
            local tank={getContainerCapacity=function() return 50 end,
                setContainerContentAmount=function(s,n) fuel=n end}
            function addVehicleDebug(script,direction,none,sq)
                assert(script=="Base.SUV" and sq:getX()==640)
                created=created+1
                return {repair=function() repaired=true end,
                getPartById=function(s,id) return tank end,
                createVehicleKey=function() return "key" end}
            end
            local p={getX=function() return 536 end,getY=function() return 48664 end,
                getInventory=function() return {AddItem=function() keys=keys+1 end} end}
            Meridian.startExpedition(p);Meridian.startExpedition(p)
            assert(created==1 and keys==1 and fuel==50 and repaired)
        ''')

    def test_all_lua_parse_and_translations(self):
        for path in LUA.rglob('*.lua'):
            self.lua.compile(path.read_text(encoding='utf-8-sig'))
        translate = LUA/'shared/Translate'
        for name in ('UI.json', 'Sandbox.json'):
            en = json.loads((translate/'EN'/name).read_text(encoding='utf-8-sig'))
            ru = json.loads((translate/'RU'/name).read_text(encoding='utf-8-sig'))
            self.assertEqual(set(en), set(ru))
            self.assertTrue(all(en.values()) and all(ru.values()))


if __name__ == '__main__':
    unittest.main()
