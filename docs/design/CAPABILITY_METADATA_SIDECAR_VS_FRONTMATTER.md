# Capability Metadata: Sidecar vs Frontmatter

**Status:** Accepted  
**Plan ID:** `m1-capability-aware-planning`  
**Issue:** [#35](https://github.com/loganware05/captains-compass-cursor/issues/35)  
**Date:** 2026-08-19  
**Related:** ADR-017, `IMPLEMENTATION_PLAN.md`

## Decision

Captain Compass will store structured capability metadata in an optional **sidecar file** named `capability.yaml` alongside each Skill (and, for reference agent profiles, in `orchestrator/reference-profiles/*.json` derived from agent Markdown).

`SKILL.md` frontmatter remains limited to **`name`** and **`description`** — the contract Cursor and `doctor.sh` already enforce.

## Context

Milestone 1 introduces a capability registry built from existing Compass Skills. Each Skill must expose machine-readable fields such as:

- `capabilities_provided`, `categories`, `tags`
- `compatible_stacks`, `lifecycle_stage`, `security_sensitivity`
- `agent_affinity`, provenance, confidence (future)

Today every Skill uses this shape:

```yaml
---
name: react-engineering
description: Implements React and TypeScript UI changes with accessible components, state, and client tests
---
```

The registry compiler must ingest metadata without breaking:

- Cursor Skill discovery (loads `SKILL.md`)
- `scripts/doctor.sh` (requires `name:` in frontmatter)
- `scripts/install.sh` / `update.sh` (copies entire `.cursor/skills/` trees)
- Human readability of procedure docs agents follow during execution

Two viable representations were evaluated.

---

## Options considered

### Option A — Extended YAML frontmatter in `SKILL.md`

Merge capability fields into the existing frontmatter block:

```yaml
---
name: react-engineering
description: Implements React and TypeScript UI changes...
capability:
  id: react-engineering
  version: "1.0.0"
  categories: [frontend, ui]
  capabilities_provided:
    - ui-component-implementation
  compatible_stacks: [react, typescript]
  lifecycle_stage: PROVEN_SKILL
---
```

**Pros**

- Single file per Skill — no orphan sidecar to forget
- Colocated metadata and procedure in one path
- Simpler install (one file already copied)

**Cons**

- Frontmatter grows large; procedure Markdown starts farther down the file
- Cursor may surface entire frontmatter to agents — noisy context during execution
- Mixes **human procedure** (body) with **machine routing** (capability graph) in one artifact
- Harder to validate independently; YAML frontmatter errors can break Skill parsing
- Merge conflicts on busy Skills hit both procedure and routing metadata
- `doctor.sh` today only checks `name:` — extended frontmatter needs new rules and risks false negatives if someone adds invalid nested YAML
- Future auto-generated metadata (from eval telemetry) would rewrite `SKILL.md`, creating noisy diffs on procedure files Captain's edit
- Agent profiles (`.cursor/agents/*.md`) have the same problem — role prose vs routing data

### Option B — Sidecar `capability.yaml` (selected)

Keep `SKILL.md` unchanged. Add optional metadata:

```text
.cursor/skills/react-engineering/
  SKILL.md              # procedure (unchanged contract)
  capability.yaml       # machine routing metadata (optional in v1.5.0, required for Compass Skills in M1)
```

Example sidecar:

```yaml
id: react-engineering
version: "1.0.0"
kind: skill
source:
  type: compass-skill
  path: .cursor/skills/react-engineering/SKILL.md
lifecycle_stage: PROVEN_SKILL
categories: [frontend, ui]
tags: [react, typescript, accessibility]
capabilities_provided:
  - ui-component-implementation
  - client-state-management
compatible_stacks: [react, typescript, vite, nextjs]
security_sensitivity: low
agent_affinity: [implementation-agent]
maturity: proven
confidence: 0.9
```

**Pros**

- **Backwards compatible:** Skills without a sidecar still work; registry uses inference fallback with a warning
- **Separation of concerns:** procedure vs routing — agents load Skills for *how*; orchestrator loads sidecars for *what/when*
- **Safer validation:** registry compiler validates YAML independently; invalid metadata does not corrupt Skill instructions
- **Cleaner diffs:** telemetry or harness updates touch `capability.yaml`, not procedure text
- **Install/update unchanged:** `install.sh` already copies skill directories recursively
- **Extensible:** future candidate capabilities from Technology Intelligence can use the same sidecar shape under different `source.type` without touching approved Skills
- **Testable:** golden fixtures can swap sidecars without rewriting Markdown procedures

**Cons**

- Two files per Skill — possible drift if `id` ≠ `name` frontmatter
- Authors must remember to add sidecar when creating new Skills (mitigated by doctor + registry compile in CI)
- Slightly more directory clutter

### Option C — Hybrid (rejected)

Minimal routing keys in frontmatter (`capability_id`, `categories`) plus full sidecar for detail.

**Rejected because:** duplicates source of truth, increases drift risk, and still pollutes Cursor-facing frontmatter without eliminating the sidecar file.

---

## Comparison matrix

| Criterion | Extended frontmatter | Sidecar `capability.yaml` |
|---|---|---|
| Backwards compatibility | Breaks if frontmatter required; optional fields awkward | Strong — sidecar optional |
| Cursor agent context noise | High — large frontmatter loaded with Skill | Low — Skill body unchanged |
| Doctor / harness validation | Must parse full SKILL.md YAML | Validate sidecar separately |
| Install / update propagation | Same | Same (directory copy) |
| Human edit of procedures | Conflicts mix routing + prose | Procedures isolated |
| Auto-generated metadata | Bad diffs on SKILL.md | Clean diffs on sidecar |
| Single source of truth | Yes (one file) | Yes (if `id` synced to `name`) |
| Inference fallback | Harder — partial frontmatter ambiguous | Clear — missing sidecar → infer |
| Technology Intelligence candidates | Awkward in approved Skill files | Natural — candidates as sidecars in staging area |
| Agent reference profiles | Pollutes agent `.md` | Profiles as JSON extracted from agents |

---

## Reference agent profiles

Static agents (`.cursor/agents/*.md`) follow the same separation principle:

- **Keep** agent Markdown as role instructions for Cursor subagents
- **Extract** routing metadata to `orchestrator/reference-profiles/<id>.json` at build time (compiled into registry)

Do not add large capability blocks to agent frontmatter for the same noise and drift reasons.

---

## Registry compiler behavior

```text
For each .cursor/skills/<slug>/:
  1. Read SKILL.md frontmatter → name, description (required)
  2. If capability.yaml exists → parse, validate schema, use as authoritative metadata
  3. Else → infer minimal capability record from description keywords (warn)
  4. Assert capability.id == frontmatter.name (or slug) — fail compile on mismatch
  5. Emit entry into .agent/capabilities/compiled/registry.json
```

M1 ships sidecars for all 23 Compass Skills so inference fallback is a safety net, not the primary path.

---

## Validation and doctor extensions (Phase B)

When `capability.yaml` is present, `doctor.sh` will:

1. Confirm file exists for listed M1 Skills (after `capability-planning` ships)
2. Run registry compile; fail on schema errors, duplicate IDs, or id/name mismatch

When absent (custom product Skills post-install):

- Warn once at compile time
- Emit inferred record with `provenance.inferred: true` and lower default confidence

---

## File layout convention

```text
.cursor/skills/<skill-slug>/
  SKILL.md                 # required; name + description frontmatter only
  capability.yaml          # optional for third-party; required for Compass control-repo Skills (M1)

orchestrator/reference-profiles/
  implementation-agent.json   # compiled from .cursor/agents/implementation-agent.md

.agent/capabilities/compiled/
  registry.json            # generated; not hand-edited
```

**Naming:** always `capability.yaml` (not `.capability.yml` variants) for predictable globbing.

**Linking:** `source.path` is relative to repository root. `id` must equal Skill frontmatter `name`.

---

## Migration and backwards compatibility

| Scenario | Behavior |
|---|---|
| Existing v1.4.0 product install | Unaffected until update to v1.5.0 |
| Update to v1.5.0 | Receives sidecars via `update.sh` skill tree copy |
| Custom Skill without sidecar | Works; inference fallback + doctor warning |
| Custom Skill with sidecar | Full registry participation |
| Editing only SKILL.md | Routing unchanged unless sidecar updated intentionally |

No changes to `plan-approval-check.sh` or Skill loading mechanics.

---

## Rejected alternatives summary

- **Extended frontmatter** — rejected for context noise, diff hygiene, and mixed concerns
- **Hybrid** — rejected for dual source of truth
- **JSON sidecar** — viable but YAML chosen for human authoring parity with existing frontmatter style and comment support
- **Central registry-only file** — rejected; colocated sidecars scale with install copy model and avoid merge bottlenecks on one global file

---

## Consequences

1. Phase B implements `capability.yaml` for all 23 Skills
2. Registry compiler enforces `id` ↔ `name` consistency
3. `doctor.sh` and CI gain compile step
4. Future auto-tuning of confidence/maturity updates sidecars or compiled registry snapshots — not procedure Markdown
5. Technology Intelligence candidates may ship as sidecars under a staging path with `lifecycle_stage: DISCOVERED` before promotion

---

## Approval

- **Captain:** approved 2026-08-19 (implementation plan + this metadata decision)
- **Implementation:** proceed on branch `feature/35-m1-capability-aware-planning`
