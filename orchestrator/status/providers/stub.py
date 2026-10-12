"""Deterministic stub StatusProvider (M51/M52). Default for CI."""

from __future__ import annotations

from typing import Any


class StubStatusProvider:
    """No-network provider — returns deterministic explanation text."""

    name = "stub"
    model = ""

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
                claim = finding.get("claim_kind") or "observed"
                lines.append(
                    f"- [{finding.get('severity')}/{claim}] {finding.get('summary')}"
                )
        else:
            lines.append("No warn/error drift detected by hermetic detectors.")
        lines.append(
            "This explanation is stub-generated (COMPASS_STATUS_PROVIDER=stub). "
            "Reconcile proposals remain proposal-only. "
            "system-map/scope-ledger are Overseer artifacts, not canonical memory."
        )
        return "\n".join(lines)
