> **APPROVED / IMPLEMENTED** (2026-10-13) — Plan ID `c1-cognitive-core-source-of-truth`.
> Captain approved; branch `feature/OVA-72-c1-cognitive-core-source-of-truth`; VERSION **1.60.0**.
> Linear: [OVA-72](https://linear.app/ovaltechnologysolutions/issue/OVA-72/c1-cognitive-core-source-of-truth-git-sync-versioned-project-state) ·
> Project [P-OVA-6 NorthStar Cognitive Core](https://linear.app/ovaltechnologysolutions/project/northstar-cognitive-core-445cdc0f12d6) ·
> Milestone **C1 — Source of Truth**.
> Evidence: `.agent/evidence/c1-cognitive-core-source-of-truth/VALIDATION.md`.

# C1 — Cognitive Core Source of Truth

Spec source: [Notion — NorthStar Cognitive Core](https://app.notion.com/p/3f8e6a901c438110882bceb01d2dd249) (C1 section)

Companion (out of scope): [Specialized Model — Mac M2 Training to Cloud Scale](https://app.notion.com/p/3f8e6a901c43815a8d24f99ba617737a)

Prerequisite: Behavior loop M46–M54 complete (v1.59.0); M51/M52 Overseer on `main`.

## One-line summary

Read-only Git sync + versioned SHA-cited project-state snapshots; freshness or stale; reuse Overseer; no REA/routing/training.

## Baseline

v1.59.0 @ `9b9d6bd` → proposed release **v1.60.0**

## Proposed operator surface

```bash
COMPASS_BRAIN_ENABLED=1 ./scripts/northstar brain sync --repo .
COMPASS_BRAIN_ENABLED=1 ./scripts/northstar brain status --repo .
COMPASS_BRAIN_ENABLED=1 ./scripts/northstar brain show --snapshot-id <id> --repo .
```

## Non-goals

- C2–C5, Specialized Model training, REA, Adaptive routing
- Live model required for CI
- Auto-approve / canonical memory rewrite
- External cognitive-core package extract (defer)

## Linear tracking

| Item | Link |
|---|---|
| Project | [P-OVA-6](https://linear.app/ovaltechnologysolutions/project/northstar-cognitive-core-445cdc0f12d6) |
| Milestone | C1 — Source of Truth |
| Issue | [OVA-72](https://linear.app/ovaltechnologysolutions/issue/OVA-72/c1-cognitive-core-source-of-truth-git-sync-versioned-project-state) |
| Deferred markers | C2 Memory, C3 Routing, C4 REA (milestones only; no active issues) |
