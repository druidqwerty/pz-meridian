"""Town-specific American street programmes and a progressively taller skyline."""

# Ordered by expedition fraction, not interchangeable copies of one village.
TOWNS = {
 0: ('cottage','ranch','generalstore','garage','police','school','duplex','diner',
     'house','firestation','gunshop','guardhut','workshop','chapel','fuel','house'),
 1: ('farm','house','generalstore','garage','vet','depot','ranch','chapel',
     'warehouse','school','workshop','diner','police','duplex','fuel','guardhut'),
 2: ('rowhouse','duplex','workshop','warehouse','police','school','stripmall','apartment',
     'garage','firestation','shop','clinic','depot','house','diner','fuel'),
 3: ('motel','apartment','diner','visitor','school','police','stripmall','clinic',
     'waterworks','house','garage','generalstore','civic','duplex','fuel','workshop'),
 4: ('midrise','officeblock','warehouse','depot','hospital','police','stripmall','rowhouse',
     'school','firestation','workshop','garage','apartment','civic','fuel','gunshop'),
 5: ('officeblock','midrise','apartment','stripmall','school','hospital','police','depot',
     'workshop','firestation','rowhouse','garage','civic','laundry','fuel','shop'),
}


def settlement_program(site,cx,cy):
    """Return cell-local placement dicts; bespoke expedition compounds keep theirs."""
    if 'structures' in site:
        return site['structures']
    if site['kind'] == 'service':
        return [dict(x=24,y=24,kind='fuel'),dict(x=152,y=152,kind='garage'),
                dict(x=92,y=28,kind='guardhut')]
    if site['kind'] == 'town':
        kinds=TOWNS[site['id']]
    else:
        tall = site['fraction'] >= .70
        kinds = ('checkpoint','barracks','lab','warehouse','guardhut','clinic',
            'officetower' if tall else 'midrise','garage','military','workshop',
            'lab','residentialtower' if tall else 'barracks','depot','relay','gatehouse',
            'officeblock' if tall else 'civic')
    # Mixed depths and setbacks, detached accessory buildings and occasional
    # vacant lots. All footprints fit within their block and leave road shoulders.
    plots=[(x,y) for y in (24,88,152,216) for x in (24,88,152,216)]
    cell_index=site['cells'].index((cx,cy)) if (cx,cy) in site['cells'] else site['cells'].index([cx,cy])
    rotation=cell_index*3
    plans=[]
    for i,(x,y) in enumerate(plots):
        kind=kinds[(i+rotation)%len(kinds)]
        if (i+cell_index*2)%13==12: continue
        # Preserve the published starting cottage and its exact spawn region.
        if site['id']==0 and i==0: kind='cottage'
        small=kind in ('garage','guardhut','house','ranch','cottage')
        shift=(cell_index+i)%3*2 if small else 0
        plans.append(dict(x=x+shift,y=y,kind=kind))
    return plans
