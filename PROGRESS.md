# Progress

## Current status

**Release: v1.30.0** — M27 NorthStar Code Reviewer MVP merged to `main`
([PR #140](https://github.com/loganware05/captains-compass-cursor/pull/140)).

| Item | Value |
|---|---|
| Release | **v1.30.0** |
| M27 | NorthStar Code Reviewer MVP (merged) |
| Issue | [#141](https://github.com/loganware05/captains-compass-cursor/issues/141) |
| Rollback | `rollback/pre-m27-northstar-code-reviewer` |
| Prior baseline | v1.29.1 / M24 + M25 (+ M26 probe) |

## In flight (Captain-directed)

- **NS-SKILL-003** started — Python settings/secrets hygiene (fixtures → sandbox);
  Linear parent [OVA-34](https://linear.app/ovaltechnologysolutions/issue/OVA-34);
  Captain gate [OVA-42](https://linear.app/ovaltechnologysolutions/issue/OVA-42);
  sandbox branch `cursor/ns-skill-003-secrets-hygiene-3b10`
- Next after Captain decision: promote/install (OVA-43/44), then M28 specialist composition for reviewer

## Completed

- M27 merged to main (v1.30.0 candidate)
- M27 plan approved with locks (hermetic CI; Skill `code-reviewer`; Phase B =
  GitHub posting later; GitHub issue only)
- Pipeline + schema + CLI + Skill/agent + doctor wiring landed
- Sandbox + bitcoin-data-collector dry-run evidence under
  `.agent/evidence/m27-northstar-code-reviewer/`
- Captain Continuation Roadmap published
  (`docs/plans/NORTHSTAR_CAPTAIN_CONTINUATION_ROADMAP.md`); Next-6 moves approved
- NorthStar install into bitcoin-data-collector (Captain-reported)
- v1.5.0–v1.29.1 / M1–M26
- Run 001 `NS-SKILL-001` retained (`craft-tokens-design-system`)
- Run 002 `NS-SKILL-002` retained (`react-engineering` accessible forms) — Linear [OVA-20](https://linear.app/ovaltechnologysolutions/issue/OVA-20) / [OVA-33](https://linear.app/ovaltechnologysolutions/issue/OVA-33); sandbox exec [#53](https://github.com/loganware05/captain-compass-sandbox/pull/53) + retain docs [#54](https://github.com/loganware05/captain-compass-sandbox/pull/54) + control PROGRESS [#138](https://github.com/loganware05/captains-compass-cursor/pull/138) merged
- Tag/release `v1.29.0`, patch `v1.29.1`
- M26 probe adapter + CLI `--cloud-agents-json` + tests ([PR #137](https://github.com/loganware05/captains-compass-cursor/pull/137) merged)
- v1.29.1 VERSION bump ([PR #136](https://github.com/loganware05/captains-compass-cursor/pull/136) merged)

## Blockers

- **OVA-42** Captain decision required before NS-SKILL-003 promote/install
