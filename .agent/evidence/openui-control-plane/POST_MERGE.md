# Post-merge closeout — openui-control-plane

| Field | Value |
|---|---|
| Feature PR | #241 merged 2026-10-24T22:35:14Z |
| Merge commit | `7d78e29` |
| Hotfix | v1.74.1 — string-literal OpenUI Lang validator false positive |
| Doctor | PASS (`.agent/evidence/openui-control-plane/post-merge-doctor.txt`) |
| Surfaces | plan/tower/scorecard/closeout emit OK after hotfix |
| Status closeout | `COMPASS_STATUS_ENABLED=1` → readiness may be `needs_captain_action` (legacy open completed issues; `issues_auto_closed: false`) |
| Authority | No auto-approve; Level 3 remains deferred |

## Hotfix detail

Nested-component allowlisting scanned `Ident(` inside string literals, rejecting
valid emits whose titles included `Plane (` or summaries included `steward (`.
Fix: strip string literals before call-name scan + regression test.
