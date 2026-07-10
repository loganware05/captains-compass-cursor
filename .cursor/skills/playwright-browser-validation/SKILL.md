---
name: playwright-browser-validation
description: Runs Playwright or browser checks, captures screenshots, and records UI evidence
---

# Playwright / Browser Validation

## Use this Skill when

Validating UI changes end-to-end, capturing screenshots, or checking browser-visible behavior after a React (or other web UI) change.

## Inputs

- Running or startable local app (dev server or preview)
- Acceptance criteria from the approved plan
- Existing Playwright/e2e config if present

## Procedure

1. Detect whether Playwright (or another e2e runner) is already configured.
2. If configured, run the project's e2e script and save output under `.agent/evidence/test-results/`.
3. If not configured, prefer the lightest addition approved by the plan (or manual browser verification with screenshots).
4. Capture before/after or success-state screenshots under `.agent/evidence/screenshots/`.
5. Spot-check keyboard focus and visible error/success states for forms.
6. Record commands, results, and evidence paths in the validation report.

## Output

Browser validation report with evidence paths for the First Mate and PR package.

## Prohibited actions

- Do not claim e2e coverage without running checks or capturing evidence.
- Do not commit large binary evidence into git unless the project already does so; prefer `.agent/evidence/` (often gitignored for private paths).
- Do not enable production crawling or authenticated production URLs without Captain approval.
