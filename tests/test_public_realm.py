"""Seam-continuity and native-safe commercial hardscape acceptance."""
from pathlib import Path
import sys, unittest
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from landscape import landscape, PAVING
from public_geometry import exterior_path, parking_stalls
from public_realm import public_realm
from building_signs import SIGNS, place_building_sign
from test_architecture import GAME, sprites


class WalkGeometryAcceptance(unittest.TestCase):
    def test_route_avoids_whole_building_not_a_broken_manhattan_line(self):
        target=np.zeros((16,16),bool);target[7,14]=True
        blocked=np.zeros_like(target);blocked[3:13,7:10]=True
        path=exterior_path((2,7),target,blocked,limit=32)
        self.assertEqual(path[0],(2,7));self.assertEqual(path[-1],(14,7))
        self.assertTrue(all(not blocked[y,x] for x,y in path))
        self.assertTrue(all(abs(a-c)+abs(b-d)==1 for (a,b),(c,d) in zip(path,path[1:])))
        self.assertTrue(all(len(line)==7 for line in parking_stalls((16,120,224,104))))

    def test_sidewalk_reaches_cell_seams_without_overwriting_road_or_wall(self):
        ground=np.full((256,256),3,np.uint8);ground[124:133,:]=4
        tiles={(x,y,0):['blends_street_01_86' if ground[y,x]==4 else
                       'blends_natural_01_16'] for x in range(256) for y in range(256)}
        tiles[0,123,0].append('vegetation_trees_01_8')
        tiles[60,123,0].append('walls_exterior_house_02_17')
        before={p:list(n) for p,n in tiles.items() if ground[p[1],p[0]]==4}
        landscape(tiles,ground,2,190,[],dict(kind='town'))
        for x in range(256):
            if x!=60:self.assertEqual(tiles[x,123,0],[PAVING])
            self.assertEqual(tiles[x,122,0],[PAVING])
        self.assertIn('walls_exterior_house_02_17',tiles[60,123,0])
        self.assertEqual(before,{p:tiles[p] for p in before})
        self.assertEqual(tiles[0,123,0],tiles[255,123,0])


@unittest.skipUnless(GAME.exists(),'Requires installed B42 native sprite oracle')
class CommercialNativeAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.db=sprites()

    def test_broad_parking_and_plaza_keep_real_asphalt_aisles_and_buildings(self):
        ground=np.full((256,256),3,np.uint8);ground[120:224,124:133]=4
        tiles={(x,y,0):['blends_street_01_86' if ground[y,x]==4 else
                       'blends_natural_01_16'] for x in range(256) for y in range(256)}
        hard=np.zeros((256,256),bool);hard[24:97,24:121]=True
        tiles[50,50,0]=['floors_interior_tilesandwood_01_40','furniture_tables_high_01_4']
        stats,mask=public_realm(tiles,ground,2,190,[],dict(
            parking=[[16,120,224,104]],plazas=[[24,100,96,16]]),hard)
        self.assertGreater(stats['parkingSquares'],20000)
        self.assertGreater(stats['plazaSquares'],1500)
        self.assertGreater(stats['parkingDividers'],100)
        self.assertIn('furniture_tables_high_01_4',tiles[50,50,0])
        for y in range(120,224):self.assertEqual(tiles[128,y,0],['blends_street_01_86'])
        for (x,y,z),names in tiles.items():
            for name in names:
                self.assertIn(name,self.db)
                if mask[y,x]:self.assertNotIn('solidtrans',self.db[name])

    def test_business_signs_are_complete_and_mount_without_sealing_door(self):
        for kind,group in SIGNS.items():
            for dx,dy,name in group:
                props=self.db[name]
                self.assertIn('Sign',props['CustomName'])
                self.assertEqual(props['Facing'],'S')
                if 'SpriteGridPos' in props:
                    self.assertEqual(props['SpriteGridPos'],f'{dx},{dy}')
            tiles={(x,30,0):['walls_exterior_house_02_17'] for x in range(20,48)}
            tiles[34,30,0]=['walls_exterior_house_02_27','fixtures_doors_01_1']
            before=list(tiles[34,30,0])
            placed=place_building_sign(tiles,(20,10,28,20),kind)
            self.assertEqual(len(placed),len(group),kind)
            self.assertEqual(tiles[34,30,0],before)


if __name__=='__main__':unittest.main()
