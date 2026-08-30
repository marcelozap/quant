# XIV World

This is the Unity 6 LTS scaffold for XIV, Marcelo's private personal world. Development can begin on the Mac, while the home PC is the intended GPU/audio validation machine. The world is centered on walking Rosco, with MaloSound as the music lane and Green Machine as the local market/data lane.

The current scene is an intentional blockout. It contains original placeholder geometry only; it is safe to replace with the high-detail Blender asset pipeline as the walk loop becomes trustworthy.

The full 12-month direction lives in [`XIV_WORLD_PLAN.md`](./XIV_WORLD_PLAN.md).

## Open the first playable park

1. Install Unity Hub and Unity `6000.0.41f1` with the build support for the machine you are testing on.
2. Open this `unity/` folder as a Unity project.
3. Wait for Package Manager to install URP, Input System, AI Navigation, and Timeline.
4. Select **XIV -> Create First Playable World** in the Unity editor menu.
5. Select **XIV -> Validate First Playable World** and resolve any failed checks.
6. Open `Assets/Scenes/XIVWorld.unity` and press Play.

For a repeatable smoke test on a machine with the Unity editor installed, run Unity in batch mode with `-projectPath` set to this `unity/` folder and `-executeMethod GreenMachine.Editor.XIVWorldValidator.BuildAndValidateFirstWorldBatch`. The command generates the first scene, runs the structural validator, and exits with code `0` only when the checks pass. Use the Unity executable that belongs to version `6000.0.41f1` on that machine.

When the first route is ready to package, select **XIV -> Build Private macOS App**. The build validates the scene first, registers only `Assets/Scenes/XIVWorld.unity` for startup, and writes the app to `Builds/XIV/XIV.app`. The batch equivalent is `GreenMachine.Editor.XIVPrivateBuild.BuildPrivateMacAppBatch`; it exits with code `0` only after a successful macOS build:

```text
/path/to/Unity -batchmode -quit -projectPath "/path/to/quant/unity" -executeMethod GreenMachine.Editor.XIVPrivateBuild.BuildPrivateMacAppBatch -logFile -
```

The editor action creates the first exterior world shell, bakes a NavMesh for the park grounds, and adds a third-person player, an expressive Rosco blockout, an authored procedural sky with depth fog, lighting, and eight named landmarks. Rosco's procedural bridge gives the placeholder a breathing idle, alternating walk cycle, curious investigation pose, tail wag, and small celebration response; the final skinned asset can keep the same companion contract. It does not store data or secrets in Unity.

Use `WASD` or the arrow keys to walk, and hold `Shift` to run. Hold the right mouse button and drag to orbit the camera, or use `Q` and `E`. The camera gently frames Marcelo and Rosco together, with collision protection around the pair. A left click on the ground sets a temporary walk destination. Press `F` to ask Rosco to wait or resume, `R` to call him back, and `Esc` to pause the private build. The in-world guide keeps the Archive Garden route visible, reflects Rosco's current moment, and settles on the saved-walk state at the destination. The first generated scene is a systems blockout, so the player and Rosco are intentionally placeholders while the route and behavior are being tested.

The eight landmarks are a map of future XIV spaces, not a promise to build eight full districts immediately. The first production milestone is the Green Gate to Archive Garden walking route.

## Art handoff

The Green Gate source lives at `Assets/Art/Source/GreenGate.blend`, with the repeatable generator at `Assets/Art/Source/generate_green_gate.py`. From the repository root, run `blender --background --python unity/Assets/Art/Source/generate_green_gate.py` on a machine with Blender installed. It writes the Blender source, a preview, and the Unity-ready FBX at `unity/Assets/Art/Exports/GreenGate.fbx`. The current Unity builder remains a safe placeholder path until that FBX is reviewed in a duplicate test scene.

The generated world also includes `XIVAudioAtmosphere`, `XIVWalkSession`, `XIVWalkDestination`, a Green Machine read-only board, and an XIV Systems board. Reaching Archive Garden completes the first walk, records the destination, celebrates with Rosco, and saves both the current session and a local walk history; the Archive Garden summary keeps the total walk count. Set `XIV_AUDIO_PATH` to a local MP3, WAV, or OGG file, or place a track in the app's local `XIV/Audio` folder; the explicit path wins, and the first alphabetically sorted local track is the fallback. The clip is analyzed locally and its energy is sent to world lights, emissive beacons, and restrained route motion. MaloSound can provide an explicit BPM and offset through `SetBeatGrid`, or XIV can load the exact `AudioAnalysisV1` JSON shape from `XIV_AUDIO_ANALYSIS_PATH`; invalid or missing timing data disables beat pulses rather than guessing. The Green Machine board reads `/world/today` from the loopback API when available and displays an offline state otherwise. The XIV Systems board reads an optional local `XIV/systems.json` file and falls back to the three-lane identity. Walk summaries and history are autosaved to the local application's data directory on whichever machine runs the build. Audio files, session saves, tokens, and private data should stay outside Git.

## Local API

Run `quant-live green-machine-serve` after setting `GREEN_MACHINE_API_TOKEN`. Set the same token only in local Unity editor settings before running a data-connected scene; do not save it in a project asset or commit it.
