"""Requirements-level checks: town diversity, skyline progression and retail access."""
from pathlib import Path
from collections import Counter
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from world import make_plan
from regional_program import settlement_program
from content_catalog import city_program
from architecture import KINDS
from surface import raster


class UrbanProgression(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.features,cls.by,cls.sites=make_plan()

    def test_first_town_has_real_public_commercial_and_small_building_mix(self):
        site=next(s for s in self.sites if s['id']==0)
        kinds={p['kind'] for cx,cy in site['cells'] for p in settlement_program(site,cx,cy)}
        self.assertTrue({'cottage','garage','guardhut','school','police','gunshop','generalstore'}<=kinds)
        compositions=[]
        for site in (s for s in self.sites if s['kind']=='town'):
            kinds=[p['kind'] for cx,cy in site['cells'] for p in settlement_program(site,cx,cy)]
            compositions.append(tuple(sorted(Counter(kinds).items())))
        self.assertEqual(len(set(compositions)),6,'Civilian centres reuse one programme')

    def test_more_and_taller_highrises_near_final_city(self):
        city=[p['kind'] for cx in range(188,192) for cy in range(4,8)
              for p in city_program(cx,cy)[1]]
        self.assertGreaterEqual(sum(KINDS[k][2]>=6 for k in city),len(city)//2)
        self.assertGreaterEqual(max(KINDS[k][2] for k in city),11)
        early=next(s for s in self.sites if s['id']==0)
        late=next(s for s in self.sites if s['id']==11)
        def heights(s):
            return [KINDS[p['kind']][2] for cx,cy in s['cells'] for p in settlement_program(s,cx,cy)]
        self.assertGreater(max(heights(late)),max(heights(early)))
        self.assertGreater(sum(h>=6 for h in heights(late)),sum(h>=6 for h in heights(early)))

    def test_large_retail_has_dry_full_sized_parking_and_no_roads_through_buildings(self):
        retail=[s for s in self.sites if s['kind']=='commercial']
        self.assertEqual(len(retail),4)
        self.assertEqual(len({tuple(s['cells'][0]) for s in retail}),4)
        for site in retail:
            cx,cy=site['cells'][0];g,_=raster(cx,cy,self.by[cx,cy])
            self.assertGreaterEqual(sum(w*h for x,y,w,h in site['parking']),20000)
            for p in site['structures']:
                x,y=p['x'],p['y'];w,h,*_=KINDS[p['kind']]
                self.assertFalse(((g[y:y+h,x:x+w]==1)|(g[y:y+h,x:x+w]==4)).any(),(site['name'],p))
            self.assertTrue({'bigboxmall','gunshop','diner'}<={p['kind'] for p in site['structures']})


if __name__=='__main__':unittest.main()
