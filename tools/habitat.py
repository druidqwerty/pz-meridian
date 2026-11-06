"""Authored Continuity wing plan; native content only, no access/quest rules."""

# Names sent to native RoomDefs must be real vanilla distribution names. The
# separate furnishing role supplies the physical scene without inventing loot.
ROOM_NAMES = {
    'shower':'bathroom', 'workshop':'storage', 'pump':'storage',
    'electrical':'storage', 'communications':'office', 'archive':'library',
    'nursery':'classroom', 'assembly':'hall',
}

# Northwest to southeast, each native cell is a recognizable functional wing.
WINGS = (
    ('triage', 'Reception hospital', 'Приёмный госпиталь',
     ('medical','hospitalroom','medicalstorage','bathroom','office','kitchen'), 16),
    ('recovery', 'Recovery and staff', 'Реабилитация и персонал',
     ('hospitalroom','medical','bedroom','shower','laundry','medicalstorage'), 18),
    ('research', 'Research campus', 'Исследовательский сектор',
     ('laboratory','office','medicalstorage','archive','kitchen','shower'), 24),
    ('isolation', 'Isolation and observation', 'Изоляция и наблюдение',
     ('medical','laboratory','hospitalroom','communications','shower','storage'), 22),
    ('reception', 'Public reception', 'Общественная приёмная',
     ('assembly','kitchen','office','library','bathroom','storage'), 48),
    ('learning', 'School and community', 'Школа и общественный центр',
     ('classroom','nursery','library','gym','assembly','bathroom'), 40),
    ('families', 'Family homes', 'Семейные квартиры',
     ('bedroom','livingroom','kitchen','nursery','laundry','shower'), 40),
    ('water', 'Water and domestic services', 'Вода и бытовые службы',
     ('pump','laundry','shower','workshop','storage','office'), 18),
    ('logistics', 'Cargo and food stores', 'Грузовой и продовольственный сектор',
     ('storage','kitchen','storage','workshop','office','bathroom'), 24),
    ('residential', 'Residents and shared kitchens', 'Жильё и общие кухни',
     ('bedroom','livingroom','kitchen','laundry','shower','library'), 48),
    ('recreation', 'Residents and recreation', 'Жильё и отдых',
     ('bedroom','gym','livingroom','assembly','kitchen','bathroom'), 40),
    ('power', 'Power distribution', 'Распределение электропитания',
     ('electrical','workshop','storage','communications','office','shower'), 20),
    ('maintenance', 'Repair and emergency crews', 'Ремонтные и аварийные службы',
     ('workshop','storage','bedroom','shower','kitchen','electrical'), 24),
    ('administration', 'Records and administration', 'Архив и управление',
     ('archive','office','assembly','library','storage','bathroom'), 22),
    ('command', 'Communications and directorate', 'Связь и руководство',
     ('communications','office','archive','bedroom','livingroom','kitchen'), 48),
    ('reserve', 'Reserve shelter and evacuation', 'Резервное жильё и эвакуация',
     ('bedroom','storage','medical','kitchen','shower','assembly'), 18),
)

ENTRANCE_ROLES = {
    (0,0):('medical','Medical reception','Приём пациентов'),
    (1,0):('staff','Hospital staff entrance','Вход персонала госпиталя'),
    (2,0):('research','Research entrance','Исследовательский вход'),
    (3,0):('isolation','Isolation emergency exit','Аварийный выход изолятора'),
    (0,1):('public','Public arrival hall','Общественный приёмный зал'),
    (3,1):('water','Water-service entrance','Вход водоснабжения'),
    (0,2):('cargo','Cargo receiving entrance','Грузовой приёмный вход'),
    (3,2):('power','Power-service entrance','Вход энергослужбы'),
    (0,3):('maintenance','Repair-crew entrance','Вход ремонтных бригад'),
    (1,3):('records','Records and administration','Архив и управление'),
    (2,3):('command','Communications entrance','Вход центра связи'),
    (3,3):('emergency','Reserve evacuation exit','Резервный эвакуационный выход'),
}


def wing_for(cx, cy, config):
    rx,ry = cx-config['minCX'],cy-config['minCY']
    main = config['maxCX']-config['minCX']==3 and config['maxCY']-config['minCY']==3
    spec = WINGS[ry*4+rx] if main else WINGS[2]
    key,en,ru,roles,tile = spec
    entrance = ENTRANCE_ROLES.get((rx,ry)) if main else (
        'research','Research annex access','Вход исследовательского комплекса')
    return dict(id=key,name=en,nameRU=ru,roles=roles,
                floor='floors_interior_tilesandwood_01_'+str(tile),
                entrance=entrance)


def role_for(wing, quadrant, row, column, level):
    # Both floors belong to the same institution; B2 is not automatically a lab.
    offset = quadrant*3+row*3+column+(2 if level==-2 else 0)
    return wing['roles'][offset % len(wing['roles'])]


def room_name(role):
    return ROOM_NAMES.get(role,role)


def wing_summary(wing):
    return {k:wing[k] for k in ('id','name','nameRU','floor')}
