# M42 Validation — Specialist added-line scope

## Result

**PASS** — M37 fail-closed detectors scoped to executable hook added lines.

## Evidence

```bash
PYTHONPATH=. python3 -B -m unittest tests.orchestrator.test_m37_agentic_security_review -v
# 9 passed (includes M40 sandbox clean pack replay)
```

## Fix summary

- `_added_text_by_file` / `_hook_added_text` ignore removed lines
- `_HOOK_SCAN_PATH` limits body scan to `.cursor/hooks/*.{sh,bash,zsh}` + hooks.json
- Docs/README under hooks no longer feed detectors

## Rollback

`git checkout rollback/pre-m42-specialist-added-line-scope`
