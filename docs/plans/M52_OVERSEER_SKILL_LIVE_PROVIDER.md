> **COMPLETE** (2026-10-11) — Merged #195 → `main` @ `448ac25` (v1.57.0). OVA-68 Done.
> Next: M53 Prompt/Policy Provenance (`IMPLEMENTATION_PLAN.md`,
> Plan ID `m53-prompt-policy-provenance`).

# M52 — Project Overseer Skill + Opt-in Live StatusProvider

Spec source: [Notion — Persistent Project Overseer Design](https://app.notion.com/p/3eae6a901c438109ba3af1de2982826a)

Linear: [OVA-68](https://linear.app/ovaltechnologysolutions/issue/OVA-68/m52-project-overseer-skill-opt-in-live-statusprovider-v1570)

Prerequisite: M51 merged (#194 / v1.56.0).

## One-line summary

Advisory Project Overseer Skill/agent + opt-in live StatusProvider + durable
system-map / scope-ledger under `.agent/status/`; CI stays stub/hermetic.

## Baseline

v1.56.0 @ `bf5ee25` → release **v1.57.0**

## Resolved decisions (Captain — 2026-10-11)

1. Scope = Skill + agent + live provider + system-map/scope-ledger
2. `COMPASS_STATUS_PROVIDER=stub|http` (default stub)
3. Secrets via env only
4. Persist under `.agent/status/`
5. Never auto-rewrite canonical memory docs
6. v1.57.0

## Deferred

- Prompt/policy provenance + exemplars → candidate M53
- AHF-P07+ (gated)
- Cursor Cloud / GH Actions scheduled overseer runs

## Operator surface (proposed)

```bash
COMPASS_STATUS_ENABLED=1 ./scripts/northstar status explain --repo .
COMPASS_STATUS_ENABLED=1 COMPASS_STATUS_PROVIDER=http \
  COMPASS_STATUS_MODEL=<model> \
  ./scripts/northstar status explain --repo .
```
