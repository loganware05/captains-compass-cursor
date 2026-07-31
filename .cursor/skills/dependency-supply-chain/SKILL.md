---
name: dependency-supply-chain
description: Reviews young or low-provenance package adds; requires Captain approval and lockfile discipline
---

# Dependency Supply Chain

## Use this Skill when

Adding or upgrading third-party packages (npm, PyPI, SwiftPM, crates, etc.),
especially unfamiliar or newly published libraries.

## Labeled guidance (not hard blocks)

Treat a package as **higher risk** when **any** of the following appear true
(guidance — Captain may still approve):

- Published / first release younger than **~90 days**
- Fewer than **~500** GitHub stars (or equivalent signal) when that metric applies
- No lockfile in the consuming project
- Maintainer / provenance unclear; binary-only releases; unusual install scripts

These thresholds are **labeled guidance**, not automated hook denials.

## Procedure

1. Identify packages being added or major-upgraded.
2. Check lockfile presence (or language equivalent) and keep it updated.
3. Prefer well-known, pinned versions; record why a young package is needed.
4. Run available audit tooling when present (`npm audit`, OSV, etc.) and record output
   under `.agent/evidence/` (scrub secrets).
5. Prefer source-as-context (`source-code-context` / opensrc) before guessing APIs.
6. **Stop and ask the Captain** before adding higher-risk packages. Do not add them
   unilaterally inside an approved plan unless the plan explicitly listed them.
7. If scope expands to new deps not in the plan, return to the approval gate.

## Output

Risk notes, audit evidence paths, and Captain decision record.

## Prohibited actions

- Adding higher-risk packages without Captain acknowledgment
- Committing secrets or tokens from registry tooling
- Weakening lockfiles to force installs
