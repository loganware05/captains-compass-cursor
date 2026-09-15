# Evidence — M31 Finding outcomes → Experience → RoutingProposal

Date: 2026-09-15  
Plan: `m31-finding-outcomes-experience` (Captain approved)  
Release target: v1.34.0  
Rollback: `rollback/pre-m31-finding-outcomes`  
Issue: [#150](https://github.com/loganware05/captains-compass-cursor/issues/150)

## Artifacts

| File | What it proves |
|---|---|
| `doctor.txt` | Doctor green including outcomes module/schema/script |
| `unittest.txt` | `tests/orchestrator/test_m31_finding_outcomes.py` green |
| `outcomes.json` | Fixture triage (accepted/rejected/deferred) for `m28-bitcoin-style-demo` |
| `experiences/*.json` | Accepted + rejected → Experience lessons; deferred skipped |
| `routing-proposal.json` | Optional proposal with `auto_apply=false`, `captain_approved=false` |
| `record-result.json` | CLI summary (`captain_approval=false`, proposal not applied) |

## Fixture triage

Source report: `.agent/evidence/m28-reviewer-specialist-composition/bitcoin-style-demo/report.json`  
Triage input: `tests/fixtures/code-review/triage-outcomes.json`

| Finding | Decision | Label | Experience |
|---|---|---|---|
| `sec-secret-in-diff` | accepted | tp | yes (success) |
| `noise-style-nit` | rejected | fp | yes (failed) |
| `sec-auth-without-tests` | deferred | unknown | no (outcomes evidence only) |

## Locks verified

- Outcomes force `captain_approval=false`
- RoutingProposal is proposal-only (`auto_apply=false`)
- Deferred findings do not write Experience
- Embedded tokens in triage notes are scrubbed (`[REDACTED]`) before Experience write
- Hermetic path — no model / no network
- Skill slug `code-reviewer` unchanged
