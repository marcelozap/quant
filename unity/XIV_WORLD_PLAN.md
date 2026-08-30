# XIV World Plan

## North star

XIV is a private personal video game world for Marcelo. It is a place to return to when he wants to walk, think, create, review, or reset. The project can be authored on the Mac and validated on the home PC; the Unity core stays cross-platform and local-first.

The first year is not an attempt to reproduce the content volume of a large commercial open-world game. It uses an AAA standard of care for a smaller world: responsive movement, believable companion behavior, authored spaces, strong camera work, layered sound, readable interaction, stable saves, and environmental detail that rewards attention.

The first real promise is simple:

> I can open XIV, walk Rosco through a beautiful route, notice something, listen to music, visit one meaningful place, and return home with the session saved.

## The three names

- **XIV**: the world, the home, and the overall personal system.
- **MaloSound**: music, audio analysis, creative technology, and performance visuals.
- **Green Machine**: market data, research, trade journaling, backtesting, and decision review.

AI and business work belong inside XIV. They do not need a fourth public name.

## Player experience

The first fifteen minutes should feel like this:

1. Marcelo enters through Green Gate and immediately sees a clear path forward.
2. Rosco notices Marcelo, falls into a comfortable walking position, and reacts naturally to the environment.
3. The player walks instead of fast-traveling. The route contains small visual, musical, and environmental discoveries.
4. Rosco stops to investigate something. The player can wait, call him back, or continue.
5. Music changes the atmosphere through controlled lighting, color, and motion in the environment.
6. The player reaches one meaningful space: MaloSound, Green Machine, or a personal archive point.
7. The player returns with Rosco, reviews a small session state, and saves.

Walking is the core loop. Data, music, and future systems should give the walk more meaning, not replace it.

## World structure

The initial map keeps the current eight landmarks as a readable outline:

- **Green Gate**: home entrance and daily orientation.
- **Semiconductor Speedway**: a bright, kinetic place for technology and systems.
- **Macro Mountain**: a slower overlook for context and long-range thinking.
- **Earnings Arcade**: a contained event-review space inside Green Machine.
- **Tape Tunnel**: execution history and market memory.
- **Signal Square**: sourced information and questions to investigate.
- **Account Observatory**: read-only personal review, never order placement.
- **Archive Garden**: songs, memories, projects, and personal context.

These are destinations, not dashboard panels pasted into a game. The world should communicate through architecture, sound, light, objects, and short interactions. Charts remain charts when precision matters.

## Twelve-month build sequence

### Month 1: project foundation

- Establish the Unity project as the canonical XIV world project.
- Add a clean scene and folder convention for world, characters, systems, art, audio, and saves.
- Confirm macOS input, URP rendering, AI Navigation, Timeline, and local build settings.
- Define the world-state and save-file boundaries before adding connected data.
- Graybox Green Gate and one short route.

**Gate:** a fresh checkout opens in Unity, creates the first scene, and contains no credentials or private data.

### Month 2: Marcelo movement and camera

- Replace prototype movement with a responsive third-person controller.
- Support walking, running, stopping, turning, camera orbit, camera collision, and a comfortable follow distance.
- Add animation state hooks even while the first character remains a placeholder.
- Make the route navigable without fast travel.
- Keep input on Unity's Input System so the Mac build does not depend on legacy input settings.

**Gate:** movement feels good for ten minutes with no camera fighting, visible jitter, or accidental falling through the world.

### Month 3: Rosco companion

- Replace the primitive follow behavior with a state-driven companion controller.
- Add follow, wait, recall, investigate, sniff, return, idle, and greeting states.
- Add navigation-aware movement, distance bands, turn anticipation, and recovery when Rosco gets stuck.
- Create a first original Rosco model brief and an animation list before commissioning final art.

**Gate:** Rosco can complete the full first route, feel present without blocking the player, and recover from normal pathing errors.

### Month 4: Green Gate landmark

- Upgrade the existing Green Gate preview into a strong original landmark.
- Add layered architecture, readable trim, path edges, plants, lanterns, signage, and a welcoming arrival composition.
- Create day, evening, and night lighting passes.
- Keep geometry modular, URP-friendly, and readable from the third-person camera.

**Gate:** a screenshot of Green Gate is recognizable as XIV without relying on a debug label.

The current builder already creates the first Green Gate and Archive Garden landmarks, a dressed route blockout, Rosco interest points, and a local `XIVAudioAtmosphere` component. `RoscoCompanion` also exposes an optional animator handoff for speed, state, investigation, and celebration, so a final skinned Rosco can replace the placeholder without rewriting the route logic. These are foundations for the gates below, not evidence that the final art or audio experience is complete.

It also creates `XIVWalkSession`, which records only local walk duration, distance, Rosco discoveries, and peak atmosphere energy. This is the first save boundary for the world; it does not import or serialize Green Machine trade data.

The generated Earnings Arcade also contains a read-only Green Machine board. It can show today's local review and song memory through `/world/today`, but it degrades to an explicit offline state and never places orders.

The generated Semiconductor Speedway also contains an XIV Systems board. It provides a small local surface for the AI/business work inside XIV and names the three lanes consistently: XIV, MaloSound, and Green Machine.

The editor also exposes **XIV -> Validate First Playable World**. It checks the generated scene, required player/Rosco/route/data objects, and the absence of serialized API-token fields before the first runtime test.

### Month 5: the complete walk

- Build the Green Gate to Archive Garden route as one authored experience.
- Add points of interest that Rosco can notice.
- Add simple interactable objects, a return-home state, and a walk-session record.
- Add a quiet end-of-walk moment so the experience has a beginning, middle, and end.
- Complete the first route when the player reaches Archive Garden, save the destination, and give Rosco a small celebration response.

**Gate:** the first fifteen minutes work from a clean launch and can be repeated without feeling like a test scene.

### Month 6: MaloSound atmosphere

- Add local music playback with a safe file boundary.
- Map musical intensity to lighting, environmental motion, and atmosphere.
- Add section changes, controlled transitions, and a fallback when no audio is loaded.
- Keep the visuals expressive while the character and movement remain smooth.

**Gate:** one song changes the world in a way that feels intentional rather than like a generic audio visualizer.

### Month 7: XIV work space

- Add one compact space for AI and business work.
- Represent systems through objects, rooms, notes, and interactions rather than a wall of UI.
- Show inputs, decisions, and outputs clearly enough that the player understands what the space is for.
- Keep all content local and editable.

**Gate:** the work space communicates one real workflow in under two minutes.

### Month 8: Green Machine space

- Connect the local Green Machine API through an explicit read-only adapter.
- Show research, backtesting, trade journaling, and review summaries with source and timestamp context.
- Handle unavailable data gracefully and label demo or stale data clearly.
- Keep order placement and automated signals permanently outside the world.

**Gate:** XIV remains useful with the API turned off, and private trading data never enters a build or source asset.

### Month 9: archive and personal context

- Add Archive Garden as the home for songs, memories, projects, and selected notes.
- Link a small number of items to locations and walks.
- Add a personal daily state without turning the game into a task manager.
- Ensure the world can be meaningful even on a day with no market activity.

**Gate:** a walk can end with a remembered moment, not only a metric or destination.

### Month 10: world integration

- Connect the route, landmarks, music, Rosco, local data, and archive into one coherent session flow.
- Add transitions, ambient events, time-of-day variation, and deliberate visual motifs.
- Replace debug labels and temporary panels that survived the prototype phase.
- Keep the playable geography compact and richly authored.

**Gate:** a new session does not require the creator to explain what to do next.

### Month 11: polish and reliability

- Profile CPU, GPU, memory, loading, and save behavior on the home PC and the development Mac.
- Improve animation blending, foot placement, camera framing, audio mixing, and lighting.
- Add settings for volume, reduced motion, input, and display quality.
- Test interrupted saves, missing media, unavailable local API, and bad source records.

**Gate:** a private tester can play the first route without a walkthrough and without encountering a blocking failure.

### Month 12: personal release

- Produce a stable private macOS build.
- Capture a short walk-through video and a small set of screenshots.
- Freeze the first world slice and write a short build report.
- Record the Year Two backlog only after the first slice is enjoyable.

**Gate:** XIV is a repeatable personal game, not just an editor scene or technical demo.

## System boundaries

The first year uses these boundaries:

- Unity owns the world, camera, player, Rosco, interaction, audio-reactive atmosphere, and local presentation.
- Green Machine owns market/data collection, encryption, research, trade journaling, and descriptive analysis.
- MaloSound owns music and audio-derived artifacts.
- The local adapter passes only the minimum read-only, validated data the world needs.
- Beat timing is optional and explicit: XIV receives a BPM and offset from MaloSound or a reviewed local artifact; it never silently invents a beat grid.
- The first audio integration accepts MaloSound's `AudioAnalysisV1` `bpm` and monotonic `beat_times` fields directly; invalid documents clear the beat grid and leave energy response available.
- Credentials, private history, and tokens never live in Unity assets, builds, screenshots, or commits.

## Quality bar

Every new feature should answer at least one of these questions:

- Does it make walking with Rosco more expressive?
- Does it make the world easier to understand without explanation?
- Does it make a place feel authored and memorable?
- Does it make a personal system more honest, reviewable, or useful?

If it answers none of them, it belongs in the backlog.

## Explicitly out of scope for year one

- A giant open-world map.
- Combat, weapons, multiplayer, or public social features.
- Automated trading or buy/sell signals.
- A crowd of generic NPCs.
- Multiple playable characters before Marcelo and Rosco feel excellent.
- A cloud dependency for the basic walk.
- Replacing precise charts with decorative 3D objects.

The world earns expansion after the first route is beautiful, stable, and worth returning to.
