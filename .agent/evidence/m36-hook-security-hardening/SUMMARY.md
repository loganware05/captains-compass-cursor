# Evidence — M36 hook security hardening

Closes Cursor Agentic Security Review medium findings on bitcoin-data-collector PR #7.

| Finding | Fix |
|---|---|
| Plan-approval self-serve via Write to IMPLEMENTATION_PLAN.md | Require COMPASS_CAPTAIN_APPROVE=1 to write APPROVED; product edits need committed plan |
| Protected-branch refspec / git -C / checkout short-circuit | Parser rewrite; short-circuit removed |

Tests: `python3 -m unittest tests.orchestrator.test_m36_hook_security_hardening` (4 OK)
Control PR: [#167](https://github.com/loganware05/captains-compass-cursor/pull/167) base=`main` MERGEABLE after rebase
Product PR: [bitcoin-data-collector#8](https://github.com/loganware05/bitcoin-data-collector/pull/8) — see APPLY_TO_PR7.md
