Validate the current change against the approved plan and Captain's Compass Definition of Done.

1. Load Skill `testing-validation`. Load `security-review` and `accessibility-review` when applicable.
2. Consult `docs/EVIDENCE_MATRIX.md` (control) or the product copy if present; collect required evidence for this change type under `.agent/evidence/<slug>/`.
3. Append a short `.agent/sessions/` note for this validation phase when useful.
4. Run applicable automated checks (doctor, unit/integration/e2e, lint, `./tests/evals/run.sh` in the control repo). Never weaken tests to force green.
5. For UI changes, capture screenshots and accessibility notes when possible.
6. Update the autonomy budget ledger for this validation cycle.
7. Optionally dispatch the `adversarial-reviewer` / `test-engineer` subagents for a fresh-context pass.
8. Reply with: pass/fail summary, evidence paths, remaining gaps, and whether `/prepare-pr` is appropriate.
