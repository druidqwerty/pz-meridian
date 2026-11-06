"""Publish authored coordinates and an honest map-content inventory."""
from collections import Counter
import json
from expedition_sites import CHAPTERS


def write_guide(root, manifest):
    cells=manifest['cells']; sites=manifest['settlements']
    records=[r for c in cells for r in c['records']]
    entries=[]
    for site in sites:
        if site['kind']!='expedition':continue
        actual=[r for r in records if r['site']==site['name']]
        assert len(actual)==len(site['structures']),('Missing compound structures',site['name'])
        entries.append(dict(id=site['archetype'],name=site['name'],nameRU=site['nameRU'],
            category=site['category'],chapter=site['chapter'],x=site['x'],y=site['y'],
            buildings=len(actual),kinds=[r['kind'] for r in actual],secondExit=bool(site.get('secondExit'))))
    home=min((r for r in records if r.get('district')=='residential' and r['kind']=='house'),
             key=lambda r:r['rect'][:2])
    entries.append(dict(id='meridian-home',name='Meridian Expedition Home',
        nameRU='Экспедиционный дом Meridian',category='base',chapter='meridian',
        x=home['spawn'][0],y=home['spawn'][1],buildings=1,kinds=['house']))
    wings=[dict(cell=c['cell'],**c['bunker']['wing']) for c in cells
        if c.get('bunker') and 188<=c['cell'][0]<=191 and 4<=c['cell'][1]<=7]
    entrances=[e for c in cells if c.get('bunker') for e in c['bunker']['entrances']]
    main_entrances=[e for e in entrances if 48128<=e['x']<49152 and 1024<=e['y']<2048]
    assert len(wings)==16 and len(main_entrances)==12
    report=dict(chapters=[dict(id=c[0],name=c[1],nameRU=c[2]) for c in CHAPTERS],
        compounds=entries,counts=dict(Counter(e['category'] for e in entries)),
        cityDistricts=dict(Counter(r['district'] for r in records if r.get('district'))),
        habitatWings=wings,entrances=main_entrances,
        convoyStages=sorted({c['convoy']['stage'] for c in cells if c.get('convoy')}),
        buildingKinds=dict(Counter(r['kind'] for r in records)))
    assert report['counts']==dict(landmark=10,stop=12,base=7)
    (root/'build/content-summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    lines=['# Expedition places / Места экспедиции','',
        'Optional coordinate spoilers. All additions are native map content, not quests.',
        'Необязательные координаты. Это места на карте, не задания. Новая игра обязательна.','',
        '| Place / место | Chapter | X | Y | Buildings |',
        '|---|---|---:|---:|---:|']
    for e in entries:
        lines.append(f"| {e['name']} / {e['nameRU']} | {e['chapter']} | {e['x']} | {e['y']} | {e['buildings']} |")
    lines+=['','Six regional bypasses rejoin the principal road locally; service roads',
        'lead to these compounds. This is not a claim of a second128km highway.',
        'The seven chapters are architectural/district themes, not terrain-height simulation.',
        'Native causeways are flat. No working dam, radio, access card or power system was added.',
        'The convoy story uses existing thirteen archives and physical supply traces;',
        'it does not add scripted vehicle events or NPCs.','',
        'See [habitat plan](HABITAT.md), [archive guide](ARCHIVES.md) and [QA](QA.md).','',
        'Copyright © 2026 druidqwerty. Original Meridian content: MIT.']
    (root/'docs/EXPEDITION-LOCATIONS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    # Existing archive keys/reader remain unchanged; regenerate only coordinates.
    text=(root/'mod/42/media/lua/shared/Meridian/00_Config.lua').read_text()
    import re
    coords=re.findall(r'id="site(\d+)",x=(\d+),y=(\d+),z=(-?\d+)',text)
    archive=['# Archive location guide / Архивы','',
        'Right-click within eight tiles. Look for the filing cabinet/document desk',
        'in the lobby. These thirteen existing archives also carry the Convoy17 story.',
        'Правая кнопка в пределах восьми клеток; ищите документы и картотеку в приёмной.',
        'В семи существующих записях прослеживается судьба колонны17.','',
        '| District / район | X | Y | Floor |','|---|---:|---:|---:|']
    for i,x,y,z in coords:
        s=next(s for s in sites if s['id']==int(i))
        archive.append(f"| {s['name']} | {x} | {y} | {z} |")
    assert len(coords)==13
    archive+=['','No new quest or radio system; records are optional exploration.',
        'Copyright © 2026 druidqwerty. MIT.']
    (root/'docs/ARCHIVES.md').write_text('\n'.join(archive)+'\n',encoding='utf-8')
