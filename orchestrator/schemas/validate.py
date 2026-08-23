"""Deterministic JSON Schema validation without external dependencies."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SCHEMA_DIR = Path(__file__).resolve().parent

SCHEMA_FILES = (
    "capability.schema.json",
    "task.schema.json",
    "agent-manifest.schema.json",
    "model-profile.schema.json",
    "candidate-capability.schema.json",
    "execution-run.schema.json",
    "experience.schema.json",
)


class ValidationError(ValueError):
    """Raised when an instance fails schema validation."""


def schemas_dir() -> Path:
    return SCHEMA_DIR


def load_schema(name: str) -> dict[str, Any]:
    path = SCHEMA_DIR / name
    if not path.is_file():
        raise FileNotFoundError(f"schema not found: {path}")
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def validate(instance: Any, schema: dict[str, Any], *, path: str = "$") -> None:
    """Validate instance against a JSON Schema subset (types, required, enum, const)."""
    schema_type = schema.get("type")
    if schema_type is not None:
        _check_type(instance, schema_type, path)

    if "const" in schema and instance != schema["const"]:
        raise ValidationError(f"{path}: expected const {schema['const']!r}, got {instance!r}")

    if "enum" in schema and instance not in schema["enum"]:
        raise ValidationError(
            f"{path}: value {instance!r} not in enum {schema['enum']!r}"
        )

    if schema_type == "object":
        if not isinstance(instance, dict):
            raise ValidationError(f"{path}: expected object, got {type(instance).__name__}")
        if schema.get("additionalProperties") is False:
            allowed = set(schema.get("properties", {}))
            extra = set(instance) - allowed
            if extra:
                raise ValidationError(f"{path}: unexpected properties {sorted(extra)}")
        for key in schema.get("required", []):
            if key not in instance:
                raise ValidationError(f"{path}: missing required property {key!r}")
        for key, prop_schema in schema.get("properties", {}).items():
            if key in instance:
                validate(instance[key], prop_schema, path=f"{path}.{key}")

    elif schema_type == "array":
        if not isinstance(instance, list):
            raise ValidationError(f"{path}: expected array, got {type(instance).__name__}")
        min_items = schema.get("minItems")
        if min_items is not None and len(instance) < min_items:
            raise ValidationError(f"{path}: expected at least {min_items} items")
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(instance):
                validate(item, item_schema, path=f"{path}[{index}]")

    elif schema_type == "string":
        if not isinstance(instance, str):
            raise ValidationError(f"{path}: expected string, got {type(instance).__name__}")
        min_length = schema.get("minLength")
        if min_length is not None and len(instance) < min_length:
            raise ValidationError(f"{path}: string shorter than minLength {min_length}")

    elif schema_type == "integer":
        if not isinstance(instance, int) or isinstance(instance, bool):
            raise ValidationError(f"{path}: expected integer, got {type(instance).__name__}")
        minimum = schema.get("minimum")
        if minimum is not None and instance < minimum:
            raise ValidationError(f"{path}: integer below minimum {minimum}")

    elif schema_type == "number":
        if not isinstance(instance, (int, float)) or isinstance(instance, bool):
            raise ValidationError(f"{path}: expected number, got {type(instance).__name__}")
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        if minimum is not None and instance < minimum:
            raise ValidationError(f"{path}: number below minimum {minimum}")
        if maximum is not None and instance > maximum:
            raise ValidationError(f"{path}: number above maximum {maximum}")

    elif schema_type == "boolean":
        if not isinstance(instance, bool):
            raise ValidationError(f"{path}: expected boolean, got {type(instance).__name__}")


def _check_type(instance: Any, schema_type: str, path: str) -> None:
    if schema_type == "object" and not isinstance(instance, dict):
        raise ValidationError(f"{path}: expected object, got {type(instance).__name__}")
    if schema_type == "array" and not isinstance(instance, list):
        raise ValidationError(f"{path}: expected array, got {type(instance).__name__}")
    if schema_type == "string" and not isinstance(instance, str):
        raise ValidationError(f"{path}: expected string, got {type(instance).__name__}")
    if schema_type == "integer" and (not isinstance(instance, int) or isinstance(instance, bool)):
        raise ValidationError(f"{path}: expected integer, got {type(instance).__name__}")
    if schema_type == "number" and (
        not isinstance(instance, (int, float)) or isinstance(instance, bool)
    ):
        raise ValidationError(f"{path}: expected number, got {type(instance).__name__}")
    if schema_type == "boolean" and not isinstance(instance, bool):
        raise ValidationError(f"{path}: expected boolean, got {type(instance).__name__}")


def validate_document(instance: Any, schema_name: str) -> None:
    schema = load_schema(schema_name)
    validate(instance, schema)


def all_schema_files_present(root: Path | None = None) -> list[str]:
    """Return missing schema filenames relative to orchestrator/schemas/."""
    base = root or SCHEMA_DIR
    missing = []
    for name in SCHEMA_FILES:
        if not (base / name).is_file():
            missing.append(name)
    return missing
