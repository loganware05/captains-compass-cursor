# Technology Intelligence integration (adapter boundary)

Captain Compass consumes **normalized candidate capabilities** from external
Technology Intelligence (TI) sources. Feeds such as GitHub Star Categorization,
package registries, or internal discovery engines connect through a **provider
adapter** — never through direct repository imports or auto-execution.

## Purpose

During `/plan-feature`, the orchestrator may surface **discovery signals** that
could become future Skills or reference implementations. These are **not**
approved Compass capabilities until the Captain promotes them through review.

Approved Compass Skills (registry `kind: skill`, lifecycle `AVAILABLE_SKILL` /
`PROVEN_SKILL`) are matched separately by the deterministic resolver.

## Provider contract

**Module:** `orchestrator/providers/technology_intelligence/`

**Protocol:**

```python
class TechnologyIntelligenceProvider(Protocol):
    def discover_candidates(
        self, objective: str, context: dict
    ) -> list[CandidateCapability]: ...
```

**Inputs:**

| Field | Description |
|---|---|
| `objective` | Same natural-language objective passed to capability planning |
| `context` | Optional repo context (stacks, discovery summary, security flags) |

**Output:** Zero or more `CandidateCapability` dataclass instances. Each
`to_dict()` payload must validate against
`orchestrator/schemas/candidate-capability.schema.json`.

### Required candidate fields

| Field | Constraint |
|---|---|
| `kind` | Must be `"candidate"` |
| `approved_for_execution` | Must be `false` (schema enforces `const: false`) |
| `lifecycle_stage` | `DISCOVERED` or `ANALYZED` only in M1 |
| `source.type` | Must be `"external-candidate"` |
| `source.path` | Opaque locator (repo URL, catalog id, etc.) — no path traversal into Compass |
| `capabilities_provided` | Non-empty list of capability ids the signal might satisfy |

Optional: `discovery_signal`, `notes`, `source.provenance_url`.

### Validation gate

`orchestrator/providers/technology_intelligence/validate.py` runs before plan
rendering. Invalid or `approved_for_execution: true` candidates **fail closed**
with `TechnologyIntelligenceValidationError`.

## Plan rendering

The plan writer (`orchestrator/plan_writer/render.py`) always renders a
**Technology Intelligence Candidates** section with this banner:

```markdown
> **NOT APPROVED FOR EXECUTION** — discovery signals only.
```

| Provider result | Rendered content |
|---|---|
| Empty (stub) | *No external candidates queried (Technology Intelligence provider: stub).* |
| Non-empty | Markdown table: ID, discovery signal, lifecycle stage |

Candidates appear **only** in this section — never in Skill ranking, task
manifests, or install targets.

## Current status (M1 / v1.5.0)

| Component | Status |
|---|---|
| `TechnologyIntelligenceProvider` protocol | Shipped |
| `StubTechnologyIntelligenceProvider` | Shipped — returns `[]` |
| `CandidateCapability` + schema | Shipped |
| Pre-render validation | Shipped |
| GitHub Star Categorization body | **Not wired** — future adapter |
| Auto-install / execute external repos | **Prohibited** |

Default pipeline (`orchestrator/plan_writer/build.py`) uses the stub provider.
Replacing it with a live adapter is a **control-repo change** requiring plan
approval and security review.

## Implementing a future provider

1. Add a class implementing `TechnologyIntelligenceProvider` in
   `orchestrator/providers/technology_intelligence/` (e.g. `github_stars.py`).
2. Map external records to `CandidateCapability` — set `approved_for_execution`
   only via `to_dict()` (always `false`).
3. Unit-test with golden fixtures; never call live APIs in CI.
4. Wire the provider in `build_capability_plan()` behind an explicit config flag
   or environment variable (not enabled by default).
5. Document provenance, rate limits, and secret handling in this file.
6. Extend `tests/evals/run.sh` with isolation sensors if behavior changes.

**Do not:**

- Import code from starred or external repositories at planning time
- Add candidates to the compiled Skill registry without promotion
- Grant agent manifests tools/permissions based on TI output alone
- Skip schema validation

## Promotion path (future milestones)

```text
DISCOVERED → ANALYZED → SECURITY_REVIEWED → SANDBOX_TESTED → APPROVED
  → AVAILABLE_SKILL → PROVEN_SKILL
```

A GitHub star, npm download count, or blog mention is a **discovery signal**, not
permission to execute. Promotion requires Captain approval, security review, and
(suggested) sandbox validation before a sidecar or Skill enters the registry.

## Captain Compass responsibilities

- Display candidates separately from approved Skills
- Never auto-install or execute external repositories
- Require explicit Captain approval before candidate promotion
- Keep TI adapters optional; product repos receive this doc via install for policy
  awareness; the Python orchestrator remains control-repo only

## Related artifacts

- Schema: `orchestrator/schemas/candidate-capability.schema.json`
- Stub tests: `tests/orchestrator/test_schemas.py`, `tests/orchestrator/test_plan_writer.py`
- Eval isolation: `tests/evals/run.sh` (stub TI sensor)
- Skill prohibition: `.cursor/skills/capability-planning/SKILL.md`
