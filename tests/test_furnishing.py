"""Local B42 oracle for genuine salvage props and authored window barricades."""
from pathlib import Path
import sys,unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from architecture import KINDS,build_structure,room_furniture
from furnishing import EXTRAS,PALETTES
from test_architecture import GAME,sprites,reachable


@unittest.skipUnless(GAME.exists(),'Requires owner-installed B42 metadata')
class FurnishingAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db=sprites()
        cls.loader=(GAME/'media/lua/server/Map/MapObjects/MOBarricade.lua').read_text()

    def test_native_furniture_is_complete_and_barricade_crates_are_salvageable(self):
        names=set(EXTRAS.values())|{n for values in PALETTES.values() for n in values}
        self.assertFalse(names-self.db.keys())
        for name in names:
            with self.subTest(sprite=name):
                self.assertIn('IsMoveAble',self.db[name])
                self.assertNotIn('SpriteGridPos',self.db[name], 'Incomplete multi-tile furnishing')
        for name in (EXTRAS['crate'],EXTRAS['metalcrate']):
            props=self.db[name]
            self.assertIn('CanScrap',props)
            self.assertIn('Material',props)
            self.assertIn('solidtrans',props)
        self.assertEqual(self.db[EXTRAS['crate']]['PickUpTool'],'Hammer')

    def test_plank_frames_are_vanilla_barricade_triggers_attached_to_windows(self):
        found=0
        for kind in KINDS:
            for seed in range(6):
                t,r,b={},[],[];rec=build_structure(t,r,b,24,24,kind,seed)
                for (x,y,z),names in t.items():
                    for name in names:
                        if not name.startswith('carpentry_01_'):continue
                        self.assertIn('MapObjects.OnNewWithSprite("'+name+'"',self.loader)
                        # Our authored north frames attach to same-square north
                        # windows; south frames attach to the next north edge.
                        n=int(name.rsplit('_',1)[1]);wy=y if n>=8 else y+1
                        self.assertIn('fixtures_windows_01_1',t.get((x,wy,z),[]))
                        self.assertIn([x,y,z],rec['barricades'])
                        found+=1
                # Main entrance stays unbarricaded and has a free approach.
                x,y,z=rec['entrance']
                self.assertNotIn([x,y,z],rec['barricades'])
        self.assertGreater(found,100)

    def test_role_details_and_public_halls_are_present_with_layout_variation(self):
        roles={role for _,_,_,group in KINDS.values() for role in group}|{'hall'}
        for role in sorted(roles):
            with self.subTest(role=role):
                props=list(room_furniture(role,10,10,12,10,7))
                self.assertGreaterEqual(len(props),6)
                self.assertFalse({n for _,_,n in props}-self.db.keys())
        for kind in KINDS:
            variants=[]
            for seed in (2,3,4,5):
                t,r,b={},[],[]; rec=build_structure(t,r,b,24,24,kind,seed)
                variants.append({n for ns in t.values() for n in ns})
                seen,free=reachable(t,self.db,tuple(rec['spawn'][:2]),0)
                self.assertIn(tuple(rec['spawn'][:2]),free)
                for room in (room for room in r if room['level']==0):
                    self.assertTrue(any((x,y) in seen for rx,ry,w,h in room['rects']
                        for x in range(rx,rx+w) for y in range(ry,ry+h)))
            self.assertGreater(len({tuple(sorted(v)) for v in variants}),1)


if __name__=='__main__':unittest.main()
