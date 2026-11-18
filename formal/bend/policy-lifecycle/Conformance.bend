# Conformance table for the policy lifecycle model.
#
# Prints one line per (from, to, captain_approved, evidence) combination:
#   <from> <to> <cap:0|1> <eval_pass shadow_ok shadow_present proven_ok: 4 bits> <accept:0|1>
# Exhaustive over all 7 x 7 x 2 x 16 inputs. orchestrator/formal/policy_lifecycle.py
# compares this output with the Python decision structure of promote_policy.

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

def pre_bits(p: M.Pre) -> String:
  match p:
    case M.Pre{eval_pass, shadow_ok, shadow_present, proven_ok}:
      bit(eval_pass) ++ bit(shadow_ok) ++ bit(shadow_present) ++ bit(proven_ok)

def states() -> List<M.State>:
  [M.Candidate{}, M.SandboxEvaluated{}, M.Shadowed{}, M.Approved{}, M.Active{}, M.Proven{}, M.Retired{}]

def pres() -> List<M.Pre>:
  [M.Pre{False{}, False{}, False{}, False{}},
   M.Pre{False{}, False{}, False{}, True{}},
   M.Pre{False{}, False{}, True{}, False{}},
   M.Pre{False{}, False{}, True{}, True{}},
   M.Pre{False{}, True{}, False{}, False{}},
   M.Pre{False{}, True{}, False{}, True{}},
   M.Pre{False{}, True{}, True{}, False{}},
   M.Pre{False{}, True{}, True{}, True{}},
   M.Pre{True{}, False{}, False{}, False{}},
   M.Pre{True{}, False{}, False{}, True{}},
   M.Pre{True{}, False{}, True{}, False{}},
   M.Pre{True{}, False{}, True{}, True{}},
   M.Pre{True{}, True{}, False{}, False{}},
   M.Pre{True{}, True{}, False{}, True{}},
   M.Pre{True{}, True{}, True{}, False{}},
   M.Pre{True{}, True{}, True{}, True{}}]

def row(+f: M.State, +t: M.State, +cap: Bool, +p: M.Pre) -> String:
  name(f) ++ " " ++ name(t) ++ " " ++ bit(cap) ++ " " ++ pre_bits(p) ++ " " ++ bit(M.decide(f, t, cap, p)) ++ "\n"

def rows_pre(ps: List<M.Pre>, +f: M.State, +t: M.State, +cap: Bool) -> String:
  match ps:
    case Nil{}:
      ""
    case Con{+p, rest}:
      row(f, t, cap, p) ++ rows_pre(rest, f, t, cap)

def rows_to(ts: List<M.State>, +f: M.State) -> String:
  match ts:
    case Nil{}:
      ""
    case Con{+t, rest}:
      rows_pre(pres(), f, t, False{}) ++ rows_pre(pres(), f, t, True{}) ++ rows_to(rest, f)

def rows_from(fs: List<M.State>) -> String:
  match fs:
    case Nil{}:
      ""
    case Con{+f, rest}:
      rows_to(states(), f) ++ rows_from(rest)

def main() -> IO(Unit):
  do IO<Unit>:
    IO.print(rows_from(states()))
