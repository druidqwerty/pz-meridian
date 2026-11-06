"""Installed-engine capabilities plus clear-road/stair/ceiling invariants."""
from pathlib import Path
import json,sys,unittest
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from test_architecture import sprites,reachable
from architecture import ROOF
from bunker import build_bunker,cover_bunker
from obstacles import ENCOUNTERS,SALVAGE_SPRITES,dress_obstacles
from surface import raster
from world import make_plan

GAME=Path('G:/Steam/steamapps/common/ProjectZomboid')


@unittest.skipUnless(GAME.exists(),'Local B42 metadata required, never distributed')
class EncounterInvariants(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db=sprites()

    def test_all_barriers_are_vanilla_salvage_not_decorative_walls(self):
        for sprite in SALVAGE_SPRITES:
            p=self.db[sprite]
            self.assertIn('IsMoveAble',p,sprite)
            self.assertIn('CanScrap',p,sprite)
            self.assertIn('solidtrans',p,sprite)
        for sprite,direction in [('fixtures_doors_01_68','W'),('fixtures_doors_01_69','N')]:
            p=self.db[sprite]
            self.assertIn('door'+direction,p)
            self.assertEqual(p['MaterialType'],'Metal')
            self.assertNotIn('forceLocked',p)

    def test_route_encounters_keep_five_tile_asphalt_gap(self):
        _,by_cell,sites=make_plan()
        site_cells={tuple(c):s for s in sites for c in s['cells']}
        result=[]; raster_cache={}
        def raster_at(cx,cy):
            if (cx,cy) not in raster_cache:
                raster_cache[cx,cy]=raster(cx,cy,by_cell[cx,cy])
            return raster_cache[cx,cy]
        for cx,cy in sorted({(s['x']//256,s['y']//256) for s in ENCOUNTERS}):
            ground,t=raster(cx,cy,by_cell[cx,cy])
            # Never overwrite an existing authored non-ground object.
            for spec in ENCOUNTERS:
                if (spec['x']//256,spec['y']//256)==(cx,cy):
                    x,y=spec['x']%256,spec['y']%256
                    t[x,y,0].append('fixtures_sinks_01_0')
            rec=dress_obstacles(cx,cy,ground,t,site_cells.get((cx,cy)))
            for spec in rec['encounters']:
                self.assertGreaterEqual(spec['distance'],1800)
                for gap in spec['gap']:
                    x,y=gap['x']%256,gap['y']%256
                    gx,gy=gap['x']//256,gap['y']//256
                    gap_ground,gap_tiles=raster_at(gx,gy)
                    self.assertEqual(gap_ground[y,x],4)
                    if (gx,gy)==(cx,cy):
                        self.assertFalse(set(t[x,y,0]) & set(SALVAGE_SPRITES))
            self.assertEqual(rec,dress_obstacles(cx,cy,ground,raster(cx,cy,by_cell[cx,cy])[1],site_cells.get((cx,cy))))
            result.extend(rec['encounters'])
        self.assertGreater(len(result),35)
        self.assertEqual({s['kind'] for s in result},{'roadworks','evacuation','checkpoint'})

    def test_bulkheads_leave_gallery_routes_and_stairs_connected(self):
        config=dict(minCX=188,maxCX=191,minCY=4,maxCY=7)
        for cx,cy in ((188,4),(189,5),(191,7)):
            t,r,b={},[],[]
            rec=build_bunker(t,r,b,cx,cy,config)
            self.assertTrue(rec['obstacles'])
            for z in (-2,-1):
                seen,_=reachable(t,self.db,(127,128),z)
                for p in ((1,128),(254,128),(128,1),(128,254),(131,136)):
                    self.assertIn(p,seen)
                self.assertIn('fixtures_doors_01_68',t[48,128,z])
                self.assertIn('fixtures_doors_01_69',t[128,48,z])
            self.assertNotIn((128,136,-1),t)
            if rec['entrances']:self.assertNotIn((128,128,0),t)

    def test_seam_fragments_are_adjacent_not_replicated_cells(self):
        _,by,sites=make_plan()
        ss={tuple(c):s for s in sites for c in s['cells']}
        relevant={(int((e['x']+dx)//256),int((e['y']+dy)//256))
                  for e in ENCOUNTERS for dx in (-12,12) for dy in (-12,12)}
        anchors=[]; objects=[]
        for cx,cy in sorted(relevant & by.keys()):
            g,t=raster(cx,cy,by[cx,cy])
            rec=dress_obstacles(cx,cy,g,t,ss.get((cx,cy)))
            anchors.extend(rec['encounters']);objects.extend(rec['objects'])
        self.assertEqual(len(anchors),len({e['id'] for e in anchors}))
        self.assertEqual(len(objects),len({(o['x'],o['y'],o['z']) for o in objects}))
        for obj in objects:
            self.assertTrue(any(max(abs(obj['x']-e['x']),abs(obj['y']-e['y']))<=12
                                for e in ENCOUNTERS),obj)
        seam=next(e for e in anchors if e['horizontal'] and e['y']%256==0)
        near=[o for o in objects if abs(o['x']-seam['x'])<12 and abs(o['y']-seam['y'])<12]
        self.assertTrue(any(o['y']<seam['y'] for o in near))
        self.assertTrue(any(o['y']>seam['y'] for o in near))

    def test_ceiling_underlay_preserves_surface_objects_and_apertures(self):
        terrain=['blends_street_01_86','street_trafficlines_01_0']
        tree=['blends_natural_01_16','vegetation_trees_01_8']
        t={(12,13,0):terrain.copy(),(14,15,0):tree.copy(),
           (11,10,-1):['floors_interior_tilesandwood_01_16']}
        cover_bunker(t,{-1:{(12,13),(14,15),(128,128)},-2:{(11,10),(128,136)}},True)
        self.assertEqual(t[12,13,0],[ROOF]+terrain)
        self.assertEqual(t[14,15,0],[ROOF]+tree)
        self.assertNotIn((128,128,0),t)
        self.assertNotIn((128,136,-1),t)
        jar=Path('G:/Steam/steamapps/workshop/content/108600/3809306528/mods/Viewpoint/42/media/java/client/Viewpoint.jar')
        if jar.exists():
            with ZipFile(jar) as z:
                self.assertIn(ROOF+' flat',z.read('viewpoint/roof-pieces.txt').decode().splitlines())


if __name__=='__main__':unittest.main()
