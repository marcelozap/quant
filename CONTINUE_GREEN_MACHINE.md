# Continue Green Machine / XIV

This is the restart point if the current chat is deleted. The source repository
is `https://github.com/marcelozap/quant.git`. Treat it as private: do not add
credentials, account numbers, raw broker exports, local voice notes, encrypted
databases, screenshots with sensitive information, or personal audio to Git.

## What This Project Is

Green Machine is a private Mac-only Unity world where Marcelo's trading history,
market research, and creative memory live together. It is a **memory palace,
not a dashboard**. It uses caveats instead of signals and never places orders,
creates automatic buy/sell calls, or lets personal P&L control Rosco or the
world's mood.

The Unity world is called XIV. Its first playable loop is Green Gate -> Rosco
-> NVDA history path -> Archive Garden. Keep the art warm, cinematic, original,
and accessible; do not copy Toontown or make it a cyberpunk/Roblox tech demo.

## Current Foundation

- Unity `6000.0.82f1` on Apple Silicon; open `unity/` with Unity Hub.
- Python local service in `src/quant_live/`; encrypted local storage and broker
  import logic are deliberately separate from Unity.
- Unity reads only loopback JSON from `127.0.0.1`; never put API secrets in
  Unity assets or PlayerPrefs.
- The trade-stone API endpoint is
  `GET /journal/symbol/{symbol}/trades`; it exposes only minimal descriptive
  fields. `TradeStonePath.cs` renders positive, negative, and neutral stones
  with equal visual dignity.
- Generated Unity scene/art files may be locally present but not committed. Run
  the Unity builder instead of hand-editing the generated scene.

## First Local Verification

1. Open `unity/` in Unity `6000.0.82f1` and activate Unity Personal if asked.
2. Run **XIV -> Create First Playable World**.
3. Run **XIV -> Validate First Playable World**.
4. Open `Assets/Scenes/XIVWorld.unity`, press Play, and follow
   `unity/XIV_HOME_PC_VALIDATION.md`.
5. Run Python verification from repo root: `.venv/bin/python -m pytest -q`.

## Paste This Into a New Coding Agent

```text
Continue the Green Machine / XIV project in the existing quant repository.
Read CONTINUE_GREEN_MACHINE.md, unity/XIV_PC_HANDOFF.md,
unity/XIV_HOME_PC_VALIDATION.md, green_machine/PRODUCT_PLAN.md, and
unity/FABLE_CREATIVE_BRIEF.md before changing code.

Use Unity 6000.0.82f1. Do not create a new repo or architecture. First inspect
git status: multiple agents may have intentional uncommitted changes. Preserve
them unless they directly conflict with the task; never reset, delete, or
silently revert work.

Product direction: Green Machine is a private memory palace, not a dashboard.
Build caveats instead of signals. No automated trade ideas, order placement,
cloud sync, embedded browser, or P&L-driven shame mechanics. Losses receive
equal beauty; market atmosphere reflects sourced market context only.

First target: make the first 10-minute loop beautiful and reliable: Green Gate
arrival, Rosco companion, fast travel, an NVDA trade-stone path linked to the
local loopback API, and Archive Garden daily-song/memory context. Keep data
private: Unity receives no API keys, no raw broker files, and no account IDs.

Before each meaningful edit, state the smallest verifiable outcome. Run Unity
validation and Python tests after changes. Report what changed, what was
verified, and one clear next step. Do not claim a live Schwab request, account
access, or visual behavior was tested unless it actually was.
```

## Next Practical Build Order

1. Activate Unity Personal and run the first visual walkthrough.
2. Make the Green Gate-to-NVDA route the polished first experience.
3. Connect `TradeStonePath` to the authenticated local API response.
4. Add an accessible, focused evidence panel beside the world-space view.
5. Only then expand more stock homes through data-driven prefab kits.
