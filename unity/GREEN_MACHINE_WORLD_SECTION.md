# Green Machine — XIV World Section

**Status:** design document. No Unity scene, script, or asset changed by this file.
**Repo:** `quant` · **Folder:** `unity/` · **Unity:** 6000.0.82f1
**Written:** 2026-08-30

Green Machine becomes the largest interactive section of the XIV world: a
walkable, local-first **research and risk-review lab**. It is not a trading
system, not a dashboard, and not a live market app.

It inherits the XIV direction unchanged — warm, cinematic, personal, an original
animated adventure world. Marcelo and Rosco stay central. Walking stays the core
loop. Green Machine gives the walk more meaning; it never replaces it.

---

## 1. What already exists (do not rebuild)

The world already has eight authored landmarks, and **six of them are already
Green Machine spaces**. Green Machine is not being added — it is being named,
connected, and finished.

| Existing landmark | World Plan role | Becomes |
|---|---|---|
| **Green Gate** | home entrance, daily orientation | **Green Gate** (unchanged) |
| **Signal Square** | sourced information, questions to investigate | **Evidence Trail** — head |
| **Earnings Arcade** | contained event-review space | **Evidence Trail** — research cards |
| **Semiconductor Speedway** | bright kinetic technology and systems | **Evidence Trail** — sector reads |
| **Macro Mountain** | slower overlook, long-range context | **Market Weather** overlook |
| **Account Observatory** | read-only personal review, never order placement | **Risk Wall** — account-state gates |
| **Tape Tunnel** | execution history and market memory | **Receipt Ledger** |
| **Archive Garden** | songs, memories, projects, personal context | **Archive Garden** (unchanged) |

**Only one structure is genuinely new: the Risk Wall itself.**

### Why the landmark names stay

`Assets/Editor/XIVWorldValidator.cs` hard-codes all eight names and asserts
`GameObject.Find(landmark) != null`. `GreenMachineParkBuilder.cs` positions them
by name at lines 20–27 and branches on them at 241–256, 985–1044. Renaming
breaks the 55/55 validator and the builder in the same commit.

The safe-language rename table in §6 applies to **signs, kiosks, prompts, and UI
copy** — the words the player reads. Landmark object names are internal
identifiers and stay as they are. Same lesson as `gatekpt`: an identifier baked
into a validator is expensive to rename; the display string is free.

---

## 2. Safe world-space diagram

```text
                          ┌───────────────────────┐
                          │    MACRO MOUNTAIN     │
                          │    Market Weather     │
                          │  conditions · context │
                          │  NO-TRADE DAY sign    │
                          └───────────┬───────────┘
                                      │ overlook, read from below
                                      │
   ┌──────────────┐          ┌────────▼─────────┐         ┌──────────────────┐
   │  GREEN GATE  │          │  SIGNAL SQUARE   │         │ EARNINGS ARCADE  │
   │              │  walk    │  Evidence Trail  │  walk   │  Research Cards  │
   │ Daily        ├─────────▶│  head            ├────────▶│  event review    │
   │ Snapshot     │          │  sources · asks  │         │  assumptions     │
   │ Station      │          │  UNKNOWN markers │         │  caveats         │
   │ Beginner     │          └────────┬─────────┘         └────────┬─────────┘
   │ lesson       │                   │                            │
   │ Paper-       │          ┌────────▼─────────┐                  │
   │ practice     │          │  SEMICONDUCTOR   │                  │
   │ idea         │          │  SPEEDWAY        │                  │
   └──────┬───────┘          │  sector reads    │                  │
          │                  └────────┬─────────┘                  │
          │                           │                            │
          │                           └──────────┬─────────────────┘
          │                                      │
          │                       ╔══════════════▼══════════════╗
          │                       ║        RISK WALL            ║   ◀── NEW
          │                       ║  stale data · spread ·      ║
          │                       ║  concentration · drawdown · ║
          │                       ║  body state                 ║
          │                       ║                             ║
          │                       ║  FAILED GATE = NO PAYLOAD   ║
          │                       ╚══════════════╦══════════════╝
          │                          pass only   ║
          │                                      ▼
          │              ┌───────────────────────────────────────┐
          │              │           TAPE TUNNEL                 │
          │              │           Receipt Ledger              │
          │              │  signed receipts · before/after reads  │
          │              │  proof manifests · journal coverage    │
          │              └───────────────────┬───────────────────┘
          │                                  │
          │              ┌───────────────────▼───────────────────┐
          │              │        ACCOUNT OBSERVATORY            │
          │              │        Risk Wall — account state      │
          │              │  READ-ONLY · never order placement    │
          │              └───────────────────┬───────────────────┘
          │                                  │
          │              ┌───────────────────▼───────────────────┐
          └─────────────▶│          ARCHIVE GARDEN               │
                         │  completed reviews · lessons learned   │
                         │  resolved reads · calm replay          │
                         │  walk saved · welcome back             │
                         └───────────────────────────────────────┘

   ROSCO walks the whole route. He is a guide and a grounding companion.
   He routes back to evidence, receipts, or a pause — never to a decision.
```

**Read the shape:** everything flows toward the Risk Wall, and only what passes
continues to the Receipt Ledger. There is no path from Evidence Trail to Receipt
Ledger that bypasses the wall. The geometry *is* the fail-closed rule.

---

## 3. Local-only data boundary

```text
  ┌──────────────────────────────────────────────────────────────┐
  │  UNITY WORLD                                                  │
  │  renders · proposes review intent · never executes            │
  │                                                               │
  │  READS   local JSON written by quant-live (file-first)        │
  │  READS   loopback API 127.0.0.1:8788 (optional, read-only)    │
  │  WRITES  its own saves, walk history, atmosphere state        │
  └────────────────────────────┬─────────────────────────────────┘
                               │ read-only
  ┌────────────────────────────▼─────────────────────────────────┐
  │  GREEN MACHINE  (src/quant_live/)                            │
  │  green-machine-serve  — loopback-only API, by design          │
  │  green-machine-init   — encrypted local storage               │
  │  research-pack · signal-sheet · end-of-day-bundle             │
  └────────────────────────────┬─────────────────────────────────┘
                               │
  ┌────────────────────────────▼─────────────────────────────────┐
  │  LOCAL DISK ONLY                                              │
  │  encrypted trade history · account snapshots · tokens in env  │
  │  NEVER in Unity assets, scenes, builds, screenshots, commits   │
  └──────────────────────────────────────────────────────────────┘
```

### Rules

1. **File-first.** Green Machine writes JSON artifacts to disk; the world reads
   files. The loopback API is an *optional accelerator*, never a requirement.
   **The world must be fully walkable and readable with the service stopped.**
2. **Loopback only.** `green-machine-serve` is documented loopback-only. The
   world never contacts a non-`127.0.0.1` host.
3. **Read-only.** The world issues no write, no order, no POST. Ever.
4. **Missing data is `UNKNOWN`.** Never `0`, never blank, never a stale value
   presented as current. `UNKNOWN` is a first-class rendered state with its own
   sign material.
5. **Tokens live in the environment.** `GREEN_MACHINE_API_TOKEN` is read at
   runtime from the environment and never serialized into a scene or asset.
6. **Encrypted at rest.** Trade history goes through `green-machine-init`
   encrypted storage. The world reads summaries, not raw account records.

### Python / Unity handshake

- Unity writes review intents to `unity/LocalState/xiv_intents.jsonl`.
- Python reads intents from `unity/LocalState/xiv_intents.jsonl`.
- Python writes sanitized receipts to `unity/LocalState/receipts.jsonl`.
- Python may write sanitized `unity/LocalState/xiv_state.json`.
- Unity reads `unity/LocalState/receipts.jsonl` and sanitized state summaries.
- Unity never reads private account data.
- Python never touches scenes, builds, assets.
- There are no shared writes; each side owns its own local files.

### Three findings to fix before Green Machine expands

Reported from a read of `Assets/Scripts/Data/LocalApiClient.cs`:

| # | Finding | Risk | Fix |
|---|---|---|---|
| 1 | `OpenSource(string url)` calls `Application.OpenURL` on **any absolute URI** | A payload-supplied URL can send the player out of the local world. This is the one real egress path. | Allowlist schemes, or delete the method. The world has no need to open external URLs. |
| 2 | `baseUrl` is a `[SerializeField]` defaulting to `127.0.0.1:8788` | Editable to a non-loopback host in the inspector | Hard-assert loopback at runtime; refuse and show `UNKNOWN` otherwise |
| 3 | `/journal/symbol/{symbol}/trades` returns trade journal rows over HTTP | Real account data crossing a transport when a file read would do | Prefer a written artifact; keep the endpoint read-only and loopback-asserted |

`XIVAudioAtmosphere.cs:229` also uses `UnityWebRequest`, but with
`new Uri(path).AbsoluteUri` behind a `File.Exists` guard — that is `file://`
scheme, local, and **benign. No action.**

---

## 4. Scene objects and interactions

All new objects are created by `GreenMachineParkBuilder`. **The scene is
generated — never hand-edit or commit `Assets/Scenes/XIVWorld.unity`.**

| Object | Type | Interaction | Reads |
|---|---|---|---|
| `Daily Snapshot Station` | kiosk, Green Gate | `E` — today's snapshot, or `UNKNOWN` | daily-review JSON |
| `Market Weather Vane` | Macro Mountain | ambient; wind/light shift by condition | dashboard JSON |
| `No-Trade Day Sign` | Macro Mountain | ambient, unmissable when raised | conditions JSON |
| `Beginner Lesson Post` | Green Gate | `E` — one authored lesson | static authored text |
| `Paper Practice Board` | Green Gate | `E` — one paper-practice idea, clearly labelled | template list |
| `Research Card Rack` | Earnings Arcade | `E` — read one card | signal-sheet JSON |
| `Assumption Stones` | Evidence Trail | `E` — the assumption behind a card | research-pack JSON |
| `Caveat Lantern` | Evidence Trail | lit when backtest/replay caveats apply | history-sheet JSON |
| `Unknown Marker` | anywhere | grey, unlit, explicit | absence of data |
| `Risk Wall Gate` ×5 | **new structure** | walk up; each gate lit or barred with its name | computed locally |
| `Payload Gate` | Risk Wall exit | **barred unless all five pass** | computed locally |
| `Receipt Plinth` | Tape Tunnel | `E` — one signed receipt, hash visible | receipt JSONL |
| `Proof Manifest Case` | Tape Tunnel | `E` — bundle manifest | end-of-day-bundle |
| `Journal Coverage Meter` | Tape Tunnel | ambient fill, honest gaps shown as gaps | daily-readme |
| `Resolved Read Bed` | Archive Garden | `E` — a closed, resolved read | analytics JSON |
| `Lesson Plaque` | Archive Garden | `E` — lesson learned, past tense | archive.json |
| `Rosco` | existing | `F` wait · `R` recall · greet/follow/investigate | — |

### Risk Wall — the one new structure

Five gates in a row, each a physical arch the player walks through. A failed
gate is **visibly barred**, carries its own name, and states its reason in plain
language. The sixth arch — the Payload Gate — stays barred unless all five are
lit.

| Gate | Passes when | Barred sign reads |
|---|---|---|
| Stale Data | newest snapshot within threshold | `STALE DATA — SNAPSHOT IS <age> OLD` |
| Abnormal Spread | spread within normal band | `ABNORMAL SPREAD — REVIEW ONLY` |
| Concentration | no position over limit | `CONCENTRATION LIMIT — REVIEW ONLY` |
| Drawdown | drawdown within guard | `DRAWDOWN GUARD ACTIVE` |
| Body State | rested / logged | `BODY STATE — COME BACK LATER` |

**A barred gate produces no execution payload, and the world says so.** That is
the same fail-closed rule the orchestrator runs on, rendered as architecture a
person can walk into.

---

## 5. Command → kiosk mapping

Every kiosk is fed by a **real existing `quant-live` subcommand**. Nothing here
is invented.

| `quant-live` command | Writes | Kiosk | World space |
|---|---|---|---|
| `green-machine-daily-review` | daily review + song | Daily Snapshot Station | Green Gate |
| `dashboard` | markdown dashboard | Market Weather Vane | Macro Mountain |
| `list-templates` | template list | Paper Practice Board | Green Gate |
| `template-snapshot` | watchlist snapshot | Snapshot capture | Green Gate |
| `watchlist-snapshot` | snapshot + summary | Snapshot capture | Green Gate |
| `signal-sheet` | nightly sheet | **Research Card Rack** | Earnings Arcade |
| `research-pack` | nightly pipeline | Assumption Stones | Evidence Trail |
| `compare-watchlist` | last-two diff | Before/After reads | Evidence Trail |
| `history-sheet` | multi-day leadership | Caveat Lantern | Evidence Trail |
| `price-history` | OHLC series | Replay caveats | Speedway |
| `quote` / `poll-quotes` | quotes | Spread gate input | Risk Wall |
| `accounts` | positions (read-only) | Concentration gate | Account Observatory |
| `green-machine-analytics` | closed-trade summary | Drawdown gate · Resolved Read Bed | Risk Wall · Archive |
| `rate-limit` | budget | Wall throughput lamp | Risk Wall |
| `tca-report` | **Simulation Recorder** report | Receipt Plinth | Tape Tunnel |
| `end-of-day-bundle` | nightly artifact folder | Proof Manifest Case | Tape Tunnel |
| `daily-readme` | markdown recap | Journal Coverage Meter | Tape Tunnel |
| `green-machine-serve` | loopback API | optional accelerator for all | — |

**Never surfaced in the world:** `refresh-token`, `account-numbers`,
`green-machine-import-trades`, `green-machine-preview-import`,
`green-machine-init`. These touch credentials or raw private records. They are
terminal-only, forever.

---

## 6. Safe language — signs and UI

Applies to every string a player reads. Enforce in review; a Unity string test is
listed in §8.

### Required in-world boundary text

These four lines must appear in the Green Machine section as signs, kiosk
footers, or Receipt Ledger helper text:

```text
System proposes; never executes trades.
Educational research only.
Missing data stays UNKNOWN.
Failed gate means no execution payload.
```

| Never write | Always write |
|---|---|
| Execution Agent | **Simulation Recorder** |
| Trading Signal | **Research Card** |
| Auto Execution | **Auto Review** |
| Proceed | **Paper Review Ready** |
| Target Price | **Scenario Level** |
| P&L | **Simulated Outcome** / **Replay Outcome** |
| Buy / Sell | **Scenario A** / **Scenario B** |
| Trade Alert | **Review Prompt** |

### Standing sign text

**Green Gate arrival board**
> GREEN MACHINE — RESEARCH AND REVIEW
> This is a review lab. Nothing here places an order.
> No advice. No recommendations. No live calls.

**Risk Wall, at every barred gate**
> GATE BARRED — NO EXECUTION PAYLOAD
> This is a review stop, not a signal.

**Receipt Ledger entry**
> RECEIPTS RECORD WHAT WAS REVIEWED.
> They are not performance claims.

**Research Card Rack**
> RESEARCH CARDS ARE QUESTIONS, NOT ANSWERS.
> Scenario levels are for review only.

**Simulated Outcome, everywhere it appears**
> SIMULATED / REPLAY ONLY — NOT A RESULT.

### Rosco's boundaries

Rosco routes the player back to **evidence, receipts, or a pause**. He has three
authored responses and no others:

- *"Let's go look at what we actually recorded."* → Receipt Ledger
- *"Where did that come from?"* → Evidence Trail
- *"Let's sit down for a minute."* → pause / Archive Garden

Rosco never mentions a symbol, a price, a direction, or a market view. He never
gives financial advice, live calls, or trade suggestions. When data is `UNKNOWN`
he says so and walks to the Archive Garden.

---

## 7. Roadmap

### Phase A — Name and sign (no new geometry)
Apply §6 language to existing signs and kiosks. Add `UNKNOWN` as a rendered
state with its own material. Fix the three §3 findings, starting with
`OpenSource`. **Validator must stay 55/55.**

### Phase B — Evidence Trail
Connect Signal Square → Earnings Arcade → Speedway as one readable trail.
Research Card Rack, Assumption Stones, Caveat Lantern, reading from
`signal-sheet` / `research-pack` / `history-sheet` artifacts on disk.

### Phase C — Risk Wall *(the largest single build)*
Five gate arches plus the Payload Gate. Gate state computed locally from
snapshot age, spread, positions, drawdown, body state. Barred gates visibly
barred, each naming its own reason.

### Phase D — Receipt Ledger
Tape Tunnel becomes walkable. Receipt Plinths carry real hashes. Proof Manifest
Case reads `end-of-day-bundle`. Journal Coverage Meter shows gaps honestly.

### Phase E — Archive Garden depth
Resolved Read Beds and Lesson Plaques. Calm replay of what happened, past tense
only. No re-litigating, no scoring.

### Phase F — Market Weather + no-trade day
Macro Mountain drives ambient light, wind, and route mood. The No-Trade Day sign
is unmissable from Green Gate.

**Ordering rule:** Phase A ships before any new geometry. Unsafe language in a
world that has grown larger is harder to remove than unsafe language in a world
that has not.

---

## 8. Validation checklist

**Unity is not installed on the machine where this document was written.** These
were not run. Run them on the PC with Unity 6000.0.82f1.

### Editor
- [ ] **XIV → Create First Playable World** completes with no errors
- [ ] **XIV → Validate First Playable World** reports **55/55** (no regression)
- [ ] All eight landmark `GameObject.Find` checks still pass
- [ ] `ProjectSettings.asset` `activeInputHandler` is still `1`
- [ ] Rosco's `NavMeshAgent` still serialized **disabled**
- [ ] New Blender materials keep a name substring `RebindImportedMaterials` matches
      (Pine, Signal Lime, Coral, Gold, Cream, Grass, Wood, Gate Stone, Arrival
      Brick, Patina Copper, Parchment, Lantern) — otherwise silent dark-teal fallback

### Runtime
- [ ] Console prints `XIV runtime ready` with all seven flags `true`
- [ ] Full walk Green Gate → Archive Garden completes; walk count saves
- [ ] `F` wait, `R` recall, `E` interact, `Esc` pause all still work
- [ ] No magenta, no blown-out lighting, no NavMesh agent errors
- [ ] Billboards readable, not mirrored

### Green Machine safety
- [ ] **Stop `green-machine-serve`. The world still walks and reads.** Every
      Green Machine kiosk shows `UNKNOWN`, not `0` and not blank
- [ ] No kiosk, sign, or prompt contains any left-column word from §6
- [ ] Every barred Risk Wall gate names its own reason and produces no payload
- [ ] Payload Gate is barred whenever any of the five gates is barred
- [ ] `Application.OpenURL` reachable only via an allowlisted scheme, or removed
- [ ] `baseUrl` refuses non-loopback at runtime
- [ ] No API token, trade history, or private source data in any scene or asset
- [ ] Atmosphere save contains only time-of-day state
- [ ] Rosco produces no symbol, price, direction, or market view in any line

### Doc/repo checks (runnable without Unity)
- [ ] `git status` clean except intended files
- [ ] No private market data or tokens staged
- [ ] `grep -rIn "Buy\|Sell\|P&L\|Trade Alert\|Target Price" unity/Assets --include=*.cs` returns only §6-compliant usages

---

## 9. Prototype vs real vs roadmap

| Layer | Status |
|---|---|
| Green Gate, Archive Garden, 6 further landmarks | **Real.** Built, 55/55, macOS build succeeded |
| Marcelo, Rosco, camera, NavMesh, walk save, welcome-back | **Real.** Runtime smoke test passed on laptop |
| Authored FBX art (`GreenGate.fbx` v2, `MarceloHero.fbx`) | **Real.** Generated headless from Blender sources |
| Audio atmosphere + `AudioAnalysisV1` beat grid | **Real.** Local files only |
| `quant-live` command surface in §5 | **Real.** Every command exists today |
| `green-machine-serve` loopback API + encrypted storage | **Real.** Documented loopback-only |
| `LocalApiClient` / `GreenMachineBoard` wiring | **Prototype.** Works; carries the three §3 findings |
| Evidence Trail, Risk Wall, Receipt Ledger, kiosks | **Roadmap.** Nothing built. Phases B–D |
| Market Weather driving light and wind | **Roadmap.** Phase F |
| Body-state gate | **Roadmap.** Needs a local personal-state source first |

**Not claimed anywhere:** live trading, broker automation, autonomous execution,
copy-trading, investment advice, guaranteed returns, account sizing, model
training, cloud services, or outside users. None of it exists and none of it is
planned.

---

## 10. Open decisions

1. **Risk Wall placement.** The diagram puts it between Evidence Trail and Tape
   Tunnel. It could instead sit at Account Observatory, reusing an existing
   landmark and adding no geometry — cheaper, but the wall stops being something
   you physically walk through, which is most of its value.
2. **Should `OpenSource` be deleted outright?** Recommendation: yes. The world
   has no reason to open an external URL, and deleting it removes the egress
   path instead of guarding it.
3. **`green_machine/` at repo root** (`app.js`, `index.html`, `styles.css`) is a
   separate browser surface. Confirm whether it stays as a prototype or folds
   into the world — two surfaces drift.

---

*XIV is the world and the parent system. Green Machine is its largest section, a
research and risk-review lab. MaloSound is a separate creative proof lane. All
data local, always.*
