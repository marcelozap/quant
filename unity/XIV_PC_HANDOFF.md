# XIV — PC Continuation Handoff (2026-08-29)

This file is the pickup point for continuing XIV on the home PC. Paste the
"CONTINUATION PROMPT" section into a fresh Claude session, or follow it yourself.

## State pushed in this commit

- 55/55 structural validator checks pass; private macOS build succeeded on the laptop.
- Player.log prints on launch:
  `XIV runtime ready: camera=true player=true rosco=true navmesh=true route=true destination=true save_root=true`
- Authored art is live: `Assets/Art/Exports/GreenGate.fbx` (v2, mesh-only) and
  `Assets/Art/Exports/MarceloHero.fbx`, generated headless from
  `Assets/Art/Source/generate_green_gate.py` / `generate_marcelo.py`.
- Full runtime smoke test passed on the laptop: WASD walk, Shift run, Rosco
  greet/follow/investigate ("Wind chime" discovery), F wait, R recall, Esc
  pause/resume, walk completion saved at Archive Garden (TOTAL WALKS 1),
  welcome-back board on relaunch, no magenta, no blown-out lighting, no
  NavMesh agent errors, billboards readable and not mirrored.
- NOT in the commit (regenerated locally): `Assets/Scenes/XIVWorld.unity`
  (run **XIV → Create First Playable World**), Builds/, Library/, Logs/,
  Blender `.blend1` backups.

## Gotchas — do not regress

- `ProjectSettings.asset` `activeInputHandler` must stay `1` (Input System);
  at `0` all input is silently dead in players.
- Rosco's NavMeshAgent must be serialized DISABLED in the scene (the builder
  does this); `RoscoCompanion` enables it after `NavMesh.SamplePosition` succeeds.
- The builder disables light/camera import on both FBXs — the Blender sources
  carry high-energy authoring lights that blow out the scene if imported.
- TextMesh billboards are correct with `LookRotation(-direction)`; mirrored text
  means a negative `localScale` snuck in somewhere, not a billboard bug.
- The scene is generated — never hand-edit or commit `XIVWorld.unity`.
- The app pauses on focus loss and does not auto-resume; Esc resumes.

## CONTINUATION PROMPT

Continue the XIV Unity project in the quant repo, folder `unity/`, Unity
6000.0.82f1. Do not create a new architecture or repo. XIV is a private personal
video-game world — warm, cinematic, personal, an original animated adventure
world, not cyberpunk/Roblox/tech-demo. Marcelo walks with his dog Rosco from
Green Gate to Archive Garden. All data local; no cloud services ever.

Task on this PC:
1. Open `unity/` in Unity 6000.0.82f1, let packages import.
2. Run **XIV → Create First Playable World**, then **XIV → Validate First
   Playable World**. Expect 55/55.
3. Press Play and do the human visual walkthrough from
   `unity/XIV_HOME_PC_VALIDATION.md`: Green Gate first view, WASD/Shift
   movement, Rosco behaviors (F/R), full walk to Archive Garden, save +
   relaunch welcome-back, Esc pause, audio pass with one local mp3; record
   GPU, screenshots, and any console errors.
4. If the FBXs ever need regenerating:
   `blender --background --python unity/Assets/Art/Source/generate_green_gate.py`
   and `...generate_marcelo.py` from the repo root.
5. Do not touch: green_machine files, projects/, scripts/, credentials,
   private market data, personal audio or save files. No cloud services,
   no model-training claims.

Heads-up: multiple AI sessions have edited this repo concurrently (art passes
via a Codex session). Diff the working tree before building and treat
unexpected changes as possibly intentional — flag them, don't revert silently.
