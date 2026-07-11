---
name: ios-engineering
description: Implements Swift/SwiftUI iOS features with Xcode project awareness, simulator testing, and accessibility labels
---

# iOS Engineering

## Use this Skill when

Working on Swift/SwiftUI (or UIKit) apps, Xcode project settings, app lifecycle, networking, persistence, permissions, simulator/device testing, or iOS accessibility.

## Inputs

- Approved IMPLEMENTATION_PLAN.md
- Existing Xcode project / SPM / CocoaPods conventions
- Accessibility and privacy expectations from PROJECT_CONTEXT.md

## Procedure

1. Match existing module and navigation patterns.
2. Prefer SwiftUI unless the project is UIKit-first.
3. Keep networking and persistence behind clear boundaries.
4. Request only required permissions; update Info.plist usage strings carefully.
5. Add accessibility labels/traits for interactive controls.
6. Validate on simulator (and device when available); capture screenshots under `.agent/evidence/`.
7. Run the project's unit/UI tests; do not weaken failing tests.
8. Document setup (Xcode version, schemes, simulators) in TESTING.md.

## Prohibited actions

- Do not commit signing certificates, provisioning profiles, or API keys
- Do not expand into unrelated backend/cloud work unless the approved plan includes it
- Do not disable ATS or security settings "temporarily" without Captain approval
