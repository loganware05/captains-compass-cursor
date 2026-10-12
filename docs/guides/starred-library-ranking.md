# NorthStar Skill library ranking — starred catalog

Source workbook: `v3_github_starred_repositories_categorized.xlsx` (98 repos).
Machine catalog: `.agent/intelligence/starred-catalog/`.
Evidence copy: `.agent/evidence/m55-captain-handbook-skills-a1/v3_github_starred_repositories_categorized.xlsx`.

**Authority:** ranking is advisory only. `approved_for_execution: false`. Learning Loop never clones/executes Stars. Promote only via Captain PR.

## How to read this

| Action | Meaning |
|---|---|
| `learn_first` | High fit for A1 Skill draft / improve existing Skill |
| `learn_soon` | Strong secondary wave |
| `watchlist` | Useful reference; not first library fills |
| `defer` | Poor control-repo Skill fit (personal/product/creative) |
| `promoted` | Captain-promoted to AVAILABLE Skill in control `.cursor/skills/` |

Workbook **Priority Picks** optimize personal products (Shop.py, etc.). This ranking optimizes the **NorthStar control Skill library**.

## Counts

```json
{
  "total": 98,
  "learn_first": 40,
  "learn_soon": 24,
  "watchlist": 21,
  "defer": 13
}
```

## Wave 1 — promoted (A1)

Captain-selected live learn + promote (OVA-71). Evidence:
`.agent/evidence/m55-captain-handbook-skills-a1/wave1-live-20261012T043000Z/` and
`wave1-promote/`.

| Star | Installed Skill | Mode | Status |
|---|---|---|---|
| `anthropics/skills` | [`agent-skills-packaging`](../../.cursor/skills/agent-skills-packaging/SKILL.md) | new AVAILABLE Skill | **promoted** |
| `aaif-goose/goose` | [`goose-agent-orchestration`](../../.cursor/skills/goose-agent-orchestration/SKILL.md) | new AVAILABLE Skill | **promoted** |
| `cloudflare/security-audit-skill` | [`security-audit-procedures`](../../.cursor/skills/security-audit-procedures/SKILL.md) | new AVAILABLE Skill | **promoted** |

Lifecycle for each candidate: `ANALYZED → SECURITY_REVIEWED → SANDBOX_TESTED → APPROVED → AVAILABLE_SKILL` with `--captain-approved`.  
Install is metadata/procedure Skills only — **no clone/exec** of the Stars.

Carry into product repos with `"$CONTROL/scripts/update.sh" "$PRODUCT"` after this lands on a control release you choose.

## Wave 1 — remaining learn-first queue

| # | Repository | Score | TI cat | Notes |
|---|---|---|---|---|
| 1 | `Agents365-ai/drawio-skill` | 97.5 | `devtool` | Next learn candidate |
| 2 | `TestSprite/testsprite-cli` | 97.5 | `devtool` | Next learn candidate |
| 3 | `bytedance/deer-flow` | 88.5 | `devtool` | Orchestration patterns |
| 4 | `Shubhamsaboo/awesome-llm-apps` | 82.5 | `backend-library` | LLM app patterns |
| 5 | `googleapis/mcp-toolbox` | 82.5 | `backend-library` | MCP procedures |

## Metadata-only track

| Repository | Score | Flags | Notes |
|---|---|---|---|
| `morluto/rea` | 67.0 | metadata_only_no_exec | Starred; procedure/MCP-pattern Skill only — no Hopper/Ghidra/IDA execution via NorthStar |

## Wave 2 — learn soon

| # | Repository | Score | TI cat | Mode | Flags |
|---|---|---|---|---|---|
| 1 | `patchy631/ai-engineering-hub` | 61.5 | `other` | improve_existing | — |
| 2 | `tauri-apps/tauri` | 61.5 | `devtool` | improve_existing | — |
| 3 | `vercel-labs/opensrc` | 61.5 | `devtool` | improve_existing | — |
| 4 | `virattt/ai-hedge-fund` | 61.5 | `ml-data` | improve_existing | ahf_adjacent_paper_only |
| 5 | `AKCodez/hackingtool-plugin` | 60.5 | `devtool` | improve_existing | — |
| 6 | `abi/screenshot-to-code` | 59.5 | `frontend-ui` | improve_existing | — |
| 7 | `microsoft/playwright` | 59.5 | `devtool` | improve_existing | — |
| 8 | `ashishpatel26/500-AI-Agents-Projects` | 58.5 | `other` | improve_existing | — |
| 9 | `sherlock-project/sherlock` | 58.0 | `devtool` | improve_existing | — |
| 10 | `public-apis/public-apis` | 57.5 | `devtool` | improve_existing | — |

## Watchlist (sample)

- `harvard-edge/cs249r_book` (47.5) — ML, Computer Vision & Edge AI
- `abhigyanpatwari/GitNexus` (47.5) — Developer Tools & Utilities
- `rmyndharis/OpenWA` (47.5) — AI Agents & Workflow Automation
- `plausible/analytics` (45.5) — Startup, Web & Business Infrastructure
- `Nutlope/hallmark` (45.5) — Design, UI & Productivity
- `cjpais/Handy` (45.5) — Design, UI & Productivity
- `Anil-matcha/Open-Generative-AI` (44.0) — Learning & Project Libraries
- `LucasHJin/vit` (44.0) — ML, Computer Vision & Edge AI
- `danveloper/flash-moe` (44.0) — ML, Computer Vision & Edge AI
- `deepseek-ai/DeepGEMM` (44.0) — ML, Computer Vision & Edge AI
- `ryanfrigo/kalshi-ai-trading-bot` (44.0) — Trading & Financial AI
- `ashishpatel26/500-AI-Machine-learning-Deep-learning-Computer-vision-NLP-Projects-with-code` (43.5) — Learning & Project Libraries

## Deferred

13 repos scored as poor Skill-library fit (career/creative/product infra). See `starred-repositories.csv` filter `recommended_action=defer`.

## Next operator steps

1. ~~Wave 1 trio learn + promote~~ (done — see table above).
2. `update.sh` sandbox/product after merge to pick up the three Skills.
3. Optionally learn remaining Wave 1 queue / Wave 2.
4. Keep REA on metadata-only track.
