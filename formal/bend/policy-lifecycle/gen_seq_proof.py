#!/usr/bin/env python3
"""Generate whole-history P4/P5 proof bodies (appended into PROOF.bend).

Run: python3 gen_seq_proof.py >> after gen_proof.py output.

Sequence proofs case-split using the baseline transition/evidence tables.
Model mutants that only *restrict* decide (laws=()) strip these laws during
mutation testing; legality mutants may trip them (listed in LEGALITY_LAWS).
"""

from __future__ import annotations

STATES = [
    "Candidate",
    "SandboxEvaluated",
    "Shadowed",
    "Approved",
    "Active",
    "Proven",
    "Retired",
]
STAGE = {s: i for i, s in enumerate(STATES)}
LEGAL = {
    "Candidate": {"SandboxEvaluated", "Retired"},
    "SandboxEvaluated": {"Shadowed", "Retired"},
    "Shadowed": {"Approved", "Retired"},
    "Approved": {"Active", "Retired"},
    "Active": {"Proven", "Retired"},
    "Proven": {"Retired"},
    "Retired": set(),
}
NEEDS_CAP = {"Approved", "Active", "Proven", "Retired"}
EVID = {
    "SandboxEvaluated": "eval_pass",
    "Shadowed": "shadow_ok",
    "Approved": "shadow_present",
    "Proven": "proven_ok",
}
POST = {"Shadowed", "Approved", "Active", "Proven"}


def ind(n: int) -> str:
    return "  " * n


def nat_lit(n: int) -> str:
    return "0n" if n == 0 else "1n+" * n + "0n"


def emit_p4() -> list[str]:
    L: list[str] = []
    L.append("# P4': stage is non-decreasing under `run` (whole histories).")
    L.append(
        "def p4_from_stage(steps: M.Plan, +k: Nat, +s: M.State, "
        "bound: {S.le(k, S.stage(s)) == True{} : Bool}) -> "
        "{S.le(k, S.stage(M.run(steps, s))) == True{} : Bool}:"
    )
    L.append(f"{ind(1)}match steps:")
    L.append(f"{ind(2)}case M.NoMore{{}}:")
    L.append(f"{ind(3)}bound")
    L.append(f"{ind(2)}case M.Attempt{{h, tl}}:")
    L.append(f"{ind(3)}match h:")
    L.append(f"{ind(4)}case M.Step{{to, cap, pre}}:")
    L.append(f"{ind(5)}match to:")
    for to in STATES:
        L.append(f"{ind(6)}case M.{to}{{}}:")
        L.append(f"{ind(7)}match cap:")
        evid = EVID.get(to)
        for cv, cb in (("True", True), ("False", False)):
            L.append(f"{ind(8)}case {cv}{{}}:")
            L.append(f"{ind(9)}match pre:")
            L.append(f"{ind(10)}case M.Pre{{eval_pass, shadow_ok, shadow_present, proven_ok}}:")

            def body(d: int, flags: dict[str, bool]) -> list[str]:
                out = [f"{ind(d)}match k:"]

                def kcases(kd: int, kval: int) -> list[str]:
                    ko = [f"{ind(kd)}case 0n:", f"{ind(kd+1)}match s:"]
                    for s in STATES:
                        legal = to in LEGAL[s]
                        cap_ok = (to not in NEEDS_CAP) or cb
                        pre_ok = True if not evid else flags[evid]
                        ok = legal and cap_ok and pre_ok
                        nxt = to if ok else s
                        ko.append(f"{ind(kd+2)}case M.{s}{{}}:")
                        if kval <= STAGE[nxt]:
                            ko.append(
                                f"{ind(kd+3)}p4_from_stage(tl, {nat_lit(kval)}, M.{nxt}{{}}, {{==}})"
                            )
                        else:
                            ko.append(
                                f"{ind(kd+3)}p4_from_stage(tl, {nat_lit(kval)}, M.{nxt}{{}}, bound)"
                            )
                    if kval < 6:
                        ko.append(f"{ind(kd)}case 1n+p:")
                        ko.append(f"{ind(kd+1)}match p:")
                        ko.extend(kcases(kd + 2, kval + 1))
                    else:
                        ko.append(f"{ind(kd)}case 1n+p:")
                        ko.append(f"{ind(kd+1)}match s:")
                        for s in STATES:
                            legal = to in LEGAL[s]
                            cap_ok = (to not in NEEDS_CAP) or cb
                            pre_ok = True if not evid else flags[evid]
                            ok = legal and cap_ok and pre_ok
                            nxt = to if ok else s
                            ko.append(f"{ind(kd+2)}case M.{s}{{}}:")
                            ko.append(
                                f"{ind(kd+3)}p4_from_stage(tl, 1n+1n+1n+1n+1n+1n+1n+p, M.{nxt}{{}}, bound)"
                            )
                    return ko

                out.extend(kcases(d + 1, 0))
                return out

            if evid:
                L.append(f"{ind(11)}match {evid}:")
                for v, b in (("True", True), ("False", False)):
                    L.append(f"{ind(12)}case {v}{{}}:")
                    L.extend(body(13, {evid: b}))
            else:
                L.extend(body(11, {}))
    L.append("")
    L.append("def Laws.p4_forward_sequences(s, steps):")
    L.append(f"{ind(1)}match s:")
    for s in STATES:
        L.append(f"{ind(2)}case M.{s}{{}}:")
        L.append(
            f"{ind(3)}p4_from_stage(steps, {nat_lit(STAGE[s])}, M.{s}{{}}, {{==}})"
        )
    L.append("")
    return L


def emit_p5() -> list[str]:
    L: list[str] = []
    L.append("# P5': from birth, Approved implies shadowed appeared in the history.")
    L.append(
        "def p5_when_at_shadowed(steps: M.Plan) -> "
        "{S.implies(S.is_approved(M.run(steps, M.Shadowed{})), "
        "S.shadowed_in_run(steps, M.Shadowed{})) == True{} : Bool}:"
    )
    L.append(f"{ind(1)}match steps:")
    L.append(f"{ind(2)}case M.NoMore{{}}:")
    L.append(f"{ind(3)}{{==}}")
    L.append(f"{ind(2)}case M.Attempt{{h, tl}}:")
    L.append(f"{ind(3)}match h:")
    L.append(f"{ind(4)}case M.Step{{to, cap, pre}}:")
    L.append(f"{ind(5)}{{==}}")
    L.append("")
    L.append(
        "def p5_from(steps: M.Plan, +s: M.State) -> "
        "{S.implies(S.is_approved(M.run(steps, s)), "
        "Bool.or(S.post_shadow(s), S.shadowed_in_run(steps, s))) == True{} : Bool}:"
    )
    L.append(f"{ind(1)}match steps:")
    L.append(f"{ind(2)}case M.NoMore{{}}:")
    L.append(f"{ind(3)}match s:")
    for s in STATES:
        L.append(f"{ind(4)}case M.{s}{{}}:")
        L.append(f"{ind(5)}{{==}}")
    L.append(f"{ind(2)}case M.Attempt{{h, tl}}:")
    L.append(f"{ind(3)}match h:")
    L.append(f"{ind(4)}case M.Step{{to, cap, pre}}:")
    L.append(f"{ind(5)}match to:")
    for to in STATES:
        L.append(f"{ind(6)}case M.{to}{{}}:")
        L.append(f"{ind(7)}match cap:")
        evid = EVID.get(to)
        for cv, cb in (("True", True), ("False", False)):
            L.append(f"{ind(8)}case {cv}{{}}:")
            L.append(f"{ind(9)}match pre:")
            L.append(f"{ind(10)}case M.Pre{{eval_pass, shadow_ok, shadow_present, proven_ok}}:")

            def nest(d: int, flags: dict[str, bool]) -> list[str]:
                if evid and evid not in flags:
                    out = [f"{ind(d)}match {evid}:"]
                    for v, b in (("True", True), ("False", False)):
                        out.append(f"{ind(d+1)}case {v}{{}}:")
                        out.extend(nest(d + 2, {**flags, evid: b}))
                    return out
                out = [f"{ind(d)}match s:"]
                for s in STATES:
                    legal = to in LEGAL[s]
                    cap_ok = (to not in NEEDS_CAP) or cb
                    pre_ok = True if not evid else flags[evid]
                    ok = legal and cap_ok and pre_ok
                    nxt = to if ok else s
                    out.append(f"{ind(d+1)}case M.{s}{{}}:")
                    if s in POST:
                        out.append(f"{ind(d+2)}{{==}}")
                    elif nxt == "Shadowed":
                        out.append(f"{ind(d+2)}p5_when_at_shadowed(tl)")
                    else:
                        out.append(f"{ind(d+2)}p5_from(tl, M.{nxt}{{}})")
                return out

            L.extend(nest(11, {}))
    L.append("")
    L.append("def Laws.p5_shadow_before_approval_sequences(steps):")
    L.append(f"{ind(1)}p5_from(steps, M.Candidate{{}})")
    L.append("")
    return L


def main() -> None:
    print("\n".join(emit_p4() + emit_p5()))


if __name__ == "__main__":
    main()
