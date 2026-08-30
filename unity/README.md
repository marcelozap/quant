# XIV World

This is the Unity 6 LTS scaffold for XIV, Marcelo's private personal world. Development can begin on the Mac, while the home PC is the intended GPU/audio validation machine. The world is centered on walking Rosco, with MaloSound as the music lane and Green Machine as the local market/data lane.

The current scene is an intentional blockout. It contains original placeholder geometry only; it is safe to replace with the high-detail Blender asset pipeline as the walk loop becomes trustworthy.

The full 12-month direction lives in [`XIV_WORLD_PLAN.md`](./XIV_WORLD_PLAN.md).

## Open the first playable park

1. Install Unity Hub and Unity `6000.0.41f1` with the build support for the machine you are testing on.
2. Open this `unity/` folder as a Unity project.
3. Wait for Package Manager to install URP, Input System, AI Navigation, and Timeline.
4. Select **XIV -> Create First Playable World** in the Unity editor menu.
5. Open `Assets/Scenes/XIVWorld.unity` and press Play.

The editor action creates the first exterior world shell, a third-person player, a Rosco placeholder companion, lighting, and eight named landmarks. It does not store data or secrets in Unity.

Use `WASD` or the arrow keys to walk. Hold the right mouse button and drag to orbit the camera, or use `Q` and `E`. A left click on the ground sets a temporary walk destination. The first generated scene is a systems blockout, so the player and Rosco are intentionally placeholders while the route and behavior are being tested.

The eight landmarks are a map of future XIV spaces, not a promise to build eight full districts immediately. The first production milestone is the Green Gate to Archive Garden walking route.

The generated world also includes `XIVAudioAtmosphere`, `XIVWalkSession`, `XIVWalkDestination`, a Green Machine read-only board, and an XIV Systems board. Reaching Archive Garden completes the first walk, records the destination, celebrates with Rosco, and saves locally. Set `XIV_AUDIO_PATH` to a local MP3, WAV, or OGG file, or call `LoadMusicFile` from a future media selector; the clip is analyzed locally and its energy is sent to the world lighting. MaloSound can provide an explicit BPM and offset through `SetBeatGrid`, or XIV can load the exact `AudioAnalysisV1` JSON shape from `XIV_AUDIO_ANALYSIS_PATH`; invalid or missing timing data disables beat pulses rather than guessing. The Green Machine board reads `/world/today` from the loopback API when available and displays an offline state otherwise. The XIV Systems board reads an optional local `XIV/systems.json` file and falls back to the three-lane identity. Walk summaries are autosaved to the local application's data directory on whichever machine runs the build. Audio files, session saves, tokens, and private data should stay outside Git.

## Local API

Run `quant-live green-machine-serve` after setting `GREEN_MACHINE_API_TOKEN`. Set the same token only in local Unity editor settings before running a data-connected scene; do not save it in a project asset or commit it.
