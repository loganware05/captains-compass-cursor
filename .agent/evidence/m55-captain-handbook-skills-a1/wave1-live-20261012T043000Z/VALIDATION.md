# M55 Wave 1 live learn — sandbox

## Targets
- anthropics/skills
- aaif-goose/goose
- cloudflare/security-audit-skill

## Blockers fixed
1. `fetch_starred_repos` used `gh api -f` (POST) → 404; fixed to GET query params (branch `fix/OVA-71-gh-starred-query-live-learn`).
2. Batch categorizer labeled these as `ml-data`; Captain manual `devtool` labels applied with `--skip-categorize`.

## Authority
- `auto_install: false`
- No live `.cursor/skills/` install
- Promote still requires Captain `--captain-approved` + PR
