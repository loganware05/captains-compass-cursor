# Evidence — M38 shell forge gate

Deny `beforeShellExecution` redirects/`tee` that promote `IMPLEMENTATION_PLAN.md`
Status to APPROVED / IN PROGRESS / VALIDATING / COMPLETE unless
`COMPASS_CAPTAIN_APPROVE=1`.

Registered `plan-approval-check.sh` on `beforeShellExecution` (fail-closed) in
addition to existing `preToolUse` Write/StrReplace gate (M36).

Validation: `python3 -m unittest tests.orchestrator.test_m38_shell_forge_gate`

Residual: `cat approved_file > IMPLEMENTATION_PLAN.md` with no promote tokens in
the command line is still allowed (content not inspectable); Captain should treat
that as a process risk / prefer M39 live review for high-assurance repos.
