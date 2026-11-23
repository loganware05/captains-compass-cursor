# Specialized Real Local Eval (durable plan copy)

> Plan ID `specialized-real-local-eval` — **COMPLETE**. Issue [#305](https://github.com/loganware05/captains-compass-cursor/issues/305).
> Budget: `.agent/budgets/specialized-real-local-eval.md`.

## Goal

Opt-in local inference student for L0/L1 specialized gold scoring. Stub remains
CI default.

## Env

```bash
COMPASS_SPECIALIZED_MODEL_ENABLED=1
COMPASS_SPECIALIZED_STUDENT='./my-student.sh'      # optional argv
COMPASS_SPECIALIZED_STUDENT_URL=https://…         # optional HTTPS
```

## Baseline

`origin/main` @ `6d9f8a0` / **v1.91.0**. Release **v1.92.0**.
Rollback: `rollback/pre-specialized-real-local-eval` @ `6d9f8a0`.
