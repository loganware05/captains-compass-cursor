# M27 validation evidence

## Approval

- Plan: `m27-northstar-code-reviewer` **APPROVED** 2026-09-12
- Issue: https://github.com/loganware05/captains-compass-cursor/issues/141
- Rollback tag: `rollback/pre-m27-northstar-code-reviewer`
- Locks: hermetic CI; Skill `code-reviewer`; Phase B = GitHub posting; GitHub only

## Commands

```bash
PYTHONPATH=. python3 -m unittest tests.orchestrator.test_m27_code_review -v
./scripts/doctor.sh
./tests/run.sh
./scripts/northstar review --repo . \
  --diff-file tests/fixtures/code-review/sample.diff \
  --candidates tests/fixtures/code-review/candidates.json \
  --plan tests/fixtures/code-review/plan.md \
  --run-id control-m27-fixture \
  --changed src/auth/session.py
./scripts/run-code-review.sh --repo-root ../captain-compass-sandbox \
  --diff-file tests/fixtures/code-review/sample.diff \
  --candidates tests/fixtures/code-review/candidates.json \
  --plan tests/fixtures/code-review/plan.md \
  --run-id sandbox-m27-dry-run \
  --changed src/auth/session.py
```

## Results

- Unit tests: 6/6 OK (see `unit-tests.txt` when captured)
- Sandbox dry-run: `github_review_posted: false`; verified=1 unverified=1 discarded=1
- Control fixture run: same posture
- Doctor + full `./tests/run.sh`: recorded below after run

## Security notes

- Context packs call `redact_secrets`
- No webhook/PR posting surfaces added
- Candidates/fixtures contain only synthetic secrets in diffs

## Accessibility

N/A (no UI)

## Rollback

```bash
git revert <merge-sha>   # or reset to rollback/pre-m27-northstar-code-reviewer
```
