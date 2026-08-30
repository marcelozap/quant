# Request for Claude: Green Machine Trajectory Review

Please give product, game-design, and technical opinions only. Do not edit files, install tools, access credentials, read private trade data, or change the architecture.

## What Green Machine is

Green Machine is a private Mac 3D world for one person’s market life. It combines:

1. A market operating system: sourced watchlists, earnings, macro context, research notes, and an eventually read-only account observatory.
2. A trading-performance lab: encrypted trade history, journaling, execution review, and descriptive pattern analysis.
3. A personal brain archive: a daily song, creative projects, memories, and life context.

It is not a signal generator, automated trader, or public social app.

## Direction locked so far

- Unity 6 LTS + C#, native Mac application, third-person exploration.
- High-detail original art, mixing warm cartoon park entrance, neon market spaces, and fantasy nature.
- An original Rosco-inspired dog companion.
- Sector lands containing individual stock homes. First real stock home: NVDA.
- Full exterior park shell first: Green Gate, Semiconductor Speedway, Macro Mountain, Earnings Arcade, Tape Tunnel, Signal Square, Account Observatory, Archive Garden.
- Data stays local: SQLCipher encrypted store, macOS Keychain key, loopback-only Python API. No orders.
- Source cards store a link, timestamp, interpretation, and verification question. They open externally only on user action.
- Market data is cached/on-demand to respect a shared Schwab rate limit.
- The first Green Gate base asset/render is at `Assets/Art/Previews/green_gate.png`.

## Current proof that it is grounded

- 2,953 real closed option trades have been validated and encrypted locally.
- The importer is idempotent and preserves raw source lineage.
- Descriptive analytics now group the history across 24 underlyings and DTE buckets, with caveats instead of signals.
- A Blender source asset and Unity editor scaffold already exist.

## Your job

Give a direct opinion in five short sections:

1. **Trajectory:** Is this a coherent personal product, or is it trying to be too many things? Name the one most important framing change if needed.
2. **First 15 minutes:** Describe the exact first session that would make someone immediately understand why this is special and return tomorrow.
3. **World design:** Which three spaces should receive disproportionate art/animation attention first, and why?
4. **Risk:** List the three biggest risks: one product risk, one game-design risk, and one technical risk. Give a practical mitigation for each.
5. **Fable’s next asset:** Give a concrete art brief for upgrading Green Gate from the current base render into a polished original landmark.

Stay decisive. Use visual language instead of generic startup language. Do not recommend automated trading, public sharing, or copying Toontown assets.
