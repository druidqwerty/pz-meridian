"""Map-only expedition content briefs and cell-local compound footprints."""

CHAPTERS = (
    ('last-light', 'Last Light', 'Ласт-Лайт', 0.00, 0.08),
    ('farmland', 'Agrarian Valley', 'Аграрная долина', 0.08, 0.24),
    ('industry', 'Industrial Belt', 'Промышленный пояс', 0.24, 0.39),
    ('reservoir', 'Reservoir Country', 'Большое водохранилище', 0.39, 0.55),
    ('forest', 'Forest Plateau', 'Лесное плато', 0.55, 0.70),
    ('restricted', 'Restricted Territory', 'Закрытая территория', 0.70, 0.94),
    ('meridian', 'Meridian', 'Меридиан', 0.94, 1.01),
)


def chapter_at(fraction):
    return next(c[0] for c in CHAPTERS if c[3] <= fraction < c[4])


def layout(*kinds):
    # A southern door/apron never faces into an adjacent building. The central
    # N/S and E/W service lanes remain completely free of structure footprints.
    anchors = ((24,24),(88,24),(152,24),(216,24),
               (24,88),(152,88),(24,152),(88,152),
               (152,152),(216,152),(24,216),(152,216))
    return [dict(x=x,y=y,kind=kind) for (x,y),kind in zip(anchors,kinds)]


POIS = (
    (.43,'sluice-seven','Sluice Seven Dam','Дамба «Шлюз-7»',
     ('waterworks','warehouse','civic','workshop','waterworks','gatehouse'),
     'Native flat causeway, control offices, machinery stores and maintenance yards.'),
    (.29,'dead-letter','Dead Letter Distribution Centre','Почтовый центр «Недоставленное»',
     ('postoffice','warehouse','warehouse','terminal','postoffice','diner'),
     'Repeated sorting halls, freight storage, loading yards and staff rooms.'),
    (.75,'test-block','Instrumented Residential Block','Испытательный жилой квартал',
     ('house','house','house','house','lab','gatehouse','warehouse'),
     'Identical homes contrast with observation offices and a fenced supply yard.'),
    (.66,'still-pines','Still Pines Sanatorium','Санаторий «Тихие сосны»',
     ('sanatorium','sanatorium','clinic','laundry','lab','house','depot'),
     'Residential wards, treatment rooms, a park and an oversized service wing.'),
    (.87,'evacuation','Unopened Evacuation Terminal','Незавершённый эвакуационный терминал',
     ('terminal','terminal','gatehouse','warehouse','clinic','depot'),
     'Boarding halls, broad staging aprons and incomplete supply positions.'),
    (.57,'regional-archive','Regional Records Archive','Региональный архив',
     ('archive','archive','civic','warehouse','house'),
     'Public reading rooms, records storage and communications offices.'),
    (.62,'relay','Crown Relay Station','Ретранслятор «Корона»',
     ('relay','workshop','warehouse','house','house','gatehouse'),
     'Communications offices, equipment stores and isolated staff housing.'),
    (.34,'quarry','Breakwater Quarry Repair Base','Карьерная ремонтная база',
     ('scrapyard','workshop','workshop','warehouse','depot','civic'),
     'Open material yards, workshops and branching service lanes; no new machinery controls.'),
    (.96,'water-intake','Meridian Water Intake','Водозабор Meridian',
     ('waterworks','waterworks','workshop','warehouse','gatehouse'),
     'An outsized utility compound outside the city and a final service-road approach.'),
    (.92,'regional-museum','Museum of Regional Construction','Музей строительства региона',
     ('museum','library','civic','warehouse','visitor'),
     'Public exhibition halls face their administrative and storage back-of-house.'),
)

STOPS = (
    (.055,'motel','Red Lantern Motel','Мотель «Красный фонарь»',('motel','motel','diner')),
    (.115,'vet','Valley Veterinary Practice','Ветеринарный пункт долины',('vet','farm','house')),
    (.18,'chapel','Roadside Memorial Chapel','Придорожная часовня',('chapel','house')),
    (.245,'scrapyard','Spare Mile Salvage','Авторазборка «Запасная миля»',('scrapyard','workshop','warehouse')),
    (.315,'weighstation','Northbound Weigh Station','Весовая станция',('weighstation','depot')),
    (.38,'truckstop','Freight Rest Truck Stop','Стоянка дальнобойщиков',('diner','motel','depot','fuel')),
    (.46,'visitor','Lakeside Visitor Centre','Приозёрный туристический центр',('visitor','camp','diner')),
    (.51,'camp','Reservoir Campground','Кемпинг водохранилища',('camp','camp','visitor')),
    (.59,'rest','Forest Rest Area','Лесная площадка отдыха',('camp','visitor')),
    (.68,'depot','Plateau Road Maintenance Depot','Дорожное депо плато',('depot','workshop','warehouse')),
    (.80,'terminal','Sector Bus Interchange','Ведомственный автобусный терминал',('terminal','gatehouse','diner')),
    (.90,'checkpoint','Final Registration Camp','Последний распределительный лагерь',('gatehouse','camp','clinic','warehouse')),
)

BASES = (
    (.002,'last-light-garage','Last Light Expedition Garage','Стартовый гараж Last Light',
     ('workshop','house','warehouse'),'Tools and turning space; supplies remain separated.'),
    (.155,'farmstead','Alder Expedition Farmstead','Фермерская экспедиционная усадьба',
     ('farm','house','warehouse'),'Broad yard and domestic rooms; away from the main road.'),
    (.335,'road-depot','Industrial Road Depot','Промышленное дорожное депо',
     ('depot','workshop','house'),'Repair and storage rooms; little civilian shopping.'),
    (.485,'reservoir-house','Reservoir Staff House','Дом персонала водохранилища',
     ('house','waterworks','warehouse'),'A domestic overnight base beside utility buildings.'),
    (.635,'forest-station','Forest Expedition Station','Лесная экспедиционная станция',
     ('house','depot','camp'),'Shelter at the end of a quiet forest service road.'),
    (.825,'observation-post','Former Observation Post','Бывший наблюдательный пост',
     ('gatehouse','house','warehouse'),'Several approaches and a supply yard near the restricted zone.'),
)

# Bespoke compounds, not the baseline settlement's repeated sixteen-slot grid.
# All building footprints fit within32x28; the axial lanes remain unobstructed.
POI_ANCHORS = {
    'sluice-seven': ((24,24),(72,24),(160,24),(208,24),(24,72),(160,72)),
    'dead-letter': ((24,24),(64,24),(24,72),(160,160),(200,160),(200,208)),
    'test-block': ((24,24),(72,24),(24,72),(72,72),(176,24),(208,72),(176,176)),
    'still-pines': ((24,24),(24,72),(176,24),(208,72),(176,176),(24,176),(24,216)),
    'evacuation': ((24,24),(176,24),(208,72),(24,176),(176,176),(208,216)),
    'regional-archive': ((24,24),(72,24),(24,176),(176,176),(208,216)),
    'relay': ((24,24),(72,72),(176,24),(176,176),(208,216),(24,176)),
    'quarry': ((24,24),(176,24),(208,72),(176,176),(208,216),(24,176)),
    'water-intake': ((24,24),(176,24),(24,176),(176,176),(208,72)),
    'regional-museum': ((24,24),(72,72),(176,24),(176,176),(208,216)),
}


def compound_layout(key, kinds):
    anchors=POI_ANCHORS.get(key)
    return ([dict(x=x,y=y,kind=kind) for (x,y),kind in zip(anchors,kinds)]
            if anchors else layout(*kinds))
