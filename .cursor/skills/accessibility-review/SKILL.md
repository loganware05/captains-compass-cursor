---
name: accessibility-review
description: Reviews UI changes for keyboard, screen-reader, and inclusive design requirements
---

# Accessibility Review

## Use this Skill when

Validating UI, form, or client-rendered changes that users interact with.

## Inputs

- UI diff and screenshots
- Acceptance criteria
- Platform expectations (web / iOS)

## Procedure

1. Verify keyboard navigation and focus order.
2. Verify semantic markup and labels.
3. Verify form errors are announced accessibly.
4. Check color contrast and motion sensitivity.
5. Check touch target sizing where relevant.
6. Capture accessibility evidence under .agent/evidence/accessibility/.

## Output

Accessibility findings with severity, location, and remediation.

## Prohibited actions

- Do not ship UI changes without labels for interactive controls.
- Do not rely on color alone to convey meaning.
