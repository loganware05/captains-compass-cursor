"""Additive COMPASS_PROFILE bundles (v0).

Named profiles expand to known ``COMPASS_*`` gate defaults. Individual flags
always win: apply only sets a key when it is unset or empty in the environment.
Profiles never enable live/network dual-gates (e.g. ``COMPASS_SENTRY_LIVE``).
"""

from __future__ import annotations

import os
from typing import Mapping

PROFILE_ENV = "COMPASS_PROFILE"

# Minimal documented sets — do not expand without Captain approval.
PROFILES: dict[str, dict[str, str]] = {
    "core": {
        "COMPASS_STATUS_ENABLED": "1",
        "COMPASS_BRAIN_ENABLED": "1",
    },
    "integrations": {
        "COMPASS_SENTRY_INGEST_ENABLED": "1",
        "COMPASS_T3_EXEC_ENABLED": "1",
        "COMPASS_APIFY_ENABLED": "1",
        "COMPASS_EXPLAIN_ENABLED": "1",
        "COMPASS_IDENTITY_ENABLED": "1",
        "COMPASS_I6_VALIDATE_ENABLED": "1",
        "COMPASS_CONVERSATION_INGEST_ENABLED": "1",
    },
}


class ProfileError(ValueError):
    """Invalid or unknown COMPASS_PROFILE."""


def list_profiles() -> list[str]:
    return sorted(PROFILES.keys())


def resolve_profile_name(name: str | None = None) -> str:
    raw = (name if name is not None else os.environ.get(PROFILE_ENV) or "").strip()
    if not raw:
        raise ProfileError(
            f"no profile specified — set {PROFILE_ENV}=core|integrations "
            "or pass a profile name"
        )
    key = raw.lower()
    if key not in PROFILES:
        known = ", ".join(list_profiles())
        raise ProfileError(f"unknown profile {raw!r}; known: {known}")
    return key


def expand_profile(name: str | None = None) -> dict[str, str]:
    """Return the gate map for a profile (copy)."""
    key = resolve_profile_name(name)
    return dict(PROFILES[key])


def apply_profile(
    name: str | None = None,
    *,
    environ: dict[str, str] | None = None,
    overwrite: bool = False,
) -> dict[str, str]:
    """Apply profile gates into environ.

    By default only sets keys that are missing or empty (additive). Returns
    the keys that were actually set.
    """
    env = environ if environ is not None else os.environ  # type: ignore[assignment]
    gates = expand_profile(name)
    applied: dict[str, str] = {}
    for key, value in gates.items():
        current = str(env.get(key, "") or "").strip()
        if overwrite or not current:
            env[key] = value
            applied[key] = value
    return applied


def export_shell(name: str | None = None, *, environ: Mapping[str, str] | None = None) -> str:
    """Emit ``export KEY=value`` lines for unset gates (safe for ``eval``)."""
    env_map = dict(environ) if environ is not None else dict(os.environ)
    applied = apply_profile(name, environ=env_map, overwrite=False)
    lines = [f"export {k}={_shell_quote(v)}" for k, v in sorted(applied.items())]
    return "\n".join(lines) + ("\n" if lines else "")


def _shell_quote(value: str) -> str:
    if value.isalnum() or (value.replace("_", "").replace("-", "").isalnum()):
        return value
    return "'" + value.replace("'", "'\"'\"'") + "'"


def active_profile_name() -> str | None:
    raw = (os.environ.get(PROFILE_ENV) or "").strip()
    if not raw:
        return None
    key = raw.lower()
    return key if key in PROFILES else raw
