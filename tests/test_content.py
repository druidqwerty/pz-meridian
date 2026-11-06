"""Integrated city and physical story-content checks, without writing map files."""
from pathlib import Path
from collections import Counter
import sys,unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from architecture import build_structure
from content_catalog import city_program
from story_scenes import CONVOY
from world import make_plan
import generate
from test_architecture import GAME,sprites,reachable


@unittest.skipUnless(GAME.exists(),'Requires owner-installed B42 metadata')
class ContentAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db=sprites()
        _,cls.by,cls.sites=make_plan()
        cls.cell_sites={tuple(c):s for s in cls.sites for c in s['cells']}

    def compile_content(self,cx,cy):
        captured={}
        def capture(folder,x,y,t,r,b,d):
            captured.update(tiles=t,rooms=r,buildings=b,density=d)
            return dict(squares=len(t),bytes=0)
        with patch.object(generate,'write_cell',capture),patch.object(generate,'audit_cell'):
            result=generate.compile_cell((cx,cy,self.by[cx,cy],self.cell_sites[cx,cy],None))
        return result,captured

    def test_four_city_districts_have_different_built_programmes_and_street_access(self):
        compositions={}
        for cx,cy in ((188,4),(190,4),(188,6),(190,6)):
            result,content=self.compile_content(cx,cy)
            zone,_=city_program(cx,cy)
            records=result['records']
            self.assertGreaterEqual(len(records),12)
            self.assertEqual({r['district'] for r in records},{zone})
            composition=Counter(r['kind'] for r in records)
            compositions[zone]=tuple(sorted(composition.items()))
            seen,_=reachable(content['tiles'],self.db,(128,128),0)
            for rec in records:
                x,y,_=rec['spawn']
                self.assertIn((x%256,y%256),seen,(zone,rec['kind'],'front door cannot be reached from street'))
            self.assertTrue(all(d==0 for d in content['density']))
        self.assertEqual(len(set(compositions.values())),4)
        self.assertIn(('waterworks',1),compositions['utilities'])
        self.assertGreater(dict(compositions['residential'])['house'],dict(compositions['civic'])['house'])

    def test_existing_archive_interactions_get_physical_reachable_filing_desks(self):
        for kind in ('civic','lab','cottage','archive','museum','postoffice'):
            t,r,b={},[],[];rec=build_structure(t,r,b,24,24,kind,7)
            x,y,z=rec['archiveDesk']
            self.assertIn('location_business_office_generic_01_16',t[x,y,z])
            seen,_=reachable(t,self.db,tuple(rec['spawn'][:2]),0)
            self.assertTrue(any(p in seen for p in ((x-1,y),(x+1,y),(x,y-1),(x,y+1))),kind)
            self.assertLessEqual(abs(x-rec['spawn'][0])+abs(y-rec['spawn'][1]),8)

    def test_all_seven_convoy_stages_emit_real_unobstructive_objects(self):
        found=set()
        for site in (s for s in self.sites if s['id'] in CONVOY):
            cx,cy=site['cells'][0]
            result,content=self.compile_content(cx,cy)
            trace=result['convoy']
            self.assertIsNotNone(trace)
            self.assertGreaterEqual(len(trace['objects']),3,(site['name'],'empty convoy scene'))
            found.add(trace['stage'])
            for obj in trace['objects']:
                x,y=obj['x']%256,obj['y']%256
                self.assertIn(obj['sprite'],self.db)
                self.assertIn(obj['sprite'],content['tiles'][x,y,0])
                self.assertNotIn('solidfloor',self.db[obj['sprite']])
                for rec in result['records']:
                    a,b,w,h=rec['rect'];a%=256;b%=256
                    self.assertFalse(a<=x<=a+w and b<=y<=b+h+2,'Convoy blocks building/entrance')
        self.assertEqual(found,set(CONVOY.values()))


if __name__=='__main__':unittest.main()
