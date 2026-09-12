# Code review report — `bitcoin-data-collector-m27-enriched`

- Repository: `/tmp/northstar-reviews/bitcoin-data-collector`
- Status: **completed**
- Created: 2026-09-12T21:55:52Z
- Domains: docs, python, tests
- Findings: 7 (verified=6, unverified=0, discarded=1)
- GitHub review posted: `False`

## Findings

### sec-secrets-via-env: Kalshi credentials loaded from env/paths — confirm key material never committed

- Severity: `medium`
- Confidence: `0.86`
- Status: **verified**
- Skill: `security-review`
- Evidence: `kalshi_client.py`

kalshi_client.py reads KALSHI_API_KEY_ID and KALSHI_PRIVATE_KEY_PATH from the environment. Pattern is sound if private key files stay untracked, but the repo should document required .gitignore entries and refuse to start when the key path resolves inside the git worktree without being ignored.

**Suggested fix:** Document env vars; assert private key path is outside the repo or gitignored; add a doctor/preflight check.

### sec-broad-except-live: Broad Exception swallowing in live/hourly runners can hide auth and data failures

- Severity: `medium`
- Confidence: `0.84`
- Status: **verified**
- Skill: `security-review`
- Evidence: `live_runner.py`, `hourly_event_scanner.py`

live_runner.py and hourly_event_scanner.py catch bare Exception in collection/decision loops (sometimes with pass). In a market-intel loop this can silently degrade into stale or empty decisions.

**Suggested fix:** Catch expected errors narrowly; fail closed to NO TRADE on collector/auth failures; never pass silently on auth errors.

### test-gap-client-live: Unit tests cover parsers/engines but not kalshi_client/live_runner failure paths

- Severity: `medium`
- Confidence: `0.82`
- Status: **verified**
- Skill: `testing-validation`
- Evidence: `tests/test_fair_value_engine.py`, `tests/test_orderbook_guardrails.py`, `kalshi_client.py`, `live_runner.py`

tests/ includes fair value, strike probability, orderbook guardrails, event target parsing. Missing hermetic tests for auth-missing client mode, subprocess collector failure, and NO TRADE fail-closed behavior.

**Suggested fix:** Add fixture-based client tests and live_runner fail-closed tests without network.

### arch-subprocess-collector: Collector invoked via subprocess with check=False

- Severity: `medium`
- Confidence: `0.8`
- Status: **verified**
- Skill: `code-reviewer`
- Evidence: `hourly_event_scanner.py`, `live_runner.py`

hourly_event_scanner.collect_snapshot and live_runner._collect_snapshot_via_subprocess run the collector as a subprocess with check=False, then scrape newest JSON. Non-zero exits can be ignored until file absence raises later.

**Suggested fix:** Use check=True or inspect returncode; surface stderr; prefer an in-process API boundary.

### data-large-artifacts-tracked: Large scan/snapshot JSON artifacts appear tracked in git

- Severity: `low`
- Confidence: `0.88`
- Status: **verified**
- Skill: `code-reviewer`
- Evidence: `live_outputs/kalshi_scans/scan_20260527T005222Z.json`, `.gitignore`

live_outputs/kalshi_scans and snapshot JSON files are present in the recent diff (~50k insertions). This bloats history and risks leaking market/session metadata.

**Suggested fix:** Gitignore live_outputs/outputs; keep only tiny fixtures under tests/fixtures/.

### intent-no-autotrade: README non-goal (no trade execution) still holds — keep order placement out of scanners

- Severity: `info`
- Confidence: `0.78`
- Status: **verified**
- Skill: `code-reviewer`
- Evidence: `README.md`, `kalshi_client.py`, `hourly_event_scanner.py`

README states recommendations only / no trade execution. Recent hourly modules appear scan/rank oriented; confirm no accidental order endpoints are called in kalshi_client or scanners.

**Suggested fix:** Keep order APIs behind an explicit --enable-execution flag defaulting false; assert in tests.

### noise-rename: Prefer slightly different helper names

- Severity: `low`
- Confidence: `0.15`
- Status: **discarded**
- Skill: `code-reviewer`
- Evidence: _none_

Style-only preference without behavioral impact.

_Discard reason:_ `missing_evidence_paths`

## Provenance

```json
{
  "candidates_source": "fixtures",
  "github_review_posted": false,
  "hermetic": true,
  "invoke_model": false,
  "pipeline": "northstar.review.v1"
}
```
