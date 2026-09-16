# Evidence — M36 hook security hardening

Closes Cursor Agentic Security Review medium findings on bitcoin-data-collector PR #7.

| Finding | Fix |
|---|---|
| Plan-approval self-serve via Write to IMPLEMENTATION_PLAN.md | Require COMPASS_CAPTAIN_APPROVE=1 to write APPROVED; product edits need committed plan |
| Protected-branch refspec / git -C / checkout short-circuit | Parser rewrite; short-circuit removed |

Tests: `python3 -m unittest tests.orchestrator.test_m36_hook_security_hardening`
Product: see APPLY_TO_PR7.md
