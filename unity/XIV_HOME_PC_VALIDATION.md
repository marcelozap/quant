# XIV Home-PC Validation

This is the first runtime gate for the private XIV world. Run it on the machine with Unity installed and the NVIDIA GPU available for audio and visual validation.

## Setup

1. Pull `main` from `https://github.com/marcelozap/quant.git`.
2. Open the repository's `unity/` folder in Unity `6000.0.41f1`.
3. Wait for Package Manager to finish importing URP, Input System, AI Navigation, and Timeline.
4. Select **XIV -> Create First Playable World**.
5. Select **XIV -> Validate First Playable World**. Record any failed check before changing anything.

## First walk

1. Open `Assets/Scenes/XIVWorld.unity` and press Play.
2. Confirm the first view is Green Gate with the guide reading `ARCHIVE GARDEN -> WALK WITH ROSCO`.
3. Walk with `WASD` or the arrow keys. Hold `Shift` to run. Hold the right mouse button and drag, or use `Q` and `E`, to orbit.
4. Confirm Rosco greets Marcelo, follows at a comfortable distance, turns naturally, and investigates at least one route point.
5. Press `F` to make Rosco wait and resume. Press `R` to recall him. Confirm neither action breaks the route.
6. Walk to Archive Garden. Confirm Rosco celebrates, the guide changes to `WALK COMPLETE`, and the summary reports a saved walk.
7. Quit and relaunch the scene. Confirm Archive Garden reports the previous total walk count.

## Audio pass

1. Put one local `.mp3`, `.wav`, or `.ogg` in the app's `XIV/Audio` folder, or set `XIV_AUDIO_PATH` to a test track.
2. Play the scene and confirm the track remains local, music energy changes lights and route motion, and the world still runs when the file is missing.
3. For a MaloSound artifact, set `XIV_AUDIO_ANALYSIS_PATH` to an `AudioAnalysisV1` JSON file. Confirm timestamped `beat_times` produce beat pulses without inventing a grid when the artifact is invalid.

## Safety pass

- Press `Esc`; confirm time and audio pause, then resume cleanly.
- Move the application window out of focus; confirm the private build pauses when focus-loss pause is enabled.
- Walk Marcelo beyond the test ground if practical; confirm he returns to Green Gate with movement cleared instead of requiring a restart.
- Complete a walk with the save directory writable, then temporarily make it unavailable and confirm the destination remains retryable rather than claiming an unsaved completion.
- After a completed walk, force-quit once and relaunch; confirm the active session and walk history remain readable.
- Confirm no API token, trade history, or private source data appears in the Unity scene or project assets.

## Evidence to bring back

Record the Unity version, validator result, GPU, one Green Gate screenshot, one Rosco-follow screenshot, one Archive Garden completion screenshot, and any console errors. Do not commit generated scenes, builds, audio, saves, tokens, or private data unless the repository rules are explicitly changed.

## Art handoff

The current Mac checkout does not contain `Assets/Art/Exports/GreenGate.fbx`, so the builder uses its procedural fallback. If Blender is available on the home PC, run from the repository root:

```text
blender --background --python unity/Assets/Art/Source/generate_green_gate.py
```

Review the generated asset in a duplicate scene first. The builder will use the FBX automatically on the next world generation, and the source now labels the landmark as XIV rather than Green Machine Park.
