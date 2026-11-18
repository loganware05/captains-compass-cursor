# Conformance table for the policy lifecycle model.
#
# Prints one line per (from, to, captain_approved) triple:
#   <from> <to> <cap:0|1> <accept:0|1>
# with every evidence precondition satisfied, so the table isolates the two
# pure gates the Python side can run without a filesystem: legality
# (states.can_transition) and the Captain gate (gates.require_captain_approved).
# orchestrator/formal/policy_lifecycle.py compares this output with Python.

import Base
import ./Model.bend as M

def name(s: M.State) -> String:
  match s:
    case M.Candidate{}:
      "candidate"
    case M.SandboxEvaluated{}:
      "sandbox_evaluated"
    case M.Shadowed{}:
      "shadowed"
    case M.Approved{}:
      "approved"
    case M.Active{}:
      "active"
    case M.Proven{}:
      "proven"
    case M.Retired{}:
      "retired"

def bit(b: Bool) -> String:
  match b:
    case True{}:
      "1"
    case False{}:
      "0"

def all_true() -> M.Pre:
  M.Pre{True{}, True{}, True{}, True{}}

def states() -> List<M.State>:
  [M.Candidate{}, M.SandboxEvaluated{}, M.Shadowed{}, M.Approved{}, M.Active{}, M.Proven{}, M.Retired{}]

def row(+f: M.State, +t: M.State, +cap: Bool) -> String:
  name(f) ++ " " ++ name(t) ++ " " ++ bit(cap) ++ " " ++ bit(M.decide(f, t, cap, all_true())) ++ "\n"

def rows_cap(ts: List<M.State>, +f: M.State, +cap: Bool) -> String:
  match ts:
    case Nil{}:
      ""
    case Con{t, rest}:
      row(f, t, cap) ++ rows_cap(rest, f, cap)

def rows_from(fs: List<M.State>) -> String:
  match fs:
    case Nil{}:
      ""
    case Con{+f, rest}:
      rows_cap(states(), f, False{}) ++ rows_cap(states(), f, True{}) ++ rows_from(rest)

def main() -> IO(Unit):
  do IO<Unit>:
    IO.print(rows_from(states()))
