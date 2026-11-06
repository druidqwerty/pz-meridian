"""Deterministic activity zoning with explicit circulation and density report."""
from dataclasses import dataclass, field
from .activity_clusters import cluster
from .furnishing_audit import audit, reachable
from .palette import DEFAULT_PALETTE
from .room_program import programme, activity_order


@dataclass
class FurnishingPlan:
    role: str
    x: int
    y: int
    w: int
    h: int
    floor: set
    reserved: set
    blocked: set
    obstacles: set
    tiles: dict = field(default_factory=dict)
    clearance: set = field(default_factory=set)
    groups: list = field(default_factory=list)
    report: dict = field(default_factory=dict)

    @property
    def occupied(self):
        return set(self.tiles)

    def props(self):
        for (x, y), layers in sorted(self.tiles.items()):
            for sprite in layers:
                yield x+self.x, y+self.y, sprite

    def place(self, recipe, x, y):
        cells = {(x+a, y+b): layers for a, b, layers in recipe.parts}
        w, h = recipe.size
        # Bounding-box apron includes interaction space beyond chairs/bed ends.
        apron = {(a, b) for a in range(x-1, x+w+1)
                 for b in range(y-1, y+h+1)}-cells.keys()
        used = self.occupied
        if (not cells.keys() <= self.floor or not apron <= self.floor or
                cells.keys() & (self.reserved | self.clearance | used | self.obstacles) or
                apron & (used | self.obstacles)):
            return False
        free = self.floor-used-cells.keys()-self.obstacles
        # Atomic commit only if every remaining floor square stays connected.
        if len(reachable(free)) != len(free):
            return False
        self.tiles.update(cells)
        self.clearance.update(apron)
        self.groups.append(dict(activity=recipe.name, x=x+self.x, y=y+self.y,
                                width=w, height=h, footprint=len(cells)))
        return True


def plan_room(role, x, y, w, h, seed=0, base=None, blocked=(), obstacles=(),
              activity=(), strict=False):
    """Plan one rectangle; all supplied masks use caller/global tile coordinates.

    blocked: WALKABLE door/stair routes. obstacles: solid columns/walls/voids.
    activity: deliberate free floor, e.g. vehicle bay, sports court or stage.
    Multi-rectangle/native RoomDefs must be planned as separate rectangles with
    connecting paths explicitly blocked. No world/installation is selected here.
    """
    if not all(isinstance(v, int) for v in (x, y, w, h, seed)) or w < 3 or h < 3:
        raise ValueError('Integer coordinates, seed and room dimensions >=3 required')
    role, policy = programme(role)
    base = DEFAULT_PALETTE if base is None else base
    floor = {(a, b) for a in range(w) for b in range(h)}
    def local(points):
        result = {(a-x, b-y) for a, b in points}
        if not result <= floor:
            raise ValueError('Room masks must lie inside the supplied rectangle')
        return result
    doors, solids, active = local(blocked), local(obstacles), local(activity)
    if solids & (doors | active):
        raise ValueError('Solid obstacles cannot overlap walkable masks')
    # A continuous rim reaches doors on every side. Wide main cross for large rooms.
    reserved = {(a, b) for a, b in floor if a in (0, w-1) or b in (0, h-1)}
    aisle = 2 if w*h >= 96 else 1
    reserved |= {(a, b) for a, b in floor if
                 w//2 <= a < w//2+aisle or h//2 <= b < h//2+aisle}
    if policy.open_activity and not active:
        # Intentional centre is labelled, not counted as accidental empty floor.
        # A supplied court/bay is exact; do not silently enlarge it to the
        # default centre and leave the caller's usable side floor unfurnished.
        active |= {(a, b) for a, b in floor if
                   3 <= a < w-3 and 3 <= b < h-3}
    plan = FurnishingPlan(role, x, y, w, h, floor, reserved | doors | active,
                          doors, solids)
    service_placed = False
    if policy.service:
        recipes = [cluster(policy.service, base)]
        if policy.service == 'kitchen':
            recipes.append(cluster('kitchen_compact', base))
        # Prefer perimeter work line; cannot straddle a main aisle or a door.
        for recipe in recipes:
            if any(plan.place(recipe, a, b) for a, b in
                   sorted(floor, key=lambda p: (p[1], p[0]))):
                service_placed = True
                break
    # Include zoning-specific activities in addition to the generic programme.
    recipes = {name: cluster(name, base) for name in
               set(policy.clusters) | {'books', 'study', 'lounge', 'wardrobe'}}
    max_tiles = int(len(floor-plan.reserved-solids)*policy.density[1])
    # Fill ALL districts rather than stopping after a quota near the entrance.
    # Seed changes the purpose-correct mix, not the safety constraints.
    offsets = [(i+seed) % 4 for i in range(4)]
    anchors = ((a, b) for oy in offsets for ox in offsets
               for b in range(1+oy, h-1, 4) for a in range(1+ox, w-1, 4))
    for a, b in anchors:
        for name in activity_order(role, policy, a, b, w, h, seed):
            recipe = recipes[name]
            if len(plan.tiles)+len(recipe.parts) <= max_tiles and plan.place(recipe, a, b):
                break
    plan.report = audit(plan, policy)
    if policy.service and not service_placed:
        plan.report['warnings'].append('missing_primary_activity: room or masks cannot fit service group')
        plan.report['accepted'] = False
    if role in ('kitchen', 'bedroom', 'bathroom') and w*h > 240:
        plan.report['warnings'].append('oversized_domestic_room: partition into named subrooms')
        plan.report['accepted'] = False
    if strict and not plan.report['accepted']:
        raise ValueError('; '.join(plan.report['warnings']))
    return plan
