"""Bend proof spike for the policy-lifecycle decision core (#278).

Links the Bend model under ``formal/bend/policy-lifecycle`` to the production
Python (``orchestrator/behavior/policy``) without changing it:

* canonical export + hash lock of ``states.py`` tables (drift detection);
* exhaustive differential check of the pure gates (legality, Captain);
* proof run (``bend PROOF.bend --verdict``);
* mutation controls: broken models/tables must be rejected;
* law integrity against a base ref (Captain-owned LAWS/SPEC files).

Scope boundary: the model abstracts evidence gates (prompt-eval, shadow,
shadow-present, proven-evidence) as booleans. The conformance table covers only
the two pure gates, so evidence-gate fidelity rests on the proofs plus code
review, not on execution of the Python gates.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest import mock

from orchestrator.behavior.policy import gates as policy_gates
from orchestrator.behavior.policy import states as policy_states
from orchestrator.formal.toolchain import Toolchain, discover

FORMAL_REL = Path("formal/bend/policy-lifecycle")
BEND_FILES = ("Model.bend", "SPEC.bend", "LAWS.bend", "PROOF.bend", "Conformance.bend")
CAPTAIN_OWNED = ("LAWS.bend", "SPEC.bend")
LOCK_NAME = "tables.lock.json"
EVIDENCE_REL = Path(".agent/evidence/bend-policy-proof-spike")
SCHEMA_VERSION = "1"

ALL_PROVED = "ALL PROOFS CHECK"


def control_root() -> Path:
    return Path(__file__).resolve().parents[2]


# --------------------------------------------------------------------------
# Tables, lock, drift
# --------------------------------------------------------------------------


def canonical_tables(
    states: frozenset[str] | None = None,
    transitions: dict[str, frozenset[str]] | None = None,
    captain_required: frozenset[str] | None = None,
) -> dict[str, Any]:
    states = policy_states.LIFECYCLE_STATES if states is None else states
    transitions = policy_states.TRANSITIONS if transitions is None else transitions
    captain_required = (
        policy_states.CAPTAIN_REQUIRED if captain_required is None else captain_required
    )
    return {
        "states": sorted(states),
        "transitions": {k: sorted(v) for k, v in sorted(transitions.items())},
        "captain_required": sorted(captain_required),
        "schema_version": policy_states.SCHEMA_VERSION,
    }


def tables_sha256(tables: dict[str, Any] | None = None) -> str:
    tables = canonical_tables() if tables is None else tables
    blob = json.dumps(tables, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def lock_path(root: Path) -> Path:
    return root / FORMAL_REL / LOCK_NAME


def write_lock(root: Path) -> dict[str, Any]:
    tables = canonical_tables()
    lock = {"tables_sha256": tables_sha256(tables), "tables": tables}
    lock_path(root).write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return lock


def check_drift(root: Path) -> dict[str, Any]:
    """Fail when states.py changed without re-proving and re-locking."""
    path = lock_path(root)
    actual = tables_sha256()
    if not path.is_file():
        return {"status": "fail", "reason": "lock file missing", "actual": actual}
    expected = json.loads(path.read_text(encoding="utf-8")).get("tables_sha256", "")
    if expected != actual:
        return {
            "status": "fail",
            "reason": "states.py tables differ from the proven lock; re-run proofs "
            "and `northstar formal lock policy-lifecycle`",
            "expected": expected,
            "actual": actual,
        }
    return {"status": "pass", "tables_sha256": actual}


# --------------------------------------------------------------------------
# Differential conformance (pure gates)
# --------------------------------------------------------------------------

Row = tuple[str, str, int]


def python_decisions() -> dict[Row, int]:
    """Accept (1) / reject (0) from the real Python gates, evidence assumed present."""
    out: dict[Row, int] = {}
    for f in sorted(policy_states.LIFECYCLE_STATES):
        for t in sorted(policy_states.LIFECYCLE_STATES):
            for cap in (0, 1):
                accept = policy_states.can_transition(f, t)
                if accept:
                    try:
                        policy_gates.require_captain_approved(t, captain_approved=bool(cap))
                    except policy_gates.PolicyGateError:
                        accept = False
                out[(f, t, cap)] = 1 if accept else 0
    return out


def parse_model_table(text: str) -> dict[Row, int]:
    rows: dict[Row, int] = {}
    for line in text.splitlines():
        parts = line.split()
        if not parts:
            continue
        if len(parts) != 4 or parts[2] not in {"0", "1"} or parts[3] not in {"0", "1"}:
            raise ValueError(f"unparseable conformance row: {line!r}")
        rows[(parts[0], parts[1], int(parts[2]))] = int(parts[3])
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
    nxt = text.find("\ndef ", start)
    nxt2 = text.find("\n# ", start)
    ends = [e for e in (nxt, nxt2) if e > 0]
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
    j = body.find(anchor, i)
    if j < 0:
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


def pre_ok_ignore(text: str, state: str, field: str) -> str:
    state = _camel(state)
    a, b = _function_slice(text, "pre_ok")
    body = text[a:b]
    i = body.find(f"    case {state}{{}}:")
    if i < 0:
        raise MutationError(f"pre_ok: no case {state}")
    old = f"          {field}\n"
    j = body.find(old, i)
    if j < 0:
        raise MutationError(f"pre_ok: field {field} not found under {state}")
    return text[:a] + body[:j] + "          True{}\n" + body[j + len(old):] + text[b:]


@dataclass(frozen=True)
class ModelMutant:
    mutant_id: str
    description: str
    apply: Callable[[str], str]


MODEL_MUTANTS: tuple[ModelMutant, ...] = (
    ModelMutant("skip-stage", "candidate -> active becomes legal",
                lambda s: set_legal(s, "candidate", "active", True)),
    ModelMutant("skip-shadow", "candidate -> approved becomes legal",
                lambda s: set_legal(s, "candidate", "approved", True)),
    ModelMutant("backward-edge", "approved -> candidate becomes legal",
                lambda s: set_legal(s, "approved", "candidate", True)),
    ModelMutant("retired-not-terminal", "retired -> candidate becomes legal",
                lambda s: _replace_in(s, "legal", "    case Retired{}:\n      False{}", "    case Retired{}:\n      True{}")),
    ModelMutant("drop-legal-gate", "decide ignores legality",
                lambda s: _replace_in(s, "decide", "legal(f, t)", "True{}")),
    ModelMutant("captain-drop-approved", "approved no longer needs the Captain",
                lambda s: set_captain_required(s, "approved", False)),
    ModelMutant("captain-drop-retired", "retired no longer needs the Captain",
                lambda s: set_captain_required(s, "retired", False)),
    ModelMutant("captain-ignored", "captain_ok always passes",
                lambda s: _replace_in(s, "captain_ok", "Bool.or(Bool.not(captain_required(t)), cap)", "True{}")),
    ModelMutant("evidence-drop-shadow-present", "approved no longer needs shadow_present",
                lambda s: pre_ok_ignore(s, "approved", "shadow_present")),
    ModelMutant("evidence-drop-proven", "proven no longer needs proven_ok",
                lambda s: pre_ok_ignore(s, "proven", "proven_ok")),
    ModelMutant("evidence-drop-eval", "sandbox_evaluated no longer needs eval_pass",
                lambda s: pre_ok_ignore(s, "sandbox_evaluated", "eval_pass")),
    ModelMutant("evidence-drop-shadow-ok", "shadowed no longer needs shadow_ok",
                lambda s: pre_ok_ignore(s, "shadowed", "shadow_ok")),
    ModelMutant("authority-granted", "a promotion sets approved_for_execution",
                lambda s: _replace_in(s, "finish", "Promoted{t, False{}, False{}}", "Promoted{t, True{}, False{}}")),
)


@dataclass(frozen=True)
class PythonMutant:
    mutant_id: str
    description: str
    transitions: dict[str, frozenset[str]] | None = None
    captain_required: frozenset[str] | None = None


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
    )


def _copy_formal(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for name in BEND_FILES:
        shutil.copy2(src / name, dst / name)


def run_model_mutants(
    tc: Toolchain, formal_dir: Path, baseline_py: dict[Row, int]
) -> list[dict[str, Any]]:
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
            if proofs["status"] != "pass":
                caught_by.append("proofs")
            try:
                model, _ = model_table(tc, work)
                if compare_tables(baseline_py, model):
                    caught_by.append("conformance")
            except RuntimeError:
                caught_by.append("conformance")
            failed = re.search(r"Location: (?:Laws\.)?(\S+)", proofs["output"])
            results.append({
                "mutant_id": m.mutant_id,
                "kind": "model",
                "description": m.description,
                "caught": bool(caught_by),
                "caught_by": caught_by,
                "first_failed_law": failed.group(1) if failed else "",
            })
    return results


def run_python_mutants(model: dict[Row, int]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for m in _python_mutants():
        with patched_python_tables(transitions=m.transitions, captain_required=m.captain_required):
            diffs = compare_tables(python_decisions(), model)
        caught_by = ["conformance"] if diffs else []
        results.append({
            "mutant_id": m.mutant_id,
            "kind": "python",
            "description": m.description,
            "caught": bool(caught_by),
            "caught_by": caught_by,
        })
    return results


def python_mutants_flag_drift(root: Path) -> list[dict[str, Any]]:
    """Each python mutant must also change the table hash (drift lock detects it)."""
    out = []
    lock = json.loads(lock_path(root).read_text(encoding="utf-8")).get("tables_sha256", "")
    for m in _python_mutants():
        mutated = tables_sha256(
            canonical_tables(transitions=m.transitions, captain_required=m.captain_required)
        )
        out.append({"mutant_id": m.mutant_id, "drift_detected": mutated != lock})
    return out


# --------------------------------------------------------------------------
# Law integrity
# --------------------------------------------------------------------------


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def law_integrity(root: Path, base_ref: str = "origin/main") -> dict[str, Any]:
    """Compare Captain-owned files with the base ref (gates come from main)."""
    files: dict[str, Any] = {}
    changed = False
    for name in CAPTAIN_OWNED:
        rel = (FORMAL_REL / name).as_posix()
        current = _sha256_file(root / rel)
        proc = subprocess.run(
            ["git", "show", f"{base_ref}:{rel}"],
            cwd=str(root), capture_output=True, check=False,
        )
        if proc.returncode != 0:
            files[name] = {"sha256": current, "base": "absent", "changed": False}
            continue
        base = hashlib.sha256(proc.stdout).hexdigest()
        differs = base != current
        changed = changed or differs
        files[name] = {"sha256": current, "base_sha256": base, "base": "present", "changed": differs}
    return {
        "base_ref": base_ref,
        "files": files,
        "changed": changed,
        "needs_captain_review": changed,
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
    base_ref: str = "origin/main",
    toolchain: Toolchain | None | str = "discover",
) -> dict[str, Any]:
    root = control_root() if root is None else root
    formal_dir = root / FORMAL_REL
    drift = check_drift(root)
    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": "bend-policy-lifecycle-check",
        "created_at": _now(),
        "drift": drift,
        "tables_sha256": tables_sha256(),
        "authority_mutation": False,
        "approved_for_execution": False,
    }
    tc = discover(root) if toolchain == "discover" else toolchain
    if tc is None:
        result["status"] = "fail" if require_tool else "skipped"
        result["reason"] = "Bend toolchain not found (set COMPASS_BEND_BIN or install under .agent/tools)"
        return result

    result["toolchain"] = {
        "bend_version": tc.version(),
        "bend_sha256": tc.binary_sha256(),
        "lean_version": tc.lean_version(),
    }
    result["files"] = {n: _sha256_file(formal_dir / n) for n in BEND_FILES}
    result["law_integrity"] = law_integrity(root, base_ref)

    result["proofs"] = run_proofs(tc, formal_dir, verdict=verdict)

    py = python_decisions()
    model, conf = model_table(tc, formal_dir)
    diffs = compare_tables(py, model)
    result["conformance"] = {
        "status": "pass" if not diffs else "fail",
        "rows": len(py),
        "diffs": diffs[:20],
        "seconds": conf["seconds"],
    }

    if mutations:
        mrows = run_model_mutants(tc, formal_dir, py) + run_python_mutants(model)
        drift_flags = python_mutants_flag_drift(root)
        caught = sum(1 for r in mrows if r["caught"])
        result["mutations"] = {
            "injected": len(mrows),
            "caught": caught,
            "caught_by_proofs": sum(1 for r in mrows if "proofs" in r["caught_by"]),
            "caught_by_conformance": sum(1 for r in mrows if "conformance" in r["caught_by"]),
            "uncaught": [r["mutant_id"] for r in mrows if not r["caught"]],
            "python_mutants_detected_by_drift_lock": sum(1 for d in drift_flags if d["drift_detected"]),
            "rows": mrows,
        }

    failures = []
    if drift["status"] != "pass":
        failures.append("drift")
    if result["proofs"]["status"] != "pass":
        failures.append("proofs")
    if result["conformance"]["status"] != "pass":
        failures.append("conformance")
    if mutations and result["mutations"]["uncaught"]:
        failures.append("mutations")
    result["status"] = "fail" if failures else "ok"
    result["failures"] = failures

    if write_evidence:
        out_dir = root / EVIDENCE_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "LATEST_check.json"
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result["evidence_path"] = str(path.relative_to(root))
    return result
