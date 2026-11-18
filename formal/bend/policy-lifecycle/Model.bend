# Policy lifecycle decision core (NorthStar M50) — Bend model.
#
# Mirrors orchestrator/behavior/policy/states.py (TRANSITIONS, CAPTAIN_REQUIRED)
# and the decision order of promote.promote_policy:
#   1. legality   (can_transition)
#   2. Captain    (require_captain_approved)
#   3. evidence   (prompt-eval / shadow / shadow-present / proven-evidence),
#                 abstracted here as boolean preconditions.
# It models decisions only: no filesystem, no JSON, no clock.

import Base

type State is Data:
  Candidate{}
  SandboxEvaluated{}
  Shadowed{}
  Approved{}
  Active{}
  Proven{}
  Retired{}

# Evidence preconditions, one per gate in promote_policy.
type Pre is Data:
  Pre{eval_pass: Bool, shadow_ok: Bool, shadow_present: Bool, proven_ok: Bool}

# Authority flags that promote_policy always writes as False.
type Outcome is Data:
  Promoted{to: State, approved_for_execution: Bool, authority_mutation: Bool}
  Rejected{}

# The transition table (states.TRANSITIONS).
def legal(f: State, t: State) -> Bool:
  match f:
    case Candidate{}:
      match t:
        case Candidate{}:
          False{}
        case SandboxEvaluated{}:
          True{}
        case Shadowed{}:
          False{}
        case Approved{}:
          False{}
        case Active{}:
          False{}
        case Proven{}:
          False{}
        case Retired{}:
          True{}
    case SandboxEvaluated{}:
      match t:
        case Candidate{}:
          False{}
        case SandboxEvaluated{}:
          False{}
        case Shadowed{}:
          True{}
        case Approved{}:
          False{}
        case Active{}:
          False{}
        case Proven{}:
          False{}
        case Retired{}:
          True{}
    case Shadowed{}:
      match t:
        case Candidate{}:
          False{}
        case SandboxEvaluated{}:
          False{}
        case Shadowed{}:
          False{}
        case Approved{}:
          True{}
        case Active{}:
          False{}
        case Proven{}:
          False{}
        case Retired{}:
          True{}
    case Approved{}:
      match t:
        case Candidate{}:
          False{}
        case SandboxEvaluated{}:
          False{}
        case Shadowed{}:
          False{}
        case Approved{}:
          False{}
        case Active{}:
          True{}
        case Proven{}:
          False{}
        case Retired{}:
          True{}
    case Active{}:
      match t:
        case Candidate{}:
          False{}
        case SandboxEvaluated{}:
          False{}
        case Shadowed{}:
          False{}
        case Approved{}:
          False{}
        case Active{}:
          False{}
        case Proven{}:
          True{}
        case Retired{}:
          True{}
    case Proven{}:
      match t:
        case Candidate{}:
          False{}
        case SandboxEvaluated{}:
          False{}
        case Shadowed{}:
          False{}
        case Approved{}:
          False{}
        case Active{}:
          False{}
        case Proven{}:
          False{}
        case Retired{}:
          True{}
    case Retired{}:
      False{}

# states.CAPTAIN_REQUIRED = {approved, active, proven, retired}
def captain_required(t: State) -> Bool:
  match t:
    case Candidate{}:
      False{}
    case SandboxEvaluated{}:
      False{}
    case Shadowed{}:
      False{}
    case Approved{}:
      True{}
    case Active{}:
      True{}
    case Proven{}:
      True{}
    case Retired{}:
      True{}

# Gate 2: a Captain-required target needs approval; others always pass.
def captain_ok(t: State, +cap: Bool) -> Bool:
  Bool.or(Bool.not(captain_required(t)), cap)

# Gate 3: the evidence gate for the target state.
def pre_ok(t: State, p: Pre) -> Bool:
  match t:
    case Candidate{}:
      True{}
    case SandboxEvaluated{}:
      match p:
        case Pre{eval_pass, shadow_ok, shadow_present, proven_ok}:
          eval_pass
    case Shadowed{}:
      match p:
        case Pre{eval_pass, shadow_ok, shadow_present, proven_ok}:
          shadow_ok
    case Approved{}:
      match p:
        case Pre{eval_pass, shadow_ok, shadow_present, proven_ok}:
          shadow_present
    case Active{}:
      True{}
    case Proven{}:
      match p:
        case Pre{eval_pass, shadow_ok, shadow_present, proven_ok}:
          proven_ok
    case Retired{}:
      True{}

# True iff promote_policy would accept the promotion.
def decide(+f: State, +t: State, +cap: Bool, p: Pre) -> Bool:
  Bool.and(legal(f, t), Bool.and(captain_ok(t, cap), pre_ok(t, p)))

# Resolve a decision into the outcome promote_policy produces: the authority
# flags are always False (approved_for_execution / authority_mutation).
def finish(ok: Bool, t: State) -> Outcome:
  match ok:
    case True{}:
      Promoted{t, False{}, False{}}
    case False{}:
      Rejected{}

def apply(+f: State, +t: State, +cap: Bool, p: Pre) -> Outcome:
  finish(decide(f, t, cap, p), t)

# Does an outcome grant any authority?
def grants_authority(o: Outcome) -> Bool:
  match o:
    case Promoted{to, afe, am}:
      Bool.or(afe, am)
    case Rejected{}:
      False{}

# Position in the lifecycle: every legal edge strictly increases it.
def rank(s: State) -> Nat:
  match s:
    case Candidate{}:
      0n
    case SandboxEvaluated{}:
      1n
    case Shadowed{}:
      2n
    case Approved{}:
      3n
    case Active{}:
      4n
    case Proven{}:
      5n
    case Retired{}:
      6n

# Helpers used to state the laws
# ------------------------------

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

def is_approved(t: State) -> Bool:
  match t:
    case Candidate{}:
      False{}
    case SandboxEvaluated{}:
      False{}
    case Shadowed{}:
      False{}
    case Approved{}:
      True{}
    case Active{}:
      False{}
    case Proven{}:
      False{}
    case Retired{}:
      False{}

def is_shadowed(t: State) -> Bool:
  match t:
    case Candidate{}:
      False{}
    case SandboxEvaluated{}:
      False{}
    case Shadowed{}:
      True{}
    case Approved{}:
      False{}
    case Active{}:
      False{}
    case Proven{}:
      False{}
    case Retired{}:
      False{}

# Sequences of promotion attempts
# -------------------------------

type Step is Data:
  Step{to: State, cap: Bool, pre: Pre}

def pick(ok: Bool, +t: State, +f: State) -> State:
  match ok:
    case True{}:
      t
    case False{}:
      f

# State after one attempt: a rejected promotion leaves the state unchanged.
def next(+f: State, +t: State, +cap: Bool, p: Pre) -> State:
  pick(decide(f, t, cap, p), t, f)

# State after an arbitrary sequence of attempts.
def run(steps: List<Step>, +s: State) -> State:
  match steps:
    case Nil{}:
      s
    case Con{h, tl}:
      match h:
        case Step{to, cap, pre}:
          run(tl, next(s, to, cap, pre))
