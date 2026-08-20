# Security review — M1 capability-aware planning (#35)

Date: 2026-08-19
Scope: control-repo orchestrator, Skills, install/doctor, TI stub

## Findings

| Severity | Finding | Status |
|---|---|---|
| Info | No new third-party Python packages; stdlib-only YAML/JSON | Accept |
| Info | Compiled `registry.json` gitignored; not a secret store | Accept |
| Low | Registry rejects `..` path segments in `source.path` | Mitigated by test |
| Info | TI candidates schema-const `approved_for_execution: false`; validation fail-closed | Accept |
| Info | Stub provider returns `[]`; no network fetch of starred repos | Accept |
| Info | `plan-approval-check.sh` unchanged; DRAFT still denies product edits (evals) | Accept |
| Info | Installer still does not overwrite product memory docs on `--force` | Accept |

No high-severity findings. No secrets in sidecars or registry fixtures.

## Recommendation

Ship. Live TI adapters (future) must stay behind explicit config and the same validation gate.
