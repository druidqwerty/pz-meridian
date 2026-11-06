"""Habitat acceptance from physical native floors/doors and installed metadata."""
from pathlib import Path
import sys,unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from bunker import build_bunker
from habitat import WINGS
from test_architecture import sprites,reachable,stairs

GAME=Path('G:/Steam/steamapps/common/ProjectZomboid')
CONFIG=dict(minCX=188,maxCX=191,minCY=4,maxCY=7)


@unittest.skipUnless(GAME.exists(),'Local B42 metadata required, never redistributed')
class HabitatAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.db=sprites()

    def test_all_wings_are_distinct_with_real_domestic_and_technical_rooms(self):
        wings=set(); entrance_roles=set(); rooms_by_role={}; floor_names=set()
        distributions=(GAME/'media/lua/server/Items/Distributions.lua').read_text(encoding='utf-8')
        for cy in range(4,8):
            for cx in range(188,192):
                t,r,b={},[],[]
                rec=build_bunker(t,r,b,cx,cy,CONFIG)
                wings.add(rec['wing']['id']);floor_names.add(rec['wing']['floor'])
                for entry in rec['entrances']:
                    entrance_roles.add(entry['role'])
                    self.assertTrue(entry['name'] and entry['nameRU'])
                    self.assertEqual(entry['wing'],rec['wing']['id'])
                for room in rec['roomRoles']:
                    rooms_by_role[room['role']]=rooms_by_role.get(room['role'],0)+1
                    self.assertRegex(distributions,rf'(?m)^\s*{room["name"]}\s*=\s*\{{')
                    # Furniture must actually exist in the declared room, not
                    # just in its descriptive manifest entry.
                    x,y,w,h=room['rect'];x%=256;y%=256;z=room['z']
                    self.assertTrue(any(len(t.get((xx,yy,z),[]))>1
                        for xx in range(x+1,x+w-1) for yy in range(y+1,y+h-1)),room)
                self.assertEqual(stairs(t,self.db),rec['stairs'])
                self.assertFalse(set(s for ns in t.values() for s in ns)-self.db.keys())
        self.assertEqual(len(wings),16)
        self.assertEqual(len(entrance_roles),12)
        self.assertGreaterEqual(len(floor_names),5)
        self.assertTrue({'laundry','shower','nursery','gym','library','assembly',
                         'pump','electrical','workshop','communications','archive'}<=rooms_by_role.keys())
        self.assertLess(rooms_by_role['laboratory'],sum(rooms_by_role.values())//8)

    def test_service_ring_remains_connected_when_central_junction_is_unavailable(self):
        # Remove the centre in a diagnostic graph, representing an unsafe crowd
        # there. A genuine ring must connect all four arms without that centre.
        for cx,cy in ((188,4),(189,5),(191,7)):
            t,r,b={},[],[];build_bunker(t,r,b,cx,cy,CONFIG)
            for z in (-2,-1):
                for x in range(120,144):
                    for y in range(120,144):t.pop((x,y,z),None)
                seen,_=reachable(t,self.db,(14,128),z)
                for p in ((128,14),(242,128),(128,242)):
                    self.assertIn(p,seen,'Service loop cannot bypass the central junction')

    def test_room_second_exits_and_original_axis_stairs_remain_accessible(self):
        for cx,cy in ((188,4),(189,5),(191,7)):
            t,r,b={},[],[];rec=build_bunker(t,r,b,cx,cy,CONFIG)
            for z in (-2,-1):
                seen,_=reachable(t,self.db,(127,128),z)
                for role in (rr for rr in rec['roomRoles'] if rr['z']==z):
                    x,y,w,h=role['rect'];x%=256;y%=256
                    self.assertIn((x,y+20 if w==28 else y+24),seen)
                    exits=0
                    boundary={(xx,yy) for xx in range(x,x+w+1) for yy in (y,y+h)}
                    boundary|={(xx,yy) for xx in (x,x+w) for yy in range(y,y+h+1)}
                    for xx,yy in boundary:
                        if any(s in ('fixtures_doors_01_68','fixtures_doors_01_69')
                               for s in t.get((xx,yy,z),[])):exits+=1
                    self.assertGreaterEqual(exits,2,role)
                for p in ((128,1),(128,254),(1,128),(254,128),(131,136)):
                    self.assertIn(p,seen)


if __name__=='__main__':unittest.main()
