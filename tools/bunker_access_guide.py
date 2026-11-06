"""Render an original, explicitly illustrative entrance guide from the manifest."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]


def font(size, bold=False):
    file = Path('C:/Windows/Fonts') / ('arialbd.ttf' if bold else 'arial.ttf')
    return ImageFont.truetype(str(file), size)


def draw_guide():
    image = Image.new('RGB', (1400, 1000), '#f5f6f2')
    draw = ImageDraw.Draw(image)
    ink, muted, road, route = '#1b2d39', '#50616b', '#d4dadd', '#be4a17'
    draw.text((40, 28), 'MERIDIAN | Public bunker entrance', font=font(36, True), fill=ink)
    draw.text((42, 80), 'Illustrative local diagram - NOT an in-game screenshot - north is up', font=font(21), fill=muted)
    draw.rounded_rectangle((40, 132, 862, 874), radius=12, fill='white', outline='#c3cdcf', width=2)
    draw.text((62, 151), 'WEST GATE TO PUBLIC PAVILION', font=font(22, True), fill=ink)
    origin, scale = (62, 208), 3.1
    point = lambda x, y: (origin[0]+(x-48100)*scale, origin[1]+(y-1360)*scale)
    rect = lambda x, y, w, h: (*point(x, y), *point(x+w, y+h))
    draw.rectangle(rect(48100, 1360, 240, 200), fill='#eef1e8')
    for y in (1408, 1472, 1536):
        draw.rectangle(rect(48100, y-5, 240, 10), fill=road)
    draw.rectangle(rect(48251, 1360, 10, 200), fill=road)
    # The broad wall cross-section is schematic, without copying game assets.
    draw.rectangle(rect(48130, 1360, 13, 166), fill='#647179')
    draw.rectangle(rect(48130, 1547, 13, 13), fill='#647179')
    draw.rectangle(rect(48130, 1526, 13, 21), fill='#f5f6f2', outline='#647179', width=2)
    path = [(48108, 1536), (48256, 1536), (48256, 1440), (48259, 1440), (48259, 1424)]
    draw.line([point(*p) for p in path], fill=route, width=8, joint='curve')
    for a, b in ((path[0], (48188, 1536)), ((48256, 1502), (48256, 1462))):
        ax, ay = point(*a); bx, by = point(*b)
        if ax != bx:
            draw.polygon(((bx, by), (bx-13, by-8), (bx-13, by+8)), fill=route)
        else:
            draw.polygon(((bx, by), (bx-8, by+13), (bx+8, by+13)), fill=route)
    draw.rectangle(rect(48248, 1400, 24, 24), fill='#cee1dd', outline='#235c59', width=4)
    draw.line((point(48259, 1424), point(48260, 1424)), fill='#be4a17', width=11)
    for number, xy, labelxy, text in (
        (1, (48136, 1536), (95, 852), 'West gate 48130,1536'),
        (2, (48256, 1490), (575, 638), 'Turn north'),
        (3, (48259, 1424), (558, 448), 'South door'),
    ):
        xx, yy = point(*xy)
        draw.ellipse((xx-15, yy-15, xx+15, yy+15), fill=route, outline='white', width=2)
        draw.text((xx-6, yy-11), str(number), font=font(18, True), fill='white')
        draw.text(labelxy, text, font=font(18, True), fill=ink)
    draw.text((600, 290), 'Public arrival pavilion', font=font(18, True), fill=ink)
    draw.text((600, 316), '24 x 24 tiles', font=font(17), fill=muted)
    draw.line((point(48272, 1405), (595, 326)), fill='#235c59', width=2)
    draw.text((240, 231), 'INSIDE MERIDIAN', font=font(20, True), fill='#50615a')
    draw.text((67, 722), 'Outside', font=font(16), fill=muted)
    # Compass is explicit; screen directions in the isometric game differ.
    draw.line((104, 302, 104, 245), fill=ink, width=3)
    draw.polygon(((104, 236), (97, 251), (111, 251)), fill=ink)
    draw.text((95, 209), 'N', font=font(22, True), fill=ink)
    draw.text((119, 263), 'Y decreases', font=font(15), fill=muted)
    draw.text((115, 806), 'Main road: Y = 1536', font=font(18, True), fill=muted)
    draw.text((909, 146), 'WALKING DIRECTIONS', font=font(22, True), fill=ink)
    lines = ['1  Cross the west gate.', '2  Go east to X = 48256.',
             '3  Follow the avenue north.', '4  Enter the SOUTH door:',
             '    48259,1424,0', '5  Use the west stair landing:', '    48255,1408,0']
    for index, line in enumerate(lines):
        draw.text((910, 187+index*30), line, font=font(21), fill=ink)
    draw.text((909, 431), 'PAVILION DETAIL', font=font(22, True), fill=ink)
    inset = lambda x, y: (928+(x-120)*14, 492+(y-120)*14)
    draw.rectangle((*inset(120, 120), *inset(144, 144)), fill='#e1e9e3', outline='#235c59', width=4)
    localpath = [(131, 144), (131, 132), (127, 132), (127, 128)]
    draw.line([inset(*p) for p in localpath], fill=route, width=6, joint='curve')
    for x in (128, 129, 130):
        draw.rectangle((*inset(x, 128), *inset(x+1, 129)), fill='#314651', outline='white', width=1)
    xx, yy = inset(127, 128)
    draw.ellipse((xx-6, yy-6, xx+6, yy+6), fill=route)
    draw.text((938, 527), 'Stairs DOWN to B1', font=font(16, True), fill=ink)
    draw.text((939, 878), 'Open shaft: do not walk across it.', font=font(16), fill=muted)
    draw.text((940, 841), 'South door', font=font(19, True), fill=route)
    draw.text((42, 910), 'Surface: zombie-free sanctuary. Below ground: infected habitat.', font=font(23, True), fill=ink)
    draw.text((42, 949), 'Coordinates identify physical doors and stairs, not teleporters. Other entrances are listed in BUNKER-ACCESS.md.', font=font(18), fill=muted)
    path = ROOT / 'docs/BUNKER-ENTRANCE.png'
    image.save(path)
    return path


def write_access(manifest):
    safe = manifest['safeCity']
    entrances = [entry for cell in manifest['cells'] for entry in (cell.get('bunker') or {}).get('entrances', [])
                 if safe[0] <= entry['x'] < safe[2] and safe[1] <= entry['y'] < safe[3]]
    entrances.sort(key=lambda e: (e['y'], e['x']))
    lines = ['# Bunker access / Как попасть в убежище', '',
        '![Illustrative public entrance guide — not an in-game screenshot](BUNKER-ENTRANCE.png)', '',
        '## Ближайший общественный вход от западных ворот', '',
        'Схема выше — **иллюстрация, не игровой скриншот**. Север наверху; на карте',
        'игры с изометрической камерой направления экрана другие. Север = уменьшение Y.', '',
        '1. Пройди западные ворота Meridian: **48130,1536,0**.',
        '2. Иди на восток по главной улице до **48256,1536,0**.',
        '3. Поверни на север по улице X=48256 к отдельному квадратному павильону.',
        '4. Зайди через южную дверь **48259,1424,0**.',
        '5. Внутри подойди к западной верхней площадке лестницы: **48255,1408,0**.',
        '6. Спустись по настоящей лестнице. Нижний подход: **48259,1408,-1**.', '',
        'Поверхность Meridian безопасна от зомби; подземные этажи заражены.',
        'Для следующей лестницы B1→B2 верхняя площадка здесь **48255,1416,-1**,',
        'нижний подход — **48259,1416,-2**. Это обычные лестницы, не телепорты.', '',
        '## Public entrance from the west gate', '',
        'The diagram is illustrative, **not a game screenshot**. North means decreasing Y.',
        'Cross the west gate at **48130,1536,0**; follow the principal road east to',
        '**48256,1536,0**, then turn north. Enter the pavilion through its south door',
        'at **48259,1424,0**. Its west upper stair landing is **48255,1408,0**;',
        'the lower approach is **48259,1408,-1**. The deeper flight has its upper',
        'landing at **48255,1416,-1** and lower approach at **48259,1416,-2**.', '',
        '## All twelve main entrances / Все двенадцать основных входов', '',
        'Door = outside south-door square; landing = upper stair approach. All door',
        'and upper-landing coordinates below are z=0. Every bottom approach is z=-1.',
        'Дверь — южный вход снаружи; площадка — верхний подход к лестнице.', '',
        '| Entrance / Вход | South door / Южная дверь | Upper landing / Верхняя площадка | B1 bottom / Нижний подход |',
        '|---|---|---|---|']
    for e in entrances:
        cx, cy = e['x']//256, e['y']//256
        lines.append(f"| {e['name']} / {e['nameRU']} | {cx*256+131},{cy*256+144} | {e['x']},{e['y']} | {e['bottom'][0]},{e['bottom'][1]} |")
    lines += ['', 'Three separate research annexes outside Meridian are not included in this main-city',
        'table. They are independent infected complexes, not shortcuts into the final city.',
        'Три отдельные исследовательские пристройки за пределами Meridian в таблицу не',
        'включены: они не являются коротким путём внутрь финального города.', '',
        'Coordinates are read from the generated manifest and fixed native pavilion geometry.',
        'A guide is not live-game proof: current QA status remains in [QA.md](QA.md).', '']
    if len(entrances) != 12:
        raise ValueError(f'Expected twelve main entrances, found {len(entrances)}')
    path = ROOT / 'docs/BUNKER-ACCESS.md'
    path.write_text('\n'.join(lines), encoding='utf-8')
    targets = [dict(name='Entrance '+e['role']+' actual stairs',
        x=e['x'], y=e['y'], z=0, room=True, safeSurface=True,
        walkTo=dict(x=e['bottom'][0], y=e['bottom'][1], z=-1),
        walkLabel='actual_pavilion_stair', noViewpoint=True, zoom=1.25)
        for e in entrances]
    (ROOT / 'build/test-bunker-entrances.json').write_text(json.dumps(targets, indent=2), encoding='utf-8')
    return path


if __name__ == '__main__':
    manifest = json.loads((ROOT / 'build/manifest.json').read_text(encoding='utf-8'))
    print(write_access(manifest))
    print(draw_guide())
