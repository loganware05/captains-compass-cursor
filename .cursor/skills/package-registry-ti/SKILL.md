---
name: package-registry-ti
description: Discovers npm/PyPI Technology Intelligence candidates via file fixtures or live registry (Captain-gated)
---

# Package Registry Technology Intelligence

## Use this Skill when

The Captain wants **package-registry discovery signals** (npm / PyPI) in
capability plans — offline fixtures or opt-in live registry queries.

## Inputs

- Offline fixtures (`COMPASS_TI_PROVIDER=package-registry-file`) or
- Live registries (`COMPASS_TI_PROVIDER=package-registry`) — Captain local only
- Optional `COMPASS_PACKAGE_TI_ECOSYSTEMS=npm,pypi` (default both)
- Optional `COMPASS_PACKAGE_TI_FIXTURES_DIR` for file mode

## Procedure

1. Offline fixtures (CI-safe):

   ```bash
   COMPASS_TI_PROVIDER=package-registry-file \
     ./scripts/query-technology-intelligence.sh --query "schema validation typescript"
   ```

2. Live npm + PyPI (Captain local; never CI default):

   ```bash
   COMPASS_TI_PROVIDER=package-registry \
     ./scripts/query-technology-intelligence.sh --query "schema validation"
   ```

3. Candidates appear only under **Technology Intelligence Candidates**
   (`NOT APPROVED FOR EXECUTION`). Promote via `candidate-promotion` /
   `skill-lifecycle` — never auto-install.

## Output

- `CandidateCapability` list with `approved_for_execution: false`

## Prohibited actions

- Live registry network calls in CI or as default provider
- Setting `approved_for_execution: true`
- Auto-installing packages or Skills from TI results
- Treating package candidates as approved Compass capabilities
