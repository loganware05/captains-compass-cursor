"""GitHub webhook signature verification (HMAC SHA-256)."""

from __future__ import annotations

import hashlib
import hmac


def verify_github_signature(
    *,
    body: bytes,
    signature_header: str | None,
    secret: str,
) -> bool:
    """Return True when X-Hub-Signature-256 matches HMAC-SHA256(secret, body)."""
    if not secret or not signature_header:
        return False
    if not signature_header.startswith("sha256="):
        return False
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    expected = "sha256=" + digest
    return hmac.compare_digest(expected, signature_header)
