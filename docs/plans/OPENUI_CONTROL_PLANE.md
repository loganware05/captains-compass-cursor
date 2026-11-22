# Open UI Control Plane — Plan Index

- **Plan ID:** `openui-control-plane`
- **Status:** COMPLETE (PR #241 merged; see root [`IMPLEMENTATION_PLAN.md`](../../IMPLEMENTATION_PLAN.md))
- **Release:** v1.74.0 (+ hotfix v1.74.1)
- **Merge:** `7d78e29` (2026-10-24)
- **Rollback:** `rollback/pre-openui-control-plane` @ `6432c23`
- **Evidence:** `.agent/evidence/openui-control-plane/`

### Operator quick start

```bash
COMPASS_OPENUI_ENABLED=1 ./scripts/northstar ui emit --surface plan --repo . --enable-gates
COMPASS_OPENUI_ENABLED=1 ./scripts/northstar ui emit --surface tower --repo . --enable-gates
COMPASS_OPENUI_ENABLED=1 ./scripts/northstar ui emit --surface scorecard --repo . --enable-gates
COMPASS_OPENUI_ENABLED=1 ./scripts/northstar ui emit --surface closeout --repo . --enable-gates
# Local viewer (v1.89.0 / audit-p3-openui-viewer):
COMPASS_OPENUI_ENABLED=1 ./scripts/northstar ui preview --repo . --enable-gates
# Optional: COMPASS_OPENUI_ENABLED=1 ./scripts/northstar ui serve --repo . --enable-gates
# Approve still requires Captain attestation:
COMPASS_CAPTAIN_APPROVE=1 COMPASS_OPENUI_ENABLED=1 ./scripts/northstar ui approve --repo . --enable-gates
```

Static widget sample (not live): `orchestrator/ui/preview.sample.html`.
Live HTML: `.agent/ui/preview.html` (gitignored).
