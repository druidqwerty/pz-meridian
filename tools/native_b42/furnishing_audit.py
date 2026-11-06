"""Geometry-only acceptance gates, not a substitute for inspected game frames."""
from collections import deque


def reachable(floor):
    if not floor:
        return set()
    seen = {min(floor)}
    pending = deque(seen)
    while pending:
        x, y = pending.popleft()
        for p in ((x-1, y), (x+1, y), (x, y-1), (x, y+1)):
            if p in floor and p not in seen:
                seen.add(p)
                pending.append(p)
    return seen


def largest_empty_square(w, h, floor):
    """Ignore named circulation/activity masks; thin long aisles are legitimate."""
    previous = [0]*(w+1)
    best = (0, 0, 0)
    for y in range(h):
        row = [0]*(w+1)
        for x in range(w):
            if (x, y) in floor:
                row[x+1] = 1+min(previous[x], previous[x+1], row[x])
                side = row[x+1]
                if side > best[2]:
                    best = (x-side+1, y-side+1, side)
        previous = row
    return best


def audit(plan, policy):
    free = plan.floor-plan.occupied-plan.obstacles
    connected = reachable(free)
    furnishing = plan.floor-plan.reserved-plan.obstacles
    occupied = len(plan.occupied)
    density = occupied/max(1, len(furnishing))
    square = largest_empty_square(plan.w, plan.h, furnishing-plan.occupied)
    warnings = []
    if not policy.density[0] <= density <= policy.density[1]:
        warnings.append('density_out_of_range: revise zoning/partition; never add random filler')
    if square[2] > policy.empty_side:
        warnings.append('unassigned_empty_patch: add a purpose-led activity zone or partition')
    if len(connected) != len(free):
        warnings.append('disconnected_floor: obstacle mask separates free floor')
    if not plan.clearance <= connected or not plan.blocked <= connected:
        warnings.append('unreachable_approach: door/stair or furniture use space is cut off')
    return dict(accepted=not warnings, purpose=plan.role, floorSquares=len(plan.floor),
                furnishingSquares=len(furnishing), occupiedSquares=occupied,
                floorDensity=round(occupied/max(1, len(plan.floor)), 4),
                furnishingDensity=round(density, 4), targetDensity=policy.density,
                largestEmptySquare=dict(x=square[0]+plan.x, y=square[1]+plan.y,
                                        side=square[2]),
                maxEmptySide=policy.empty_side, groups=len(plan.groups),
                decorLayers=sum(len(s)-1 for s in plan.tiles.values()),
                connectedFloor=len(connected) == len(free), warnings=warnings)
