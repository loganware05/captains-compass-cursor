---
name: technology-intelligence-live
description: Opt-in live GitHub Stars Technology Intelligence for capability planning (Captain-gated)
---

# Technology Intelligence (Live GitHub Stars)

## Use this Skill when

The Captain wants **live** discovery signals from **starred GitHub repositories**
during capability planning — not offline fixtures and not CI defaults.

## Prerequisites

- `gh` CLI installed and authenticated (`gh auth login`)
- Explicit opt-in: `COMPASS_TI_PROVIDER=github-stars`
- Captain understands candidates are **NOT APPROVED FOR EXECUTION**

## Inputs

- Natural-language objective (same as capability planning)
- Optional `--top N` for result limit

## Topology (required)

TI refresh / learning CLIs live only in the **control** repository. Product /
sandbox checkouts do **not** contain `scripts/refresh-ti-cache.sh`,
`scripts/run-skill-learning-loop.sh`, or `scripts/northstar`.

```bash
CONTROL=/path/to/captains-compass-cursor
SANDBOX=/path/to/captain-compass-sandbox
```

Prefer:

```bash
"$CONTROL/scripts/northstar" skills refresh --repo "$SANDBOX"
"$CONTROL/scripts/northstar" skills learn --repo "$SANDBOX" --objective "…"
```

Equivalent:

```bash
"$CONTROL/scripts/refresh-ti-cache.sh" --repo-root "$SANDBOX"
"$CONTROL/scripts/run-skill-learning-loop.sh" --repo-root "$SANDBOX" --objective "…"
```

## Procedure

1. Verify `gh auth status` succeeds locally.
2. Query live starred repos (read-only):

   ```bash
   COMPASS_TI_PROVIDER=github-stars \
     "$CONTROL/scripts/query-technology-intelligence.sh" --query "accessible react forms"
   ```

3. Review JSON candidates — each has `approved_for_execution: false` and
   lifecycle `DISCOVERED`.
4. Use **Technology Intelligence Candidates** in capability plans as informational
   input only; never clone or execute starred repos without Captain approval.
5. To promote a candidate, switch to Skill `candidate-promotion` (staging ceiling
   `SANDBOX_TESTED`; Skill install requires Captain PR).
6. **Offline cache** (optional — separate provider):

   ```bash
   "$CONTROL/scripts/northstar" skills refresh --repo "$SANDBOX"
   "$CONTROL/scripts/northstar" skills refresh --repo "$SANDBOX" --if-stale 24
   # equivalent:
   "$CONTROL/scripts/refresh-ti-cache.sh" --repo-root "$SANDBOX"
   "$CONTROL/scripts/refresh-ti-cache.sh" --repo-root "$SANDBOX" --if-stale 24
   COMPASS_TI_PROVIDER=github-stars-cached \
     "$CONTROL/scripts/query-technology-intelligence.sh" --query "accessible react forms"
   ```

   Cache envelope includes `fetched_at` (and legacy `refreshed_at`).
7. **Hugging Face file TI** (offline fixtures / Captain export dir — no Hub network in CI):

   ```bash
   COMPASS_TI_PROVIDER=huggingface-file \
     "$CONTROL/scripts/query-technology-intelligence.sh" --query "sentence embeddings"
   ```

8. **Package-registry file TI** (npm/PyPI-shaped fixtures — no registry network in CI):
   use Skill `package-registry-ti` or:

   ```bash
   COMPASS_TI_PROVIDER=package-registry-file \
     "$CONTROL/scripts/query-technology-intelligence.sh" --query "schema validation"
   ```

9. **Live package-registry TI** (Captain local — npm + PyPI):

   ```bash
   COMPASS_TI_PROVIDER=package-registry \
     "$CONTROL/scripts/query-technology-intelligence.sh" --query "schema validation"
   ```

10. **Batch categorized Stars** (offline ML from manual labels — no live training in CI):

   ```bash
   "$CONTROL/scripts/categorize-github-stars.sh" --source fixtures   # offline test path
   # or after refresh:
   "$CONTROL/scripts/categorize-github-stars.sh" --source ti-cache
   COMPASS_TI_PROVIDER=github-stars-categorized \
     "$CONTROL/scripts/query-technology-intelligence.sh" --query "react forms"
   ```

11. **Skill learning loop** (M19/M24 — staging + harness + drafts / improvement proposals):

   ```bash
   "$CONTROL/scripts/northstar" skills learn \
     --repo "$SANDBOX" \
     --source fixtures \
     --objective "accessible react forms"
   # equivalent:
   "$CONTROL/scripts/run-skill-learning-loop.sh" \
     --repo-root "$SANDBOX" \
     --source fixtures \
     --objective "accessible react forms"
   ```

   Review drafts under `.agent/capabilities/candidates/skill-drafts/` and
   improvement proposals under `skill-improvement-proposals/`. Live install still
   requires Captain approval (`skill-learning-loop` Skill).

12. **Live Hugging Face Hub TI** (Captain local — Hub models API):

   ```bash
   COMPASS_TI_PROVIDER=huggingface-hub \
     "$CONTROL/scripts/query-technology-intelligence.sh" --query "sentence embeddings"
   # optional auth for gated models:
   # COMPASS_HF_HUB_TOKEN=hf_... COMPASS_TI_PROVIDER=huggingface-hub ...
   ```

## Output

- JSON list of normalized `CandidateCapability` payloads
- Plan section **Technology Intelligence Candidates** when planning with
  `COMPASS_TI_PROVIDER=github-stars`, `github-stars-cached`, `github-stars-categorized`,
  `huggingface-file`, `huggingface-hub`, `package-registry-file`, or `package-registry`

## Prohibited actions

- Running live TI in CI or as default provider
- Setting `approved_for_execution: true`
- Auto-cloning, installing, or executing external repositories
- Live Hugging Face Hub or npm/PyPI registry network calls from CI defaults
- Assuming TI/learning scripts exist inside product/sandbox checkouts
