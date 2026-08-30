# XIV Green Gate: Fable Creative Handoff

## Your lane

Work only in `unity/Assets/Art/` and `unity/Assets/Scripts/Park/` unless the user explicitly expands scope. Do not edit Python, `.env`, database files, API authentication, import logic, or trade-history data.

## First creative task

Take `Assets/Art/Source/GreenGate.blend` and evolve it into a more detailed original XIV entrance.

- Preserve the warm cartoon + neon-market + fantasy-nature blend.
- Keep the teal, signal-lime, coral, cream, and gold palette.
- Make it unmistakably original. Do not reuse Toontown characters, logos, signs, map layouts, or assets.
- Upgrade geometry: layered tower roofs, decorative trim, ticket-window details, modular lanterns, garden planters, better trees, a readable path, and a welcoming Rosco companion statue/shape.
- Preserve a clear path through the arch for the third-person player and leave the actual Rosco companion to Unity.
- Keep the landmark performant for Unity URP: modular meshes, baked lighting friendly, no excessive tiny geometry, and no textures larger than 2048px in the first pass.
- Export a Unity-ready FBX to `Assets/Art/Exports/GreenGate.fbx` and save the updated Blender source beside the current source file.
- Render one PNG preview to `Assets/Art/Previews/`.

## Acceptance check

The asset should read clearly at third-person distance, look inviting in daylight and neon at night, and leave room for a world-space XIV arrival board. The landmark should say XIV, not Green Machine; Green Machine appears later as a read-only interior lane. Do not create a complete park map or touch data-connected UI yet.
