# Policy lifecycle: the specification vocabulary.
#
# CAPTAIN-OWNED. These definitions are the *independent* statement of what the
# lifecycle must satisfy; they deliberately do not reuse Model.bend's tables.
# A mutation to the model's table cannot also change the spec, so the laws
# cannot be satisfied vacuously. Agents must not edit this file.

import Base
import ./Model.bend as M

# a implies b. Matches b first so that a concrete b computes without a.
def implies(+a: Bool, b: Bool) -> Bool:
  match b:
    case True{}:
      True{}
    case False{}:
      Bool.not(a)

# a < b on Nat.
def lt(+a: Nat, +b: Nat) -> Bool:
  match a:
    case 0n:
      match b:
        case 0n:
          False{}
        case 1n+q:
          True{}
    case 1n+p:
      match b:
        case 0n:
          False{}
        case 1n+q:
          lt(p, q)

# a == b on Nat.
def eq(+a: Nat, +b: Nat) -> Bool:
  match a:
    case 0n:
      match b:
        case 0n:
          True{}
        case 1n+q:
          False{}
    case 1n+p:
      match b:
        case 0n:
          False{}
        case 1n+q:
          eq(p, q)

# The lifecycle is a pipeline of stages: candidate, sandbox_evaluated,
# shadowed, approved, active, proven, with `retired` as the exit.
def stage(s: M.State) -> Nat:
  match s:
    case M.Candidate{}:
      0n
    case M.SandboxEvaluated{}:
      1n
    case M.Shadowed{}:
      2n
    case M.Approved{}:
      3n
    case M.Active{}:
      4n
    case M.Proven{}:
      5n
    case M.Retired{}:
      6n

def is_retired(t: M.State) -> Bool:
  match t:
    case M.Candidate{}:
      False{}
    case M.SandboxEvaluated{}:
      False{}
    case M.Shadowed{}:
      False{}
    case M.Approved{}:
      False{}
    case M.Active{}:
      False{}
    case M.Proven{}:
      False{}
    case M.Retired{}:
      True{}

# Entry vocabulary (Finding 001 / P12): birth must be candidate.
def is_candidate(t: M.State) -> Bool:
  match t:
    case M.Candidate{}:
      True{}
    case M.SandboxEvaluated{}:
      False{}
    case M.Shadowed{}:
      False{}
    case M.Approved{}:
      False{}
    case M.Active{}:
      False{}
    case M.Proven{}:
      False{}
    case M.Retired{}:
      False{}

def entry_ok(s: M.State) -> Bool:
  is_candidate(s)

# Moving from f to t is a single pipeline step, or the exit to `retired`.
def successor_ok(+f: M.State, +t: M.State) -> Bool:
  Bool.or(is_retired(t), eq(stage(t), 1n+stage(f)))

# Only these targets need the Captain: approved, active, proven, retired.
def needs_captain(t: M.State) -> Bool:
  match t:
    case M.Candidate{}:
      False{}
    case M.SandboxEvaluated{}:
      False{}
    case M.Shadowed{}:
      False{}
    case M.Approved{}:
      True{}
    case M.Active{}:
      True{}
    case M.Proven{}:
      True{}
    case M.Retired{}:
      True{}

def is_sandbox_evaluated(t: M.State) -> Bool:
  match t:
    case M.Candidate{}:
      False{}
    case M.SandboxEvaluated{}:
      True{}
    case M.Shadowed{}:
      False{}
    case M.Approved{}:
      False{}
    case M.Active{}:
      False{}
    case M.Proven{}:
      False{}
    case M.Retired{}:
      False{}

def is_shadowed(t: M.State) -> Bool:
  match t:
    case M.Candidate{}:
      False{}
    case M.SandboxEvaluated{}:
      False{}
    case M.Shadowed{}:
      True{}
    case M.Approved{}:
      False{}
    case M.Active{}:
      False{}
    case M.Proven{}:
      False{}
    case M.Retired{}:
      False{}

def is_approved(t: M.State) -> Bool:
  match t:
    case M.Candidate{}:
      False{}
    case M.SandboxEvaluated{}:
      False{}
    case M.Shadowed{}:
      False{}
    case M.Approved{}:
      True{}
    case M.Active{}:
      False{}
    case M.Proven{}:
      False{}
    case M.Retired{}:
      False{}

def is_proven(t: M.State) -> Bool:
  match t:
    case M.Candidate{}:
      False{}
    case M.SandboxEvaluated{}:
      False{}
    case M.Shadowed{}:
      False{}
    case M.Approved{}:
      False{}
    case M.Active{}:
      False{}
    case M.Proven{}:
      True{}
    case M.Retired{}:
      False{}

# Evidence available to a promotion attempt.
def has_eval_pass(p: M.Pre) -> Bool:
  match p:
    case M.Pre{eval_pass, shadow_ok, shadow_present, proven_ok}:
      eval_pass

def has_shadow_ok(p: M.Pre) -> Bool:
  match p:
    case M.Pre{eval_pass, shadow_ok, shadow_present, proven_ok}:
      shadow_ok

def has_shadow_present(p: M.Pre) -> Bool:
  match p:
    case M.Pre{eval_pass, shadow_ok, shadow_present, proven_ok}:
      shadow_present

def has_proven_ok(p: M.Pre) -> Bool:
  match p:
    case M.Pre{eval_pass, shadow_ok, shadow_present, proven_ok}:
      proven_ok

# Does an outcome grant any authority? (approved_for_execution / authority_mutation)
def grants_authority(o: M.Outcome) -> Bool:
  match o:
    case M.Promoted{to, afe, am}:
      Bool.or(afe, am)
    case M.Rejected{}:
      False{}

# An outcome agrees with the decision: a promotion lands exactly on the
# requested target; a rejection happens exactly when the decision was no.
def outcome_agrees(ok: Bool, t: M.State, o: M.Outcome) -> Bool:
  match o:
    case M.Promoted{to, afe, am}:
      Bool.and(ok, eq(stage(to), stage(t)))
    case M.Rejected{}:
      Bool.not(ok)
