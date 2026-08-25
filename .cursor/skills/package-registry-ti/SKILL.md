---
name: package-registry-ti
description: Discovers offline npm/PyPI-shaped Technology Intelligence candidates (file fixtures only)
---

# Package Registry Technology Intelligence

## Use this Skill when

The Captain wants **package-registry discovery signals** (npm / PyPI-shaped) in
capability plans without live registry network calls.

## Inputs

- Offline fixtures (default package fixtures or
  `COMPASS_PACKAGE_TI_FIXTURES_DIR`)
- Env `COMPASS_TI_PROVIDER=package-registry-file`

## Procedure

1. Query offline package candidates:

   ```bash
   COMPASS_TI_PROVIDER=package-registry-file \
     ./scripts/query-technology-intelligence.sh --query "schema validation typescript"
   ```

2. Optional: point at a Captain-curated local export directory:

   ```bash
   COMPASS_TI_PROVIDER=package-registry-file \
   COMPASS_PACKAGE_TI_FIXTURES_DIR=/path/to/exports \
     ./scripts/query-technology-intelligence.sh --query "react forms"
   ```

3. Candidates appear only under **Technology Intelligence Candidates**
   (`NOT APPROVED FOR EXECUTION`). Promote via `candidate-promotion` /
   `skill-lifecycle` — never auto-install.

## Output

- `CandidateCapability` list with `approved_for_execution: false`

## Prohibited actions

- Live npm/PyPI registry network calls in CI
- Setting `approved_for_execution: true`
- Auto-installing packages or Skills from TI results
- Treating package candidates as approved Compass capabilities
