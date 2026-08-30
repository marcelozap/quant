# Green Machine

Local market-data, research, and execution-review software for learning how decisions hold up under real evidence.

Green Machine is not an automated trading system, a signal generator, or a promise of profitable calls. It is the market/data lane inside XIV: a private tool for making research, trade history, execution quality, and review visible.

## Target role

This project is now explicitly aimed at roles like Franklin Templeton's `Junior Quantitative Trader`:

- execution and workflow oriented, not academic-model oriented
- focused on equities, FX, cash, and real trading outcomes
- useful for learning market structure, trading venues, slippage, and best execution
- built around Python, data analysis, automation, and recurring desk reporting

If you want to become better at trading by understanding how fills, latency, liquidity, workflow, and controls affect outcomes, this is the lane.

## What it does

- reads credentials and endpoint settings from environment variables
- fetches quotes
- polls quotes in batches so one call can cover more symbols
- fetches account-number mappings and account snapshots
- fetches basic price history
- throttles this project's calls through a shared local state file so multiple apps can coordinate
- backs off and retries on 429 rate-limit responses
- writes a daily markdown recap so you can review what you actually did and learned
- captures research watchlist snapshots with a compact cross-sectional summary
- compares the last two watchlist snapshots so you can see how the basket evolved
- builds a nightly signal sheet across watchlists so you can review the whole board
- exports CSV alongside JSON snapshots so you can analyze data outside the CLI
- includes built-in watchlist templates for common baskets
- writes a simple markdown dashboard from the latest research outputs
- assembles a nightly end-of-day bundle so the key files live in one place
- exports simple HTML versions of snapshots, signal sheets, and dashboards
- lets you tune watchlist scoring weights from env vars
- adds a history sheet so you can see which watchlists stayed important over several days
- runs the full nightly research flow in one command for selected templates
- analyzes execution blotters with a desk-style TCA report focused on slippage and venue quality
- keeps the auth path simple so you can plug in your linked Schwab app safely

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install .
cp .env.example .env
```

Load your environment variables however you prefer, then run:

```bash
quant-live quote AAPL MSFT
quant-live poll-quotes AAPL MSFT NVDA SPY --batch-size 2 --interval-seconds 5 --rounds 3
quant-live account-numbers
quant-live accounts
quant-live price-history AAPL --period-type day --period 5
quant-live rate-limit
quant-live daily-readme
quant-live watchlist-snapshot semis NVDA AMD TSM AVGO --print-summary
quant-live compare-watchlist semis
quant-live signal-sheet semis indexes megacap --print-summary
quant-live list-templates
quant-live template-snapshot semis --print-summary
quant-live dashboard --print-summary
quant-live end-of-day-bundle
quant-live history-sheet --lookback 5 --print-summary
quant-live tca-report data/sample_execution_blotter.csv --name sample_desk_day --print-summary
quant-live research-pack semis indexes megacap
```

## XIV World and Green Machine

XIV is the private Unity world built around walking Rosco. MaloSound is its music and creative-technology lane. Green Machine is the local market/data lane that supplies research, trade journaling, backtesting, and descriptive review.

The Unity 6 LTS world scaffold and its 12-month build contract live in [`unity/`](./unity/) and [`unity/XIV_WORLD_PLAN.md`](./unity/XIV_WORLD_PLAN.md). The core walk remains useful with the data service turned off.

## Green Machine Foundation

The Unity park and its local data service live in this repository. The Python side is deliberately local-only and will not place orders or transmit your history to third parties.

```bash
# Install runtime and test tooling. The existing virtualenv uses an older pip,
# so use a normal local install rather than editable mode.
.venv/bin/pip install .[dev]

# SQLCipher is required before encrypted Green Machine storage can initialize.
.venv/bin/pip install .[green-machine-secure-store]

# Read only filenames, paths, extensions, size, and modified timestamps.
quant-live green-machine-inventory

# Validate a selected export before storing anything.
quant-live green-machine-preview-import /path/to/clean_trades.csv

# Encrypt the selected export and import its normalized trade records.
quant-live green-machine-import-trades /path/to/clean_trades.csv

# Produce descriptive review analytics from encrypted closed-trade history.
quant-live green-machine-analytics

# Initialize encrypted storage, then start the Unity-facing local API.
export GREEN_MACHINE_API_TOKEN="use-a-long-private-random-token"
quant-live green-machine-init
quant-live green-machine-serve
```

The service binds only to `127.0.0.1:8788`. Unity must pass the same local token in the `X-Green-Machine-Token` header; never save that token in a committed Unity asset. See [unity/README.md](/Users/a14/Documents/quant/unity/README.md) for the full park prototype scaffold.

## First workflow for this role

If your goal is execution-focused quant trading, start here:

```bash
quant-live quote SPY
quant-live template-snapshot indexes --print-summary
quant-live template-snapshot semis --print-summary
quant-live signal-sheet indexes semis megacap --print-summary
quant-live tca-report data/sample_execution_blotter.csv --name sample_desk_day --print-summary
```

That combination trains the right instincts:

- what the tape and cross-section look like
- which groups are active or dispersing
- how to talk about execution quality
- how to summarize slippage and venue behavior like a desk-facing analyst

## Environment

Required now:

- `SCHWAB_ACCESS_TOKEN`

Usually useful:

- `SCHWAB_API_BASE_URL`
- `SCHWAB_MARKETDATA_BASE_URL`
- `SCHWAB_TRADER_BASE_URL`
- `SCHWAB_ACCOUNT_HASH`
- `SCHWAB_RATE_LIMIT_PER_MINUTE`
- `SCHWAB_RESERVE_CALLS_PER_MINUTE`
- `SCHWAB_RATE_LIMIT_STATE_PATH`
- `SCHWAB_MAX_RETRIES`
- `SCHWAB_BACKOFF_SECONDS`
- `SCHWAB_QUOTE_BATCH_SIZE`
- `QUANT_LIVE_ACTIVITY_LOG_PATH`
- `QUANT_LIVE_DAILY_README_DIR`
- `QUANT_LIVE_RESEARCH_SNAPSHOT_DIR`
- `QUANT_LIVE_SIGNAL_SHEET_DIR`
- `QUANT_LIVE_DASHBOARD_DIR`
- `QUANT_LIVE_END_OF_DAY_BUNDLE_DIR`
- `QUANT_LIVE_HTML_EXPORT_DIR`
- `QUANT_LIVE_SCORE_AVERAGE_WEIGHT`
- `QUANT_LIVE_SCORE_DISPERSION_WEIGHT`
- `QUANT_LIVE_HISTORY_DIR`
- `QUANT_LIVE_EXECUTION_REPORT_DIR`

Optional refresh support:

- `SCHWAB_APP_KEY`
- `SCHWAB_APP_SECRET`
- `SCHWAB_REFRESH_TOKEN`
- `SCHWAB_TOKEN_URL`

## Notes

- The default path layout in this starter follows common Schwab Trader API conventions.
- If your Schwab app uses a different host or path, override the base URLs in the environment instead of editing code.
- This project does not store secrets on disk beyond whatever you place in your own environment files.
- By default this project assumes a 60 call/minute ceiling and reserves 20 calls/minute for your other apps, so its own effective cap is 40 calls/minute unless you override it.
- Cross-project coordination works when your local Schwab apps point at the same `SCHWAB_RATE_LIMIT_STATE_PATH`.
- Quote polling is most quota-efficient when you batch symbols instead of polling each symbol separately.
- `quant-live daily-readme` writes a nightly recap to `reports/daily/YYYY-MM-DD.md` by default, based on the commands you ran locally.
- `quant-live watchlist-snapshot` writes timestamped JSON snapshots under `reports/watchlists/` so you can compare watchlists over time.
- `quant-live compare-watchlist <name>` compares the last two snapshots for that watchlist and highlights the biggest changes.
- `quant-live signal-sheet` writes a nightly markdown board under `reports/signal_sheets/` from the latest snapshot of each watchlist.
- `quant-live watchlist-snapshot` now writes both JSON and CSV files for each capture.
- `quant-live template-snapshot <template>` uses a built-in watchlist like `semis`, `indexes`, or `megacap`.
- `quant-live dashboard` writes a single markdown page under `reports/dashboard/` with the latest nightly research view.
- `quant-live end-of-day-bundle` writes a dated folder with a manifest pointing at the day’s key research files.
- HTML exports are written under `reports/html/` so you can open the latest research outputs in a browser.
- `quant-live history-sheet` reads recent signal sheets and highlights which watchlists have stayed elevated across days.
- `quant-live research-pack ...` captures template snapshots, then writes the signal sheet, dashboard, daily readme, history sheet, and end-of-day bundle in one pass.
- `quant-live tca-report ...` reads a CSV or JSON execution blotter and writes a markdown, JSON, and HTML execution report under `reports/execution/`.

## Why this matches the target role

- `Trading & Execution Support`: live quote pulls, watchlists, and execution-style reporting keep the repo tied to market conditions and desk review.
- `Algorithm & Performance Analysis`: slippage summaries, symbol/venue breakdowns, and nightly sheets train you to discuss performance drivers, not just PnL.
- `Workflow & Data Engineering`: batch polling, file outputs, HTML export, shared rate-limits, and automation commands show practical workflow design.
- `Risk & Controls`: daily readmes, history sheets, and end-of-day bundles reinforce repeatable process and operational discipline.

## Sample execution input

A sample blotter is included at [data/sample_execution_blotter.csv](/Users/a14/Documents/quant/data/sample_execution_blotter.csv:1) so you can run the TCA flow immediately.
