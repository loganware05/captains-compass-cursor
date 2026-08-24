# Procedure: Bounded Autonomy Weight Apply

Staging draft — Captain PR required before use as live playbook.

## Source knowledge items

- `know-adr-020` — ADR-020: Persistent-role promotion and bounded Level 3 weight apply

## Steps

1. Confirm routing proposal has `captain_approved: true`.
2. Verify autonomy budget headroom for weight apply.
3. Run `./scripts/apply-routing-proposal.sh` with evidence paths.
4. Record audit under `.agent/routing/applied/`.
