# XIV Unity and Green Machine Repo Coordination

**Status:** coordination contract.
**Repo:** `quant`
**Last updated:** 2026-08-30

This repo currently contains both the Unity world and the Green Machine local
research tooling. Treat `unity/GREEN_MACHINE_DATA_CONTRACT.md` as the interface
between them.

## Ownership Boundaries

| Area | Owner | Notes |
|---|---|---|
| `unity/Assets/` | Unity world work | Do not commit generated scenes, Library, builds, saves, audio, or private data. |
| `unity/LocalState/` | local runtime only | Ignored by Git. Contains receipts, intents, state export, local Rosco overrides, and evidence cards. |
| `unity/Examples/` | shared examples | Tracked, safe, redacted examples only. |
| `src/quant_live/` | Green Machine tooling | Market/research commands and local summaries. No Unity scene writes. |
| `data/` | existing repo sample data | Keep public and redacted. Do not place private runtime state here. |
| `green_machine/` | web/demo surface | Not the main Unity product. Do not build a parallel Flask trading app as the main path. |

## Parallel Work Rule

Parallel work is safe only when both sides respect file ownership:

- Unity writes intents only.
- XIV/runner writes signed receipts and exported world state.
- Green Machine tooling writes evidence and research artifacts.
- Humans edit config and approve actions.

No two systems should write the same JSONL file.

## Branching and Review

- Keep generated Unity files out of commits.
- Commit documentation and source code only after local checks pass.
- If a change touches both `unity/Assets/` and `src/quant_live/`, include a note
  explaining which data-contract field connects them.
- If a file appears that contains tokens, private account data, raw trade
  history, or local audio, stop and remove it from the commit plan.

## Daily Sync Checklist

1. `git status --short --branch`
2. Read `unity/XIV_PC_HANDOFF.md`
3. Read `unity/XIV_HOME_PC_VALIDATION.md`
4. Check `unity/GREEN_MACHINE_DATA_CONTRACT.md` before adding integration code
5. Run available non-secret checks
6. Report changed files and validation results before committing

## Current Integration Priority

1. Keep the warm Marcelo and Rosco walking-world direction intact.
2. Use Green Machine as a research and risk-review world section.
3. Build read direction first: receipts and exported state into Unity.
4. Add intent writing only after read-only rendering is stable.
5. Keep real execution outside the Unity runtime.
