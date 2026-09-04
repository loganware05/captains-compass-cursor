# Implementation Plan — Post-M20 Roadmap Options (M21+)

- Status: **AWAITING APPROVAL**
- Plan ID: `m21-roadmap-options`
- Issue: *pending — create after Captain picks a path*
- Baseline: v1.24.0 (`cb79190` on `main`)
- Rollback: N/A (planning only until a path is approved)

| Field | Value |
|---|---|
| **Plan ID** | `m21-roadmap-options` |
| **Status** | **AWAITING APPROVAL** |
| **Baseline** | v1.24.0 (`cb79190`) |
| **Issue** | TBD after Captain decision |
| **Target release** | TBD (likely v1.25.0+) |
| **Rollback** | Per chosen milestone |

## Problem statement

M19–M20 shipped as **v1.24.0** (skill learning loop + Experience bridge +
Captain-gated Skill improvement apply). There is no locked next milestone.
Private sandbox refresh to 1.24.0 is still pending because this cloud agent
cannot access `loganware05/captain-compass-sandbox` (GitHub App installation
is control-repo only).

## Immediate unblock (sandbox refresh — not a product change)

**Blocked here:** GitHub App / environment repos = `captains-compass-cursor` only.

**Captain options (pick one):**

1. **Grant access** — add `loganware05/captain-compass-sandbox` to Cursor GitHub
   App repository access + this Cloud Agent environment repos, then reply so the
   agent can clone, `update.sh`, doctor, and open the refresh PR.
2. **Local refresh** — run:

```bash
cd /path/to/captains-compass-cursor && git checkout main && git pull
./scripts/update.sh /path/to/captain-compass-sandbox
./scripts/doctor.sh /path/to/captain-compass-sandbox
cd /path/to/captain-compass-sandbox
git checkout -b chore/refresh-compass-1.24.0
git add -A && git commit -m "chore: refresh Captain Compass to 1.24.0"
git push -u origin HEAD
gh pr create --title "chore: refresh Captain Compass to 1.24.0" \
  --body "Refresh private sandbox to Compass v1.24.0 (M19/M20)."
```

Paste the sandbox PR URL back so control-repo validation docs can be updated.

## Captain decision needed — next milestone

Choose **one primary path** for M21 (or approve a sequenced backlog):

| Option | Theme | Scope (invasive?) | Why |
|---|---|---|---|
| **A** | **Live skill-learning in private sandbox** | Medium — wire Stars categorize + learning loop against real sandbox `ti-cache`/live; checklist item 9 live path; evidence under release/sandbox | Completes the M19/M20 story outside fixtures |
| **B** | **Pinecone (or second) vector adapter** | Medium — new hosted adapter beside Neon/pgvector; env + doctor + smoke | ADR left Pinecone as future second adapter |
| **C** | **Harness / hygiene debt** | Low–medium — close stale issues (e.g. #50 M4 already shipped), soft-hook skip-env inheritance, stacked-PR guardrails, doctor coverage | Stabilize before new surface area |
| **D** | **First Mate orchestration polish** | Medium–high — better multi-worktree / parallel-agent playbooks, budget stop UX, review-fix loop defaults | Moves toward design “command center” without new data stores |
| **E** | **Captain-specified** | TBD | You name the objective |

### Recommended default

**A then C:** finish live sandbox learning evidence after the 1.24.0 refresh PR,
then a small hygiene sweep (close #50, doc drift). Defer B/D until you want more
platform surface.

## Desired behavior (after approval of a path)

1. Create GitHub issue + feature branch for the chosen option.
2. Replace this plan with a concrete milestone plan (APPROVED) before product edits.
3. Ship target release with sandbox smokes + private sandbox refresh PR.

## Assumptions

- v1.24.0 remains the baseline until the next release PR.
- Private sandbox stays private; cloud agent needs explicit repo grant to operate there.
- No product implementation starts from *this* plan — only a path selection.

## Risks

- Choosing B/D before A leaves learning loop fixture-only in the private sandbox.
- Without sandbox App access, release closeout rows for private refresh stay Captain-manual.

## Acceptance criteria (for this planning PR)

- [x] Sandbox refresh blocker documented with grant + local commands
- [ ] Captain selects option A–E (or sequenced backlog)
- [ ] Follow-up issue + concrete IMPLEMENTATION_PLAN created for that path

## Autonomy budget

| Limit | Value |
|---|---|
| Iterations | 3 |
| Wall time | N/A (planning) |
| Cost | Minimal |

## Capability planning

Artifacts: `.agent/plans/m21-roadmap-options/` (`resolve.json`, `task-graph.json`, `manifests.json`).

## Approval Boundary

**Do not implement a new milestone until the Captain picks a path and a concrete
follow-up plan is APPROVED.**

Reply with: sandbox access/PR URL **and** roadmap option **A / B / C / D / E**.
