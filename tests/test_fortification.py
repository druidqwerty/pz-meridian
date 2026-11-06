"""Independent native clearance and walkability checks for the thick city wall."""
from pathlib import Path
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from fortification import build_wall, HEIGHT, INNER, OUTER
from map_binary import _room_index
from test_architecture import sprites,reachable,stairs,GAME,combine


@unittest.skipUnless(GAME.exists(),'Owner B42 metadata required')
class FortificationAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.db=sprites()

    def test_width_height_native_stair_flights_and_walkable_crown(self):
        t,r,b={},[],[]
        rec=build_wall(188,5,t,r,b)
        _room_index(r)
        self.assertEqual(rec['depth'],13)
        self.assertEqual(stairs(t,self.db),HEIGHT)
        for z in range(HEIGHT+1):
            seen,free=reachable(t,self.db,(3,232),z)
            self.assertIn((7,230),seen)
            self.assertIn((10,220),seen)
        seen,_=reachable(t,self.db,(23,231),0)
        self.assertIn((7,232),seen,'Bastion cannot be entered from city side')
        self.assertEqual(set(s for names in t.values() for s in names)-self.db.keys(),set())

    def test_road_gate_keeps_native_vehicle_clearance_and_arch_above(self):
        t,r,b={},[],[]
        rec=build_wall(188,6,t,r,b)
        for x in range(OUTER,INNER):
            for y in range(0,10):
                for z in range(4):
                    p=combine(self.db,t.get((x,y,z),[]))
                    self.assertFalse(any(k in p for k in ('WallW','WallN','solid','solidtrans')))
                self.assertIn('solidfloor',combine(self.db,t[x,y,4]))
        self.assertEqual(rec['gateClearHeight'],4)

    def test_corner_has_disjoint_rooms_and_continuous_roofwalk(self):
        t,r,b={},[],[];build_wall(188,4,t,r,b)
        _room_index(r)
        seen,_=reachable(t,self.db,(8,200),HEIGHT)
        self.assertIn((200,8),seen)


if __name__=='__main__': unittest.main()
