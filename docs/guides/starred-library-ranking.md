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

## Wave 1 — learn first (A1 targets)

| # | Repository | Score | TI cat | Mode | Improve Skills | Flags |
|---|---|---|---|---|---|---|
| 1 | `Agents365-ai/drawio-skill` | 97.5 | `devtool` | improve_existing | candidate-promotion, capability-planning, compass-evaluator, execution-telemetry | — |
| 2 | `TestSprite/testsprite-cli` | 97.5 | `devtool` | improve_existing | candidate-promotion, capability-planning, compass-evaluator, execution-telemetry | — |
| 3 | `aaif-goose/goose` | 97.5 | `devtool` | improve_existing | candidate-promotion, capability-planning, compass-evaluator, execution-telemetry | — |
| 4 | `anthropics/skills` | 97.5 | `devtool` | improve_existing | candidate-promotion, capability-planning, compass-evaluator, execution-telemetry | — |
| 5 | `cloudflare/security-audit-skill` | 89.5 | `devtool` | improve_existing | candidate-promotion, capability-planning, code-reviewer, experience-routing | — |
| 6 | `bytedance/deer-flow` | 88.5 | `devtool` | improve_existing | capability-planning, experience-routing, github-integration | — |
| 7 | `Shubhamsaboo/awesome-llm-apps` | 82.5 | `backend-library` | improve_existing | capability-planning, embedding-providers, experience-routing, github-integration | — |
| 8 | `googleapis/mcp-toolbox` | 82.5 | `backend-library` | improve_existing | capability-planning, embedding-providers, experience-routing, github-integration | — |

### Suggested learn objectives

- `Agents365-ai/drawio-skill` — agent skill packaging and promotion gates
- `TestSprite/testsprite-cli` — agent skill packaging and promotion gates
- `aaif-goose/goose` — agent skill packaging and promotion gates
- `anthropics/skills` — agent skill packaging and promotion gates
- `cloudflare/security-audit-skill` — security review procedures for agent workflows
- `bytedance/deer-flow` — multi-agent orchestration and routing procedures
- `Shubhamsaboo/awesome-llm-apps` — MCP tool integration patterns for Cursor agents
- `googleapis/mcp-toolbox` — MCP tool integration patterns for Cursor agents

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

1. Refresh TI cache from control against sandbox.
2. Run `northstar skills learn` for Wave 1 repos (one objective at a time).
3. Scorecard → promote `--captain-approved` → PR into `.cursor/skills/`.
4. `update.sh` into sandbox/product.
5. Keep REA on metadata-only track.
