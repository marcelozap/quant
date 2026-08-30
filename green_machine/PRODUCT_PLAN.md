# Green Machine Park: Product Plan

## Objective

Build a private, local-first market-research world that helps Marcelo turn his own trading history, market observations, events, and music into a consistent daily practice. It should feel like an amusement park, but work like a disciplined research workstation.

Green Machine is not an automated trading system, a promise of profitable signals, or an app that invents buy/sell calls from incomplete history. Its job is to make evidence, decisions, and learning visible.

## Product Principles

1. **Personal and local first.** Trading history, Schwab credentials, account data, and notes stay on Marcelo's machine unless he explicitly chooses otherwise.
2. **Every market claim has context.** Save source, timestamp, and whether an item is a fact, an observation, or a hypothesis.
3. **No fake live data.** Every displayed value shows its source and freshness. Demo data is visibly marked as demo.
4. **No automated execution.** Green Machine can prepare research and journal reviews. It will not send orders or turn political/social posts into trade instructions.
5. **The world has a purpose.** A park location must answer a useful question or support a repeatable habit, not exist only as decoration.
6. **Build the data spine before deep 3D.** A beautiful world without trustworthy personal history will not solve the actual problem.

## Audience and Success

Primary user: Marcelo, building stronger discretionary market process and execution/data skills for a junior quantitative trader or trading-technology path.

The first successful version answers these in under one minute:

- What do I own or watch, and why?
- What changed today?
- What did I actually do and learn?
- What event or level matters next?
- Where is the evidence behind my view?

Longer-term success is not a win-rate promise. It is a complete, searchable record of decisions and a calmer, more repeatable daily review routine.

## The Park Map

| District | Research purpose | First useful interaction |
| --- | --- | --- |
| Green Gate | Daily orientation | Market weather, one priority, daily song |
| Semiconductor Speedway | Sector and stock research | Open NVDA/AMD/TSM homes; see thesis, price, event, evidence |
| Macro Mountain | Regime and calendar | Review futures, rates, FX, scheduled macro events |
| Earnings Arcade | Event preparation and review | Save expectations, key KPI, implied move, actual reaction |
| Tape Tunnel | Trading journal and execution review | Compare plan, fill, exit, and behavior patterns |
| Signal Square | News and narrative intake | Capture source, interpretation, and observable market response |
| Archive Garden | Long-term memory | Search old theses, trades, lessons, and daily songs |

## Data Architecture

```text
Schwab market data ──> Quant Live collectors ──> normalized local database ──> Green Machine API ──> Park UI
Trading exports / manual journal ────────────────> normalized local database ────────────────┘
Calendar / earnings / news links ───────────────> source records ────────────────────────────┘
```

### Data layers

1. **Raw intake**: Immutable source captures such as Schwab responses, broker trade exports, CSVs, and manually saved links.
2. **Normalized local database**: SQLite first. It is private, easy to back up, and sufficient for one person. This becomes the source of truth instead of scattered JSON and browser storage.
3. **Research layer**: Symbols, watchlists, theses, events, notes, sources, tags, and daily reviews.
4. **Analytics layer**: Time-of-day patterns, setup summaries, hold time, realized results, execution metrics, review completion, and data quality flags.
5. **Presentation layer**: A local API feeds the park, tables, charts, journal, and eventually 3D scenes.

### Minimum trade-history record

The project cannot honestly generate useful insight until a trade record has enough context. Each imported or manually entered trade should preserve:

- `trade_id`, account alias, symbol, asset class, side, quantity
- order time, fill time, exit time, prices, fees, realized result
- setup name, timeframe, intended entry, risk level, planned exit
- market regime, catalyst/event, thesis, confidence
- source/import batch, data-quality status
- post-trade note: strength, mistake, lesson

The app must never overwrite original broker fields. Enrichment fields stay separate and editable.

## Delivery Phases

### Phase 0: Product and data audit

**Goal:** Define what exists, where it lives, and what can be trusted.

- Inventory available trading history, exports, notes, screenshots, and existing `reports/` data.
- Define the data dictionary and a private backup policy.
- Identify which source can provide earnings/calendar/news data and what its license or API limits are.
- Decide the initial universe: start with equities and semiconductors; add futures/FX only when their data is ready.
- Turn the current static park prototype into a tracked design reference, not a data product yet.

**Done when:** We have a written data inventory, a field dictionary, three example trade records, and no secrets in application files.

### Phase 1: Trading History Foundation

**Goal:** Make the raw history usable, trustworthy, and searchable.

- Add a local SQLite schema and migrations.
- Build an import preview for CSV/broker exports with column mapping and validation.
- Preserve raw import files; reject or flag duplicates and missing dates/prices.
- Build a journal form for adding setup, thesis, execution, and review fields.
- Add a simple data-quality dashboard: number of trades, unknown setups, missing exits, missing notes.

**Done when:** A real history export can be imported repeatedly without corrupting data and the user can find any trade by date, symbol, or setup.

### Phase 2: Research Workstation

**Goal:** Connect the existing Quant Live data engine to clear daily research.

- Replace static park quotes with a read-only local API backed by latest `reports/watchlists/` snapshots.
- Add symbol pages: snapshot, source/time, thesis, levels, catalysts, earnings/events, related notes.
- Add daily dashboard: market weather, watchlist changes, planned events, open questions, nightly review prompt.
- Add research capture: link/headline, source, timestamp, tags, interpretation, follow-up question.
- Treat political figures and social posts as sourced context only. Display original-source link and timestamp, never inferred trade action.

**Done when:** The user can open NVDA and see the current sourced snapshot plus their own view and next event in one screen.

### Phase 3: Analytics and Learning Loop

**Goal:** Discover patterns in the user's process without pretending correlation is a strategy.

- Calculate trade and journal summaries by setup, symbol, time of day, hold period, and market regime.
- Add execution analytics: planned versus actual entry, fill quality, adverse excursion when data supports it, and behavior tags.
- Create observation cards that cite the sample size and data-quality caveat.
- Add weekly review: three strengths, three recurring issues, and questions to test next week.
- Keep generated output in the form of hypotheses, for example: "Your 18 sample trades in X after 2pm had worse average result; inspect whether this is a time, setup, or market-regime effect."

**Done when:** Green Machine produces sourced observations from history and every observation links back to the trades behind it.

### Phase 4: World and Interaction Design

**Goal:** Make the research workflow emotionally engaging without making it harder to use.

- Establish art direction, avatar style, park map, accessibility contrast, motion settings, and keyboard-first navigation.
- Build the 2D/2.5D park as the dependable navigation shell.
- Add animated district entrances, a visible daily change log, and collectible-style research cards.
- Prototype one 3D district using Three.js or React Three Fiber after the underlying view has clear data and navigation requirements.
- Test performance on the actual computer and provide a reduced-motion/low-graphics option.

**Done when:** A user can navigate from map to an NVDA thesis, daily note, or journal review faster than through a normal sidebar.

### Phase 5: Personal Operating System

**Goal:** Turn the app into an enduring daily routine.

- Morning: market weather, calendar, watchlist focus, one question.
- During market: quick observation capture and trade journal events.
- Evening: compare thesis to outcome, complete a short review, choose one song.
- Weekly: archive good lessons and select one process experiment.
- Backups, export, versioned schema, and a clear "what changed today" log.

**Done when:** Green Machine supports the routine for four consecutive weeks with reliable data and no reliance on memory alone.

## Technical Direction

- **Application:** local React + TypeScript frontend with a small local Python API, keeping the existing `quant_live` Python work useful.
- **Storage:** SQLite, with raw files retained in a private `data/raw/` directory excluded from Git.
- **Charts:** straightforward web charts for accuracy and speed; world visuals are a navigation layer, not chart replacements.
- **3D:** Three.js / React Three Fiber only after the 2D data model and one district workflow are proven.
- **Deployment:** run locally first. Packaging as a desktop app is a later decision, not a dependency for building the core.
- **Secrets:** `.env` only; no keys, account numbers, raw account snapshots, or personal trade history committed to Git.

## Current Status

The repository currently has:

- Quant Live Python collectors for Schwab quotes, watchlist snapshots, daily reports, signal sheets, and a basic TCA-style execution report.
- A sample execution blotter and structured report folders.
- A new static `green_machine/` park prototype with demo data, navigation, browser-local notes, and a daily-song prompt.

The prototype is a design artifact only. It is not connected to live data, contains no database, and is not the foundation for the production data model.

## Immediate Next Work

1. Perform Phase 0 data inventory: identify actual trade-history files and their columns without moving or editing them.
2. Write the SQLite schema and import contract from the real export shape.
3. Build the importer preview and data-quality checks.
4. Only then replace demo data in Green Machine with a read-only local data endpoint.

## Decisions We Are Deliberately Deferring

- Automatic signal generation or trade recommendations.
- Order placement, account actions, or any automated execution.
- Cloud sync, public hosting, or third-party sharing of private trading history.
- Multiple asset classes beyond equities until import and data quality are solid.
- Full 3D park production before one district has a validated daily use case.
