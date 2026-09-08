# Notion MCP live auth status

Captain requested live Notion checking. Cloud Agents cannot complete interactive
MCP authentication (`mcp_auth` requires Cursor desktop IDE).

- Environment action requested: `notion-mcp-auth`
- Bridge behavior: `--notion-mode live` returns explicit
  `notion_mcp_unauthenticated` skip without failing the routine
- Fixture mode (`--notion-mode fixtures`) is green in CI

After desktop auth, re-run with `--notion-mode live` against an allowlisted page.
