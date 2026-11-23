# Policy lifecycle: the laws.
#
# CAPTAIN-OWNED. The Captain writes and reviews these claims; agents must not
# edit this file or SPEC.bend except under an approved plan that explicitly
# authorizes a law change (e.g. bend-adr-110-go / #278 entry-state P12).
# PROOF.bend proves each law with a def of the same name.
# `northstar formal check --strict-laws --base-ref origin/main` compares
# LAWS.bend and SPEC.bend with the base ref and fails if they changed or the
# ref is unusable. (CI wiring of --strict-laws remains deferred.)
#
# Model under test: Model.bend (mirrors orchestrator/behavior/policy/states.py
# and the decision order of promote.promote_policy). Vocabulary: SPEC.bend,
# which is independent of the model's tables.
#
# `decide(f, t, c, p)` is True iff promoting a policy from state f to state t,
# with Captain approval c and evidence p, would be accepted.

import Base
import ./Model.bend as M
import ./SPEC.bend as S

# P1 PIPELINE: an accepted promotion is a single pipeline step or the exit to
# `retired`. It can never skip a stage or move backwards.
law p1_pipeline:
  for +f: M.State
  for +t: M.State
  for +c: Bool
  for +p: M.Pre
  {S.implies(M.decide(f, t, c, p), S.successor_ok(f, t)) == True{} : Bool}

# P2 CAPTAIN GATE: an accepted promotion into approved, active, proven or
# retired always carries Captain approval.
law p2_captain_gate:
  for +c: Bool
  for +t: M.State
  for +f: M.State
  for +p: M.Pre
  {S.implies(Bool.and(S.needs_captain(t), M.decide(f, t, c, p)), c) == True{} : Bool}

# P3 TERMINAL: nothing is accepted out of `retired`.
law p3_terminal:
  for +t: M.State
  for +c: Bool
  for +p: M.Pre
  {M.decide(M.Retired{}, t, c, p) == False{} : Bool}

# P3' TERMINAL FOR ALL SEQUENCES: a retired policy stays retired under any
# sequence of promotion attempts, accepted or not.
law p3_terminal_sequences:
  for steps: M.Plan
  {M.run(steps, M.Retired{}) == M.Retired{} : M.State}

# P4 FORWARD ONLY: every accepted promotion strictly increases the stage, so
# no accepted promotion revisits a state (the lifecycle is acyclic).
law p4_forward_only:
  for +f: M.State
  for +t: M.State
  for +c: Bool
  for +p: M.Pre
  {S.implies(M.decide(f, t, c, p), S.lt(S.stage(f), S.stage(t))) == True{} : Bool}

# P5 SHADOW BEFORE APPROVAL: an accepted promotion into `approved` comes from
# `shadowed`.
law p5_shadow_before_approval:
  for +f: M.State
  for +t: M.State
  for +c: Bool
  for +p: M.Pre
  {S.implies(Bool.and(S.is_approved(t), M.decide(f, t, c, p)), S.is_shadowed(f)) == True{} : Bool}

# P6 NO AUTHORITY GRANT: no promotion outcome sets approved_for_execution or
# authority_mutation.
law p6_no_authority_grant:
  for +f: M.State
  for +t: M.State
  for +c: Bool
  for +p: M.Pre
  {S.grants_authority(M.apply(f, t, c, p)) == False{} : Bool}

# P7 EVIDENCE GATES: an accepted promotion into sandbox_evaluated, shadowed,
# approved or proven carries the evidence that gate demands.
law p7a_sandbox_needs_eval_pass:
  for +p: M.Pre
  for +t: M.State
  for +f: M.State
  for +c: Bool
  {S.implies(Bool.and(S.is_sandbox_evaluated(t), M.decide(f, t, c, p)), S.has_eval_pass(p)) == True{} : Bool}

law p7b_shadowed_needs_shadow_ok:
  for +p: M.Pre
  for +t: M.State
  for +f: M.State
  for +c: Bool
  {S.implies(Bool.and(S.is_shadowed(t), M.decide(f, t, c, p)), S.has_shadow_ok(p)) == True{} : Bool}

law p7c_approved_needs_shadow_present:
  for +p: M.Pre
  for +t: M.State
  for +f: M.State
  for +c: Bool
  {S.implies(Bool.and(S.is_approved(t), M.decide(f, t, c, p)), S.has_shadow_present(p)) == True{} : Bool}

law p7d_proven_needs_proven_ok:
  for +p: M.Pre
  for +t: M.State
  for +f: M.State
  for +c: Bool
  {S.implies(Bool.and(S.is_proven(t), M.decide(f, t, c, p)), S.has_proven_ok(p)) == True{} : Bool}

# P8 REJECTION LEAVES THE STATE; ACCEPTANCE LANDS ON THE TARGET: after one
# attempt the policy is at the target if and only if the decision was yes, and
# otherwise unchanged. (Compared by stage, which is injective on states.)
law p8a_rejected_stays:
  for +f: M.State
  for +t: M.State
  for +c: Bool
  for +p: M.Pre
  {Bool.or(M.decide(f, t, c, p), S.eq(S.stage(M.next(f, t, c, p)), S.stage(f))) == True{} : Bool}

law p8b_accepted_lands:
  for +f: M.State
  for +t: M.State
  for +c: Bool
  for +p: M.Pre
  {Bool.or(Bool.not(M.decide(f, t, c, p)), S.eq(S.stage(M.next(f, t, c, p)), S.stage(t))) == True{} : Bool}

# P9 SEQUENCES ARE REPEATED ATTEMPTS: an empty sequence changes nothing, and a
# sequence applies its first attempt, then the rest.
law p9a_run_empty:
  for +s: M.State
  {M.run(M.NoMore{}, s) == s : M.State}

law p9b_run_step:
  for +to: M.State
  for +cap: Bool
  for +pre: M.Pre
  for +tl: M.Plan
  for +s: M.State
  {M.run(M.Attempt{M.Step{to, cap, pre}, tl}, s) == M.run(tl, M.next(s, to, cap, pre)) : M.State}

# P10 OUTCOME AGREES WITH DECISION: a promotion outcome names the requested
# target exactly when the decision was yes.
law p10_outcome_agrees:
  for +f: M.State
  for +t: M.State
  for +c: Bool
  for +p: M.Pre
  {S.outcome_agrees(M.decide(f, t, c, p), t, M.apply(f, t, c, p)) == True{} : Bool}

# P11 LIVENESS: every law above is a safety law, and a model that rejects
# everything satisfies all of them. This one does not. With Captain approval and
# every piece of evidence present, each pipeline step (and the exit to
# `retired`) is accepted, except out of `retired` (P3).
law p11_liveness:
  for +f: M.State
  for +t: M.State
  {Bool.or(S.is_retired(f), Bool.or(Bool.not(S.successor_ok(f, t)), M.decide(f, t, True{}, M.Pre{True{}, True{}, True{}, True{}}))) == True{} : Bool}

# P12 ENTRY STATE (Finding 001): a newly created policy is always born in
# `candidate`. Elevated states are reachable only through accepted promotions.
# Authorized by Captain-approved plan bend-adr-110-go (#278).
law p12_entry_candidate:
  {S.entry_ok(M.birth()) == True{} : Bool}
