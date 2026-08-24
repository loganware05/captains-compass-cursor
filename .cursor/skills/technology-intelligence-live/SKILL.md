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

## Procedure

1. Verify `gh auth status` succeeds locally.
2. Query live starred repos (read-only):

   ```bash
   COMPASS_TI_PROVIDER=github-stars \
     ./scripts/query-technology-intelligence.sh --query "accessible react forms"
   ```

3. Review JSON candidates — each has `approved_for_execution: false` and
   lifecycle `DISCOVERED`.
4. Use **Technology Intelligence Candidates** in capability plans as informational
   input only; never clone or execute starred repos without Captain approval.
5. To promote a candidate, switch to Skill `candidate-promotion` (staging ceiling
   `SANDBOX_TESTED`; Skill install requires Captain PR).
6. **Offline cache** (optional — separate provider):

   ```bash
   ./scripts/refresh-ti-cache.sh
   COMPASS_TI_PROVIDER=github-stars-cached \
     ./scripts/query-technology-intelligence.sh --query "accessible react forms"
   ```

## Output

- JSON list of normalized `CandidateCapability` payloads
- Plan section **Technology Intelligence Candidates** when planning with
  `COMPASS_TI_PROVIDER=github-stars` or `github-stars-cached`

## Prohibited actions

- Running live TI in CI or as default provider
- Setting `approved_for_execution: true`
- Auto-cloning, installing, or executing external repositories
- Using topic/search APIs beyond starred repos (M7 scope)
