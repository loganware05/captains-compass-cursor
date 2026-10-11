"""Deterministic stub StatusProvider (M51). Placeholder for future Kimi."""

from __future__ import annotations

from typing import Any


class StubStatusProvider:
    """No-network provider — returns deterministic explanation text."""

    name = "stub"

    def explain(self, snapshot: dict[str, Any]) -> str:
        findings = snapshot.get("findings") or []
        warns = [f for f in findings if f.get("severity") == "warn"]
        errors = [f for f in findings if f.get("severity") == "error"]
        version = snapshot.get("northstar_version") or "unknown"
        sha = snapshot.get("repository_sha") or "unknown"
        lines = [
            f"NorthStar Project Overseer snapshot for version {version} @ {sha}.",
            f"Findings: {len(findings)} total ({len(errors)} error, {len(warns)} warn).",
        ]
        if errors or warns:
            lines.append("Notable drift:")
            for finding in list(errors) + list(warns):
                lines.append(f"- [{finding.get('severity')}] {finding.get('summary')}")
        else:
            lines.append("No warn/error drift detected by hermetic detectors.")
        lines.append(
            "This explanation is stub-generated (no live Kimi). "
            "Reconcile proposals remain proposal-only."
        )
        return "\n".join(lines)
