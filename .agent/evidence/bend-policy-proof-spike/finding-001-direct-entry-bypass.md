# Finding 001 — Direct entry into a gated lifecycle state (outside the proved model)

- Plan: `bend-policy-proof-spike` (#278) · Severity: **Medium** (no execution authority is granted)
- Status: **Production fixed in #280** (`ensure_policy_for_instruction` always creates `candidate`). Formal Bend entry-state law remains a #278 follow-up.
- Found by: adversarial review of the spike while asking what the proved laws do **not** cover. It was not produced by a failing proof.
- Re-probed on every run by `probe_direct_entry()` (temp directory only; `known_gaps[0]` in `LATEST_check.json`). After #280, `bypass_observed` is **false** and `entered_state` is **candidate**.

## What the proofs establish

For every accepted *transition* `from → to` the model proves legality (P1), the Captain gate (P2), forward-only movement (P4), `shadowed` before `approved` (P5) and the evidence gates (P7). These hold for transitions out of a state the policy legitimately reached.

## Historical gap (pre-#280)

`ensure_policy_for_instruction` created the policy record from an instruction and **trusted the instruction's `approval_state`**. It did not call `promote_policy`, so none of the gates above ran. An instruction with `approval_state = "proven"` produced a policy already in `proven`.

## Production fix (#280)

`ensure_policy_for_instruction` always initializes `lifecycle_state = "candidate"` and realigns the instruction's `approval_state` to `candidate` on create. Elevated states are reachable only through `promote_policy` gates.

## Remaining formal follow-up (#278)

Extend the Bend model/laws with an explicit entry-state invariant (a policy may only be born in `candidate`) and conformance-check the entry path. Until then, entry remains `outside_model` even though the Python bypass is closed.
