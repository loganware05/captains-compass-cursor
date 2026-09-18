# Progress

## Current status

**Landing v1.39.0** — M37 agentic-equivalent fail-closed detectors (rebased onto
`main`; PR #168 had merged into the M36 branch first).

| Item | Value |
|---|---|
| Tagged | **v1.38.1** (M36) — [release](https://github.com/loganware05/captains-compass-cursor/releases/tag/v1.38.1) |
| Landing | **v1.39.0** / M37 via closeout PR → `main` |
| Next plan | **`m38-shell-forge-gate`** AWAITING APPROVAL ([#169](https://github.com/loganware05/captains-compass-cursor/issues/169)) |
| Also queued | **`m39-agentic-security-phase-b`** AWAITING ([#170](https://github.com/loganware05/captains-compass-cursor/issues/170)) |
| Rollback | `rollback/pre-m37-agentic-security-review` |

## In flight

- Merge this closeout / land-M37-on-main PR → tag **v1.39.0**
- Captain approve M38 (shell forge) and/or M39 (live Cursor Security ingest)

## Completed

- **M37 Phase A** hermetic fail-closed hook detectors (ADR-054)
- **M36** → v1.38.1 (control #167, product #8)
- **M35 / C2** → v1.38.0 (control #166, product #7)
- Track B complete through B5 / v1.36.0

## Recommended sequence

1. Land M37 on `main` + tag v1.39.0  
2. Approve **M38** shell forge gate (closes ADR-053 residual)  
3. Approve **M39** live Agentic Security ingest (opt-in)  
4. Then Track **C3** connected routine (roadmap)
