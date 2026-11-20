# Finding 001 — Direct entry into a gated lifecycle state (outside the proved model)

- Plan: `bend-policy-proof-spike` (#278) · Severity: **Medium** (no execution authority is granted) · Status: **Reported, not fixed** (production change is out of scope)
- Found by: adversarial review of the spike while asking what the proved laws do **not** cover. It was not produced by a failing proof.
- Re-demonstrated on every run by `probe_direct_entry()` (temp directory only; `known_gaps[0]` in `LATEST_check.json`).

## What the proofs establish

For every accepted *transition* `from → to` the model proves legality (P1), the Captain gate (P2), forward-only movement (P4), `shadowed` before `approved` (P5) and the evidence gates (P7). These hold for transitions out of a state the policy legitimately reached.

## What they cannot say

`ensure_policy_for_instruction` (`orchestrator/behavior/policy/`) creates the policy record from an instruction and **trusts the instruction's `approval_state`**. It does not call `promote_policy`, so none of the gates above run.

## Repro (observed)

1. Write an instruction whose `approval_state` is `"proven"` into an isolated temp repo.
2. Call `ensure_policy_for_instruction` for it.
3. Result: the policy exists with `lifecycle_state = "proven"`, `captain_approved_at = null`, `shadow_report_id = null`, `prompt_eval_report_id = null`.

Observed in the recorded run: `entered_state: proven`, `captain_approved_at: null`, `shadow_report_id: null`, `authority_flags_false: true`.

## Impact and limits

- Execution-authority flags (`approved_for_execution`, `authority_mutation`) stay `false`.
- `policy_apply_enabled()` gates whether active-state instructions are composed into prompts, so reaching influence still requires a separate opt-in.
- The lifecycle *state label* can nonetheless claim a level of vetting that never happened, which defeats the point of the Captain gate as an audit signal.

## Suggested follow-up (needs its own plan and Captain approval)

Make `ensure_policy_for_instruction` create policies only in `candidate`, or route a non-candidate `approval_state` through `promote_policy`, or reject it. Then extend the model/laws with an "entry" law (a policy may only be born in `candidate`) and conformance-check the entry path.
