# Cognitive Core E2E Summary

- report_id: `e2e-cc-0dc684488d`
- mode: `hermetic`
- overall_status: **pass**
- repository_sha: `bb1b5b949769600bcb848700b513dc99998cb4e7`
- northstar_version: `1.66.1`

## Stages

- **C1** `c1-brain-sync` — pass: brain sync freshness=fresh status=ok
- **C2** `c2-brain-context-goldset` — pass: context evidence_linked=True; goldset evidence-linked 30/30 (100.0%; target 90%; expect_kinds 57%)
- **C3** `c3-assess` — pass: band=moderate score=29.83; assess backtest 5/5 (100%)
- **C4** `c4-cycle` — pass: cycle cycle-c18ee4118e2c-f6c4f0 closed; authority_locked=True
- **C5** `c5-model-route` — pass: adapter=hosted eval_cases=3
- **C6** `c6-rea` — pass: rea packet claim_kinds=['hypothesis', 'observed'] artifact_hash=True
- **C7** `c7-train-bridge` — pass: export_id=train-export-d73f16474245-f00981 trajectories=10 auto_uploaded=False

## Baselines

- brain_goldset_rate: 1.0
- assess_backtest_pass_rate: 1.0
- route_eval_case_count: 3
- cycle_authority_locked: True
- train_auto_uploaded: False
