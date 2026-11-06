# Urban/interior revision — native PZ B42.21 evidence

## Frozen final candidate

- Version: `0.2.0-alpha.1`; 2,387 native cell pairs; 4,796 mod files.
- Candidate tree SHA-256:
  `bce864b2bd7c0892a2351f69bb42f6697a8a64c8db91b274e71b9de52f0e7339`.
- 1,188 surface structures, 25,423 RoomDefs, 1,234 BuildingDefs.
- The final change places lamps/switches on directly supported north/west walls.
  No product files changed during either successful run below.

## Final fresh tour — 20261106-142304-247195

Overall native result and wrapper: **PASS**. Eleven selected targets in a new,
isolated world; no mouse/keyboard input or user saves/settings were used.

- Native floors/rooms, real doors and generated loot loaded.
- Cottage kitchen, bedroom and living room rendered; complete bed and sensible
  appliance/counter facing are visible in the selected frames.
- Three authored native room switches were toggled at night, with the diagnostic
  torch off. Actual measured brightness differences: cottage **0.396078**, tower
  **0.301961**, B1 kitchen **0.301961**. The driver creates no room lights, bulbs
  or electrical power. It restores switch state, lab time and diagnostic torch.
- Four ordinary `ISWalkToTimedAction` traversals passed: tower z0→1, tower z11→12,
  fortification z7→8, and public bunker z0→-1. Teleports between test sites and
  diagnostic light-observer placement are not traversal evidence.
- Sanctuary-bound surface samples contained zero zombies; B1 remained infected.
- The native atlas opened/loaded; actual overview and street-zoom frames exist.
- The 181 sprite names in this exact compiled candidate were checked against the
  native read-only named registry: zero missing, zero invalid textureless sprites,
  seven legitimate native seasonal tree proxies. Negative control and unchanged
  registry size passed; no placeholder-creating `getSprite(name)` lookup was used.
- No Lua stack/error lines and no unknown missing-tile/texture errors were found.
  Six observed startup font/Piano fallback diagnostics are retained verbatim in
  the sanitized receipt; this is not a claim that the entire log has no warnings,
  nor that a fresh unmodded baseline was run for this revision.

Files: [raw report](final-report.txt), [sanitized receipt](final-receipt.json),
[26-frame index](final-screenshot-index.json).

## Save/reload — 20261106-142928-051777

Overall native result and wrapper: **PASS**. The previous isolated saved world
reloaded with its persisted token, exact position/floor and physical floor intact.
All 4,796 reloaded mod files match the frozen candidate SHA-256 tree. Sprite
registry gates passed again; Lua/map-resource gates remained clear. This narrow
run does not repeat the whole tour or claim long-term save compatibility.

Files: [reload report](reload-report.txt), [sanitized receipt](reload-receipt.json),
[reload frame](reload-reload.png).

## Visual acceptance and limits

The root reviewer inspected the final cottage and tower night ON/OFF pairs,
cottage bedroom, upper tower stair, parking, fortification walkway and B1 kitchen.
Lamps are visibly wall-supported; illumination changes and parking markings are
visible. The wall crown frame proves the immediate walkway, not a panoramic
skyline. The upper bunker-shaft frame has substantial cutaway/black-floor occlusion;
the after-descent frame visibly shows the player on B1 and physical stairs. It is
not complete entrance-pavilion visual coverage. The separate entrance guide is a
wayfinding diagram, not an in-game screenshot.

This final condensed tour does not re-certify Viewpoint first-person ceiling
finish, every building/entrance, all room angles, multiplayer, full-route driving
or the proposed driving-time ratio. Prior documented underground Viewpoint
terrain/ceiling bands remain an alpha limitation.

## Earlier unsuccessful evidence retained

- `interrupted-before-field-fix-*`: run 20261106-140755-162327 stopped after an
  invalid public-Java-field access from Lua. Partial records are not an overall
  PASS. The corrected probe uses exposed native methods and brightness samples.
- `pre-final-floating-lamps-*`: run 20261106-141459-061956 retains its actual FAIL.
  This older candidate had the foreground-wall lamp issue; the old texture gate
  also misclassified seven valid tree proxies. Its room/parking/tower/wall/bunker
  assertions are useful historical evidence, not proof of the final lamp bytes.

The successful fresh run above uses a newly created world and the final bytes;
the unsuccessful reports were not rewritten or relabeled as successful.

## Published artifact

[GitHub prerelease 0.2.0-alpha.1](https://github.com/druidqwerty/pz-meridian/releases/tag/0.2.0-alpha.1)
was published from source commit `22e2111`. The packaged ZIP is 111,962,694 bytes,
SHA-256 `29c386ca41b28b4420d8a45704ba2da32ea994f08b0b8f63d163ef3538e5526d`.
All 4,796 mod files match the successful fresh-game copy and installed copy;
archive CRC verification passed. See [release binding](release-binding.json).
Both release assets were downloaded anonymously and matched their local bytes:
[public retrieval receipt](public-release.json). These repository receipts were
added after publication; the already-verified ZIP was not repackaged.
