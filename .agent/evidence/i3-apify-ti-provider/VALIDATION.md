# Validation — i3-apify-ti-provider (#253)

## Commands

```bash
PYTHONPATH=. python3 -m unittest discover -s tests/orchestrator -p 'test_i3_apify*.py' -v
COMPASS_APIFY_ENABLED=1 ./scripts/northstar apify search --query "web research"
COMPASS_STATUS_ENABLED=1 ./scripts/northstar status snapshot --repo .
./scripts/doctor.sh
```

## Results

- Unit tests: 9/9 pass
- Fixture search packet: `apify-research-24fb954d8898`
- Overseer snapshot: `psnap-83a4d89defff` with `research_refs` + `dev-apify-research`
- Doctor: 0 errors (apify fail-closed verified)
