"""Bounded exploration scheduling; no simulated result substitutes for game QA."""
import unittest
import test_runtime as runtime


class BunkerQueue(unittest.TestCase):
    def setUp(self):
        self.harness = runtime.Runtime()
        self.harness.setUp()
        self.lua = self.harness.lua
        self.harness.load('server/Meridian/30_Bunkers.lua')
        self.lua.execute('''
            function ticks(n) for i=1,n do Meridian.processBunkerQueue() end end
            player={x=49088,y=1984,z=-1}
            function player:getX() return self.x end
            function player:getY() return self.y end
            function player:getZ() return self.z end
            function getNumActivePlayers() return 1 end
            function getSpecificPlayer(i) if i==0 then return player end end
        ''')

    def test_unloaded_backlog_cannot_delay_new_loaded_room(self):
        # The old FIFO produces zero spawns after 720 ticks in this scenario.
        self.lua.execute('''
            for i=0,255 do
                Meridian.queueBunkerSquare(square(48128+(i%32)*8,
                    1024+math.floor(i/32)*8,-2))
            end
            Meridian.queueBunkerSquare(square(49056,1952,-1))
            gridCalls=0
            cell.getGridSquare=function(s,x,y,z)
                gridCalls=gridCalls+1
                if z==-1 and x>=49056 and x<49064 and y>=1952 and y<1960 then
                    return square(x,y,z)
                end
            end
            ticks(60)
            assert(spawnCalls==1 and Meridian.bunkerSpawned==3)
            assert(gridCalls<400, 'Do not scan all64squares of every stale job')
            ticks(660);assert(spawnCalls==1)
        ''')

    def test_same_floor_priority_preserves_fair_slot_and_four_job_budget(self):
        self.lua.execute('''
            spawned={}
            function addZombiesInOutfit(x,y,z,count)
                spawnCalls=spawnCalls+1;spawned[#spawned+1]=z
                return {size=function() return count end}
            end
            for i=0,4 do Meridian.queueBunkerSquare(square(48128+i*8,1024,-2)) end
            for i=0,3 do Meridian.queueBunkerSquare(square(49024+i*8,1952,-1)) end
            ticks(60)
            assert(spawnCalls==4)
            assert(spawned[1]==-1 and spawned[2]==-1 and spawned[3]==-1)
            assert(spawned[4]==-2, 'Old loaded floor needs a fair turn')
            ticks(59);assert(spawnCalls==4)
            ticks(1);assert(spawnCalls==8)
        ''')

    def test_saturated_stale_queue_admits_new_room_before_load_event_is_lost(self):
        self.lua.execute('''
            for i=0,2047 do
                Meridian.queueBunkerSquare(square(48128+(i%32)*8,
                    1024+(math.floor(i/32)%32)*8,i<1024 and -2 or -1))
            end
            gridCalls=0
            cell.getGridSquare=function(s,x,y,z)
                gridCalls=gridCalls+1
                if z==-1 and x>=49056 and x<49064 and y>=1952 and y<1960 then
                    return square(x,y,z)
                end
            end
            Meridian.queueBunkerSquare(square(49056,1952,-1))
            ticks(60)
            assert(spawnCalls==1, 'Old2048jobs cannot discard the new room')
            assert(gridCalls<2200, 'Saturation pruning must be anchor-only and bounded')
        ''')

    def test_player_protected_bucket_retries_after_move_without_square_reload(self):
        self.lua.execute('''
            player.x=48643;player.y=1539
            Meridian.queueBunkerSquare(square(48640,1536,-1))
            ticks(360);assert(spawnCalls==0)
            player.x=48680
            ticks(60);assert(spawnCalls==1)
            Meridian.queueBunkerSquare(square(48640,1536,-1))
            ticks(240);assert(spawnCalls==1)
        ''')

    def test_proximity_safety_buckets_do_not_starve_nearest_safe_bucket(self):
        self.lua.execute('''
            player.x=48643.5;player.y=1539.5
            for _,p in ipairs({{48640,1536},{48632,1536},{48648,1536},
                              {48640,1528},{48640,1544},{48672,1536}}) do
                Meridian.queueBunkerSquare(square(p[1],p[2],-1))
            end
            ticks(60)
            assert(spawnCalls==1, 'Protected nearby buckets cannot monopolize all4jobs')
        ''')

    def test_temporary_blocking_retries_with_no_players(self):
        self.lua.execute('''
            function getNumActivePlayers() return 0 end
            blocked=true
            cell.getGridSquare=function(s,x,y,z)
                local q=square(x,y,z)
                q.isFree=function() return not blocked end
                return q
            end
            Meridian.queueBunkerSquare(square(48640,1536,-1))
            ticks(360);assert(spawnCalls==0)
            blocked=false;ticks(60);assert(spawnCalls==1)
        ''')

    def test_unloaded_unseeded_bucket_can_requeue_on_actual_load(self):
        self.lua.execute('''
            function getNumActivePlayers() return 0 end
            Meridian.queueBunkerSquare(square(48640,1536,-1))
            cell.getGridSquare=function() return nil end
            ticks(60);assert(spawnCalls==0)
            cell.getGridSquare=function(s,x,y,z) return square(x,y,z) end
            Meridian.queueBunkerSquare(square(48640,1536,-1))
            ticks(60);assert(spawnCalls==1)
        ''')

    def test_population_cap_and_live_disable_do_not_lose_pending_bucket(self):
        self.lua.execute('''
            Meridian.queueBunkerSquare(square(48640,1536,-1))
            cell.getZombieList=function() return {size=function() return 1600 end} end
            ticks(360);assert(spawnCalls==0)
            SandboxVars.MeridianLongWayHome={BunkerHordes=false}
            cell.getZombieList=function() return emptyList end
            ticks(360);assert(spawnCalls==0)
            SandboxVars.MeridianLongWayHome.BunkerHordes=true
            ticks(60);assert(spawnCalls==1)
        ''')

    def test_saved_bucket_is_not_spawned_after_runtime_reload(self):
        self.lua.execute('''
            Meridian.queueBunkerSquare(square(48640,1536,-1))
            ticks(60);assert(spawnCalls==1)
        ''')
        self.harness.load('server/Meridian/30_Bunkers.lua')
        self.lua.execute('''
            Meridian.queueBunkerSquare(square(48640,1536,-1))
            ticks(120);assert(spawnCalls==1)
        ''')

    def test_multiplayer_client_cannot_queue_or_seed(self):
        self.lua.execute('''
            client=true
            Meridian.queueBunkerSquare(square(48640,1536,-1))
            ticks(120);assert(spawnCalls==0)
            client=false;ticks(120);assert(spawnCalls==0)
        ''')


if __name__ == '__main__':
    unittest.main()
