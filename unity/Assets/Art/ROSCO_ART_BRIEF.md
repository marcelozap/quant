# Rosco: XIV Companion Art Brief

## Purpose

Rosco is the first character the player trusts in XIV. He should make the world feel inhabited before any district is fully built. His job is not to explain the systems or behave like a mascot on a menu. He walks, notices, waits, gets briefly distracted, and makes the route feel worth taking on foot.

This brief replaces the procedural placeholder as the production target. The placeholder in the first-world builder remains useful for testing movement, triggers, saves, and companion timing.

## Visual direction

- Original, warm, expressive companion with a clear silhouette at third-person distance.
- Friendly mixed-breed dog rather than a recognizable existing character or breed mascot.
- Compact athletic body, slightly oversized head, expressive ears, bright eyes, and a tail that reads clearly while moving.
- Fur palette: chestnut, warm cream, and a small signal-coral collar accent. Materials should feel soft without becoming furry-card overdraw.
- The design belongs beside Green Gate's teal, lime, coral, cream, and gold world language while remaining readable in Archive Garden, neon market spaces, and night lighting.
- Personality comes from posture and timing: eager greeting, curious pause, relaxed follow, alert investigation, and quiet end-of-walk pride.
- No weapons, armor, tactical gear, branded marks, copied cartoon silhouettes, or overly robotic parts.

## Model and rig

- One skinned dog rig with a clean root, pelvis, spine, neck, head, jaw, ears, front legs, back legs, paws, and tail chain.
- Separate material regions for fur, muzzle/chest, nose/eyes, collar, and optional small tag.
- Keep the face simple enough for real-time animation: eye aim, blink, ear tilt, jaw open, and a subtle brow or cheek deformation if the chosen rig supports it.
- Target a performant first pass: approximately 12k-25k triangles, one 2048px albedo/roughness set, one small mask set, and no required runtime hair simulation.
- Provide a lower-detail LOD and a shadow-friendly material variant before the final scene is populated with more landmarks.
- Export a Unity-ready FBX with scale and forward axis documented in the import notes. The source file stays beside the export under `Assets/Art/Source/`.

## Animation set

Required clips:

1. `Rosco_IdleRelaxed`: breathing, occasional blink, small tail motion.
2. `Rosco_Greet`: look to Marcelo, quick step or bounce, tail wag, settle.
3. `Rosco_Walk`: relaxed four-legged walk with a loop that blends cleanly at low speed.
4. `Rosco_Trot`: optional faster loop for distance recovery, never frantic.
5. `Rosco_Investigate`: slow approach, sniff, head turn, and hold.
6. `Rosco_Wait`: sit or stand near Marcelo, looking between him and the point of interest.
7. `Rosco_Recall`: turn toward Marcelo and return with visible recognition.
8. `Rosco_Celebrate`: small joyful hop, tail wag, and settle for Archive Garden completion.
9. `Rosco_StuckRecover`: turn in place, look around, and rejoin the route.

Animation principles:

- Keep the body smooth and grounded. Personality should come from anticipation, weight shifts, and eye line, not constant squash-and-stretch.
- Feet should not skate at normal walking speed. Root motion is optional; the first integration may remain code-driven with clips used for presentation.
- Every clip must have a clean first and last pose for interruption and blending.
- The companion controller owns state and distance. The animator owns pose, gaze, ears, tail, and facial response.

## Runtime handoff

The final asset must preserve the existing scene contract:

- Root object name: `Rosco`.
- Root receives `RoscoCompanion`.
- The controller can find or receive Marcelo as its player target.
- Investigation points continue to emit their existing point name through `InterestDiscovered`.
- The model must not add colliders to every visible child. Use one root collider or a deliberate navigation collider only if the runtime test proves it is needed.
- Animation parameters should be minimal and stable: `Speed`, `State`, `IsInvestigating`, `Celebrate`, and an optional `LookAtWeight`.

## Acceptance test

At the third-person camera distance, a new player can identify Rosco in under one second, tell which direction he is facing, and understand whether he is following or investigating without reading debug text. On the Green Gate to Archive Garden route he should feel like a companion with a point of view, not a moving primitive or a second player character.

## Handoff order

1. Concept sheet: front, side, three-quarter, expression strip, and color/material callouts.
2. Clean low-poly blockout with the final silhouette.
3. Rig and required animation clips.
4. Materials, LOD, and Unity FBX import.
5. Replace the procedural child meshes in a duplicate test scene before touching the authored first route.

