---
name: design-before-plan
description: Use before creative or behavior-changing work — tease out approaches and a short design for Captain sign-off before writing IMPLEMENTATION_PLAN.md
---

# Design Before Plan

Patterns inspired by [obra/superpowers](https://github.com/obra/superpowers)
`brainstorming` (DISCOVERED inspiration — not a plugin install).

## Use this Skill when

- Creating features, changing product behavior, or non-trivial design choices
- The request leaves approach, UX, or architecture open
- Before `/plan-feature` / writing `IMPLEMENTATION_PLAN.md`

## Skip (quick tasks)

When the request already specifies everything that matters (e.g. “rename X to Y”,
“make the icon cornflower blue”), do the work under normal rules — do not force
a design ceremony.

## Inputs

- Captain request
- Existing project memory and relevant code/docs
- Any prior decisions the Captain already made

## Procedure

1. **Look before you ask.** Read referred files and related code until you can
   explain how things work today and what would change. Do not re-ask what the
   repo or Captain already answered.
2. **Lay out approaches** in their own message (2–3 realistic options, trade-offs).
   Ask the Captain to pick one (or amend).
3. **Write a short design** (or fuller design doc for large work): goal, chosen
   approach, boundaries, non-goals, risks. Size to what a Captain can actually read.
4. **Get explicit design approval** before creating or updating
   `IMPLEMENTATION_PLAN.md`.
5. After design approval, load Skill `implementation-planning` / run
   `/plan-feature` and produce the approval-gated plan as usual.

Spikes the Captain explicitly approved are exploration only — still no product
behavior ship without a later plan gate when implementation follows.

## Output

- Approaches + chosen design (Captain-approved)
- Handoff into `IMPLEMENTATION_PLAN.md` (still AWAITING APPROVAL until plan gate)

## Prohibited actions

- Do not skip the Captain plan-approval gate after design
- Do not implement product files during design
- Do not install third-party Superpowers/ECC plugins
- Do not reopen decided Captain choices without new evidence
