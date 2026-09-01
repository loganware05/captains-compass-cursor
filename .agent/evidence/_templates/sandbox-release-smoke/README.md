# Sandbox release smoke evidence templates (M18)

Copy into `.agent/evidence/release-vX.Y.Z/` during release closeout.

| File | Purpose |
|---|---|
| `sandbox-smokes-automated.json` | Written by `./scripts/run-sandbox-release-smokes.sh --version X.Y.Z` |
| `sandbox-smokes-interactive.json` | Captain/agent checklist attestation after manual sandbox exercises |
| `interactive-smoke-report.md` | Optional narrative notes for interactive rows |

Validate before closeout:

```bash
./scripts/validate-sandbox-release-smokes.sh --version X.Y.Z
```

Interactive checklist: `docs/evals/SANDBOX_BEHAVIORAL_CHECKLIST.md`
