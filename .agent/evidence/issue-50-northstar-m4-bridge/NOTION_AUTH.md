# Notion MCP live auth status

Captain completed Notion MCP desktop authentication (2026-09-09).

| Check | Result |
|---|---|
| `notion-fetch` id=`self` | Authenticated — Logan Ware’s Space |
| `notion-search` | Available (ai_search plan_required) |
| Allowlisted pages fetched | `3cae6a901c4381fd8482e9158ac9e6cc`, `3c1e6a901c4381c4bb5fdc91dc8b4d71` |
| Live cache | `.agent/knowledge/external/notion-live/<page-id>.md` |
| `notion_research_context(..., mode="live")` | `skipped=false`, count=2 |
| Authority | Research/summary only — approvals remain GitHub-only |

Bridge live mode now reads the allowlisted cache (populated via MCP fetch).
If allowlist or cache is missing, the routine skips Notion with an explicit
non-fatal reason (`notion_allowlist_missing` / `notion_live_cache_missing`).
