# Interiors and electrical rooms

## Changes from alpha.1

- Kitchen appliances, counters and sinks against a north wall now all face
  south into the room. Previously the stove faced east and the sink north.
- South-wall dressers, desks and shelves face north. Desk chairs look toward
  their desks; dining seats face the table. Living rooms have complete sofas,
  reading/work corners, supported TVs and lamps instead of an isolated line
  of chairs and a large empty lobby.
- Bedroom beds can be placed lengthwise or crosswise. Each bed and sofa is
  placed as a complete native sprite-grid object. A doorway exclusion rejects
  the whole object, never just one half.
- Kitchens include worktops and dining clusters where space permits; bedrooms
  have bedside storage, lamps, clothing storage and study corners. Classrooms
  use repeated desk/seat banks. Shops, storage rooms, laundry and technical
  rooms have purpose-specific furniture with open aisles.
- New layouts pass their real door/stair approach exclusions to the furniture
  helper. A central cross-aisle remains open in larger rooms. The generator
  does not place unrelated floor furniture on top of a sink or cupboard.

## Real light circuits, not decorative switch pictures

Every enclosed native RoomDef gets a `type=7` light-switch metaobject, a physical vanilla
wall switch and at least one visible powered wall fixture on a solid wall.
Large rooms receive spaced fixtures. This applies above ground and underground;
it does not depend on windows or the player's torch.
The twelve open-air wall-crown sections deliberately have no enclosed room circuit.

The map stores cell-local `(7,x,y)` object coordinates in `.lotheader`. This is
the format consumed by the game's native MetaGrid loader. Room switches control
native room lighting; movable wall lamps are normal independently switchable
bulb-bearing light objects. Electricity shutoff, generators, removable bulbs
and normal PZ switch behavior are not overridden by a custom lighting system.

Switches use the correct attached wall side. They are not put on a window or
doorframe without a supporting wall. The room-light metadata makes light
availability known even when the physical switch's chunk has not loaded yet.

## Source-of-truth checks

All sprite names and directional tables were checked against the owner's
installed PZ42.21 `newtiledefinitions.tiles.txt`; no game art is redistributed.
The curated table uses native `Facing` values rather than numeric-ID rotation.
Complete beds/sofas use the exact native `SpriteGridPos` coordinates.

Native Java bytecode confirms:

- `IsoRoom.hasLightSwitches()` checks `RoomDef.objects` for type7.
- `IsoRoom.createLights(boolean)` creates native room lights per RoomRect.
- A non-RGB `IsoLightSwitch` belongs to its square's room circuit; RGB lamp
  sprites create their own point lights using `lightR/G/B` and `LightRadius`.
- Physical switches expose `isActivated`, `setActive` and `toggle`.

`tests/test_interiors.py` verifies actual native sprite properties, complete
grid coordinates, blocked-door group placement, seat facing, real light
properties and metadata serialization. These are static/native-format gates,
not a substitute for night-time in-game ON/OFF evidence. Current live status
belongs in [QA.md](QA.md).
