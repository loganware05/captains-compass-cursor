# M4 validation evidence

Plan: `m4-persistent-roles-bounded-autonomy`  
Issue: #50  
Branch: `feature/50-m4-persistent-roles-bounded-autonomy`  
Date: 2026-08-24

## Commands

```bash
./scripts/compile-capability-registry.sh
PYTHONPATH=. python3 -m unittest discover -s tests/orchestrator -p 'test_*.py' -q
./scripts/doctor.sh
./tests/evals/run.sh
./tests/run.sh
```

## Results

| Check | Result |
|---|---|
| Unit tests (orchestrator) | 92 passed |
| Doctor | 0 errors, 0 warnings |
| Evals | 39 passed (includes M4 apply-without-captain reject) |
| tests/run.sh | 114 passed, 0 failed |

## Security notes

- Weight apply requires `captain_approved: true` per proposal
- Persistent roles never write `.cursor/agents/` from CLI
- Path-safe proposal/agent ids; budget weight-apply ceiling enforced
- `auto_apply` remains `false`

## Accessibility

N/A (no UI)
