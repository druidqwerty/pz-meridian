"""Release gates independent of the builder: sprites, pairs, bounds and density."""
from pathlib import Path
import json,re,sys
from map_binary import _Reader

ROOT=Path(__file__).resolve().parents[1]
GAME=Path('G:/Steam/steamapps/common/ProjectZomboid')


def main():
    m=json.loads((ROOT/'build/manifest.json').read_text())
    folder=ROOT/'mod/common/media/maps/Meridian'
    defs=(GAME/'media/newtiledefinitions.tiles.txt').read_text()
    sprites=set(re.findall(r'// (\S+)\s+tile\s*\{',defs))
    unknown=set();rooms=0;buildings=0;safe=0;densities=[]
    for c in m['cells']:
        x,y=c['cell'];h=folder/f'{x}_{y}.lotheader';p=folder/f'world_{x}_{y}.lotpack'
        assert h.is_file() and p.is_file(),(x,y,'pair absent')
        r=_Reader(h.read_bytes());assert r.take(4)==b'LOTH' and r.uint()==1
        names=[r.line() for _ in range(r.count())];unknown.update(set(names)-sprites)
        density=h.read_bytes()[-1024:]
        if 188<=x<=191 and 4<=y<=7:
            assert max(density)==0,('safe city density',x,y);safe+=1
        rooms+=c['rooms'];buildings+=c['buildings']
        densities.append([x,y,min(density),max(density)])
    assert not unknown,sorted(unknown)
    assert safe==16
    assert len(list(folder.glob('*.lotheader')))==len(m['cells'])
    assert len(list(folder.glob('*.lotpack')))==len(m['cells'])
    # Conservative actual header envelope plus per-room and building metadata.
    part0=24+8*192*192+10*rooms+23*buildings
    assert part0<9000000
    assert 127000<m['road_tiles']<130000
    report=dict(native_pairs=len(m['cells']),rooms=rooms,buildings=buildings,
        native_bytes=sum(c['bytes'] for c in m['cells']),safe_zero_density_cells=safe,
        unknown_sprites=sorted(unknown),metadata_part0_bytes=part0,
        main_route_tiles=m['road_tiles'],
        min_density=min(c[2] for c in densities),max_density=max(c[3] for c in densities))
    (ROOT/'build/static-audit.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
