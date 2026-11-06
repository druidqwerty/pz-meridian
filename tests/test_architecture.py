"""Independent native-engine metadata, traversability, and codec acceptance."""
from collections import deque
from pathlib import Path
import re,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from architecture import KINDS,TILES,build_structure
from bunker import build_bunker
from map_binary import write_cell,read_cell,_room_index
GAME=Path('G:/Steam/steamapps/common/ProjectZomboid')

def sprites():
    data={}
    for file in (GAME/'media').glob('*.tiles.txt'):
        name=None
        for raw in file.read_text(encoding='utf-8-sig').splitlines():
            line=raw.strip()
            if line.startswith('// '):
                candidate=line[3:]; name=candidate if re.fullmatch(r'[\w-]+_\d+',candidate) else None
                if name: data.setdefault(name,{})
            elif name and '=' in line:
                k,v=line.split('=',1); data[name][k.strip()]=v.strip()
    return data

def combine(db,names):
    out={}
    for name in names: out.update(db[name])
    return out

def reachable(tiles,db,origin,z):
    props={(x,y):combine(db,names) for (x,y,zz),names in tiles.items() if zz==z}
    free={p for p,v in props.items() if 'solidfloor' in v and not any(k in v for k in ('solid','solidtrans'))
          and not any(k.startswith('stairs') for k in v)}
    # Furniture with moveability but no collision flags may still block movement.
    for (x,y,zz),names in tiles.items():
        if zz==z and any('IsMoveAble' in db[n] and 'solidfloor' not in db[n] and
                        not any(k in db[n] for k in ('windowN','windowW','doorN','doorW')) for n in names):
            free.discard((x,y))
    seen={origin}; pending=deque([origin])
    while pending:
        x,y=pending.popleft()
        for dx,dy,d in [(1,0,'W'),(-1,0,'W'),(0,1,'N'),(0,-1,'N')]:
            nxt=x+dx,y+dy
            if nxt not in free or nxt in seen: continue
            edge=props.get((max(x,nxt[0]),max(y,nxt[1])),{})
            if any(k+d in edge for k in ('Wall','Window','DoorWall')) and 'door'+d not in edge: continue
            seen.add(nxt); pending.append(nxt)
    return seen,free

def stairs(tiles,db):
    count=0
    for (x,y,z),names in tiles.items():
        if 'stairsTW' not in combine(db,names): continue
        count+=1
        for distance,kind in enumerate(('T','M','B')):
            assert 'stairs'+kind+'W' in combine(db,tiles[x+distance,y,z])
            assert 'solidfloor' not in combine(db,tiles.get((x+distance,y,z+1),[]))
        assert 'solidfloor' in combine(db,tiles[x-1,y,z+1])
    return count

@unittest.skipUnless(GAME.exists(),'Requires local B42 metadata, never redistributed')
class NativeArchitecture(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.db=sprites()

    def test_surface_rooms_furniture_and_stairs_accessible(self):
        text=(GAME/'media/lua/server/Items/Distributions.lua').read_text(encoding='utf-8')
        for kind in KINDS:
            for seed in (0,1,7):
                with self.subTest(kind=kind,seed=seed):
                    t,r,b={},[],[]; rec=build_structure(t,r,b,24,24,kind,seed)
                    self.assertEqual(set(s for v in t.values() for s in v)-self.db.keys(),set())
                    self.assertEqual(stairs(t,self.db),rec['levels']-1)
                    _room_index(r)
                    for z in range(rec['levels']):
                        origin=tuple(rec['spawn'][:2]) if z==0 else (25,24+rec['rect'][3]-3)
                        seen,free=reachable(t,self.db,origin,z)
                        self.assertIn(origin,free)
                        for room in (rr for rr in r if rr['level']==z):
                            self.assertRegex(text,rf'(?m)^\s*{room["name"]}\s*=\s*\{{')
                            self.assertTrue(any((x,y) in seen for rx,ry,w,h in room['rects']
                                for x in range(rx,rx+w) for y in range(ry,ry+h)),room)
                        if z<rec['levels']-1: self.assertIn((29,24+rec['rect'][3]-3),seen)
                    for x,y,z in rec['caches']: self.assertIn(TILES['metal'],t[x,y,z])

    def test_bunker_rooms_and_seam_corridors_are_connected(self):
        config=dict(minCX=188,maxCX=191,minCY=4,maxCY=7)
        for cx,cy in ((188,4),(189,5),(191,7)):
            with self.subTest(cell=(cx,cy)):
                t,r,b={},[],[]; rec=build_bunker(t,r,b,cx,cy,config)
                self.assertEqual(set(s for v in t.values() for s in v)-self.db.keys(),set())
                self.assertEqual(stairs(t,self.db),rec['stairs'])
                _room_index(r)
                for z in (-2,-1):
                    seen,free=reachable(t,self.db,(127,128),z)
                    for room in (rr for rr in r if rr['level']==z):
                        self.assertTrue(any((x,y) in seen for rx,ry,w,h in room['rects']
                            for x in range(rx,rx+w) for y in range(ry,ry+h)),room)
                    for x,y in ((128,1),(128,254),(1,128),(254,128)):
                        self.assertIn((x,y),seen,'Cell seam inaccessible')
                    self.assertIn((131,136),seen,'Lower stair bottom blocked')
                if rec['entrances']:
                    self.assertIn((131,128),reachable(t,self.db,(127,128),-1)[0])
                    self.assertTrue(any(rr['level']==-1 and any(x<=128<x+w and y<=128<y+h
                        for x,y,w,h in rr['rects']) for rr in r))
                    self.assertNotIn((128,128,0),t)
                for cache in rec['caches']:
                    self.assertIn(TILES['metal'],t[cache['x']%256,cache['y']%256,cache['z']])

    def test_native_roundtrip_preserves_negative_floor_rooms(self):
        t,r,b={},[],[]
        build_bunker(t,r,b,188,4,dict(minCX=188,maxCX=191,minCY=4,maxCY=7))
        with tempfile.TemporaryDirectory() as out:
            write_cell(out,188,4,t,r,b,0)
            got=read_cell(out,188,4)
            self.assertEqual(got['tiles'],t)
            self.assertEqual(len(got['rooms']),len(r))
            self.assertEqual(got['min_level'],-2)

if __name__=='__main__': unittest.main()
