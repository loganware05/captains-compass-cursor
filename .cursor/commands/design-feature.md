Run Skill `design-before-plan` before planning.

1. Load Skill `design-before-plan` and follow it.
2. Investigate the current implementation and Captain request.
3. Present approaches, then a short design, and **stop for design approval**.
4. After the Captain approves the design, run `/plan-feature` (Skill
   `implementation-planning` + `capability-planning`) to produce
   `IMPLEMENTATION_PLAN.md` at **AWAITING APPROVAL**.
5. Do **not** implement product files in this command.

Treat any text after this command as the feature request / design prompt.
Quick tasks that already specify everything may skip design and go straight to
implementation under normal rules — still never skip the plan gate for behavior
changes.
