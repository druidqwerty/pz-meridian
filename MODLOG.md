# Meridian: The Long Way Home — development journal

## Goal and authorization
Original fictional PZ42.21 standalone SW→NE expedition map. Owner asks for the
map-content portions of the attached development brief; NO new gameplay systems.
GitHub only (source+ZIP prerelease). NO Steam/Boosty. Retired Real Russia stays
retired; no restoration, game-art redistribution or user-save migration.

## Current frozen candidate — 2026-11-06
- Version0.1.0-alpha.1; ID MeridianLongWayHome, map Meridian. New Sandbox world.
- DONE2381native cellpairs,832surface structures,866BuildingDefs,6270RoomDefs;
  660745098native bytes. Full tile-order decode/roundtrip on every compiled cell.
- DONE27regression tests PASS; static-audit PASS, unknownsprites0; safe city
  density0 in16cells; metadataPart0 estimate2090650bytes (<9MB safetygate).
- DONE unchanged128256tile principalroad,6regionaldetours,28service spurs,
  25second exits,7chapter themes,10landmarks,12stoptypes,7potentialbases.
- DONE4citydistrict programmes,16habitatwings,12mainentrance roles and3annexes;
  service rings+column aisles+second room doors keep real alternate routes.
- DONE59roadencounters/796roadprops/3474buildingbarrier squares/494tunnelprops;
  144523furniture/decor spriteinstances (includes paired furniture parts),
  202supply lockers and13EN/RUarchives. Seven convoy stages use existing reader
  plus physical abandoned belongings; no scripted vehicles/NPCs/questjournal.
- DONE final generation69.4seconds; manifest and content-summary.json in build/.
- DONE installed4784files, every SHA256matches. Previous install backed up at
  build/install-backups/20261106-052821. User saves/options/profile untouched.
- DONE final run053010-285473: six changed sites,12camera assertions,both actual
  stairs,16tile service-ring walk,nonblank atlas and save. Overall FAIL retained
  for two boundary-radius assertions counting infected outside the city.
- DONE narrow reload053547-819680: overall PASS,Lua-error-clean,persisted token/
  position/floor,zero in-city surface zombies at both same boundary sites;
  outside116/110 and below726/660 zombies retained. Real20tile detour walk passed.
  All4784boundfiles unchanged. Sanitized reports/screenshots exported to
  docs/test-results/2026-11-06-expansion; parent visually inspected final school,
  laundry,street atlas and detour frames. Ceiling-edge seams remain an alpha limit.
- DONE independent read-only release review: claims/evidence/notices consistent;
  no private paths/secrets in release text. README journal link made absolute so
  it also resolves in the ZIP without bundling a stale working journal.
- DONE publish lint:4784product files,0failures; its sole missing-README warning
  is resolved in the complete ZIP, which includes bilingual install instructions.
- DONE packaged once:4851entries,31094347bytes; CRC,relative Markdown links and
  all4784product bytes match the tested tree. ZIP SHA256:
  5982eb199d5c4e11ce21dc12c9286c681ddead12b574aa0179c5580fa4074c5e.
  Receipt:build/release-verification.json; dist/SHA256SUMS.txt ready.
- DONE source9154af7 pushed; GitHub prerelease0.1.0-alpha.1 published with ZIP and
  SHA256SUMS: https://github.com/druidqwerty/pz-meridian/releases/tag/0.1.0-alpha.1.
  Public anonymous downloads of BOTH assets match local bytes and SHA256; tag
  resolves to9154af768f3ff7827c5a4edb136cb20e266d8b4a. Release notes match exactly.
  Public verification:docs/test-results/2026-11-06-expansion/public-release.json
  (post-publication receipt,not part of the already frozen ZIP). Anonymous API
  quota was exhausted,so metadata used gh auth; actual downloads used NO auth.
- COMPLETE authorized scope. No Steam/Boosty publication,no user-save changes.
  User testing requires NEW Sandbox world on Meridian. Full-route driving,time
  ratio,multiplayer and flawless Viewpoint ceilings remain explicitly unverified.

## Files and completed owners
- world.py/expedition.py/expedition_sites.py/expedition_decor.py:static geography,
  compounds and scenery. expedition_guide.py writes real coordinate inventory;
  overview.py draws original route-plan figure. docs/EXPEDITION*.md.
- architecture.py/content_catalog.py/themed_rooms.py/furnishing.py:vanilla-only
  differentiated buildings and domestic/technical furniture. story_scenes.py:
  real filing cabinets and nonblocking convoy motifs. docs/ARCHITECTURE.md.
- bunker.py/habitat.py:16functional wings,12role-specific pavilions,6verifiedfloor
  palettes,steeldoors,unchangedrealstairs,ringroutes. docs/HABITAT.md.
- Shipped existing Lua:surface-only sanctuary,first-visit infectedbasement/cache
  fill,one starterSUV,optional archive reader. No new gameplay Lua in this pass.
  MapPreview/VectorAtlas fixes are scoped rendering/compatibility corrections.
- playtest.py/gameplay_probe.py/content_targets.py:private diagnosticdriver only;
  never packaged as product. QA owns docs/QA.md and test-results evidence.
- install.py:a dedicated resolved Meridian folder backup+SHA256copy only.
- package.py:mod+docs+notices, excludes testdrivers/Java/gamefiles; ZIPcrcgate.

## Verified history, not tasks to repeat
- Initial candidate37c19ce already pushed. Original nativeQA043948 baselinePASS;
  045129stairs/cameras/loot/surface0+infectedbelow PASS, directcarentry oracleFAIL;
  045701reload+ordinary entry completion+engine Running PASS, no productcarfix.
- Furniture/obstacles candidate2299cells wasbuilt/installedbefore this new brief;
  do not call that old candidate the current map. All18oldregressionspassed.
-051328external interruption left stale running status/no report. Its genuine
  crowbar unbarricade2→1 passed. Wrong-side051035oraclefailure retained.
-051844missing-onlyrun:roadreal scrap,steeldoor,bothstairs,surface/belowPASS;
  tunnel scrap rejected occupiedcontainer (normalnative rule, not productbug).
-052458reload+normal inventorytransfer followed by actual tunnel scrapPASS;
  no instantaction/directobjectdelete/movablescheat/skillchange. Luaerrorclean.
- Screenshotreadback was stale while gameHWND minimized; display restored without
  input/focus. Atlas screenshots require held phases before zoomchange/close.
- Atlas vectors now render. Viewpoint ceiling coverage improved but overlying
  grass-texture bands remain in some underground views: explicitalphalimit,
  not a claim of flawlessfirstpersonceilings. Latest QA ledger owns finalproof.

## Gotchas and limits
- B42native256tilecells/8tilechunks; sparse wilderness extends beyond49152square.
- Sanctuary z>=0ONLY; negativefloorzombies must remain infected.
- Nativeflat dam/causeway/quarry scenery is not elevated terrain or workingpower.
- No full-route driving,5×drivingtime,multiplayer or complete visual polish claim.
- Allnew buildingroom names verified against native lootdistributions. Mechanical
  workshopprops are groundobjects, not tabletopgrinders; archiveplaques not floated.
- New geometry requires NEW world; never load into user's old saves for tests.
