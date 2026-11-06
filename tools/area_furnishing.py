"""Bind purpose-led room plans to actual Meridian geometry and audit records.

Plans are cached in room-local coordinates as immutable props/serialized reports;
callers receive independent reports. No planner object is shared between rooms.
"""
from copy import deepcopy
from functools import lru_cache
import json

from native_b42 import plan_room, DEFAULT_PALETTE
from native_b42.room_program import programme as resolve_programme


def inside(points, x, y, w, h):
    return tuple(sorted({(a-x, b-y) for a, b in points
                         if x <= a < x+w and y <= b < y+h}))


@lru_cache(maxsize=768)
def _zoned(role, w, h, phase, blocked, activity, obstacles, palette):
    """Try distinct legitimate activity layouts, not density-only filler."""
    attempts = []
    for offset in range(4):
        candidate = (phase+offset) % 4
        plan = plan_room(role, 0, 0, w, h, candidate, dict(palette),
                         blocked=blocked, activity=activity, obstacles=obstacles)
        attempts.append(dict(seed=candidate, accepted=plan.report['accepted'],
                             warnings=list(plan.report['warnings'])))
        if plan.report['accepted']:
            report = deepcopy(plan.report)
            report['groups'] = deepcopy(plan.groups)
            report['attempts'] = attempts
            report['seed'] = candidate
            return tuple(plan.props()), json.dumps(report)
    raise ValueError(f'Unaccepted {role} room {w}x{h}, masks={blocked}: {attempts}')


def plan_furnishing(role, x, y, w, h, seed=0, base=None, blocked=(), *,
                    programme=None, activity=(), obstacles=(), force=False):
    """Return actual props plus acceptance evidence, without changing loot names.

    Main mall corridors are intentional circulation, not empty functional rooms.
    Compact domestic rooms retain fitted recipes when a wide-cross zoning grid
    would leave activity bays smaller than a complete lounge group.
    """
    purpose, _ = resolve_programme(programme or role)
    report = dict(rect=[x, y, w, h], requestedRole=role, purpose=purpose,
                  seed=seed, accepted=None, warnings=[])
    if role == 'hall' and min(w, h) < 8:
        report.update(policy='circulation', reason='Dedicated connecting corridor',
                      densityAudited=False)
        return (), report
    compact_lounge = purpose == 'livingroom' and w <= 10 and h <= 10
    if not force and (w*h < 96 or min(w, h) < 6 or compact_lounge):
        from interior_layouts import furnish_room
        names = DEFAULT_PALETTE if base is None else base
        # Legacy fitted groups still place atomically. Reserve the complete
        # solid's apron too, so a cabinet added by the caller neither overlaps
        # a bed nor steals the neighbouring furniture's interaction space.
        solids = {(x+a, y+b) for a, b in inside(obstacles, x, y, w, h)}
        routes = {(x+a, y+b) for a, b in inside(blocked, x, y, w, h)}
        active = {(x+a, y+b) for a, b in inside(activity, x, y, w, h)}
        if solids & (routes | active):
            raise ValueError('Solid obstacles cannot overlap walkable masks')
        reserve = routes | active | {(a+dx, b+dy) for a, b in solids
                    for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
        props = tuple(furnish_room(role, x, y, w, h, seed, names, reserve))
        report.update(policy='compact', reason='Fitted small-room recipe',
                      densityAudited=False,
                      floorSquares=w*h,
                      occupiedSquares=len({(a, b) for a, b, _ in props}))
        return props, report
    palette = tuple(sorted((DEFAULT_PALETTE | (base or {})).items()))
    props, encoded = _zoned(purpose, w, h, seed % 4,
                           inside(blocked, x, y, w, h),
                           inside(activity, x, y, w, h),
                           inside(obstacles, x, y, w, h), palette)
    report.update(json.loads(encoded), policy='zoned', densityAudited=True)
    for group in report['groups']:
        group['x'] += x
        group['y'] += y
    report['largestEmptySquare']['x'] += x
    report['largestEmptySquare']['y'] += y
    return tuple((a+x, b+y, sprite) for a, b, sprite in props), report


def world_reports(reports, cx, cy):
    """Shift cell-local report geometry exactly once before manifest export."""
    for report in reports:
        report['rect'][0] += cx*256
        report['rect'][1] += cy*256
        for group in report.get('groups', ()):
            group['x'] += cx*256
            group['y'] += cy*256
        if 'largestEmptySquare' in report:
            report['largestEmptySquare']['x'] += cx*256
            report['largestEmptySquare']['y'] += cy*256
