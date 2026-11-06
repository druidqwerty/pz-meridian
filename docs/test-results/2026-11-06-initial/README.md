# Initial frozen-candidate native-game evidence

These images are actual PZ B42.21 + Viewpoint0.1.6.1 frames, not generated previews.
The isolated test used a god/ghost player and a vanilla diagnostic flashlight.
No player saves or installed game files were edited.

- Fresh run: `20261106-045129-812755`, native/runtime bytes bound by `candidate-bind.json`.
- Reload/engine recheck: `20261106-045701-832212`.
- Fresh report intentionally says FAIL: its sole failed assertion was the first direct-entry engine attempt.
  The focused recheck proved actual engine Running after ordinary entry-state completion.
- Both genuine descending stair flights,16first/thirdcamera checks, safe surface with preserved
  below-ground hordes, loot, ordinary walking, physical doors and native remote wilderness passed.
- No Lua stack traces in either completed run.
- Actual atlas data loaded, but the overview was visually blank; API PASS does not prove useful rendering.
- Basement first-person ceiling-edge sky leaks were visible.

These two visual issues are preserved here as BEFORE evidence. Do not describe them
as fully verified/polished compatibility until an after-fix native-game test is recorded.

## Images

- `meridian-first.png` / `meridian-third.png`: coherent facade, canopy, windows, pavement.
- `bunker-first-before-ceiling-fix.png`: zombies retained below ground; bright ceiling gaps visible.
- `medical-first-before-ceiling-fix.png`: furnished medical bay, diagnostic torch, same gap.
- `atlas-before-vector-fix.png`: blank overview despite data-loaded API state.

No driving-time benchmark or full128km drive is claimed.
