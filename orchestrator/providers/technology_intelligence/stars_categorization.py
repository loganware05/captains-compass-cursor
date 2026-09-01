"""Offline batch categorization for GitHub starred repositories (M14).

Trains a lightweight multinomial Naive Bayes classifier from Captain manual
labels (fixture-derived) and categorizes starred repo records for TI planning.
"""

from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

_TOKEN = re.compile(r"[a-z0-9]{2,}", re.I)

DEFAULT_CATEGORIES = (
    "frontend-ui",
    "backend-library",
    "devtool",
    "ml-data",
    "other",
)

DEFAULT_LABELS_FIXTURE = (
    Path(__file__).resolve().parents[3]
    / "tests"
    / "fixtures"
    / "ti"
    / "github-stars-labels"
    / "manual-labels.json"
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def categorized_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "ti" / "github-stars-categorized"


def categorized_path(repo_root: Path) -> Path:
    return categorized_dir(repo_root) / "categorized.json"


def tokenize(text: str) -> list[str]:
    return [match.group(0).lower() for match in _TOKEN.finditer(text or "")]


def repo_feature_text(repo: dict) -> str:
    topics = repo.get("topics") or repo.get("topics_redacted") or []
    if isinstance(topics, list) and topics and isinstance(topics[0], dict):
        topics = [str(t.get("name") or "") for t in topics if isinstance(t, dict)]
    return " ".join(
        [
            str(repo.get("full_name") or ""),
            str(repo.get("description") or ""),
            " ".join(str(t) for t in topics),
        ]
    )


def load_manual_labels(path: Path | None = None) -> list[dict]:
    labels_path = path or DEFAULT_LABELS_FIXTURE
    if not labels_path.is_file():
        return []
    with labels_path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list):
        return []
    labels: list[dict] = []
    for row in payload:
        if not isinstance(row, dict):
            continue
        full_name = str(row.get("full_name") or "").strip()
        category = str(row.get("category") or "").strip()
        if full_name and category:
            labels.append(dict(row))
    return labels


def train_naive_bayes(
    labeled_rows: list[dict],
    *,
    categories: tuple[str, ...] = DEFAULT_CATEGORIES,
) -> dict:
    """Train token log-probabilities per category from manual labels."""
    category_docs: dict[str, list[list[str]]] = {cat: [] for cat in categories}
    for row in labeled_rows:
        category = str(row.get("category") or "other")
        if category not in category_docs:
            category_docs[category] = []
        tokens = tokenize(repo_feature_text(row))
        if tokens:
            category_docs[category].append(tokens)

    category_docs = {cat: docs for cat, docs in category_docs.items() if docs}
    total_docs = sum(len(docs) for docs in category_docs.values()) or 1
    vocab: set[str] = set()
    token_counts: dict[str, dict[str, int]] = {cat: {} for cat in category_docs}
    for cat, docs in category_docs.items():
        for doc in docs:
            vocab.update(doc)
        for doc in docs:
            seen: set[str] = set()
            for token in doc:
                if token in seen:
                    continue
                seen.add(token)
                token_counts[cat][token] = token_counts[cat].get(token, 0) + 1

    vocab_size = max(len(vocab), 1)
    log_priors = {
        cat: math.log(len(docs) / total_docs) for cat, docs in category_docs.items()
    }
    log_likelihoods: dict[str, dict[str, float]] = {}
    for cat in category_docs:
        denom = sum(token_counts[cat].values()) + vocab_size
        log_likelihoods[cat] = {
            token: math.log((token_counts[cat].get(token, 0) + 1) / denom) for token in vocab
        }
        log_likelihoods[cat]["__default__"] = math.log(1 / denom)

    return {
        "categories": list(category_docs.keys()),
        "log_priors": log_priors,
        "log_likelihoods": log_likelihoods,
        "vocab": sorted(vocab),
        "trained_from": len(labeled_rows),
        "trained_at": _utc_now(),
    }


def predict_category(model: dict, repo: dict) -> tuple[str, float]:
    """Return (category, confidence) for a GitHub API-shaped repo record."""
    tokens = tokenize(repo_feature_text(repo))
    if not tokens:
        return "other", 0.0
    categories = model.get("categories") or list(DEFAULT_CATEGORIES)
    log_priors = model.get("log_priors") or {}
    log_likelihoods = model.get("log_likelihoods") or {}
    best_cat = "other"
    best_score = float("-inf")
    for cat in categories:
        score = float(log_priors.get(cat, math.log(1 / max(len(categories), 1))))
        cat_ll = log_likelihoods.get(cat) or {}
        default_ll = float(cat_ll.get("__default__", math.log(0.001)))
        for token in tokens:
            score += float(cat_ll.get(token, default_ll))
        if score > best_score:
            best_score = score
            best_cat = cat
    # Convert log score to a rough confidence in (0,1]
    confidence = round(1 / (1 + math.exp(-best_score / max(len(tokens), 1))), 4)
    return str(best_cat), confidence


def categorize_records(
    repos: list[dict],
    *,
    model: dict | None = None,
    labels: list[dict] | None = None,
) -> list[dict]:
    """Attach predicted category metadata to repo records."""
    labels = labels if labels is not None else load_manual_labels()
    model = model if model is not None else train_naive_bayes(labels)
    categorized: list[dict] = []
    for repo in repos:
        if not isinstance(repo, dict):
            continue
        category, confidence = predict_category(model, repo)
        row = dict(repo)
        row["star_category"] = category
        row["star_category_confidence"] = confidence
        row["star_category_model"] = "naive-bayes-manual-labels-v1"
        categorized.append(row)
    return categorized


def write_categorized_envelope(
    repo_root: Path,
    records: list[dict],
    *,
    model: dict,
    source: str,
) -> Path:
    repo_root = Path(repo_root)
    path = categorized_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    envelope = {
        "categorized_at": _utc_now(),
        "source": source,
        "record_count": len(records),
        "model": {
            "kind": "naive-bayes-manual-labels-v1",
            "trained_from": model.get("trained_from"),
            "trained_at": model.get("trained_at"),
            "categories": model.get("categories"),
        },
        "records": records,
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(envelope, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def read_categorized_records(repo_root: Path) -> list[dict]:
    path = categorized_path(repo_root)
    if not path.is_file():
        return []
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, dict) and isinstance(payload.get("records"), list):
        return [item for item in payload["records"] if isinstance(item, dict)]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return []


def run_batch_categorization(
    repo_root: Path,
    repos: list[dict],
    *,
    labels_path: Path | None = None,
    source: str = "batch",
) -> dict:
    """Train from manual labels and write categorized envelope."""
    labels = load_manual_labels(labels_path)
    if not labels:
        raise RuntimeError("batch categorization requires manual labels fixture")
    model = train_naive_bayes(labels)
    categorized = categorize_records(repos, model=model, labels=labels)
    path = write_categorized_envelope(repo_root, categorized, model=model, source=source)
    return {
        "categorized_path": str(path),
        "record_count": len(categorized),
        "trained_from": model.get("trained_from"),
        "categories_seen": sorted({str(r.get("star_category") or "") for r in categorized}),
    }
