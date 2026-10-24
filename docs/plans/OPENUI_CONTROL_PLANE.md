# Open UI Control Plane — Plan Index

- **Plan ID:** `openui-control-plane`
- **Status:** APPROVED / implementing (see root [`IMPLEMENTATION_PLAN.md`](../../IMPLEMENTATION_PLAN.md))
- **Release:** v1.74.0
- **Branch:** `cursor/openui-control-plane-010c`
- **Rollback:** `rollback/pre-openui-control-plane` @ `6432c23`
- **Capability artifacts:** `.agent/plans/openui-control-plane/`
- **Sources:** Repository State assessment 2026-10-24; `northstar-openui-meta-prompt.md`

### Operator quick start

```bash
COMPASS_OPENUI_ENABLED=1 ./scripts/northstar ui emit --surface plan --repo . --enable-gates
COMPASS_OPENUI_ENABLED=1 ./scripts/northstar ui emit --surface tower --repo . --enable-gates
COMPASS_OPENUI_ENABLED=1 ./scripts/northstar ui emit --surface scorecard --repo . --enable-gates
COMPASS_OPENUI_ENABLED=1 ./scripts/northstar ui emit --surface closeout --repo . --enable-gates
# Approve still requires Captain attestation:
COMPASS_CAPTAIN_APPROVE=1 COMPASS_OPENUI_ENABLED=1 ./scripts/northstar ui approve --repo . --enable-gates
```

This file is a durable index. The approval-gated contract lives in the repository root `IMPLEMENTATION_PLAN.md`.
