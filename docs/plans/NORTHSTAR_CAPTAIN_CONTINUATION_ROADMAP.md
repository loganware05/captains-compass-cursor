# NorthStar Captain Continuation Roadmap

> Prepared 2026-09-12 after M24 Skills Learning Loop ledger + M27 Code Reviewer MVP,
> plus a live dry-run of `code-reviewer` against `loganware05/bitcoin-data-collector`.

## 0. Where we are

```
Stars / TI ──► Skill Learning Loop (M19–M24) ──► Sandbox Skills
                                                      │
Intent (plan/issue) ──► Code Reviewer (M27) ──► Evidence reports
                                                      │
                                                      ▼
                         Experience / Routing proposals (Captain-gated)
```

| Capability | Status | Authority model | Primary gap |
|---|---|---|---|
| Skills Learning Loop + Linear ledger | Shipped (v1.29.x) | GitHub + Captain approve; Linear records only | Full M1–M7 automated ledger transitions; more retained Skills |
| Agent router wakeability | Shipped (M25/M26) | Fail closed on expired Cloud pins | Live MCP probe still operator-supplied JSON |
| Code Reviewer MVP | On PR #140 (v1.30.0) | Evidence-only; no GitHub posts | Verification depth; GitHub posting; intent packs on product repos |

### Live dry-run: `bitcoin-data-collector`

Mac path `/Users/loganware/.../bitcoin-data-collector` is not mounted in Cloud.
Reviewed GitHub clone `loganware05/bitcoin-data-collector` @ `cursor/kalshi-live-decision-system`.

| Mode | Result |
|---|---|
| Hermetic heuristics only | 0 verified / 1 unverified / 1 discarded — too quiet for a real product delta |
| Specialist candidates → verify gate | **6 verified**, 1 discarded noise; `github_review_posted: false` |

**Verified themes:** secrets-via-env hygiene, broad `Exception` swallowing in live/hourly runners, subprocess collector `check=False`, tracked large JSON artifacts, test gaps on client/live fail-closed paths, intent “no autotrade” still holds.

Evidence: `.agent/evidence/m27-northstar-code-reviewer/bitcoin-data-collector/`

---

## 1. NorthStar north star (product thesis)

Do **not** try to become “another CodeRabbit + another Skill marketplace.”

Become the system that closes this loop:

```
INTENT  →  IMPLEMENTATION  →  REVIEW  →  LEARNING  →  BETTER INTENT
   ▲                                                      │
   └────────────────── Captain authority ─────────────────┘
```

Two engines already started:

1. **Learning engine** — Stars→TI→Skill drafts→sandbox→Captain→Experience
2. **Review engine** — Detect→Investigate→Verify→Evidence (intent-aware)

The Captain’s job is to **wire them together** so review outcomes improve Skills, and Skills improve review.

---

## 2. Operating model for the Captain

### Weekly cadence (suggested)

| Cadence | Action |
|---|---|
| Every working session | One Learning Run **or** one Review Run — not both unless budgeted |
| Weekly | Promote ≤1 Skill past `SANDBOX_TESTED` with evidence |
| Weekly | Run Code Reviewer on 1 product PR/branch; triage verified findings |
| Biweekly | Merge a control-repo milestone PR only after doctor + tests + evidence |
| Monthly | Retire or demote low-precision Skills/review heuristics |

### Hard authorities (do not erode)

1. Captain approves plans and Skill promotions
2. GitHub/repo evidence is engineering truth
3. Linear is flight recorder only
4. Sandbox-first for any Skill execution
5. Code Reviewer defaults to evidence-only until a Phase B plan is approved

---

## 3. Dual-track roadmap (mapped)

### Track A — Skills Learning Loop (ledger → flywheel)

| Phase | Goal | Concrete next actions | Depends on | Exit criteria |
|---|---|---|---|---|
| **A0 — Stabilize** | Keep M24 ledger trustworthy | After each Learning Run: `northstar skills sync-ledger`; attach SHAs + evidence links | Shipped M24 | Every retained Skill has reconstructable Linear parent + GitHub evidence |
| **A1 — Fill the library** | 3–5 high-precision Skills beyond craft-tokens / react forms | Pick Stars in `backend-library`, `devtool`, `ml-data`; run learn→sandbox→Captain | TI scorecard (M23) | 3 Skills with precision notes in Experience |
| **A2 — Ledger automation** | Advance M1–M7 status sync beyond minimal slice | Plan: automated milestone transitions from evidence artifacts; still no Linear approval | A0 | Sub-issues 01–13 auto-advance on evidence events |
| **A3 — Review-informed learning** | Feed Code Reviewer TP/FP into Skill reputation | Schema for finding outcomes; Experience lessons; RoutingProposal only | B1 | At least one Skill confidence delta proposed from review outcomes |
| **A4 — Domain packs** | Kalshi/BTC, frontend, backend Skill packs | Curate procedure playbooks from trusted Stars; sandbox prove | A1 | Installable pack docs + doctor checks |

### Track B — Code Reviewer (signal → product surface)

| Phase | Goal | Concrete next actions | Depends on | Exit criteria |
|---|---|---|---|---|
| **B0 — Merge MVP** | Land v1.30.0 | Merge PR #140 after Captain read of Skill prose | PR #140 | Tag v1.30.0 on main |
| **B1 — Specialist composition** | Stop relying on bare heuristics | Wire security/adversarial/test Skills to emit candidate JSON into verify | B0 | Enriched mode documented; bitcoin-style dry-run is the default demo |
| **B2 — Intent packs** | Product repos carry reviewable intent | Template `IMPLEMENTATION_PLAN.md` / AC export in installer; optional Linear issue body ingest | B0 | Review without hand-written temp plan |
| **B3 — GitHub posting (opt-in)** | Phase B from original brief | New plan: draft reviews only, severity floor, Captain allowlist, sandbox repo first | B1 | Posted review on sandbox PR with low noise |
| **B4 — Repair loop** | FIND→PROVE→FIX→TEST→SUBMIT | Child task spawn via Learning Loop / agent router; never auto-merge | B3 + A3 | One supervised repair PR from a verified finding |
| **B5 — Precision ledger** | Skill/reviewer reputation | Store accepted/rejected findings; gate invocation priority | A3 | Precision dashboards in evidence/Experience |

### Track C — Platform glue (makes A+B compound)

| Phase | Goal | Concrete next actions |
|---|---|---|
| **C1 — Single launcher UX** | `northstar skills …` and `northstar review …` feel like one product | Help text, docs index, install path into product repos |
| **C2 — Product-repo install** | bitcoin-data-collector (and others) get NorthStar docs/Skills without control scripts | `install.sh` into product; memory docs preserved |
| **C3 — Connected routine** | Issue→plan→approve→dispatch→review→ledger | Extend ingress carefully; PR events only after B3 plan |
| **C4 — Eval harness** | Golden diffs with known defects | Fixture repos; measure precision/recall of reviewer |

---

## 4. Recommended sequence (next 6 Captain decisions)

```
1) Merge M27 (#140) → tag v1.30.0
2) Install NorthStar into bitcoin-data-collector (memory docs + Skills only)
3) Open Learning Run NS-SKILL-003 from a Star relevant to that repo (e.g. httpx/retry or pydantic settings)
4) Approve plan: M28 Code Reviewer specialist composition (B1) — still no GitHub posts
5) Approve plan: M29 Intent packs + installer templates (B2)
6) Only then consider M30 GitHub draft-review posting (B3) on sandbox
```

Why this order: **merge → use on a real repo → learn a Skill that helps that repo → deepen review → then automate posting.** Posting before signal quality invites mute-and-ignore.

---

## 5. How the two big implementations feed each other

```
                    ┌─────────────────────────┐
                    │  Skills Learning Loop   │
                    │  (ledger + TI + sandbox) │
                    └───────────┬─────────────┘
                                │ produces Skills:
                                │ security-review, python-ml, …
                                ▼
┌──────────────┐      candidates JSON       ┌────────────────────┐
│ Product PR / │ ─────────────────────────► │ Code Reviewer      │
│ bitcoin-data │   + IMPLEMENTATION_PLAN    │ detect→…→verify    │
└──────┬───────┘                            └─────────┬──────────┘
       │                                              │
       │ verified findings                            │ TP/FP after human triage
       ▼                                              ▼
┌──────────────┐                            ┌────────────────────┐
│ review-fix  │                            │ Experience +       │
│ loop / agent │                            │ RoutingProposal    │
└──────────────┘                            └─────────┬──────────┘
                                                      │ Captain gate
                                                      ▼
                                            better Skill confidence
                                            + better review heuristics
```

**Rule:** every verified finding that a human accepts/rejects should eventually become an Experience lesson. That is the reputation system from the ChatGPT brief — without building a separate SaaS.

---

## 6. Budget / risk controls

| Risk | Mitigation |
|---|---|
| Reviewer noise | Keep verify gate; no GitHub posts until B3; severity floor |
| Learning loop sprawl | One Learning Run at a time; sandbox-only execution |
| Scope creep to “CodeRabbit clone” | Re-read non-goals; require new plan for posting/webhooks |
| Secret leakage in review packs | Continue `redact_secrets`; never ingest live keys into evidence |
| Autonomy burnout | Autonomy budgets per plan; stop reports under `.agent/evidence/` |

---

## 7. Success metrics (Captain scoreboard)

| Metric | Target (near-term) |
|---|---|
| Retained Skills with sandbox proof | ≥5 |
| Learning Runs with complete ledger linkage | 100% of new runs |
| Code review runs on product repos / month | ≥4 |
| Verified finding acceptance rate | ≥70% after B1 |
| GitHub posted comments (until B3) | **0** |
| Captain plan approvals without silent scope expand | 100% |

---

## 8. Immediate backlog tickets (ready to become plans)

1. **M28** — Code Reviewer specialist composition (security/adversarial/test → candidates)
2. **M29** — Intent pack templates in installer + optional Linear issue body → intent
3. **NS-SKILL-003** — Learning Run aimed at bitcoin-data-collector pain (HTTP client resilience or settings/secrets hygiene)
4. **M30** — Opt-in GitHub draft reviews (sandbox allowlist only)
5. **M31** — Finding outcome → Experience → RoutingProposal bridge
6. **Product install** — NorthStar into `bitcoin-data-collector` (no control script copy)

---

## 9. Captain one-liner

**Use the Learning Loop to grow capabilities; use the Code Reviewer to police intent-vs-implementation; only automate posting after precision is proven on repos you own.**
