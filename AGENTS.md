# Meridian development rules

- Original fictional world, not a continuation of any retired geographic mod.
- User explicitly authorizes GitHub only until further notice. NO Steam/Boosty.
- Standalone B42.21 map, native 256-cell/8-chunk format; keep user saves intact.
- Sanctuary surface (z>=0) is zombie-free; negative levels must remain infected.
- Vanilla sprites only. Do not redistribute game art or external mod assets.
- Compile reproducibly: python tools/generate.py; build outputs are ignored.
- Keep MODLOG.md current. Distinguish static, simulation and live-game evidence.
- Driving-time ratio must not be called verified without a timed vehicle run.

## Current 0.2.1-alpha.1 checkpoint (supersedes old publication next-steps)
- Finalfresh154258/reload155013/supplement155309 PASS;root inspected finalPNGs.
- 4796files treec3f2943fba4181fb70ee805324dd1675d5064ca8e5792632f92fecfee8d49435.
  PackedONCE155309776bytes SHA2568c21ac7a31b694af665734aede696daeff12e805d443bbb71718eff5fc4bb5fc.
  source==installed==tested==ZIP verified. Do not repeat successful game/build/install/package.
- Evidence/newlimits in docs/test-results/2026-11-06-density and docs/QA.md;failed
  initialpopulationrun+readonlydiagnosis preserved;queue runtime repaired.
- Next authorized:commit/push,GitHubONLY0.2.1-alpha.1 prerelease+anonymoushashcheck.
  NeverSteam/Boosty;do not touchplayer saves.
