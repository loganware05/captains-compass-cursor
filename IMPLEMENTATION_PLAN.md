# Implementation Plan — M41 / Jev Decision Service (Shadow Skill Suggestion)

## Metadata

| Field | Value |
|---|---|
| Status | **VALIDATING** |
| Plan ID | `m41-jev-decision-service` |
| Approved | 2026-09-24 — Captain: "I approve." + WS0 fold-in; pin `jev-1.13.0`; evidence under `.agent/evidence/` only; next trials: ranking enablement → review triage → agent routing |
| Supersedes | — (builds on M3 matcher / experience-routing, M25 agent router contract, optional-provider pattern from TI/embeddings) |
| Product | **NorthStar** |
| Baseline | **v1.41.0** @ `cec4da2` (M40 closeout on `main`; prior plan archived at `docs/plans/M40_FILESYSTEM_GATED_CONTEXT.md`) |
| Prepared | 2026-09-24 |
| Spec source | Notion: [NorthStar × Jev — Decision Service Implementation Draft](https://app.notion.com/p/3e4e6a901c43819a8173c581b91a04f0) (research draft 2026-09-23; **not** an approved plan) |
| Control repo | `loganware05/captains-compass-cursor` |
| Validation proving ground | `loganware05/captain-compass-sandbox` (task examples + behavioral evidence only; **no** Jev service code in sandbox) |
| Proposed release | **v1.42.0** (tentative; shadow-only slice) |
| Rollback checkpoint | `rollback/pre-m41-jev-decision-service` @ `cec4da2` (origin/main at approval) |
| Branch | `cursor/m41-jev-decision-service-753c` |
| Issue | Local placeholder per ADR-004 — Captain to file GitHub issue (`gh` is read-only for the agent) |
| Linear | Optional flight-recorder issue after approval (does not originate authority) |
| Captain | Logan Ware |

> Path note: the fail-closed plan-approval hook gates on **root**
> `IMPLEMENTATION_PLAN.md`. Machine planning artifacts live under
> `.agent/plans/m41-jev-decision-service/`.

## Request

Add **Jev** (TypeSafe System One) as an **optional, version-pinned decision
service** inside NorthStar's Python control repository. First slice:
**shadow-mode skill suggestion** — compare Jev rankings against the existing
deterministic matcher without changing dispatch. Cursor coding agents still
plan, implement, and explain. NorthStar's deterministic policy and Captain
approval gates remain authoritative.

## Problem Statement (evidence-based)

- Skill ranking today is fully local and deterministic
  (`orchestrator/matcher/score.py` via `resolve_capabilities()`). Eligibility
  and weighted scoring are strong for hard rules, but semantic task↔skill fit
  is keyword/capability overlap only.
- TypeSafe positions Jev for structured Choice/Score/Boolean decisions (not
  code generation). Vendor skill-suggestion cookbook (Hermes, 488 requests)
  reported wrong skill loads 16.8%→7.3% and unnecessary loads 9.8%→4.0%;
  **roster and agent differ from NorthStar** — must reproduce locally.
- Optional network providers already exist for TI and embeddings (`COMPASS_*`,
  stub/file default, CI hermetic). There is **no** `DecisionProvider` today.
- Notion draft explicitly forbids treating itself as an approved plan and
  requires a Captain-reviewable `IMPLEMENTATION_PLAN.md` first.

## Decision Summary (proposed)

| Principle | Implication |
|---|---|
| Optional | Default `COMPASS_DECISION_PROVIDER=stub`; CI unchanged |
| Version-pinned | Trial pins an explicit Jev model ID (not `jev-latest`) |
| Shadow first | Never mutate `recommended_skill_ids` until a later Captain-approved plan |
| Matcher authoritative | Registry eligibility, lifecycle, `approved_for_execution` stay in code |
| Fail closed | API failure / uncertain / unsupported → withhold suggestion; keep baseline route |
| No authority leakage | Jev cannot approve plans, promote Skills, authorize merges, or unblock tools |

## Scope

### In scope (this plan — first implementation slice)

1. **`DecisionProvider` contract** for a narrow skill-suggestion call.
2. **Adapters:** stub (default), file (offline fixtures), optional Jev HTTP
   adapter (Captain-local / opt-in only).
3. **Shadow wiring** in `resolve_capabilities()` after deterministic
   `rank_skills()`: write comparison evidence; do not change rankings.
4. **Compact state construction** from objective + eligible skill metadata
   only (id, name, description, maturity/lifecycle, limited evidence notes).
5. **Two-pass suggestion protocol** (rank → recheck top-N with fuller
   descriptions + explicit no-fit), recorded with question revision IDs.
6. **Telemetry / evidence schema** for shadow runs (model version, question
   revision, roster hash, distribution, confidence, latency, tokens, cost,
   baseline route, disposition placeholder).
7. **Labeled evaluation harness** (hermetic file fixtures + Captain-local live
   runs) comparing wrong / unnecessary / missed skill loads vs baseline.
8. Docs: `docs/integrations/decision-provider.md`, ADR, TESTING/PROGRESS/
   CHANGELOG updates; budget ledger after approval.

### Explicitly out of scope (deferred; later Captain-gated plans)

| Deferred | Why |
|---|---|
| Agent routing semantic fit via Jev | Notion “later trial”; keep `agent_router` hard filters sole authority |
| Code-review / PR triage via Jev | Candidate later trial; must not replace boundary/evidence gates |
| Agentic tool-call security triage via Jev | Candidate later trial; policy allowlists remain sole execution authority |
| Technology Intelligence relevance via Jev | Later trial; TI validation + Captain promotion unchanged |
| Enabling live Jev to **mutate** skill rankings | Requires separate plan + labeled release gate after shadow evidence |
| M37 specialist FP on removed diff lines | Separate follow-up (see Prioritization) |
| Compiler `SKILL_SLUGS` gap (`code-reviewer`, `northstar-connected-routine`) | Separate small fix (see Prioritization) |
| New Python package dependencies that break hermetic CI | Prefer stdlib + optional thin HTTP client already used by live TI, or inject `http_get` |

## Prioritization note (Captain context)

After M40, two documents also await prioritization:

1. M37 specialist false positive on **removed** diff lines
2. Compiler `SKILL_SLUGS` missing `code-reviewer` / `northstar-connected-routine`

This plan prioritizes the **Jev Decision Service** draft per Captain request.
The two M40 follow-ups remain **deferred** unless the Captain asks to fold the
`SKILL_SLUGS` one-liner into M41 documentation/CI hygiene (recommended optional
WS0 — see Workstreams).

## Current Behavior

```
objective
  → infer_capabilities()
  → load_registry() / eligible skills only
  → rank_skills()   # deterministic weights
  → recommended_skill_ids = top_n
  → resolve.json / capability-plan sections
```

- Agent routing (`orchestrator/routing/agent_router.py`) is a **separate** path
  (agents, not Skills) and must not receive DecisionProvider calls in M41.
- Experience-routing proposals remain Captain-gated weight apply (`routing/apply.py`).
- CI defaults: TI `stub`, embeddings `tfidf`, no DecisionProvider.

## Desired Behavior (post-approval implementation)

```
objective
  → … deterministic rank_skills() as today …
  → if COMPASS_DECISION_SHADOW=1 and provider ≠ stub:
        build compact eligible roster state
        DecisionProvider.suggest_skills(state)  # Choice/Score/Noul-shaped
        write .agent/evidence/.../decision-shadow.json
        optionally render “Shadow suggestions (not applied)” in plan text
  → recommended_skill_ids UNCHANGED
  → on provider failure / abstain: evidence note + baseline only
```

Env contract (proposed):

| Variable | Default | Meaning |
|---|---|---|
| `COMPASS_DECISION_PROVIDER` | `stub` | `stub` \| `file` \| `jev` |
| `COMPASS_DECISION_SHADOW` | unset/off | When set, record shadow comparison; never mutate rankings in M41 |
| `COMPASS_JEV_MODEL_ID` | required when `jev` | Version-pinned model id |
| `COMPASS_JEV_API_*` | unset | Captain-local credentials (never committed) |
| `COMPASS_DECISION_FIXTURES_DIR` | package fixtures | Offline file provider |

## Proposed Architecture

### Package layout (mirrors TI)

```
orchestrator/providers/decision/
  __init__.py          # Protocol DecisionProvider + StubDecisionProvider
  types.py             # SkillSuggestionRequest/Result, Choice/Score shapes
  state.py             # compact eligible roster + roster content hash
  file_provider.py     # offline fixtures + select_decision_provider()
  jev_provider.py      # optional HTTP; injected transport for tests
  shadow.py            # compare matcher vs provider; write evidence only
  questions/           # versioned question JSON (skill_suggest_v1, recheck_v1)
```

### Authority boundaries (non-negotiable)

1. Provider output is **suggestion-only**; never sets `approved_for_execution`.
2. Eligibility filtering happens **before** any model call (code only).
3. Hard rules (numbers, dates, allowlists, budgets, plan approval) stay in code.
4. Unknown provider name → stub (fail closed to offline).
5. Live Jev never runs in default CI.

### Insertion point

Primary: `orchestrator/resolver/resolve.py` after `rank_skills()`.
Secondary (optional, post-shadow): plan render section only — not
`assembler/manifest.py` mutation.

## Workstreams

| ID | Workstream | Boundary | Parallel? |
|---|---|---|---|
| WS0 | **Optional hygiene:** add `code-reviewer` + `northstar-connected-routine` to `SKILL_SLUGS` (clears compile drift warnings). **Only if Captain includes it.** | `orchestrator/registry/compiler.py` + one unit assert | yes |
| WS1 | DecisionProvider protocol, stub, file fixtures, selector, schemas | `orchestrator/providers/decision/**`, schemas | yes w/ WS0 |
| WS2 | Shadow compare + evidence writer + resolve wiring (no ranking mutation) | `resolver/resolve.py`, `shadow.py` | after WS1 |
| WS3 | Jev adapter (version-pinned, redacted inputs, injected HTTP) + Captain-local smoke | `jev_provider.py`, scripts | after WS1 |
| WS4 | Labeled evaluation harness + metrics report template | `tests/`, `.agent/evidence/m41-…/` | after WS2 |
| WS5 | Docs, ADR-058, TESTING/PROGRESS/CHANGELOG, integration guide | docs + memory | after WS2 |
| WS6 | Sandbox behavioral objectives (control-repo code only; sandbox as task corpus) | evidence under control or linked sandbox paths | after WS4 |

## Acceptance Criteria

1. With defaults unset, `./scripts/doctor.sh`, `./tests/run.sh`, and
   `./tests/evals/run.sh` pass with **zero** DecisionProvider network calls.
2. `COMPASS_DECISION_PROVIDER=file` + `COMPASS_DECISION_SHADOW=1` produces a
   shadow evidence artifact that includes matcher ranking, provider ranking,
   roster hash, and disagreement list — and **`recommended_skill_ids` match
   the baseline** bit-for-bit.
3. Stub/unknown provider never raises into capability-plan; failures are
   recorded and withheld.
4. Jev adapter refuses to run without pinned `COMPASS_JEV_MODEL_ID`.
5. Compact state builder never includes secrets, whole-repo trees, unfiltered
   diffs, or unrelated memory docs (unit-tested redaction invariants).
6. Docs state clearly: shadow ≠ dispatch; later enablement needs a new plan.
7. Evaluation report exists for at least one hermetic fixture corpus with
   metrics: wrong skill loads, unnecessary loads, missed useful skills,
   disagreement rate, latency (fixture=0), cost (fixture=0).
8. No change to agent router hard filters, boundary review gate, plan-approval
   hooks, or Skill promotion gates.
9. Rollback: unset env vars / revert provider package; matcher path identical.

## Validation Plan

| Layer | Command / artifact |
|---|---|
| Static / doctor | `./scripts/doctor.sh` |
| Unit / orchestrator | `PYTHONPATH=. python3 -m unittest discover -s tests/orchestrator -p 'test_*decision*' -v` + full `./tests/run.sh` |
| Evals | `./tests/evals/run.sh` |
| Shadow file run | `COMPASS_DECISION_PROVIDER=file COMPASS_DECISION_SHADOW=1 ./scripts/capability-resolve.sh "…"` |
| Captain-local live (optional) | Pinned Jev model; evidence under `.agent/evidence/m41-jev-decision-service/live/` (gitignored secrets) |
| Security | Review API credential handling, redaction, no secrets in evidence JSON |
| Rollback review | Diff proves matcher return path untouched when shadow off |

Evidence root: `.agent/evidence/m41-jev-decision-service/`

## Evaluation & Release Gate (shadow → optional enable)

**Not part of M41 merge criteria** — criteria for a **future** plan that would
allow suggestions to influence rankings:

- Separate train/tune vs holdout labeled sets from NorthStar tasks
- Improve wrong / unnecessary / missed loads vs baseline on holdout
- Zero authority bypasses in adversarial cases
- Captain review of any authority change; easy rollback to matcher-only

M41 only ships shadow + fixtures + optional live adapter behind flags.

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Network in CI | Default stub; file fixtures; injected HTTP only in live tests marked optional |
| Authority confusion | Shadow side-channel fields; plan render labels “not applied” |
| Vendor eval ≠ NorthStar | Local labeled set; do not cite vendor % as NorthStar savings |
| Jev jaggedness (counting, adversarial) | Keep hard rules in code; abstain path; redacted compact state |
| Secret leakage via API | Redaction unit tests; never send `.env`, tokens, full diffs |
| Scope creep into review/routing | Explicit out-of-scope table; reject expansions without re-approval |

## Assumptions

1. Captain wants M41 to implement the Notion **first slice** (shadow skill
   suggestion), not the later review/routing/TI trials.
2. Control repo remains the sole home for DecisionProvider code.
3. No requirement to vendor TypeSafe SDKs if a minimal HTTP adapter suffices;
   prefer existing live-provider patterns.
4. Sandbox is used for objectives/evidence, not for installing Jev service code.

## Open Questions (Captain) — RESOLVED 2026-09-24

1. **WS0:** Fold into M41 — add `code-reviewer` + `northstar-connected-routine` to `SKILL_SLUGS`.
2. **Pinned model:** `jev-1.13.0` (refuse aliases `jev-latest` / `jev-preview` for live runs).
3. **Evidence location:** Shadow artifacts only under `.agent/evidence/`; plans/`resolve.json` reference by path/ID (no duplication).
4. **Next trials (ordered):** ranking enablement → review triage → agent routing (separate Captain-gated plans).

## Autonomy Budget (post-approval)

| Limit | Maximum |
|---|---|
| Implementation iterations | 8 |
| Failed validation cycles | 3 |
| Estimated live Jev API cost (Captain-local) | Cap to be set by Captain before live runs (vendor list ~$0.042 / M input tokens; shadow fixtures are free) |
| Wall-clock focus blocks | Stop and Budget Stop Report if stalled after 3 failed cycles |

Ledger: `.agent/budgets/m41-jev-decision-service.md` (created only after APPROVED).

## Rollback

1. Unset `COMPASS_DECISION_PROVIDER` / `COMPASS_DECISION_SHADOW`.
2. Revert M41 commits or checkout `rollback/pre-m41-jev-decision-service`.
3. Matcher-only path must restore prior `resolve.json` rankings for the same
   objective (deterministic golden test).

## Machine-generated capability sections

> Generated 2026-09-24 via `./scripts/capability-plan.sh --plan-id m41-jev-decision-service`.
> Proposals only — not authority.

### Required Capabilities

- auth-review, authorization-review, secrets-scan, injection-review
- supply-chain-approval-gate
- github-issue-create, github-pr-create, pr-description-assembly

**Domains detected:** security, github  
**Security-sensitive:** yes

### Reusable Capabilities Found (top)

| Skill | Score | Notes |
|---|---:|---|
| `security-review` | 0.625 | security-sensitive objective |
| `dependency-supply-chain` | 0.4562 | supply-chain gate |
| `github-integration` | 0.4125 | issue/PR workflow |
| `pull-request-preparation` | 0.3563 | PR assembly |
| `implementation-planning` / `capability-planning` / `testing-validation` / `embedding-providers` / `technology-intelligence-live` / `experience-routing` / `compass-evaluator` | ≥0.255 | planning + optional-provider + eval patterns |

### Capability Gaps

None detected for inferred requirements. (Human note: no existing Skill named
`decision-provider`; implementation uses TI/embedding provider Skills as
patterns rather than a new Skill slug in M41.)

### Technology Intelligence Candidates

*No external candidates queried (TI provider: stub).*

### Task Graph

| Task ID | Objective | Dependencies | Parallelizable |
|---|---|---|---|
| `task-discovery` | Discover repository structure, tooling, risks, and conventions | — | no |
| `task-architecture` | Define DecisionProvider contracts, data, rollback | task-discovery | no |
| `task-implementation` | Implement shadow DecisionProvider slice | task-architecture (hard) | no |
| `task-validation` | Validation + evidence | task-implementation (symlink) | no |
| `task-security-review` | Auth, secrets, injection, egress | task-implementation (symlink) | yes |
| `task-documentation` | Memory docs + changelog | task-validation, task-security-review | no |

Artifacts: `.agent/plans/m41-jev-decision-service/{resolve,task-graph,manifests}.json`

### Proposed Agent Configuration

| Task | Profile | Skills (proposed) |
|---|---|---|
| discovery | `repository-scout` | `repository-discovery`, `capability-planning`, `dependency-supply-chain` |
| architecture | `architecture-agent` | `dependency-supply-chain`, `capability-planning`, `code-structure-cleanup` |
| implementation | `implementation-agent` | `autonomy-budget`, `code-structure-cleanup`, `dependency-supply-chain` |
| validation | `test-engineer` | `testing-validation`, `dependency-supply-chain` |
| security | `security-reviewer` | `security-review`, `dependency-supply-chain` |
| documentation | `documentation-agent` | `pull-request-preparation`, `autonomy-budget` |

### Evaluation Strategy

- Hermetic fixture shadow parity + disagreement metrics
- Security review of egress/redaction
- Adversarial review before merge
- Live Jev optional and Captain-budgeted; never required for CI green

### Learning Plan

Retain plan artifacts + shadow evidence. Use labeled disagreements to tune
thresholds in a **future** plan before any ranking enablement.

### Approval Boundary

**Implementation must not begin until the Captain explicitly approves this
plan** (status → APPROVED with recorded utterance). The Notion draft is
research input only.

## First Mate recommendation

Approve **M41 shadow-only skill suggestion** as specified. Optionally approve
**WS0** in the same utterance if you want the compiler drift warnings cleared
with this milestone. Keep M37 removed-line FP as a separate small fix plan.
Defer all “later trial” Decision points until shadow evidence exists.
