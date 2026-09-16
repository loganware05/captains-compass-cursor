# Progress

## Current status

**Release: v1.38.0** — M35 / C2 product-repo install on branch
`cursor/m35-c2-product-repo-install-3b10` (**PARTIAL** — product PR pending Captain).

| Item | Value |
|---|---|
| Release | **v1.38.0** (pending tag after merge) |
| M35 / C2 | Local install `0b7bb96` + rewrite; product PR needs Captain push (403) |
| Issue | [#164](https://github.com/loganware05/captains-compass-cursor/issues/164) |
| Rollback | `rollback/pre-c2-product-repo-install` |
| Evidence | `.agent/evidence/c2-product-repo-install/` |

## In flight (Captain-directed)

- Control C2 PR ready for review
- Product branch prepared locally — see `APPLY.md` (bot cannot push to bitcoin-data-collector)
- NS-SKILL-003 / OVA-45 remain parallel queue items
- Docs closeout PR [#165](https://github.com/loganware05/captains-compass-cursor/pull/165) may be superseded

## Completed

- **M34 / C1** merged + tagged **v1.37.0**
- **M33 / B5** merged + tagged **v1.36.0** — Track B complete

## Blockers

Product-repo write access for Cloud Agent (optional) — otherwise Captain applies patch.
