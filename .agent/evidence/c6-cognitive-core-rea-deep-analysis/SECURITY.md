# Security review — c6-cognitive-core-rea-deep-analysis

| Item | Assessment |
|---|---|
| Authority expansion | None — schema const false |
| Live execution | Default fixture; live needs checklist + `--allow-live`; no auto-exec of REA against targets |
| Speculative claims | Hypothesis claim_kind required; forbidden training-corpus recovery questions refused |
| Secrets | Target/question treated as local text |
| Network | Fixture path requires no network |
| Gate | Fail-closed without `COMPASS_REA_ENABLED` |

Residual risk: low for fixture mode. Live REA binary presence is detect-only in this release.
