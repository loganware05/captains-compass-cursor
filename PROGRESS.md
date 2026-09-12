# Progress

## Current status

**M25 SHIPPED** — Agent router wakeability gate (OVA-19 / OVA-17 learning).

| Item | Value |
|---|---|
| Release baseline | **v1.29.1** (M24+M25) |
| M25 control PR | https://github.com/loganware05/captains-compass-cursor/pull/134 (**merged**) |
| M25 merge commit | `69e949413adb87d608dcce62beaeacc17ee63bda` |
| Sandbox registry PR | https://github.com/loganware05/captain-compass-sandbox/pull/48 (**merged**) |
| Sandbox merge commit | `7404066a7db43752c2e71a0748d568d9cdc615ca` |
| Linear | OVA-19 Done |
| Evidence | `.agent/evidence/m25-agent-router-wakeability/VALIDATION.md` |

## Completed

- v1.5.0–v1.29.0 / M1–M24
- M24 Linear Skills Learning Loop flight recorder + `northstar` launcher
- Run 001 `NS-SKILL-001` closed **retain**; sandbox Skill `craft-tokens-design-system` AVAILABLE
- M25: `northstar.agent_router.v1` wakeability fail-closed; historical pin marked expired in sandbox registry
- Tag/release `v1.29.0`

## Next (optional, Captain-directed)

1. Cut a patch tag (e.g. `v1.29.1`) if you want M25 on a release artifact (currently CHANGELOG Unreleased on main)
2. Optional live Cursor Cloud probe adapter (injectable hook already supported)
3. New Skill learning run / additional Experiences toward prove

## Blockers

None.
