# Green Machine Park

A local, playful market-research interface for the existing `quant-live` project. It is a place to make observations and retain your market thinking, not a machine for placing trades or producing unverified buy/sell calls.

## Open it

From the repository root:

```bash
python3 -m http.server 8787 --directory green_machine
```

Then open `http://localhost:8787`.

## What exists now

- A Toontown-inspired park map with keyboard walking and six research districts.
- Symbol homes for stocks such as NVDA, AMD, TSM, and AVGO.
- Persistent browser notes and a one-song-a-day ritual.
- Explicit demo data labels, so the interface never pretends static data is live.

## Next build: connect the data engine

The clean connection is to add a small local endpoint in `quant_live` that reads the latest files under `reports/watchlists/`, `reports/signal_sheets/`, and `reports/dashboard/` and exposes a safe read-only JSON payload to the park. That would replace the demo ticker and populate each stock home with the latest snapshot data.

Keep each item as an observation, evidence, or hypothesis. Do not use political/news items or generated text as automatic trade instructions.
