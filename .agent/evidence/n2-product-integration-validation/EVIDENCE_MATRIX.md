# N2 Product Integration Validation — Evidence Matrix

| Step | Result | Artifact |
|---|---|---|
| Target | `captain-compass-sandbox` (writable; #164 M35 already shipped) | — |
| Update 1.59.0 → **1.71.1** | PASS | `update.log.txt` |
| Memory docs preserved | PASS (keep lines in update log) | `update.log.txt` |
| Control doctor | PASS | doctor during N1/N2 |
| Brain sync `--repo` sandbox | PASS | `brain-sync.json` |
| Assess `--repo` sandbox | PASS after control-profile fallback fix | `assess.json` (band=moderate) |
| Capability plan | PASS | `capability-plan.md` |
| Product feature + tests | PASS 37/37; build PASS | `sandbox-test.log.txt`, `sandbox-build.log.txt` |
| Code review | PASS (evidence-only) | `review.stdout.txt` |
| Oversight run | PASS | `oversight.json` |
| Status closeout | PASS (`issues_auto_closed: false`) | `status-closeout.json` |
| Recovery: ungated closeout | PASS exit 2 | `recovery-closeout-ungated.txt` |

## Integration fix (control)

`northstar assess --repo <product>` previously failed with missing
`orchestrator/reference-profiles`. N2 ships `COMPASS_CONTROL_ROOT` fallback in
registry compile / affinity checks (product Skills still load from product
`.cursor/skills`).

## Non-goals honored

No Level 3 / paid GPU; no GitHub issue auto-close; no Skill auto-promotion.
