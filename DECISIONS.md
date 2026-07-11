# Decisions

## ADR-001: Separate control repository

- **Status:** Accepted
- **Date:** 2026-07-10
- **Context:** Workflow rules must not be contaminated by product-specific code.
- **Decision:** Captain's Compass lives in its own GitHub template repository and is installed into product repos via scripts.
- **Consequences:** Product context stays in product repos; workflow updates are versioned centrally.

## ADR-002: Version 0.1 is deliberately minimal

- **Status:** Accepted
- **Date:** 2026-07-10
- **Context:** Full autonomy (hooks, MCP, overnight tasks, every framework) increases failure surface area.
- **Decision:** V0.1 includes five rules, seven Skills, eight agents, templates, install/doctor, one example, and installer tests only.
- **Consequences:** Tech modules, hooks, and MCP arrive in later versions after sandbox proof.

## ADR-003: Approval gate before product changes

- **Status:** Accepted
- **Date:** 2026-07-10
- **Context:** Agents must not implement before the Captain agrees on scope and approach.
- **Decision:** Agents may discover and plan freely; they must not modify product implementation files until IMPLEMENTATION_PLAN.md status is APPROVED with an approval record.
- **Consequences:** Slightly slower start; much safer autonomous execution after approval.

## ADR-004: Local issue/PR fallback when GitHub is unavailable

- **Status:** Accepted
- **Date:** 2026-07-10
- **Context:** Sandbox validation showed the workflow can create branches, rollbacks, and tests without GitHub auth, but cannot open remote PRs.
- **Decision:** When GitHub auth/MCP is unavailable, use a documented local issue placeholder and a PR-ready description. Do not treat missing remote PR creation as a workflow failure.
- **Consequences:** Real issues/PRs require authenticated `gh` and/or GitHub MCP (Stage 1 docs/Skill added in V0.2).

## ADR-005: V0.2 adds GitHub Stage 1, React/Playwright Skills, and first hooks

- **Status:** Accepted
- **Date:** 2026-07-10
- **Context:** V0.1 sandbox passed; design sequence calls for GitHub → Playwright → hooks → React module next.
- **Decision:** Ship V0.2.0 with `github-integration`, `react-engineering`, `playwright-browser-validation`, and the first three hooks (secrets, protected branch, plan approval). Keep hooks fail-open (`failClosed: false`) initially.
- **Consequences:** Stronger enforcement without freezing work if a hook misbehaves; remaining hooks and tech modules deferred to later versions.

## ADR-006: V0.3 adds Node and Postgres/Prisma Skills

- **Status:** Accepted
- **Date:** 2026-07-10
- **Context:** Design roadmap versions Node + PostgreSQL/Prisma as v0.3.0 after React/Playwright.
- **Decision:** Add `node-engineering` and `postgres-prisma` Skills plus integration docs and an illustrative Prisma example schema. Keep them as Skills (not always-on rules).
- **Consequences:** Agents load backend/data guidance only when relevant; production DB access remains approval-gated and out of default agent context.

## ADR-007: Complete the seven-hook safety set in V0.3.1

- **Status:** Accepted
- **Date:** 2026-07-10
- **Context:** Design Part 10 lists seven hooks; V0.2 shipped the first three after sandbox proof.
- **Decision:** Add branch-name, pre-commit formatting, pre-push tests, and PR evidence hooks with fail-open defaults and skip env vars (`COMPASS_SKIP_FORMAT`, `COMPASS_SKIP_TESTS`, `COMPASS_SKIP_PR_EVIDENCE`). Resolve target repos via cwd/`cd` helpers.
- **Consequences:** Stronger local enforcement without freezing cross-repo agent work; skip valves for intentional overrides.

## ADR-008: V0.4 adds Docker and cloud preview Skill

- **Status:** Accepted
- **Date:** 2026-07-10
- **Context:** Design roadmap versions Docker and cloud previews as v0.4.0 after Node/Prisma.
- **Decision:** Add `docker-cloud` Skill focused on containers and preview/staging deploys. Production destructive actions remain Captain-approved and out of default autonomy.
- **Consequences:** Agents can containerize and document preview deploys without gaining production release authority.

## ADR-009: V0.5 adds Linear and Notion MCP Skills without moving approval out of the repo

- **Status:** Accepted
- **Date:** 2026-07-11
- **Context:** Design MCP stages 3–4 cover Linear and Notion after GitHub/Playwright.
- **Decision:** Ship `linear-integration` and `notion-integration` Skills plus setup docs. Repository plans/decisions remain authoritative; Linear/Notion are coordination and research surfaces.
- **Consequences:** Agents can use MCP when configured; offline fallbacks remain valid.

## ADR-010: V0.6 adds Python/ML Skill and explicit Cloud MCP Stage 5 limits

- **Status:** Accepted
- **Date:** 2026-07-11
- **Context:** Design tech-module order places Python/ML after Docker; MCP Stage 5 covers cloud platforms.
- **Decision:** Add `python-ml` Skill plus Stage 5 docs that keep production cloud actions Captain-approved. Also document stacked-PR landing onto `main`.
- **Consequences:** Agents gain ML guidance without expanding production cloud autonomy; release PRs must target `main`.
