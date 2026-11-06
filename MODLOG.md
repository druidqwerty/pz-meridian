# Meridian: The Long Way Home — development journal

## Goal and authorization
Original fictional PZ42.21 standalone SW→NE expedition map. Owner asks for the
map-content portions of the attached development brief; NO new gameplay systems.
GitHub only (source+ZIP prerelease). NO Steam/Boosty. Retired Real Russia stays
retired; no restoration, game-art redistribution or user-save migration.

## Current frozen candidate — 2026-11-06
Superseded by active urban/interior revision below; these are alpha.1 receipts.
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

## Active owner review — urban/interior revision 2026-11-06
- Goal: correct furniture facing/density; genuine native room switches/lights;
  replace identical town templates with American small-town/service/civic/military
  building families; progressive skyline ending in dense highrise Meridian;
  replace paper-thin wall with tall wide walkable fortification.
- Preserve original seven expedition chapters/landmarks/road networks and existing
  map-only scope, user saves and GitHub-only publication restriction.
- Root: regional programmes, generator integration, wall geometry, build/install/QA.
- urban_buildings: distinct footprints/room layouts/towers/city programmes.
- furniture_light: verified sprite orientation, useful furnishings, native type7
  light-switch room metadata; tests and evidence notes.
- references_plan: realizable online US references, plan recovery, QA target builder.
- Next: integrate APIs, validate native rooms/stairs/lighting and street access,
  compile then test representative interiors/night switch/towers/wall in isolation.
- Existing alpha.1 publication is historical, NOT evidence for this new revision.
- DONE root integration: regional_program.py gives six different civilian town
  compositions, military build-up and mixed sizes/setbacks; world.py adds rear
  service lanes. generate.py uses it instead of repeated eight-building list.
- DONE root fortification.py: 13-tile deep, 8-storey wall with roof walkway,
  four-storey high/21-tile wide west gate and north-gate bastion stair access.
  Native geometry/tests/live proof still pending; do not call verified yet.
- Steering incorporated: continuous sidewalks; 4dedicated96x72 shopping centres,
  >20,000square-tile parking lots/plazas, local gunshops, native building/road signs.
  New urban_destinations.py keeps large retail out of ordinary64tile house lots.
- Owner cannot find bunker: nearest public entrance door48259,1424/stairs48255,1408
  (westgate east125then north112). Added diagram+wayfinding task; entry positions
  remain unchanged. Reusable native interior/publicrealm recipes will be retained
  in pz-map-tools after validation, never game art or retired map data.
- Root fortification tests3/3PASS. Intermediate global run30tests had1stale
  barricadecount failure while architecture writer was active; rerun after freeze.
- DONE final geometry build74.2s:2387cellpairs,1188surface structures,1234BuildingDefs,
  25423RoomDefs,704173338nativebytes; every cell decoded/roundtripped. Corrected
  new thickwall collision by pulling south/east edge plots216→200 behind wall241.
- DONE static-audit PASS:0unknown propertynames,2,290,644metadataPart0 bytes;
  248Meridian buildings,140six+storeys,max13;4largeTcs,13gunshops.
  Roomlightcircuits25411 (12open-air crowns deliberately unlit),24505surface switches.
- DONE streets summary: no unconnected approaches; four actual concrete lots
  21449/22360/22432/22432squares;1209building signparts/1436roadside signs.
- DONE installed4796files SHA256verified; priorinstall backup140728. Saves/options
  untouched. Owner runninggame PID53024 left alone; existingworld will not migrate.
- DONE46tests fullsuite PASS +all12pavilion wayfinding parameterizedPASS +actual
  southeastcorner compiledroom/street/wall integrationPASS. Sharedtools9testsPASS.
- NativeQA ACTIVE immutable4796file copy140755-162327,25targets. Foundtwo missing
  runtime sprites vegetation_groundcover_01_18/21 despite sidecarpropertyexistence;
  evidence retained, sourcefix and finalrebind pending. Add actualruntime registry
  gate using IsoSpriteManager.getNamedMap (getSprite creates placeholders!).
- Owner requested Telegram completion message. conversations_list empty, but enabled
  Telegram CLI channel exists; linked historical Ivan recipient resolved. Send only
  after completion, record actual delivery receipt; do not merely promise sent.
- Final VISUAL fix: directly backedN/W lamps/switches only. E/S backattachments
  are native-valid but looked floating when foregroundwall cut away in actualPNG.
  Full rebuild75.4s+auditPASS,installed4796SHAfiles backup142056; native geometry
  counts unchanged. Interiors3PASS; final allkind/3seed architecture rerun receipt
  build/urban-final-architecture.txt. No further productmod edits planned.
- PRE-FINALQA141459 contains genuine room/parking/tower/wall/bunker/ONOFF proofs
  but is NOT final: used previouslampplacement and overstrict texturegate counted
  native seasonal treeproxies. Preserve rawFAIL. Correctgate tree type+size1..8
  independentlybytecodeverified; getSprite lookup creates placeholders, forbidden.
- QAowner /root/references_plan now prepares FRESH11point condensedtour fromfinal
  actual native roomgeometry/switchcoords, followedby save/reload and sanitizedQA.
  Root must inspect selectedfinalPNGs, verify4796files tested==installed==ZIP.
- Puretoolrecipes committed locally pz-map-tools8978e8b,10testsPASS. Owner
  /root/urban_buildings fixes canonicalLF provenance/exports so clonehashes agree;
  root must commit thatfix too. No remote configured for toolrepo.
- Pending afterQA: finalize docsQA/MODLOG, package0.2.0-alpha.1 once, run
  tools/release_verify.py --run <SUCCESSFRESH> --zip dist/MeridianLongWayHome-0.2.0-alpha.1.zip,
  commit/pushproject, gh release create0.2.0-alpha.1 ZIP+SHA256SUMS --prerelease
  --latest=false --target main --notes-file RELEASE_NOTES.md, publicdownload/hash.
  GitHubONLY; noSteamBoosty. Update daily memory/MEMORY readbeforewrite.
- Userexplicitly requested Telegramcompletion. Enabled channeldefault account;
  no conversationsrefs available. Historical linkedIvan recipient resolved via
  sessionssearch. Use CLI message send to confirmedprivateIvan chat afterDONE,
  attach docs/BUNKER-ENTRANCE.png plus concise release/NEWworld/door48259,1424 text.
  Record deliveryresult; never claim sent without success. RootfinalRussian must
  include release link, actualscope, bunkercoordinates+schemalink and TGstatus.
- DONE final fresh native QA20261106-142304-247195 overall+wrapperPASS:
  all11targets,4actualstairtraversals,3native nightONOFF illuminationdeltas
  0.396078/0.301961/0.301961;181actualcompiledsprites0missing0invalidtextures,
  7verifiedseasonaltreeproxies.0Lua/0unknownmapresourceerrors;6startupfont/Piano
  diagnostics retained. Frozen4796file treeSHA256
  bce864b2bd7c0892a2351f69bb42f6697a8a64c8db91b274e71b9de52f0e7339.
- DONE isolated reload20261106-142928-051777 native+wrapperPASS token/position/floor;
  4796files equal finaltree. Exported final26frames+reload1frame with sanitized
  reports/receipts and evidenceREADME in docs/test-results/2026-11-06-urban.
  Rootinspected selectedfinalPNGs: realbrightness,backedlamps,bed,stairs,parking.
  Wallcrownframe onlywalkway notpanorama; bunkershaftBEFOREoccluded,AFTERshowsB1
  player+physicalstairs. No fullpavilionvisual/firstperson/fullroute/MPclaim.
- Publication resumed after interruption: final fresh/reload receipts confirmed;
  no build, install or game run repeated. QA ledger now links final urban evidence.
  Packaging and exact-byte release binding are the next open publication steps.
  The owner's new area/destination-aware density rule is a separate pz-map-tools
  improvement, NOT part of the frozen, already-tested 0.2.0-alpha.1 map bytes.
- DONE packaged0.2.0-alpha.1 ONCE:111962694bytes ZIP SHA256
  29c386ca41b28b4420d8a45704ba2da32ea994f08b0b8f63d163ef3538e5526d.
  tools/release_verify.py PASS: all4796sourcefiles==installed==successfulgamecopy
  ==releaseZIP; frozen candidate tree unchanged. Gitdiffcheck clean.
  Next: commit/push, publish GitHub prerelease and anonymous asset/hash retrieval.
- DONE source/evidence commit22e2111 pushed origin/main. GitHub ONLY prerelease:
  https://github.com/druidqwerty/pz-meridian/releases/tag/0.2.0-alpha.1
  Published ZIP111962694bytes +SHA256SUMS.txt105bytes; both anonymously downloaded
  and exact-byte/hash matched. docs/test-results/2026-11-06-urban now retains
  sanitized release-binding.json/public-release.json. No Steam/Boosty, no duplicate
  game tests or map builds/installs, no player saves touched. ZIP not repackaged.
  DONE owner-facing completion: private Telegram release notification + entrance
  diagram delivered successfully; root memory updated. No notification retry
  needed. New density-rule tool is complete separately in pz-map-tools (14new
  +10urban tests PASS); it is NOT included in the frozen released map files.


## Active area-aware interiors integration — 2026-11-06
- DONE: vendored six pure native_b42 modules with canonicalLF SHA256provenance
  and originalMIT notice; no sibling checkout/game artwork/geography dependency.
- DONE: area_furnishing adapter caches immutable local props/reports, clips
  cell-wide door masks, records every actualroom's programme/density/access.
  Functional rooms>=96tiles use zoning; small fittedlounges/rooms and thin
  circulation keep explicit policies with densityAudited=false/accepted=null.
- DONE: up to4deterministic legitimate activity layouts; retain failedattempt
  warnings; stop generation if nonepass, never filler/hiddenlarge-room fallback.
- DONE: commercial kitchens/foodseating and institutional beds use explicit
  publicprogrammes. Bunker nowplans each real28x40/96x96room ONCE rather than
  multiplying whole kitchenlines per12x10bay; publickitchens/dorms/washrooms
  retain their native lootnames. Cachecontainers are solidobstacle masks.
- DONE: surface/bunker furnishingreports exported in compile_cell manifest
  with worldcoords, floor, lootRole, purpose, actualgroups and acceptance metrics.
  Roomlights/stairs/doors/sanctuarysurface/undergroundinfection unchanged.
- Focusedtests:6newarea+3furnishing+3nativeinteriors+3nativearchitecturePASS.
  Surface allkinds seed7:0.953s,605reports(389zoned/212compact/4circulation);
  full188,4bunker9.594s with43logicalroomplans. All16winghabitat3testsPASS in179.867s (native doors/stairs/seams/loot/sprites).
- NEXT parent: fullbuild/audit, fresh isolatedlarge-room visual/access QA,
  onlythen any install/package/GitHubrelease. Old0.2.0gameproof is not newproof.

## Independent furnishing review — 2026-11-06
- Fixed an actual post-plan surface cache obstruction (visitor seed0/28): the
  cabinet was inserted in front of a south-facing counter after acceptance.
  Surface caches now enter room planning as solids, with their own S use square
  reserved before any furnishing; no longer chosen from arbitrary bare floor.
- Compact fitted recipes also honor explicit activity/solid masks. Solids reserve
  a one-tile apron; overlapping solid/walkable masks fail rather than silently
  clipping groups. Compact acceptance deliberately remains null, not density-pass.
- Eight area integration tests and three native interior tests PASS; an independent
  265-layout sweep (all53kinds x seeds0/7/14/21/28) found no cache-blocked native
  container/appliance fronts, and each cache's own S front was empty.
- Vendor six-module canonical-LF hashes match current map-tools source exactly.

## Loaded bunker infection scheduling — 2026-11-06
- Fresh density QA exposed empty newly visited B1 kitchen/dormitory samples.
  Actual compiled kitchen retains6739conservative free squares and140buckets
  outside player14tile safety; dense furniture was not exhausting spawn floor.
  Old FIFO simulation:256unloaded jobs before1loaded job yielded0spawns after
  720ticks. Native same-candidate diagnostic independently ruled out1600cap:
  kitchen/dormitory remained0global zombies at15/30/60seconds despite thousands
  of eligible loaded floor tiles. Failed receipts are preserved, not a release pass.
- Replaced FIFO with bounded loaded-job scheduling:3nearest jobs (same-floor
  first, safety-overlap buckets last) plus1oldest eligible job per60ticks.
  Full64square candidate search still runs for atmost4jobs, not every queued job.
- Unloaded/already-seeded jobs are pruned. Saturated2048queues prune anchor-only
  at most once/tick for admission, so stale work cannot discard a new room load.
  Temporary blocked/player-protected/capped jobs retry while loaded after120ticks,
  with fair rotated age; moving away needs no new square-load event.
- Preserved authority, no-zombie/live-disable, player14tile exclusion,1600cap,
  once-per-save/bucket/floor persistence and native addZombiesInOutfit behavior.
  No debug exports or oracle-specific runtime behavior added.
- Ten queue negative-control regressions and five existing runtime tests PASS.
  Geometry unchanged. Parent must freeze/reinstall changed runtime and run a
  fresh native density tour plus reload; old failed build is not successful proof.

## Density candidate build gates — 2026-11-06
- Source version 0.2.1-alpha.1; full Meridian discovery PASS:57 checks in290.793s.
  Following final cache/compact fix:8area checks PASS(2.796s),3native architecture
  checks PASS(32.970s); reviewer also reran3native interiors PASS.
- Map-tools access/mask fixes committed locally4df2e98; no remote configured.
  Relevant16furnishing+10urban checks PASS; historical all-discovery fixture
  failures are retained in that repo MODLOG, not repaired by reviving retired data.
- Static audit now requires current manifest version and actual per-room furnishing
  reports; all zoned plans must be accepted/connected with no final warnings.
  Compact/circulation policies remain explicitly not density-audited.
- Full native build in progress. No new game result/release claimed yet.

## Final density/runtime acceptance — 2026-11-06
- Runtime-only queue fix installed with backup; geometry not rebuilt again.
  Final4796file tree c3f2943fba4181fb70ee805324dd1675d5064ca8e5792632f92fecfee8d49435.
- Fresh154258-021984 native+wrapperPASS:7real10tileaisles,2realstairs,2native
  night-light deltas0.400000006/0.235294104;B1kitchen103/dorm74nearbybelow.
  184sprites0missing0invalidtextures7seasonalproxies;0Lua/0unknownresources,
  6stockstartupdiagnostics retained. Oldfailed+readonlydiagnosis preserved.
- Reload155013-062068 PASS token/exactposition/floor;439below retained;all4796
  reloadedfiles equal finaltree. No user saves/settings or unrelatedmods touched.
- Semanticcoverage fix: original Schoollabel chose nursery;Dininglabel chose
  commercialkitchen. Rawtargets/runs unchanged;futurepreparer filtersactualpurpose.
  FourtargetchecksPASS. Supplemental155309-686353 actualclassroom+dining both
  ordinary10tilewalksPASS;native/wrapper/reload/sprite/resource gatesPASS.
- Root inspected finalkitchen/dorm/retail+bothnightpairs and actualclassroom/dining
  PNGs. Complete localgroups/aisles/visibleinfected/brightnesschanges shown;FoV
  hidesfarsides. No everyroom,fullroute,MP,combat or perfectViewpointceilingclaim.
- Evidence docs/test-results/2026-11-06-density retains failed29+diagnostic5+
  final29+reload1+supplement7 actualframes and sanitizedreceipts. Private
  diagnosticdrivers staysource-only;playableZIP nowexcludesdocs codeextensions.
- NEXT: packageONCE,release_verify against finalfresh154258,sourcecommit/push,
  GitHubONLY prerelease0.2.1-alpha.1 +anonymousasset/hashcheck. NoSteam/Boosty.

- DONE packaged0.2.1-alpha.1 ONCE155309776bytes ZIP SHA256
  8c21ac7a31b694af665734aede696daeff12e805d443bbb71718eff5fc4bb5fc.
  release_verify PASS:all4796sourcefiles==installed==successfulfresh==ZIP.
  Sanitizedbinding in density/release-binding.json; no map rebuild/repackage.
  NEXTcommit/push,GitHubprerelease,anonymousZIP+checksumretrieval.

- DONE GitHubONLY0.2.1-alpha.1 published from09db0ae:
  https://github.com/druidqwerty/pz-meridian/releases/tag/0.2.1-alpha.1
  ZIP155309776bytes+SHA256SUMS105bytes anonymouslydownloaded/exacthashmatched.
  Publicreceipt density/public-release.json;source/tested/installed/ZIP stillbound.
  NoSteam/Boosty,player saves/settings/unrelatedmods untouched;no repeatbuild/
  install/game/package needed. Owner completion+memory filing next.

- DONE private Telegram completion+actual finaldormPNG delivered message4252.
  Memory filed in main/modder workspaces. No notification retry or pending release step.
