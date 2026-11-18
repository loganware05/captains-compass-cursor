# Policy lifecycle: the proofs.
#
# Agent-written. Each `def Laws.<name>` proves the law of the same name in
# LAWS.bend. Run `bend PROOF.bend` (and `--verdict`) as the gate.

import Base
import ./Model.bend as M
import ./LAWS.bend as Laws

# Boolean lemmas
# --------------

# (a and b) implies a
def and_left(a: Bool, b: Bool) -> {M.implies(Bool.and(a, b), a) == True{} : Bool}:
  match a:
    case True{}:
      {==}
    case False{}:
      {==}


# P1: decide is a conjunction whose first conjunct is legality.
def Laws.p1_legality(f, t, c, p):
  and_left(M.legal(f, t), Bool.and(M.captain_ok(t, c), M.pre_ok(t, p)))

# P3: `legal` on `retired` is False for every target, and False absorbs `and`.
def Laws.p3_terminal(t, c, p):
  {==}

# P6: `finish` only ever builds Promoted{_, False, False}.
def finish_no_authority(ok: Bool, t: M.State) -> {M.grants_authority(M.finish(ok, t)) == False{} : Bool}:
  match ok:
    case True{}:
      {==}
    case False{}:
      {==}

def Laws.p6_no_authority_grant(f, t, c, p):
  finish_no_authority(M.decide(f, t, c, p), t)

# (l and (((not cr) or c) and pp)) and cr  implies  c
def captain_lemma(l: Bool, pp: Bool, cr: Bool, +c: Bool) -> {M.implies(Bool.and(Bool.and(l, Bool.and(Bool.or(Bool.not(cr), c), pp)), cr), c) == True{} : Bool}:
  match l:
    case True{}:
      match pp:
        case True{}:
          match cr:
            case True{}:
              match c:
                case True{}:
                  {==}
                case False{}:
                  {==}
            case False{}:
              match c:
                case True{}:
                  {==}
                case False{}:
                  {==}
        case False{}:
          match cr:
            case True{}:
              match c:
                case True{}:
                  {==}
                case False{}:
                  {==}
            case False{}:
              match c:
                case True{}:
                  {==}
                case False{}:
                  {==}
    case False{}:
      match pp:
        case True{}:
          match cr:
            case True{}:
              match c:
                case True{}:
                  {==}
                case False{}:
                  {==}
            case False{}:
              match c:
                case True{}:
                  {==}
                case False{}:
                  {==}
        case False{}:
          match cr:
            case True{}:
              match c:
                case True{}:
                  {==}
                case False{}:
                  {==}
            case False{}:
              match c:
                case True{}:
                  {==}
                case False{}:
                  {==}

def Laws.p2_captain_gate(f, t, c, p):
  captain_lemma(M.legal(f, t), M.pre_ok(t, p), M.captain_required(t), c)

# P4: rank strictly increases along every legal edge; the 49 (from, to) pairs
# are checked by computation.
def Laws.p4_forward_only(f, t, c, p):
  match f:
    case M.Candidate{}:
      match t:
        case M.Candidate{}:
          {==}
        case M.SandboxEvaluated{}:
          {==}
        case M.Shadowed{}:
          {==}
        case M.Approved{}:
          {==}
        case M.Active{}:
          {==}
        case M.Proven{}:
          {==}
        case M.Retired{}:
          {==}
    case M.SandboxEvaluated{}:
      match t:
        case M.Candidate{}:
          {==}
        case M.SandboxEvaluated{}:
          {==}
        case M.Shadowed{}:
          {==}
        case M.Approved{}:
          {==}
        case M.Active{}:
          {==}
        case M.Proven{}:
          {==}
        case M.Retired{}:
          {==}
    case M.Shadowed{}:
      match t:
        case M.Candidate{}:
          {==}
        case M.SandboxEvaluated{}:
          {==}
        case M.Shadowed{}:
          {==}
        case M.Approved{}:
          {==}
        case M.Active{}:
          {==}
        case M.Proven{}:
          {==}
        case M.Retired{}:
          {==}
    case M.Approved{}:
      match t:
        case M.Candidate{}:
          {==}
        case M.SandboxEvaluated{}:
          {==}
        case M.Shadowed{}:
          {==}
        case M.Approved{}:
          {==}
        case M.Active{}:
          {==}
        case M.Proven{}:
          {==}
        case M.Retired{}:
          {==}
    case M.Active{}:
      match t:
        case M.Candidate{}:
          {==}
        case M.SandboxEvaluated{}:
          {==}
        case M.Shadowed{}:
          {==}
        case M.Approved{}:
          {==}
        case M.Active{}:
          {==}
        case M.Proven{}:
          {==}
        case M.Retired{}:
          {==}
    case M.Proven{}:
      match t:
        case M.Candidate{}:
          {==}
        case M.SandboxEvaluated{}:
          {==}
        case M.Shadowed{}:
          {==}
        case M.Approved{}:
          {==}
        case M.Active{}:
          {==}
        case M.Proven{}:
          {==}
        case M.Retired{}:
          {==}
    case M.Retired{}:
      match t:
        case M.Candidate{}:
          {==}
        case M.SandboxEvaluated{}:
          {==}
        case M.Shadowed{}:
          {==}
        case M.Approved{}:
          {==}
        case M.Active{}:
          {==}
        case M.Proven{}:
          {==}
        case M.Retired{}:
          {==}

# P5: only `shadowed -> approved` reaches `approved`; checked by computation.
def Laws.p5_shadow_before_approval(f, t, c, p):
  match f:
    case M.Candidate{}:
      match t:
        case M.Candidate{}:
          {==}
        case M.SandboxEvaluated{}:
          {==}
        case M.Shadowed{}:
          {==}
        case M.Approved{}:
          {==}
        case M.Active{}:
          {==}
        case M.Proven{}:
          {==}
        case M.Retired{}:
          {==}
    case M.SandboxEvaluated{}:
      match t:
        case M.Candidate{}:
          {==}
        case M.SandboxEvaluated{}:
          {==}
        case M.Shadowed{}:
          {==}
        case M.Approved{}:
          {==}
        case M.Active{}:
          {==}
        case M.Proven{}:
          {==}
        case M.Retired{}:
          {==}
    case M.Shadowed{}:
      match t:
        case M.Candidate{}:
          {==}
        case M.SandboxEvaluated{}:
          {==}
        case M.Shadowed{}:
          {==}
        case M.Approved{}:
          {==}
        case M.Active{}:
          {==}
        case M.Proven{}:
          {==}
        case M.Retired{}:
          {==}
    case M.Approved{}:
      match t:
        case M.Candidate{}:
          {==}
        case M.SandboxEvaluated{}:
          {==}
        case M.Shadowed{}:
          {==}
        case M.Approved{}:
          {==}
        case M.Active{}:
          {==}
        case M.Proven{}:
          {==}
        case M.Retired{}:
          {==}
    case M.Active{}:
      match t:
        case M.Candidate{}:
          {==}
        case M.SandboxEvaluated{}:
          {==}
        case M.Shadowed{}:
          {==}
        case M.Approved{}:
          {==}
        case M.Active{}:
          {==}
        case M.Proven{}:
          {==}
        case M.Retired{}:
          {==}
    case M.Proven{}:
      match t:
        case M.Candidate{}:
          {==}
        case M.SandboxEvaluated{}:
          {==}
        case M.Shadowed{}:
          {==}
        case M.Approved{}:
          {==}
        case M.Active{}:
          {==}
        case M.Proven{}:
          {==}
        case M.Retired{}:
          {==}
    case M.Retired{}:
      match t:
        case M.Candidate{}:
          {==}
        case M.SandboxEvaluated{}:
          {==}
        case M.Shadowed{}:
          {==}
        case M.Approved{}:
          {==}
        case M.Active{}:
          {==}
        case M.Proven{}:
          {==}
        case M.Retired{}:
          {==}

# P3': induction on the sequence. A step out of `retired` is rejected (P3), so
# `next` leaves the state at `retired` and the induction hypothesis applies.
def Laws.p3_terminal_sequences(steps):
  match steps:
    case Nil{}:
      {==}
    case Con{h, tl}:
      match h:
        case M.Step{to, cap, pre}:
          Laws.p3_terminal_sequences(tl)
