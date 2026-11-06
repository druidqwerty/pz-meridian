"""Choose representative live-game targets from the freshly compiled manifest."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    manifest=json.loads((ROOT/'build/manifest.json').read_text(encoding='utf-8'))
    objects=[o for c in manifest['cells'] for o in c.get('roadside',{}).get('objects',[])]
    road=next(o for o in sorted(objects,key=lambda o:abs(o['y']-48640)+abs(o['x']-512))
              if o['kind']=='roadblock' and o['y']<48640)
    # The normal roadblock row extends across the road; stand alongside it.
    road_target=dict(name='Roadwork salvage',x=road['x']+(road['sprite'].endswith('_8')),
                     y=road['y']+(road['sprite'].endswith('_9')),z=0,
                     salvage={k:road[k] for k in ('x','y','z','sprite')},yaw=3.14159265)
    bunker=next(c['bunker'] for c in manifest['cells'] if c['cell']==[188,4])
    crate=next(o for o in bunker['obstacles']
               if o['x']==48200 and o['y']==1151 and o['z']==-2)
    targets=[
        dict(name='Furnished cottage',x=539,y=48670,z=0,room=True,yaw=-1.57079632679),
        dict(name='Cottage real plank barricade',x=538,y=48665,z=0,
             unbarricade=dict(x=538,y=48664,z=0,sprite='fixtures_windows_01_1'),noViewpoint=True),
        road_target,
        dict(name='Departure SUV',x=640,y=48644,z=0,vehicle=True,noViewpoint=True),
        dict(name='Meridian surface',x=48228,y=1124,z=0,safeSurface=True,noViewpoint=True),
        dict(name='Surface bunker stairs',x=48255,y=1152,z=0,room=True,safeSurface=True,
             walkTo=dict(x=48259,y=1152,z=-1)),
        dict(name='Deep bunker stairs',x=48255,y=1160,z=-1,room=True,infected=True,
             walkTo=dict(x=48259,y=1160,z=-2),noViewpoint=True),
        dict(name='Steel gallery door',x=48177,y=1152,z=-1,room=True,
             metalDoor=dict(x=48176,y=1152,z=-1,sprite='fixtures_doors_01_68'),yaw=3.14159265),
        dict(name='Tunnel salvage',x=48200,y=1152,z=-2,room=True,infected=True,
             salvage={k:crate[k] for k in ('x','y','z','sprite')},yaw=-1.57079632679),
        dict(name='Continuity medical habitation',x=48350,y=1116,z=-1,room=True,
             infected=True,yaw=-0.7853981634),
    ]
    target=ROOT/'build/test-added-content.json'
    target.write_text(json.dumps(targets,indent=2),encoding='utf-8')
    print(target)
    print(f'{len(targets)} targets; {len(objects)} authored roadside objects available')


if __name__=='__main__':main()
