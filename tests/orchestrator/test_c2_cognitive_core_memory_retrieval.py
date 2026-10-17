"""C2 Cognitive Core — memory/retrieval context + hermetic gold-set."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
_FIXTURE_ROOT = ROOT / ".agent" / "tmp-c2-tests"
GOLDSET = ROOT / "tests" / "fixtures" / "brain-goldset" / "questions.json"

from orchestrator.cognitive.context import build_context
from orchestrator.cognitive.decisions import load_decision_entries, rank_decision_links
from orchestrator.cognitive.service import BrainServiceError, context, sync
from orchestrator.knowledge.index import write_index
from orchestrator.knowledge.ingest import items_from_decisions_md
from orchestrator.knowledge.store import write_knowledge_item
from orchestrator.schemas.validate import ValidationError, validate_document


def _mk_fixture_dir(prefix: str) -> Path:
    _FIXTURE_ROOT.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=prefix, dir=str(_FIXTURE_ROOT)))


_DECISIONS_MD = """# Decisions

## ADR-078: Plan-approval hook PEP604 + approve→PR standing order (v1.60.1)

- **Status:** Accepted
- **Context:** Hook crash on Python <3.10; Captain standing order that plan
  approval includes commit + open PR. Never auto rewrite canonical memory docs.
- **Decision:** Add `from __future__ import annotations`; document standing order.

## ADR-077: Cognitive Core C1 Source of Truth (v1.60.0)

- **Status:** Accepted
- **Context:** Durable SHA-cited project-state snapshot freshness independent of chat.
  COMPASS_BRAIN_ENABLED gate fail closed. Always approved_for_execution false and
  authority_mutation false. Adaptive Intelligence routing deferred C5; REA deep
  analysis deferred C6. Rollback checkpoint feature branch policy retained.
- **Decision:** Gated northstar brain sync status show; repository SHA cited citations observed.

## ADR-076: Behavior Loop Operator Closure (v1.59.0 M54)

- **Status:** Accepted
- Behavior loop operator closure exemplars and provenance wiring.

## ADR-075: Prompt/Policy Provenance + Behavior Exemplars (v1.58.0 M53)

- **Status:** Accepted
- Prompt policy provenance execution ledger under evaluations.

## ADR-073: Kimi K3 Project Overseer (v1.56.0 M51)

- **Status:** Accepted
- M51 Kimi Project Overseer read-oriented status surface; no authority mutation.

## ADR-074: Overseer Skill + Live StatusProvider (v1.57.0 M52)

- **Status:** Accepted
- M52 overseer skill live status provider; Project Overseer status snapshot authority remains false.

## ADR-079: Cognitive Core C2 Memory and Retrieval (v1.61.0)

- **Status:** Accepted
- Memory retrieval hybrid search gold set; IMPLEMENTATION_PLAN status APPROVED gate retained.
"""

_EXTRA_KNOWLEDGE = [
    {
        "title": "Hybrid knowledge search vector experience",
        "summary": "M6 hybrid knowledge search vector experience store with TF-IDF fallback.",
        "keywords": ["hybrid", "knowledge", "search", "vector", "experience"],
        "path": "docs/plans/M6_VECTOR.md",
        "kind": "knowledge",
    },
    {
        "title": "Knowledge steward ingest decisions markdown",
        "summary": "Knowledge steward ingest decisions markdown ADR headings into store.",
        "keywords": ["knowledge", "steward", "ingest", "decisions", "markdown"],
        "path": "orchestrator/knowledge/ingest.py",
        "kind": "knowledge",
    },
    {
        "title": "Filesystem gated context inodes",
        "summary": "M40 filesystem gated context inodes walk routes safely.",
        "keywords": ["filesystem", "gated", "context", "inodes"],
        "path": "docs/plans/M40_FILESYSTEM_GATED_CONTEXT.md",
        "kind": "knowledge",
    },
    {
        "title": "Captain Handbook skills library fill",
        "summary": "M55 Captain Handbook skills library fill A1 runbook.",
        "keywords": ["captain", "handbook", "skills", "library", "fill"],
        "path": "docs/guides/captain-handbook.md",
        "kind": "knowledge",
    },
    {
        "title": "Wave 1 Stars Skills packaging goose security",
        "summary": "Wave 1 Stars Skills packaging goose security-audit procedures promoted.",
        "keywords": ["wave", "stars", "skills", "packaging", "goose", "security"],
        "path": "docs/guides/skills-library-fill-a1.md",
        "kind": "knowledge",
    },
    {
        "title": "Skill learning loop promote candidate",
        "summary": "Skill learning loop promote candidate remains Captain-gated.",
        "keywords": ["skill", "learning", "loop", "promote", "candidate"],
        "path": "docs/guides/skills-learning.md",
        "kind": "knowledge",
    },
    {
        "title": "Capability planning task graph manifests",
        "summary": "Capability planning task graph manifests for implementation plans.",
        "keywords": ["capability", "planning", "task", "graph", "manifests"],
        "path": "orchestrator/plan_writer/build.py",
        "kind": "knowledge",
    },
    {
        "title": "Doctor script schema project-state brain",
        "summary": "Doctor script schema project-state brain checks for Cognitive Core.",
        "keywords": ["doctor", "script", "schema", "project-state", "brain"],
        "path": "scripts/doctor.sh",
        "kind": "knowledge",
    },
    {
        "title": "Evidence under agent evidence validation",
        "summary": "Evidence under .agent/evidence validation reports for each milestone.",
        "keywords": ["evidence", "agent", "validation"],
        "path": ".agent/evidence/README.md",
        "kind": "knowledge",
    },
    {
        "title": "VERSION northstar release cognitive core",
        "summary": "VERSION northstar release cognitive core tracking for C1/C2.",
        "keywords": ["version", "northstar", "release", "cognitive", "core"],
        "path": "VERSION",
        "kind": "knowledge",
    },
    {
        "title": "COMPASS_BRAIN_ENABLED gate fail closed",
        "summary": "COMPASS_BRAIN_ENABLED gate fail closed when unset for brain CLI.",
        "keywords": ["compass_brain_enabled", "gate", "fail", "closed"],
        "path": "orchestrator/cognitive/enabled.py",
        "kind": "knowledge",
    },
    {
        "title": "northstar brain sync status show context",
        "summary": "northstar brain sync status show and context operator surface.",
        "keywords": ["northstar", "brain", "sync", "status", "show", "context"],
        "path": "scripts/run-brain.sh",
        "kind": "knowledge",
    },
]


def _write_extra_items(repo: Path) -> None:
    from orchestrator.knowledge.ingest import _base_item

    for idx, spec in enumerate(_EXTRA_KNOWLEDGE, start=1):
        item = _base_item(
            item_id=f"know-c2-fixture-{idx:02d}",
            kind=spec["kind"],
            title=spec["title"],
            summary=spec["summary"],
            source_type="fixture",
            source_id=f"c2-{idx:02d}",
            source_path=spec["path"],
            keywords=spec["keywords"],
            confidence=0.85,
            provenance={"fixture": "c2-goldset"},
        )
        write_knowledge_item(repo, item)


def _seed_repo(repo: Path, *, version: str = "1.61.0") -> None:
    (repo / "VERSION").write_text(f"{version}\n", encoding="utf-8")
    for name in (
        "AGENTS.md",
        "PROJECT_CONTEXT.md",
        "PROGRESS.md",
        "TESTING.md",
        "IMPLEMENTATION_PLAN.md",
    ):
        (repo / name).write_text(
            f"# {name}\n\nIMPLEMENTATION_PLAN status APPROVED gate.\n",
            encoding="utf-8",
        )
    (repo / "DECISIONS.md").write_text(_DECISIONS_MD, encoding="utf-8")
    (repo / "IMPLEMENTATION_PLAN.md").write_text(
        "# Plan\n\n- Status: APPROVED\n\n"
        "| Field | Value |\n|---|---|\n"
        "| Plan ID | `c2-cognitive-core-memory-retrieval` |\n",
        encoding="utf-8",
    )
    proc = subprocess.run(
        ["git", "init"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git init failed: {proc.stderr or proc.stdout}")
    subprocess.run(
        ["git", "config", "user.email", "c2@test.local"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "C2 Test"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "commit.gpgsign=false", "commit", "-m", "seed"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    for item in items_from_decisions_md(_DECISIONS_MD, "DECISIONS.md"):
        write_knowledge_item(repo, item)
    _write_extra_items(repo)
    write_index(repo)


def _is_evidence_linked(doc: dict) -> bool:
    """Query-grounded only — snapshot/git alone does not count."""
    return bool(doc.get("hits") or doc.get("decision_links"))


def _expect_satisfied(doc: dict, expect: list[str]) -> bool:
    kinds: set[str] = set()
    if doc.get("hits"):
        kinds.add("knowledge")
        for hit in doc["hits"]:
            if hit.get("kind") == "decision":
                kinds.add("decision")
    if doc.get("decision_links"):
        kinds.add("decision")
    for cite in doc.get("citations") or []:
        kind = cite.get("kind")
        if kind in {"knowledge", "decision", "snapshot"}:
            kinds.add(str(kind))
    return set(expect).issubset(kinds)


class DecisionLinkTests(unittest.TestCase):
    def test_load_and_rank_adrs(self) -> None:
        repo = _mk_fixture_dir("c2-decisions-")
        try:
            (repo / "DECISIONS.md").write_text(_DECISIONS_MD, encoding="utf-8")
            entries = load_decision_entries(repo)
            self.assertGreaterEqual(len(entries), 5)
            links = rank_decision_links(repo, "Cognitive Core project-state", top_n=3)
            self.assertTrue(links)
            self.assertTrue(any("adr-077" in l["adr_id"] for l in links))
            self.assertEqual(links[0]["claim_kind"], "documented")
        finally:
            pass


class ContextSchemaTests(unittest.TestCase):
    def test_context_schema_locks_authority(self) -> None:
        doc = {
            "schema_version": "1",
            "query": "test",
            "mode": "keyword",
            "freshness": "fresh",
            "repository_sha": "abc",
            "citations": [],
            "hits": [],
            "decision_links": [],
            "approved_for_execution": False,
            "authority_mutation": False,
        }
        validate_document(doc, "brain-context-response.schema.json")
        bad = dict(doc)
        bad["approved_for_execution"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad, "brain-context-response.schema.json")
        bad2 = dict(doc)
        bad2["authority_mutation"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad2, "brain-context-response.schema.json")

    def test_invalid_mode_rejected(self) -> None:
        repo = _mk_fixture_dir("c2-mode-")
        try:
            _seed_repo(repo)
            with mock.patch.dict(os.environ, {"COMPASS_BRAIN_ENABLED": "1"}):
                with self.assertRaises(BrainServiceError):
                    context(repo, query="anything", mode="foobar")
        finally:
            pass


class ContextServiceTests(unittest.TestCase):
    def test_gate_required(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_BRAIN_ENABLED", None)
            with self.assertRaises(PermissionError):
                context(ROOT, query="anything")

    def test_context_composes_state_knowledge_decisions(self) -> None:
        repo = _mk_fixture_dir("c2-ctx-")
        try:
            _seed_repo(repo)
            with mock.patch.dict(os.environ, {"COMPASS_BRAIN_ENABLED": "1"}):
                sync(repo)
                doc = context(
                    repo,
                    query="Cognitive Core project-state snapshot freshness",
                    mode="keyword",
                    top_n=10,
                )
            validate_document(doc, "brain-context-response.schema.json")
            self.assertEqual(doc["approved_for_execution"], False)
            self.assertEqual(doc["authority_mutation"], False)
            self.assertIn(doc["freshness"], {"fresh", "stale", "no_snapshot"})
            self.assertTrue(doc["decision_links"] or doc["hits"])
            self.assertTrue(_is_evidence_linked(doc))
            cite_kinds = {c["kind"] for c in doc["citations"]}
            self.assertTrue(cite_kinds & {"decision", "knowledge", "git", "snapshot"})
        finally:
            pass

    def test_cli_context(self) -> None:
        repo = _mk_fixture_dir("c2-cli-")
        try:
            _seed_repo(repo)
            env = os.environ.copy()
            env["COMPASS_BRAIN_ENABLED"] = "1"
            env["PYTHONPATH"] = str(ROOT)
            sync_proc = subprocess.run(
                [
                    str(ROOT / "scripts" / "run-brain.sh"),
                    "sync",
                    "--repo-root",
                    str(repo),
                ],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(sync_proc.returncode, 0, sync_proc.stderr)
            proc = subprocess.run(
                [
                    str(ROOT / "scripts" / "run-brain.sh"),
                    "context",
                    "--query",
                    "ADR-077 source of truth brain sync",
                    "--mode",
                    "keyword",
                    "--repo-root",
                    str(repo),
                ],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertTrue(payload.get("decision_links"))
            self.assertFalse(payload.get("approved_for_execution"))
        finally:
            pass

    def test_cli_requires_query(self) -> None:
        env = os.environ.copy()
        env["COMPASS_BRAIN_ENABLED"] = "1"
        proc = subprocess.run(
            [str(ROOT / "scripts" / "run-brain.sh"), "context"],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)

    def test_empty_query_errors(self) -> None:
        repo = _mk_fixture_dir("c2-empty-")
        try:
            _seed_repo(repo)
            with mock.patch.dict(os.environ, {"COMPASS_BRAIN_ENABLED": "1"}):
                with self.assertRaises(BrainServiceError):
                    context(repo, query="   ")
        finally:
            pass


class GoldSetTests(unittest.TestCase):
    def test_goldset_evidence_linked_rate(self) -> None:
        spec = json.loads(GOLDSET.read_text(encoding="utf-8"))
        questions = spec["questions"]
        self.assertEqual(len(questions), 30)
        target = float(spec["target_evidence_linked_rate"])

        repo = _mk_fixture_dir("c2-gold-")
        try:
            _seed_repo(repo)
            with mock.patch.dict(os.environ, {"COMPASS_BRAIN_ENABLED": "1"}):
                sync(repo)
                linked = 0
                failures: list[str] = []
                expect_failures: list[str] = []
                for q in questions:
                    doc = build_context(
                        repo,
                        q["query"],
                        mode="keyword",
                        top_n=10,
                    )
                    ok = _is_evidence_linked(doc) and bool(doc.get("evidence_linked"))
                    if ok:
                        linked += 1
                    else:
                        failures.append(q["id"])
                    if not _expect_satisfied(doc, list(q.get("expect") or [])):
                        expect_failures.append(q["id"])
            rate = linked / len(questions)
            self.assertGreaterEqual(
                rate,
                target,
                f"evidence-linked rate {rate:.2%} < {target:.0%}; "
                f"failures={failures}",
            )
            self.assertEqual(
                expect_failures,
                [],
                f"expect citation kinds unmet: {expect_failures}",
            )
        finally:
            pass

    def test_negative_queries_not_evidence_linked(self) -> None:
        spec = json.loads(GOLDSET.read_text(encoding="utf-8"))
        negatives = spec.get("negatives") or []
        self.assertGreaterEqual(len(negatives), 3)
        repo = _mk_fixture_dir("c2-neg-")
        try:
            _seed_repo(repo)
            with mock.patch.dict(os.environ, {"COMPASS_BRAIN_ENABLED": "1"}):
                sync(repo)
                for n in negatives:
                    doc = build_context(
                        repo,
                        n["query"],
                        mode="keyword",
                        top_n=10,
                    )
                    self.assertFalse(
                        doc.get("evidence_linked"),
                        f"{n['id']} unexpectedly evidence_linked",
                    )
                    self.assertFalse(_is_evidence_linked(doc))
        finally:
            pass

    def test_nonsense_query_after_sync_not_linked(self) -> None:
        repo = _mk_fixture_dir("c2-nonsense-")
        try:
            _seed_repo(repo)
            with mock.patch.dict(os.environ, {"COMPASS_BRAIN_ENABLED": "1"}):
                sync(repo)
                doc = build_context(
                    repo,
                    "zzzzqyxwvut nebula quark xylophone",
                    mode="keyword",
                    top_n=5,
                )
            self.assertTrue(doc.get("snapshot_id"))
            self.assertFalse(doc.get("evidence_linked"))
        finally:
            pass


if __name__ == "__main__":
    unittest.main()
