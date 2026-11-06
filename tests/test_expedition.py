"""Map geography/compound acceptance, independent of manifest counts."""
from pathlib import Path
import sys,unittest
from shapely.geometry import LineString,Point

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from world import make_plan,ROUTE,SIZE,SAFE
from expedition import enrich_plan
from expedition_sites import CHAPTERS,POIS,BASES
from expedition_decor import decorate,ALL_SPRITES
from architecture import KINDS,build_structure
from surface import raster,dress
from test_architecture import sprites,reachable


class ExpeditionGeography(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.features,cls.by_cell,cls.sites=make_plan()
        cls.compounds=[s for s in cls.sites if s.get('kind')=='expedition']

    def test_distinct_content_is_dry_and_clear_of_all_driving_lanes(self):
        self.assertEqual(len(self.compounds),28)
        self.assertEqual(sum(s['category']=='landmark' for s in self.compounds),10)
        self.assertEqual(sum(s['category']=='stop' for s in self.compounds),12)
        self.assertEqual(sum(s['category']=='base' for s in self.compounds),6)
        city=next(s for s in self.sites if s['kind']=='city')
        self.assertEqual(city['expeditionBase']['id'],'meridian-home')
        self.assertEqual({s['chapter'] for s in self.sites},{c[0] for c in CHAPTERS})
        self.assertEqual(len({tuple(c) for s in self.compounds for c in s['cells']}),28)
        for site in self.compounds:
            cx,cy=site['cells'][0]
            g,t=raster(cx,cy,self.by_cell[cx,cy])
            for spec in site['structures']:
                x,y=spec['x'],spec['y'];w,h,*_=KINDS[spec['kind']]
                footprint=g[y-1:y+h+4,x-1:x+w+2]
                self.assertFalse(((footprint==1)|(footprint==4)).any(),(site['name'],spec))
            self.assertEqual(g[128,128],4)
        dam=next(s for s in self.compounds if s['archetype']=='sluice-seven')
        cx,cy=dam['cells'][0]
        self.assertGreater((raster(cx,cy,self.by_cell[cx,cy])[0]==1).sum(),10000)

    def test_three_road_classes_reconnect_without_cross_region_shortcuts(self):
        categories={prop[1] for _,material,prop in self.features
                    if material=='road' and prop and prop[0]=='highway'}
        self.assertTrue({'primary','secondary','service'}<=categories)
        self.assertEqual(ROUTE.length,128256)
        secondary=[g for g,m,p in self.features if m=='road' and p==('highway','secondary')]
        self.assertEqual(len(secondary),6)
        for site in self.compounds:
            arm=LineString(site['connector'])
            self.assertLessEqual(arm.length,1400)
            self.assertLess(ROUTE.distance(Point(arm.coords[0])),.001)
            self.assertEqual(tuple(arm.coords[-1]),(site['x'],site['y']))
            if 'secondExit' in site:
                loop=LineString(site['secondExit'])
                self.assertLess(ROUTE.distance(Point(loop.coords[-1])),.001)
                self.assertLessEqual(Point(loop.coords[-1]).distance(Point(arm.coords[0])),256.001)
        self.assertGreaterEqual(sum('secondExit' in s for s in self.compounds),20)

    @unittest.skipUnless(Path('G:/Steam/steamapps/common/ProjectZomboid').exists(),'Local metadata required')
    def test_ten_setpieces_use_native_sprites_and_leave_every_entrance_reachable(self):
        db=sprites();self.assertFalse(set(ALL_SPRITES)-db.keys())
        themes=set();arrangements=set()
        for site in (s for s in self.compounds if s['category']=='landmark'):
            cx,cy=site['cells'][0]
            g,t=raster(cx,cy,self.by_cell[cx,cy]);rooms=[];buildings=[];records=[]
            for index,spec in enumerate(site['structures']):
                records.append(build_structure(t,rooms,buildings,spec['x'],spec['y'],spec['kind'],seed=index))
            dress(cx,cy,g,t,True)
            road_before={p:tuple(v) for p,v in t.items() if p[2]==0 and g[p[1],p[0]]==4}
            stats=decorate(t,g,cx,cy,records,site)
            themes.add(stats['setpiece'])
            arrangements.add(tuple((s['x'],s['y']) for s in site['structures']))
            self.assertGreater(stats['props'],0,site['name'])
            self.assertEqual(road_before,{p:tuple(t[p]) for p in road_before})
            seen,_=reachable(t,db,(128,128),0)
            for record in records:
                self.assertIn(tuple(record['spawn'][:2]),seen,(site['name'],record['kind']))
        self.assertEqual(len(themes),10)
        self.assertEqual(len(arrangements),10)


if __name__=='__main__':unittest.main()
