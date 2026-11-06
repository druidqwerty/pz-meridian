"""Actual southeast-cell compile: tower lots must not overlap thick ramparts."""
from pathlib import Path
from unittest.mock import patch
import sys,unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tests')]
import generate
from world import make_plan
from map_binary import _room_index
from test_architecture import GAME,sprites,reachable


@unittest.skipUnless(GAME.exists(),'Requires owner-installed B42 metadata')
class MetropolitanPerimeter(unittest.TestCase):
    def test_compiled_corner_retains_disjoint_rooms_street_access_and_thick_wall(self):
        _,features,sites=make_plan()
        site=next(s for s in sites if s['name']=='Meridian')
        bunker=dict(minCX=188,maxCX=191,minCY=4,maxCY=7)
        captured={}
        def capture(folder,cx,cy,tiles,rooms,buildings,density):
            captured.update(tiles=tiles,rooms=rooms,buildings=buildings,density=density)
            return dict(squares=len(tiles),bytes=0)
        with patch.object(generate,'write_cell',capture),patch.object(generate,'audit_cell'):
            result=generate.compile_cell((191,7,features[191,7],site,bunker))
        # Native RoomDefs reject even one overlap; this catches wall/tower
        # intersection before a real save can be generated with corrupt rooms.
        _room_index(captured['rooms'])
        db=sprites();tiles=captured['tiles']
        seen,_=reachable(tiles,db,(64,64),0)
        self.assertEqual(len(result['records']),16)
        for record in result['records']:
            x,y,z=record['spawn']
            self.assertIn((x%256,y%256),seen,(record['kind'],'city street to front door'))
            a,b,w,h=record['rect'];a%=256;b%=256
            self.assertLess(a+w,241)
            self.assertLess(b+h+3,241)
        for axis in range(20,241):
            self.assertIn((192,axis),seen,'North-south street severed')
            self.assertIn((axis,192),seen,'East-west street severed')
        self.assertTrue(all(value==0 for value in captured['density']))
        rampart=result['cityWall']
        self.assertGreaterEqual(rampart['height'],8)
        self.assertGreaterEqual(rampart['depth'],12)
        for z in (0,rampart['walkwayZ']):
            self.assertIn('floors_exterior_tilesandstone_01_0',tiles[247,200,z])
            self.assertIn('floors_exterior_tilesandstone_01_0',tiles[200,247,z])
        self.assertTrue(any(rr['level']==8 for rr in captured['rooms']))


if __name__=='__main__':unittest.main()
