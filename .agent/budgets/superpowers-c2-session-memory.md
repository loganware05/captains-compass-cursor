# Autonomy budget — superpowers-c2-session-memory

| Limit | Value | Used |
|---|---|---|
| Iterations | 24 | 2 |
| Failed validation cycles | 4 | 1 (fixed) |
| Wall time (minutes) | 2880 | ~90 |
| Cost (USD) | Captain discretion | 0 |

Status: **ACTIVE** — validation green; PR next

Issue: [#272](https://github.com/loganware05/captains-compass-cursor/issues/272)
Branch: `feature/272-superpowers-c2-session-memory`
Rollback: `rollback/pre-superpowers-c2-session-memory` @ `151ce6a`

## Cycle log

| date | iteration | result | notes |
|---|---|---|---|
| 2026-11-12 | 1 | fail | registry count assert still 47; doctor env -u order |
| 2026-11-12 | 2 | pass | doctor 0; tests/run.sh green; registry 51 |
