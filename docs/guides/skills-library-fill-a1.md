# A1 — Skills library fill (operator runbook)

Roadmap Track A / **A1**: retain **3–5** high-precision Skills beyond early craft
examples, each with Experience precision notes. Companion to the
[Captain Handbook](captain-handbook.md) and
[Stars → Skills](starred-repos-to-skills.md) guide.

**Baseline:** NorthStar ≥ v1.59.0 · Plan `m55-captain-handbook-skills-a1` (OVA-71).

## Exit criteria

| Criterion | Done when |
|---|---|
| Count | ≥3 Skills retained in control `.cursor/skills/` **or** staged `AVAILABLE_SKILL` proposals awaiting Captain PR |
| Quality | Each has TI scorecard (security + supply-chain) + sandbox-test evidence |
| Experience | ≥1 Experience (or learning-run bridge) with precision notes per retained Skill |
| Portability | At least one Skill proven via `update.sh` / install into sandbox or a product repo |
| Authority | No auto-install; `approved_for_execution` remains false on TI candidates |

## Selection criteria (Stars)

Prefer repos you already trust and have **starred**:

| Category | Good for | Avoid |
|---|---|---|
| `frontend-ui` | Accessible forms, React patterns | Unmaintained UI kits |
| `design-system` | Tokens, theming procedures | Binary-only design dumps |
| `backend-library` | API / data access procedures | Secrets-laden templates |
| `devtool` | CLI/workflow procedures | Tools that require clone/exec to “work” |
| `ml-data` | Evaluation / dataset hygiene | Unlicensed model weights workflows |
| `other` | Only with explicit Captain note | Unknown provenance |

**Metadata-only rule:** Learning captures procedures and gates. It never clones
or runs the Star. Tooling that is only useful as a live MCP/binary runtime
(e.g. reverse-engineering stacks) may still be starred for procedure drafts —
they are **not** installed by NorthStar.

### Current Captain Stars of interest

| Repo | Role in A1 |
|---|---|
| [morluto/rea](https://github.com/morluto/rea) | Starred for **metadata/procedure** candidacy only — not REA MCP/Hopper/Ghidra execution inside NorthStar |

Full imported catalog (98 repos) + NorthStar library ranking:

- Guide: [`starred-library-ranking.md`](starred-library-ranking.md)
- Machine data: `.agent/intelligence/starred-catalog/`
- Source workbook copy: `.agent/evidence/m55-captain-handbook-skills-a1/v3_github_starred_repositories_categorized.xlsx`

Start with **Wave 1** in the ranking guide (skills / evaluation / security / MCP / orchestration).

## Path A — Hermetic dry run (required each M55 validation)

From **control** (no live network TI required):

```bash
CONTROL=/path/to/captains-compass-cursor
# Target may be control or sandbox; fixtures do not need a product app.
"$CONTROL/scripts/northstar" skills learn \
  --repo "$CONTROL" \
  --source fixtures \
  --objective "accessible react forms"
```

Or the design-system example:

```bash
"$CONTROL/scripts/example-design-repo-scorecard.sh"
```

Record under `.agent/evidence/m55-captain-handbook-skills-a1/`:

- Command stdout / run id
- Paths to scorecards / skill-drafts / learning-runs
- Confirmation: no files written under `.cursor/skills/` by the learn CLI

## Path B — Live Stars checklist (Captain-supervised)

```bash
CONTROL=/path/to/captains-compass-cursor
SANDBOX=/path/to/captain-compass-sandbox

gh auth status
# Ensure target repos are starred (including REA if desired for metadata).

"$CONTROL/scripts/northstar" skills refresh --repo "$SANDBOX"
"$CONTROL/scripts/categorize-github-stars.sh" --source ti-cache

"$CONTROL/scripts/northstar" skills learn \
  --repo "$SANDBOX" \
  --source ti-cache \
  --objective "<your objective>" \
  --category <frontend-ui|devtool|backend-library|…>
```

For each candidate:

1. Read `.agent/evidence/ti-scorecards/<id>/` — reject on fail-closed gaps.
2. Promote only with `--captain-approved` to `AVAILABLE_SKILL` (proposal).
3. Open a PR copying into `.cursor/skills/<slug>/`.
4. After merge: `"$CONTROL/scripts/update.sh" "$SANDBOX"` (or product).
5. Record an Experience on a real task (`skills_used` includes the slug).
6. Optional: `northstar skills sync-ledger --run <learning-run.json> --mode fixtures`.

## Promotion reminder

```bash
"$CONTROL/scripts/northstar" skills promote \
  --repo "$SANDBOX" \
  --candidate <staging.json> \
  --stage AVAILABLE_SKILL \
  --evidence <sandbox-test>,<security-review>,<dependency-supply-chain> \
  --captain-approved \
  --skill-slug <slug>
```

Staging ≠ installed. Live `.cursor/skills/` only via Captain-reviewed PR.

## Evidence layout

```text
.agent/evidence/m55-captain-handbook-skills-a1/
  VALIDATION.md
  fixture-learn-stdout.txt
  …
```

## Related

- [`captain-handbook.md`](captain-handbook.md)
- [`starred-repos-to-skills.md`](starred-repos-to-skills.md)
- `docs/integrations/technology-intelligence.md`
- `docs/plans/NORTHSTAR_CAPTAIN_CONTINUATION_ROADMAP.md` (Track A / A1)
