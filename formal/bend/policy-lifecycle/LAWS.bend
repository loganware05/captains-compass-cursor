# Policy lifecycle: the laws.
#
# CAPTAIN-OWNED. The Captain writes and reviews these claims; agents must not
# edit this file. PROOF.bend proves each law with a def of the same name.
# CI compares this file against `main` so a branch cannot weaken its own gate.
#
# Model: Model.bend (mirrors orchestrator/behavior/policy/states.py and the
# decision order of promote.promote_policy).

import Base
import ./Model.bend as M

# P1 LEGALITY: a promotion is accepted only along an edge of the transition
# table.
law p1_legality:
  for +f: M.State
  for +t: M.State
  for +c: Bool
  for +p: M.Pre
  {M.implies(M.decide(f, t, c, p), M.legal(f, t)) == True{} : Bool}

# P2 CAPTAIN GATE: an accepted promotion into a Captain-required state always
# carries Captain approval.
law p2_captain_gate:
  for +f: M.State
  for +t: M.State
  for +c: Bool
  for +p: M.Pre
  {M.implies(Bool.and(M.decide(f, t, c, p), M.captain_required(t)), c) == True{} : Bool}

# P3 TERMINAL: nothing is accepted out of `retired`.
law p3_terminal:
  for +t: M.State
  for +c: Bool
  for +p: M.Pre
  {M.decide(M.Retired{}, t, c, p) == False{} : Bool}

# P3' TERMINAL FOR ALL SEQUENCES: a retired policy stays retired under any
# sequence of promotion attempts, accepted or not.
law p3_terminal_sequences:
  for steps: List<M.Step>
  {M.run(steps, M.Retired{}) == M.Retired{} : M.State}

# P4 FORWARD ONLY: every accepted promotion strictly increases the lifecycle
# rank, so no accepted promotion revisits a state (the lifecycle is acyclic).
law p4_forward_only:
  for +f: M.State
  for +t: M.State
  for +c: Bool
  for +p: M.Pre
  {M.implies(M.decide(f, t, c, p), M.lt(M.rank(f), M.rank(t))) == True{} : Bool}

# P5 SHADOW BEFORE APPROVAL: an accepted promotion into `approved` comes from
# `shadowed`.
law p5_shadow_before_approval:
  for +f: M.State
  for +t: M.State
  for +c: Bool
  for +p: M.Pre
  {M.implies(Bool.and(M.is_approved(t), M.decide(f, t, c, p)), M.is_shadowed(f)) == True{} : Bool}

# P6 NO AUTHORITY GRANT: no promotion outcome sets approved_for_execution or
# authority_mutation.
law p6_no_authority_grant:
  for +f: M.State
  for +t: M.State
  for +c: Bool
  for +p: M.Pre
  {M.grants_authority(M.apply(f, t, c, p)) == False{} : Bool}
