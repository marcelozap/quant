# XIV Marcelo Character Brief

## Role

Marcelo is the player character in XIV: a capable, stylish traveler moving between music, systems, training, and memory. He should read as a real human being with a confident silhouette, not a mascot, robot, toy, or generic game avatar.

## Visual direction

- Athletic and natural proportions with a relaxed, slightly heroic posture.
- Warm human face and visible hands; the character should feel alive even at a distance.
- Contemporary travel clothing with a tailored teal outer layer, warm amber inner layer, dark trousers, practical boots, and one signal-lime XIV accent.
- Small personal details: cap, scarf, compact backpack, and a restrained XIV emblem.
- Premium stylized realism: clean shapes, believable materials, expressive animation, and controlled color.
- The silhouette must remain readable from the third-person camera when Marcelo and Rosco share the frame.

## Avoid

- Roblox-like block bodies, stick limbs, featureless capsules, exaggerated armor, weapons, military styling, or a neon tactical suit.
- A crowded logo wall or UI pasted onto the character.
- Copying a recognizable existing character design.

## Animation contract

The Unity player root owns movement and the `ThirdPersonMover` component. A replacement asset should expose or preserve named transforms for `body`, `head`, `armLeft`, `armRight`, `legLeft`, `legRight`, `shoulderLeft`, `shoulderRight`, and `scarf` so `MarceloProceduralAnimator` can continue to provide a temporary bridge until authored clips exist.

Required authored clips later: idle breathing, relaxed walk, purposeful run, stop and turn, look toward Rosco, and a small arrival gesture at Archive Garden.

## Acceptance image

Render Marcelo from behind at Green Gate during golden hour, with Rosco visible at his side and the path readable ahead. The image should communicate that XIV is a private world built for walking, attention, and movement.
