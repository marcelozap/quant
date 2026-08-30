# XIV Green Gate: Fable Creative Handoff

## Your lane

Work only in `unity/Assets/Art/` and `unity/Assets/Scripts/Park/` unless the user explicitly expands scope. Do not edit Python, `.env`, database files, API authentication, import logic, or trade-history data.

## First creative task

Take `Assets/Art/Source/GreenGate.blend` and evolve it into a more detailed original XIV entrance.

- Preserve the warm cartoon + neon-market + fantasy-nature blend.
- Keep the teal, signal-lime, coral, cream, and gold palette.
- Make it unmistakably original. Do not reuse Toontown characters, logos, signs, map layouts, or assets.
- Upgrade geometry: layered tower roofs, decorative trim, ticket-window details, modular lanterns, garden planters, better trees, a readable path, and a welcoming Rosco companion statue/shape.
- Break the landmark's symmetry intentionally: give the left tower a compact ranger booth or lantern post where Rosco can wait, and the right tower a mounted park-map board.
- Add a shallow copper-green curved roof with a small overhang and visible underside over the header; it must feel substantial when the player walks under it.
- Use materials, not flat color blocks: painted wood with subtle edge wear, brushed brass for `MACHINE`, signal-lime emissive lettering and real inset lamps.
- Ground the towers with a stone footing course and grass tufts. Make the path transition from concrete outside the gate to warm brick inside it.
- Include only two story details: a small ticker-tape relief band across the header and a hanging `EST. [first trade year]` sign that can be populated locally later.
- Compose the preview for a golden-hour arrival shot from behind the player, with gate lamps already on.
- Preserve a clear path through the arch for the third-person player and leave the actual Rosco companion to Unity.
- Keep the landmark performant for Unity URP: modular meshes, baked lighting friendly, no excessive tiny geometry, and no textures larger than 2048px in the first pass.
- Export a Unity-ready FBX to `Assets/Art/Exports/GreenGate.fbx` and save the updated Blender source beside the current source file.
- Render one PNG preview to `Assets/Art/Previews/`.

## Acceptance check

The asset should read clearly at third-person distance, look inviting in daylight and neon at night, and leave room for a world-space XIV arrival board. The landmark should say XIV, not Green Machine; Green Machine appears later as a read-only interior lane. Do not create a complete park map or touch data-connected UI yet.

## Non-negotiable emotional rule

The park never judges a user by profit or loss. Do not create damaged, gloomy, or punitive assets for losses or drawdowns. Market state can change the park's atmosphere descriptively; personal P&L cannot.
