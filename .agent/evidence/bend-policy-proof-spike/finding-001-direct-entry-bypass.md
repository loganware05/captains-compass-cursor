# Finding 001 — Direct entry into a gated lifecycle state

- Plan: `bend-policy-proof-spike` (#278) → closed formally by `bend-adr-110-go`
- Severity: **Medium** (no execution authority is granted)
- Status: **Production fixed in #280**; **Bend P12 shipped in bend-adr-110-go** (`p12_entry_candidate`)
- Found by: adversarial review of the spike while asking what the proved laws do **not** cover.

## What the proofs establish (transitions)

For every accepted *transition* `from → to` the model proves legality (P1), the Captain gate (P2),
forward-only movement (P4), `shadowed` before `approved` (P5) and the evidence gates (P7).

## Production fix (#280)

`ensure_policy_for_instruction` always initializes `lifecycle_state = "candidate"` and realigns
the instruction's `approval_state` to `candidate` on create.

## Formal closeout (P12 / bend-adr-110-go)

- Model: `M.birth() -> Candidate{}`
- Spec: `S.entry_ok` / `S.is_candidate`
- Law: `p12_entry_candidate`
- Probe: `probe_direct_entry()` reports `outside_model: false`, `entry_ok: true`, `law: p12_entry_candidate`

Elevated states remain reachable only through `promote_policy` / `M.decide`.
