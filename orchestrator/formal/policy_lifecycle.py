"""Bend proof spike for the policy-lifecycle decision core (#278).

Links the Bend model under ``formal/bend/policy-lifecycle`` to the production
Python (``orchestrator/behavior/policy``) without changing it:

* the *structure* of ``promote_policy`` (which gates exist and which evidence
  gate guards which target state) is extracted from its source with ``ast``;
  the real ``can_transition`` / ``require_captain_approved`` supply the tables;
* an exhaustive differential check over all ``7 x 7 x 2 x 16`` inputs compares
  that Python reference with the Bend model;
* a hash lock pins the tables, that structure, and the law manifest (drift);
* the proofs run with the Lean kernel recheck (``bend PROOF.bend --verdict``);
* mutation controls: broken models, tables, and promote source must be rejected,
  and each proof-caught mutant must trip the *expected* law;
* law integrity: Captain-owned files are compared with a base ref (fail closed).

Boundaries (see the spike report): the evidence gates themselves (prompt-eval,
shadow, shadow-present, proven-evidence) are modeled as booleans, and gate
*order* inside ``promote_policy`` is pinned by the drift lock but not proved.
The direct-entry path (``ensure_policy_for_instruction``) is outside the model
and is probed separately as a known gap.
"""

from __future__ import annotations

import ast
import contextlib
import hashlib
import inspect
import itertools
import json
import os
import re
import shutil
import subprocess
import tempfile
import textwrap
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest import mock

from orchestrator.behavior.policy import gates as policy_gates
from orchestrator.behavior.policy import promote as policy_promote
from orchestrator.behavior.policy import states as policy_states
from orchestrator.formal.gates import require_bend_proof_enabled
from orchestrator.formal.toolchain import Toolchain, ToolchainError, discover, explicit_bin

FORMAL_REL = Path("formal/bend/policy-lifecycle")
BEND_FILES = ("Model.bend", "SPEC.bend", "LAWS.bend", "PROOF.bend", "Conformance.bend")
CAPTAIN_OWNED = ("LAWS.bend", "SPEC.bend")
LOCK_NAME = "tables.lock.json"
EVIDENCE_REL = Path(".agent/evidence/bend-policy-proof-spike")
SCHEMA_VERSION = "2"
ALL_PROVED = "ALL PROOFS CHECK"
PRE_FIELDS = ("eval_pass", "shadow_ok", "shadow_present", "proven_ok")

# promote_policy calls these per target state; each maps to one model precondition.
GATE_FIELD = {
    "require_prompt_eval_pass": "eval_pass",
    "run_shadow": "shadow_ok",
    "require_shadow_present": "shadow_present",
    "require_proven_evidence": "proven_ok",
}


def control_root() -> Path:
    return Path(__file__).resolve().parents[2]


# --------------------------------------------------------------------------
# promote_policy structure (ast)
# --------------------------------------------------------------------------


def structure_from_source(source: str) -> dict[str, Any]:
    """Which gates ``promote_policy`` applies, and the evidence gate per target."""
    tree = ast.parse(textwrap.dedent(source))
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef))

    def call_name(node: ast.Call) -> str:
        f = node.func
        return f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else ""

    calls = [(n.lineno, call_name(n)) for n in ast.walk(fn) if isinstance(n, ast.Call)]
    first = {}
    for lineno, name in sorted(calls):
        first.setdefault(name, lineno)

    evidence: dict[str, list[str]] = {}
    for node in ast.walk(fn):
        if not (isinstance(node, ast.If) and isinstance(node.test, ast.Compare)):
            continue
        cmp = node.test
        if not (
            isinstance(cmp.left, ast.Name) and cmp.left.id == "to_state"
            and len(cmp.ops) == 1 and isinstance(cmp.ops[0], ast.Eq)
            and isinstance(cmp.comparators[0], ast.Constant)
            and isinstance(cmp.comparators[0].value, str)
        ):
            continue
        fields = sorted({
            GATE_FIELD[call_name(c)]
            for c in ast.walk(node)
            if isinstance(c, ast.Call) and call_name(c) in GATE_FIELD
        })
        if fields:
            evidence[cmp.comparators[0].value] = sorted(set(evidence.get(cmp.comparators[0].value, [])) | set(fields))

    legality = "can_transition" in first
    captain = "require_captain_approved" in first
    evidence_lines = [first[n] for n in GATE_FIELD if n in first]
    order_ok = (
        legality and captain
        and first["can_transition"] < first["require_captain_approved"]
        and all(first["require_captain_approved"] < line for line in evidence_lines)
    )
    return {
        "legality": legality,
        "captain": captain,
        "evidence": dict(sorted(evidence.items())),
        "order_ok": bool(order_ok),
        # Coarse but honest: the extracted flags above only see *which* gates are called,
        # not their arguments, guards or the authority assignments. Pinning a hash of the
        # whole function makes any edit to promote_policy require a re-prove + re-lock.
        "ast_sha256": hashlib.sha256(_ast_canonical(fn).encode("utf-8")).hexdigest(),
    }


def _ast_canonical(node: Any) -> str:
    """Serialize an AST the same way on every Python version.

    ``ast.dump`` is not stable: 3.13 stopped printing ``None``/``[]`` fields, and
    new versions add empty fields (e.g. ``type_params``). Always omitting them
    keeps the lock hash identical between local and CI interpreters.
    """
    if isinstance(node, ast.AST):
        fields = []
        for name in node._fields:
            value = getattr(node, name, None)
            if value is None or value == []:
                continue
            fields.append(f"{name}={_ast_canonical(value)}")
        return f"{type(node).__name__}({','.join(fields)})"
    if isinstance(node, list):
        return "[" + ",".join(_ast_canonical(item) for item in node) + "]"
    return repr(node)


def promote_structure(source: str | None = None) -> dict[str, Any]:
    """Structure of ``promote_policy`` (or of ``source``, for mutants) plus binding identity."""
    structure = structure_from_source(inspect.getsource(policy_promote.promote_policy) if source is None else source)
    # The grid calls states.can_transition / gates.require_captain_approved; promote_policy
    # must be using those same objects, not a shadowed local or a different import.
    structure["bindings_ok"] = bool(
        getattr(policy_promote, "can_transition", None) is policy_states.can_transition
        and getattr(policy_promote, "require_captain_approved", None) is policy_gates.require_captain_approved
    )
    return structure


# --------------------------------------------------------------------------
# Tables, lock, drift
# --------------------------------------------------------------------------


def law_names(root: Path) -> dict[str, list[str]]:
    d = root / FORMAL_REL
    laws = re.findall(r"^law\s+(\w+)\s*:", (d / "LAWS.bend").read_text(encoding="utf-8"), re.M)
    proofs = re.findall(r"^def\s+Laws\.(\w+)\s*\(", (d / "PROOF.bend").read_text(encoding="utf-8"), re.M)
    return {"laws": sorted(laws), "proofs": sorted(proofs)}


def canonical_tables(
    states: frozenset[str] | None = None,
    transitions: dict[str, frozenset[str]] | None = None,
    captain_required: frozenset[str] | None = None,
    structure: dict[str, Any] | None = None,
) -> dict[str, Any]:
    states = policy_states.LIFECYCLE_STATES if states is None else states
    transitions = policy_states.TRANSITIONS if transitions is None else transitions
    captain_required = policy_states.CAPTAIN_REQUIRED if captain_required is None else captain_required
    return {
        "states": sorted(states),
        "transitions": {k: sorted(v) for k, v in sorted(transitions.items())},
        "captain_required": sorted(captain_required),
        "promote_structure": promote_structure() if structure is None else structure,
        "schema_version": SCHEMA_VERSION,
    }


def tables_sha256(tables: dict[str, Any] | None = None) -> str:
    tables = canonical_tables() if tables is None else tables
    blob = json.dumps(tables, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def lock_path(root: Path) -> Path:
    return root / FORMAL_REL / LOCK_NAME


def _atomic_write(path: Path, text: str) -> None:
    if path.is_symlink():
        raise OSError(f"refusing to write through symlink: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp, path)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(tmp)
        raise


# Files whose content links the proved `M.decide` to the printed conformance grid.
LOCKED_FILES = ("Model.bend", "Conformance.bend")


def locked_file_hashes(root: Path) -> dict[str, str]:
    d = root / FORMAL_REL
    return {n: hashlib.sha256((d / n).read_bytes()).hexdigest() for n in LOCKED_FILES}


def write_lock(root: Path) -> dict[str, Any]:
    require_bend_proof_enabled()
    tables = canonical_tables()
    lock = {
        "tables_sha256": tables_sha256(tables),
        "tables": tables,
        "laws": law_names(root)["laws"],
        "files_sha256": locked_file_hashes(root),
    }
    _atomic_write(lock_path(root), json.dumps(lock, indent=2, sort_keys=True) + "\n")
    return lock


def check_drift(root: Path) -> dict[str, Any]:
    """Fail when tables, the promote structure, or the law manifest changed unlocked."""
    path = lock_path(root)
    actual = tables_sha256()
    if not path.is_file():
        return {"status": "fail", "reason": "lock file missing", "actual": actual}
    lock = json.loads(path.read_text(encoding="utf-8"))
    problems = []
    if lock.get("tables_sha256", "") != actual:
        problems.append(
            "states.py tables or promote_policy gate structure differ from the proven lock; "
            "re-run proofs and `northstar formal lock policy-lifecycle`"
        )
    names = law_names(root)
    if names["laws"] != names["proofs"]:
        problems.append(f"law/proof mismatch: laws-only={sorted(set(names['laws']) - set(names['proofs']))} "
                        f"proofs-only={sorted(set(names['proofs']) - set(names['laws']))}")
    if names["laws"] != lock.get("laws", []):
        problems.append(
            f"law manifest changed vs lock: removed={sorted(set(lock.get('laws', [])) - set(names['laws']))} "
            f"added={sorted(set(names['laws']) - set(lock.get('laws', [])))}"
        )
    try:
        current_files = locked_file_hashes(root)
    except OSError as exc:
        current_files = {}
        problems.append(f"locked formal file unreadable: {exc}")
    if current_files and current_files != lock.get("files_sha256", {}):
        changed = sorted(n for n in LOCKED_FILES if current_files.get(n) != lock.get("files_sha256", {}).get(n))
        problems.append(f"{', '.join(changed)} changed since the lock; re-prove and re-lock (Captain reviews the lock diff)")
    if problems:
        return {"status": "fail", "reason": "; ".join(problems),
                "expected": lock.get("tables_sha256", ""), "actual": actual}
    return {"status": "pass", "tables_sha256": actual, "laws": names["laws"]}


# --------------------------------------------------------------------------
# Differential conformance
# --------------------------------------------------------------------------

Row = tuple[str, str, int, str]  # from, to, captain_approved, evidence bits (PRE_FIELDS order)
PRE_COMBOS = ["".join(map(str, bits)) for bits in itertools.product((0, 1), repeat=4)]


def python_decisions(structure: dict[str, Any] | None = None) -> dict[Row, int]:
    """Accept (1) / reject (0) as ``promote_policy`` would, given its gate structure.

    Legality and the Captain gate use the real ``can_transition`` /
    ``require_captain_approved``; which gates apply and which evidence guards
    which target come from the extracted structure.
    """
    st = promote_structure() if structure is None else structure
    out: dict[Row, int] = {}
    for f in sorted(policy_states.LIFECYCLE_STATES):
        for t in sorted(policy_states.LIFECYCLE_STATES):
            for cap in (0, 1):
                for bits in PRE_COMBOS:
                    pre = dict(zip(PRE_FIELDS, (b == "1" for b in bits)))
                    accept = True
                    if st["legality"]:
                        accept = accept and policy_states.can_transition(f, t)
                    if st["captain"] and accept:
                        try:
                            policy_gates.require_captain_approved(t, captain_approved=bool(cap))
                        except policy_gates.PolicyGateError:
                            accept = False
                    for field_name in st["evidence"].get(t, ()):
                        accept = accept and pre[field_name]
                    out[(f, t, cap, bits)] = 1 if accept else 0
    return out


def parse_model_table(text: str) -> dict[Row, int]:
    rows: dict[Row, int] = {}
    for line in text.splitlines():
        parts = line.split()
        if not parts:
            continue
        if (
            len(parts) != 5
            or parts[2] not in {"0", "1"}
            or not re.fullmatch(r"[01]{4}", parts[3])
            or parts[4] not in {"0", "1"}
        ):
            raise ValueError(f"unparseable conformance row: {line!r}")
        key = (parts[0], parts[1], int(parts[2]), parts[3])
        if key in rows:
            raise ValueError(f"duplicate conformance row: {key}")
        rows[key] = int(parts[4])
    return rows


def compare_tables(py: dict[Row, int], model: dict[Row, int]) -> list[str]:
    diffs: list[str] = []
    for key in sorted(set(py) | set(model)):
        if key not in model:
            diffs.append(f"missing in model: {key}")
        elif key not in py:
            diffs.append(f"missing in python: {key}")
        elif py[key] != model[key]:
            diffs.append(f"{key}: python={py[key]} model={model[key]}")
    return diffs


@contextlib.contextmanager
def patched_python_tables(
    *,
    transitions: dict[str, frozenset[str]] | None = None,
    captain_required: frozenset[str] | None = None,
) -> Iterator[None]:
    """Temporarily replace the tables the Python gates read (mutation controls)."""
    with contextlib.ExitStack() as stack:
        if transitions is not None:
            stack.enter_context(mock.patch.object(policy_states, "TRANSITIONS", transitions))
        if captain_required is not None:
            stack.enter_context(mock.patch.object(policy_states, "CAPTAIN_REQUIRED", captain_required))
            stack.enter_context(mock.patch.object(policy_gates, "CAPTAIN_REQUIRED", captain_required))
        yield


def model_table(tc: Toolchain, formal_dir: Path) -> tuple[dict[Row, int], dict[str, Any]]:
    res = tc.run(["Conformance.bend"], cwd=formal_dir, timeout=120)
    if res["exit_code"] != 0:
        raise RuntimeError(f"conformance program failed: {res['stderr'] or res['stdout']}")
    return parse_model_table(res["stdout"]), res


# --------------------------------------------------------------------------
# Proofs
# --------------------------------------------------------------------------


def run_proofs(tc: Toolchain, formal_dir: Path, *, verdict: bool = True) -> dict[str, Any]:
    args = ["PROOF.bend"] + (["--verdict"] if verdict else [])
    res = tc.run(args, cwd=formal_dir, timeout=900)
    passed = res["exit_code"] == 0 and ALL_PROVED in res["stdout"]
    return {
        "status": "pass" if passed else "fail",
        "verdict": verdict,
        "exit_code": res["exit_code"],
        "seconds": res["seconds"],
        "output": (res["stdout"] + res["stderr"]).strip()[-2000:],
        "command": res["command"],
    }


# --------------------------------------------------------------------------
# Mutation controls
# --------------------------------------------------------------------------


class MutationError(ValueError):
    """The anchor a mutant edits is absent (the model changed shape)."""


def _function_slice(text: str, name: str) -> tuple[int, int]:
    start = text.find(f"\ndef {name}(")
    if start < 0:
        raise MutationError(f"def {name} not found")
    start += 1
    ends = [e for e in (text.find("\ndef ", start), text.find("\n# ", start)) if e > 0]
    return start, (min(ends) if ends else len(text))


def _replace_in(text: str, name: str, old: str, new: str) -> str:
    a, b = _function_slice(text, name)
    body = text[a:b]
    if old not in body:
        raise MutationError(f"anchor not found in def {name}: {old!r}")
    return text[:a] + body.replace(old, new, 1) + text[b:]


def _camel(state: str) -> str:
    return "".join(part.capitalize() for part in state.split("_"))


def set_legal(text: str, f: str, t: str, value: bool) -> str:
    """Flip one edge of the model's ``legal`` table."""
    f, t = _camel(f), _camel(t)
    a, b = _function_slice(text, "legal")
    body = text[a:b]
    head = f"    case {f}{{}}:\n      match t:\n"
    i = body.find(head)
    if i < 0:
        raise MutationError(f"legal: no block for {f}")
    anchor = f"        case {t}{{}}:\n          "
    nxt = body.find("\n    case ", i + 1)
    j = body.find(anchor, i)
    if j < 0 or (0 < nxt < j):
        raise MutationError(f"legal: no case {t} under {f}")
    k = j + len(anchor)
    cur = "True{}" if body[k:].startswith("True{}") else "False{}"
    new = "True{}" if value else "False{}"
    return text[:a] + body[:k] + new + body[k + len(cur):] + text[b:]


def set_captain_required(text: str, t: str, value: bool) -> str:
    t = _camel(t)
    cur = "False{}" if value else "True{}"
    new = "True{}" if value else "False{}"
    return _replace_in(text, "captain_required", f"    case {t}{{}}:\n      {cur}", f"    case {t}{{}}:\n      {new}")


def pre_ok_edit(text: str, state: str, old: str, new: str) -> str:
    """Replace ``old`` with ``new`` inside pre_ok, within ``state``'s case only."""
    state = _camel(state)
    a, b = _function_slice(text, "pre_ok")
    body = text[a:b]
    i = body.find(f"    case {state}{{}}:")
    if i < 0:
        raise MutationError(f"pre_ok: no case {state}")
    nxt = body.find("\n    case ", i + 1)
    end = len(body) if nxt < 0 else nxt + 1
    seg = body[i:end]
    if old not in seg:
        raise MutationError(f"pre_ok: {old!r} not found under {state}")
    return text[:a] + body[:i] + seg.replace(old, new, 1) + body[end:] + text[b:]


_PRE_PAT = "        case Pre{eval_pass, shadow_ok, shadow_present, proven_ok}:\n"


def pre_ok_ignore(text: str, state: str, field: str) -> str:
    return pre_ok_edit(text, state, f"      match p:\n{_PRE_PAT}          {field}\n", "      True{}\n")


@dataclass(frozen=True)
class ModelMutant:
    mutant_id: str
    description: str
    apply: Callable[[str], str]
    laws: tuple[str, ...]  # law/lemma that may report the failure; () = proofs must still pass


LEGALITY_LAWS = ("p1_pipeline", "p3_terminal", "p4_forward_only", "p5_shadow_before_approval")

MODEL_MUTANTS: tuple[ModelMutant, ...] = (
    ModelMutant("skip-stage", "candidate -> active becomes legal",
                lambda s: set_legal(s, "candidate", "active", True), LEGALITY_LAWS),
    ModelMutant("skip-shadow", "candidate -> approved becomes legal",
                lambda s: set_legal(s, "candidate", "approved", True), LEGALITY_LAWS),
    ModelMutant("backward-edge", "approved -> candidate becomes legal",
                lambda s: set_legal(s, "approved", "candidate", True), LEGALITY_LAWS),
    ModelMutant("retired-not-terminal", "retired -> candidate becomes legal",
                lambda s: _replace_in(s, "legal", "    case Retired{}:\n      False{}", "    case Retired{}:\n      True{}"),
                LEGALITY_LAWS),
    ModelMutant("drop-legal-gate", "decide ignores legality",
                lambda s: _replace_in(s, "decide", "legal(f, t)", "True{}"), LEGALITY_LAWS),
    ModelMutant("always-reject", "decide rejects everything (vacuously satisfies every safety law)",
                lambda s: _replace_in(s, "decide", "Bool.and(legal(f, t), Bool.and(captain_ok(t, cap), pre_ok(t, p)))",
                                      "False{}"), ("p11_liveness",)),
    ModelMutant("captain-drop-approved", "approved no longer needs the Captain",
                lambda s: set_captain_required(s, "approved", False), ("p2_captain_gate",)),
    ModelMutant("captain-drop-retired", "retired no longer needs the Captain",
                lambda s: set_captain_required(s, "retired", False), ("p2_captain_gate",)),
    ModelMutant("captain-ignored", "captain_ok always passes",
                lambda s: _replace_in(s, "captain_ok", "Bool.or(Bool.not(captain_required(t)), cap)", "True{}"),
                ("p2_captain_gate",)),
    ModelMutant("evidence-drop-shadow-present", "approved no longer needs shadow_present",
                lambda s: pre_ok_ignore(s, "approved", "shadow_present"), ("p7c_approved_needs_shadow_present",)),
    ModelMutant("evidence-drop-proven", "proven no longer needs proven_ok",
                lambda s: pre_ok_ignore(s, "proven", "proven_ok"), ("p7d_proven_needs_proven_ok",)),
    ModelMutant("evidence-drop-eval", "sandbox_evaluated no longer needs eval_pass",
                lambda s: pre_ok_ignore(s, "sandbox_evaluated", "eval_pass"), ("p7a_sandbox_needs_eval_pass",)),
    ModelMutant("evidence-drop-shadow-ok", "shadowed no longer needs shadow_ok",
                lambda s: pre_ok_ignore(s, "shadowed", "shadow_ok"), ("p7b_shadowed_needs_shadow_ok",)),
    ModelMutant("authority-granted", "a promotion sets approved_for_execution",
                lambda s: _replace_in(s, "finish", "Promoted{t, False{}, False{}}", "Promoted{t, True{}, False{}}"),
                ("p6_no_authority_grant", "finish_no_authority")),
    # Mutants the first review round showed the original laws could not see.
    ModelMutant("next-ignores-gates", "a rejected attempt still moves the state when legal",
                lambda s: _replace_in(s, "next", "pick(decide(f, t, cap, p), t, f)", "pick(legal(f, t), t, f)"),
                ("p8a_rejected_stays", "next_rejected")),
    ModelMutant("run-ignores-next", "sequences stop applying attempts",
                lambda s: _replace_in(s, "run", "run(tl, next(s, to, cap, pre))", "run(tl, s)"),
                ("p9b_run_step",)),
    ModelMutant("finish-swapped", "accept and reject outcomes are swapped",
                lambda s: _replace_in(s, "finish", "    case True{}:\n      Promoted{t, False{}, False{}}\n    case False{}:\n      Rejected{}",
                                      "    case True{}:\n      Rejected{}\n    case False{}:\n      Promoted{t, False{}, False{}}"),
                ("p10_outcome_agrees", "outcome_lemma")),
    ModelMutant("finish-wrong-target", "a promotion lands on retired",
                lambda s: _replace_in(s, "finish", "Promoted{t, False{}, False{}}", "Promoted{Retired{}, False{}, False{}}"),
                ("p10_outcome_agrees", "outcome_lemma")),
    # Restrictive-direction mutants: safe for the laws, visible only to the evidence grid.
    ModelMutant("restrict-active-needs-eval", "active additionally requires eval_pass",
                lambda s: pre_ok_edit(s, "active", "      True{}\n", f"      match p:\n{_PRE_PAT}          eval_pass\n"), ()),
    ModelMutant("restrict-retired-needs-eval", "retired additionally requires eval_pass",
                lambda s: pre_ok_edit(s, "retired", "      True{}\n", f"      match p:\n{_PRE_PAT}          eval_pass\n"), ()),
    ModelMutant("restrict-approved-needs-eval", "approved additionally requires eval_pass",
                lambda s: pre_ok_edit(s, "approved", f"{_PRE_PAT}          shadow_present\n",
                                      f"{_PRE_PAT}          Bool.and(shadow_present, eval_pass)\n"), ()),
    ModelMutant("restrict-proven-needs-shadow", "proven additionally requires shadow_ok",
                lambda s: pre_ok_edit(s, "proven", f"{_PRE_PAT}          proven_ok\n",
                                      f"{_PRE_PAT}          Bool.and(proven_ok, shadow_ok)\n"), ()),
    ModelMutant("evidence-fields-swapped", "approved checks shadow_ok instead of shadow_present",
                lambda s: pre_ok_edit(s, "approved", f"{_PRE_PAT}          shadow_present\n",
                                      f"{_PRE_PAT}          shadow_ok\n"), ("p7c_approved_needs_shadow_present",)),
)


@dataclass(frozen=True)
class PythonMutant:
    mutant_id: str
    description: str
    transitions: dict[str, frozenset[str]] | None = None
    captain_required: frozenset[str] | None = None
    source_edit: tuple[str, str] | None = None  # (old, new) applied to promote_policy source
    grid_visible: bool = True  # False: behavior change the extractor/grid cannot see; only the lock can


def _python_mutants() -> tuple[PythonMutant, ...]:
    base = dict(policy_states.TRANSITIONS)
    skip = dict(base)
    skip["candidate"] = base["candidate"] | {"active"}
    gone = dict(base)
    gone["approved"] = base["approved"] - {"active"}
    revive = dict(base)
    revive["retired"] = frozenset({"candidate"})
    cap = policy_states.CAPTAIN_REQUIRED
    return (
        PythonMutant("py-skip-stage", "python: candidate -> active added", transitions=skip),
        PythonMutant("py-edge-removed", "python: approved -> active removed", transitions=gone),
        PythonMutant("py-retired-revived", "python: retired -> candidate added", transitions=revive),
        PythonMutant("py-captain-drop-approved", "python: approved leaves CAPTAIN_REQUIRED",
                     captain_required=cap - {"approved"}),
        PythonMutant("py-captain-drop-active", "python: active leaves CAPTAIN_REQUIRED",
                     captain_required=cap - {"active"}),
        PythonMutant("py-promote-no-captain-gate", "promote_policy no longer calls require_captain_approved",
                     source_edit=("require_captain_approved(to_state, captain_approved=captain_approved)", "pass")),
        PythonMutant("py-promote-no-shadow-present", "promote_policy no longer calls require_shadow_present",
                     source_edit=("require_shadow_present(policy)", "pass")),
        PythonMutant("py-promote-no-legality", "promote_policy no longer calls can_transition",
                     source_edit=("if not can_transition(from_state, to_state):", "if False:")),
        PythonMutant("py-promote-proven-gate-moved", "the proven evidence gate guards active instead",
                     source_edit=('if to_state == "proven":', 'if to_state == "active":')),
        # Evasions: same gates are *called*, behavior differs. Only the AST pin sees these.
        PythonMutant("py-evade-captain-arg-true", "captain gate is called but always passed True",
                     source_edit=("require_captain_approved(to_state, captain_approved=captain_approved)",
                                  "require_captain_approved(to_state, captain_approved=True)"),
                     grid_visible=False),
        PythonMutant("py-evade-legality-inverted", "legality check inverted",
                     source_edit=("if not can_transition(from_state, to_state):",
                                  "if can_transition(from_state, to_state):"), grid_visible=False),
        PythonMutant("py-evade-shadow-dead-call", "shadow-present gate called only under a dead conditional",
                     source_edit=("require_shadow_present(policy)",
                                  "require_shadow_present(policy) if False else None"), grid_visible=False),
        PythonMutant("py-evade-authority-flag", "promote sets approved_for_execution to True",
                     source_edit=('policy["approved_for_execution"] = False',
                                  'policy["approved_for_execution"] = True'), grid_visible=False),
        PythonMutant("py-evade-event-authority", "audit event records authority_mutation True",
                     source_edit=('"authority_mutation": False,', '"authority_mutation": True,'),
                     grid_visible=False),
        PythonMutant("py-evade-skip-write", "promoted policy is never written",
                     source_edit=("write_policy(repo_root, policy)\n    _sync", "pass\n    _sync"),
                     grid_visible=False),
    )


def _copy_formal(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for name in BEND_FILES:
        shutil.copy2(src / name, dst / name)


def run_model_mutants(tc: Toolchain, formal_dir: Path, baseline_py: dict[Row, int]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="bend-mutant-") as tmp:
        work = Path(tmp)
        for m in MODEL_MUTANTS:
            _copy_formal(formal_dir, work)
            original = (formal_dir / "Model.bend").read_text(encoding="utf-8")
            mutated = m.apply(original)
            if mutated == original:
                raise MutationError(f"mutant {m.mutant_id} did not change Model.bend")
            (work / "Model.bend").write_text(mutated, encoding="utf-8")
            proofs = run_proofs(tc, work, verdict=False)
            caught_by: list[str] = []
            failed_law = ""
            if proofs["status"] != "pass":
                found = re.search(r"Location: (?:Laws\.)?(\S+)", proofs["output"])
                failed_law = found.group(1) if found else ""
                if "SOME PROOFS FAIL" in proofs["output"] and failed_law:
                    caught_by.append("proofs")
            try:
                model, _ = model_table(tc, work)
                if compare_tables(baseline_py, model):
                    caught_by.append("conformance")
            except (RuntimeError, ValueError):
                caught_by.append("conformance")
            if m.laws:
                as_expected = "proofs" in caught_by and failed_law in m.laws
            else:
                as_expected = caught_by == ["conformance"]
            results.append({
                "mutant_id": m.mutant_id,
                "kind": "model",
                "description": m.description,
                "caught": bool(caught_by),
                "caught_by": caught_by,
                "first_failed_law": failed_law,
                "expected_laws": list(m.laws),
                "as_expected": as_expected,
            })
    return results


def run_python_mutants(model: dict[Row, int]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    base_src = inspect.getsource(policy_promote.promote_policy)
    for m in _python_mutants():
        structure = None
        if m.source_edit:
            old, new = m.source_edit
            if old not in base_src:
                raise MutationError(f"python mutant {m.mutant_id}: anchor missing in promote_policy")
            structure = promote_structure(base_src.replace(old, new, 1))
        with patched_python_tables(transitions=m.transitions, captain_required=m.captain_required):
            diffs = compare_tables(python_decisions(structure), model)
            drift = tables_sha256(canonical_tables(structure=structure)) != tables_sha256()
        caught_by = (["conformance"] if diffs else []) + (["drift-lock"] if drift else [])
        grid_saw_it = bool(diffs)
        results.append({
            "mutant_id": m.mutant_id,
            "kind": "python",
            "description": m.description,
            "caught": bool(caught_by),
            "caught_by": caught_by,
            "grid_visible": m.grid_visible,
            # A grid-visible mutant must be seen by the grid; an evasion must NOT be (that is
            # exactly why the AST pin exists) and must still trip the lock.
            "as_expected": bool(caught_by) and grid_saw_it == m.grid_visible,
        })
    return results


def python_mutants_flag_drift(root: Path) -> list[dict[str, Any]]:
    """Each python mutant must also change the lock hash (drift detects it)."""
    lock = json.loads(lock_path(root).read_text(encoding="utf-8")).get("tables_sha256", "")
    base_src = inspect.getsource(policy_promote.promote_policy)
    out = []
    for m in _python_mutants():
        structure = promote_structure(base_src.replace(*m.source_edit, 1)) if m.source_edit else None
        mutated = tables_sha256(canonical_tables(
            transitions=m.transitions, captain_required=m.captain_required, structure=structure))
        out.append({"mutant_id": m.mutant_id, "drift_detected": mutated != lock})
    return out


# --------------------------------------------------------------------------
# Law integrity
# --------------------------------------------------------------------------


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args], cwd=str(root), capture_output=True, check=False, timeout=60,
        env={k: v for k, v in os.environ.items() if not k.startswith("GIT_")},
    )


def law_integrity(root: Path, base_ref: str = "origin/main") -> dict[str, Any]:
    """Compare Captain-owned files with the base ref; fail closed on a bad ref.

    ``status`` is ``ok`` (compared), or ``error`` when the ref is unusable, in
    which case nothing was compared and callers must not treat it as clean.
    """
    if not base_ref or base_ref.startswith("-"):
        return {"status": "error", "base_ref": base_ref, "reason": "invalid base ref", "changed": None}
    try:
        verified = _git(root, "rev-parse", "--verify", "--quiet", "--end-of-options", f"{base_ref}^{{commit}}")
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "error", "base_ref": base_ref, "reason": str(exc), "changed": None}
    if verified.returncode != 0:
        return {"status": "error", "base_ref": base_ref, "reason": "base ref not found", "changed": None}
    verified_sha = verified.stdout.decode("utf-8", "replace").strip()

    files: dict[str, Any] = {}
    changed = False
    for name in CAPTAIN_OWNED:
        rel = (FORMAL_REL / name).as_posix()
        try:
            current = _sha256_file(root / rel)
        except OSError:
            current = "missing"
        listing = _git(root, "ls-tree", "--name-only", verified_sha, "--", rel)
        if listing.returncode != 0:
            return {"status": "error", "base_ref": base_ref, "reason": "git ls-tree failed", "changed": None}
        if not listing.stdout.strip():
            # First introduction of a Captain-owned file is itself a law change.
            files[name] = {"sha256": current, "base": "absent", "changed": True}
            changed = True
            continue
        proc = _git(root, "show", "--end-of-options", f"{verified_sha}:{rel}")
        if proc.returncode != 0:
            return {"status": "error", "base_ref": base_ref, "reason": "git show failed", "changed": None}
        base = hashlib.sha256(proc.stdout).hexdigest()
        differs = base != current  # includes "missing"
        changed = changed or differs
        files[name] = {"sha256": current, "base_sha256": base, "base": "present", "changed": differs}
    return {
        "status": "ok",
        "base_ref": base_ref,
        "files": files,
        "changed": changed,
        "needs_captain_review": changed,
    }


# --------------------------------------------------------------------------
# Known gap probe (not modeled): direct entry into a gated state
# --------------------------------------------------------------------------


def probe_direct_entry() -> dict[str, Any]:
    """Probe whether ``ensure_policy_for_instruction`` can skip into a gated state.

    Runs entirely in a temp dir. Production fix (#280): new policies always start
    at ``candidate``. ``bypass_observed`` should be False; a Bend entry-state law
    remains a #278 follow-up (still ``outside_model``).
    """
    from orchestrator.behavior.instructions import store as instr_store

    with tempfile.TemporaryDirectory(prefix="bend-probe-") as tmp:
        root = Path(tmp)
        doc = instr_store.build_instruction(
            title="direct-entry probe", body="probe", scope="proposal", approval_state="proven"
        )
        instr_store.write_instruction(root, doc)
        policy = policy_promote.ensure_policy_for_instruction(root, doc["instruction_id"])
    entered = str(policy.get("lifecycle_state"))
    bypass = (
        entered in policy_states.CAPTAIN_REQUIRED
        and not policy.get("captain_approved_at")
        and not policy.get("shadow_report_id")
    )
    return {
        "name": "direct-entry-bypass",
        "outside_model": True,
        "bypass_observed": bool(bypass),
        "entered_state": entered,
        "captain_approved_at": policy.get("captain_approved_at"),
        "shadow_report_id": policy.get("shadow_report_id"),
        "authority_flags_false": policy.get("approved_for_execution") is False
        and policy.get("authority_mutation") is False,
        "note": "Production (#280): ensure_policy_for_instruction always creates "
        "candidate. Formal entry-state law still outside the Bend model (#278).",
    }


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def check(
    root: Path | None = None,
    *,
    mutations: bool = True,
    verdict: bool = True,
    write_evidence: bool = True,
    require_tool: bool = False,
    strict_laws: bool = False,
    base_ref: str = "origin/main",
    toolchain: Toolchain | None | str = "discover",
) -> dict[str, Any]:
    require_bend_proof_enabled()
    root = control_root() if root is None else root
    formal_dir = root / FORMAL_REL
    drift = check_drift(root)
    integrity = law_integrity(root, base_ref)
    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": "bend-policy-lifecycle-check",
        "created_at": _now(),
        "drift": drift,
        "law_integrity": integrity,
        "tables_sha256": tables_sha256(),
        "promote_structure": promote_structure(),
        "authority_mutation": False,
        "approved_for_execution": False,
    }

    failures: list[str] = []
    if drift["status"] != "pass":
        failures.append("drift")
    if strict_laws and (integrity["status"] != "ok" or integrity["changed"]):
        failures.append("laws-unverified" if integrity["status"] != "ok" else "laws-changed-vs-base")

    try:
        tc = discover(root) if toolchain == "discover" else toolchain
    except ToolchainError as exc:
        result.update(status="fail", failures=failures + ["toolchain-untrusted"], reason=str(exc))
        return result

    if tc is None:
        explicit = explicit_bin()
        if explicit:
            failures.append("toolchain-explicit-missing")
            result["reason"] = f"COMPASS_BEND_BIN is not an executable file: {explicit}"
        elif require_tool:
            failures.append("toolchain-missing")
            result["reason"] = "Bend toolchain not found"
        else:
            result["reason"] = "Bend toolchain not found (set COMPASS_BEND_BIN or install under .agent/tools)"
        # Pure-Python checks still count: drift and strict law integrity.
        result["status"] = "fail" if failures else "skipped"
        result["failures"] = failures
        return result

    result["toolchain"] = {
        "bend_version": tc.version(),
        "bend_sha256": tc.binary_sha256(),
        "lean_version": tc.lean_version(),
        "pinned": bool((os.environ.get("COMPASS_BEND_SHA256") or "").strip()),
    }
    result["files"] = {n: _sha256_file(formal_dir / n) for n in BEND_FILES}

    result["proofs"] = run_proofs(tc, formal_dir, verdict=verdict)
    if result["proofs"]["status"] != "pass":
        failures.append("proofs")

    py = python_decisions()
    model, conf = model_table(tc, formal_dir)
    diffs = compare_tables(py, model)
    result["conformance"] = {
        "status": "pass" if not diffs else "fail",
        "rows": len(py),
        "model_rows": len(model),
        "diffs": diffs[:20],
        "seconds": conf["seconds"],
    }
    if diffs:
        failures.append("conformance")

    result["known_gaps"] = [probe_direct_entry()]

    if mutations:
        mrows = run_model_mutants(tc, formal_dir, py) + run_python_mutants(model)
        drift_flags = python_mutants_flag_drift(root)
        result["mutations"] = {
            "injected": len(mrows),
            "caught": sum(1 for r in mrows if r["caught"]),
            "caught_by_proofs": sum(1 for r in mrows if "proofs" in r["caught_by"]),
            "caught_by_conformance": sum(1 for r in mrows if "conformance" in r["caught_by"]),
            "uncaught": [r["mutant_id"] for r in mrows if not r["caught"]],
            "unexpected": [r["mutant_id"] for r in mrows if not r["as_expected"]],
            "python_mutants": sum(1 for r in mrows if r["kind"] == "python"),
            "python_mutants_detected_by_drift_lock": sum(1 for d in drift_flags if d["drift_detected"]),
            "rows": mrows,
        }
        if result["mutations"]["uncaught"] or result["mutations"]["unexpected"]:
            failures.append("mutations")

    skipped_components = [name for name, ran in (("verdict", verdict), ("mutations", mutations)) if not ran]
    result["skipped_components"] = skipped_components
    result["degraded"] = bool(skipped_components)
    result["status"] = "fail" if failures else ("partial" if skipped_components else "ok")
    result["failures"] = failures

    if write_evidence:
        path = root / EVIDENCE_REL / "LATEST_check.json"
        _atomic_write(path, json.dumps(result, indent=2, sort_keys=True) + "\n")
        result["evidence_path"] = str(path.relative_to(root))
    return result
