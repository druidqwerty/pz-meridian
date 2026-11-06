"""Geometric acceptance for distinct uses, storefronts and a metropolitan core."""
from collections import Counter
from pathlib import Path
import sys,unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from architecture import KINDS,build_structure
from building_layouts import layout
from content_catalog import city_program
from test_architecture import GAME,sprites,reachable


class UrbanProgrammes(unittest.TestCase):
    def test_metropolis_has_a_real_highrise_majority_not_lowrise_relabels(self):
        stock=Counter()
        for cx in range(188,192):
            for cy in range(4,8):
                zone,plots=city_program(cx,cy)
                for p in plots:
                    w,h,levels,_=KINDS[p['kind']]
                    self.assertLess(p['x']+w,255)
                    self.assertLess(p['y']+h+3,255)
                    stock[levels]+=1
                    self.assertFalse(p['x']<=128<=p['x']+w)
        self.assertGreater(sum(v for k,v in stock.items() if k>=6),sum(stock.values())//2)
        _,core=city_program(190,6)
        self.assertGreater(sum(KINDS[p['kind']][2]>=6 for p in core),12)

    def test_ranch_has_a_real_outdoor_court_and_compact_home_has_no_giant_lobby(self):
        w,h,levels,roles=KINDS['ranch']
        rooms,_,owners=layout(w,h,roles,'ranch',levels=levels)
        self.assertNotIn((w-2,2),owners)
        self.assertIn((2,2),owners)
        w,h,levels,roles=KINDS['cottage']
        rooms,_,owners=layout(w,h,roles,'cottage',levels=levels)
        self.assertLess(sum(a*b for _,_,a,b in rooms[0]['rects']),w*h//3)


@unittest.skipUnless(GAME.exists(),'Requires owner-installed B42 sprite properties')
class UrbanNativeAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.db=sprites()

    def build(self,kind):
        t,r,b={},[],[]
        rec=build_structure(t,r,b,24,24,kind,7)
        return t,r,rec

    def test_garage_is_a_complete_three_part_native_vehicle_door(self):
        t,r,rec=self.build('garage')
        for dx,index in ((3,3),(4,4),(5,5)):
            name='walls_garage_01_'+str(index)
            self.assertIn(name,t[24+dx,24,0])
            self.assertEqual(self.db[name]['GarageDoor'],str(dx-2))
            self.assertIn('doorN',self.db[name])
        for dx in range(2,7):
            for dy in range(1,5):
                props=[self.db[n] for n in t[24+dx,24+dy,0]]
                self.assertFalse(any('IsMoveAble' in p and any(k in p for k in
                    ('solid','solidtrans')) for p in props))

    def test_stripmall_units_have_individual_public_storefront_doors(self):
        t,r,rec=self.build('stripmall')
        stores=[rr for rr in r if rr['name']=='grocery']
        self.assertEqual(len(stores),3)
        for store in stores:
            x,y,w,h=store['rects'][0]
            self.assertIn('fixtures_doors_01_0',t[x,y+h//2,0])
            self.assertIn('solidfloor',self.db[t[x-1,y+h//2,0][0]])

    def test_mall_contains_reachable_shops_food_and_service_rooms_on_both_storeys(self):
        t,r,rec=self.build('bigboxmall')
        self.assertEqual(rec['rect'][2:],[96,72])
        self.assertEqual(rec['levels'],2)
        for z in range(2):
            origin=tuple(rec['spawn'][:2]) if z==0 else (25,93)
            seen,_=reachable(t,self.db,origin,z)
            self.assertGreaterEqual(len([rr for rr in r if rr['level']==z]),10)
            for rr in (rr for rr in r if rr['level']==z):
                self.assertTrue(any((x,y) in seen for a,b,w,h in rr['rects']
                                    for x in range(a,a+w) for y in range(b,b+h)))
                self.assertEqual(sum(o[0]==7 for o in rr['objects']),1)
            names={n for (x,y,zz),ns in t.items() if zz==z for n in ns}
            self.assertTrue(all('location_shop_mall_signs_02_'+str(i) in names for i in range(20,24)))
        self.assertTrue({'departmentstore','sportstore','kitchen','office','storage','bathroom'}<=
                        {rr['name'] for rr in r})

    def test_gunshop_retains_native_gun_distributions_and_security_storage(self):
        t,r,rec=self.build('gunshop')
        self.assertTrue({'gunstore','gunstorestorage'}<={rr['name'] for rr in r})
        self.assertIn('location_shop_generic_01_110',{n for ns in t.values() for n in ns})


if __name__=='__main__':unittest.main()
