# XRV W2 — Eight-Pillar Repository Readiness Assessor

> **IN PROGRESS** — Issue [#263](https://github.com/loganware05/captains-compass-cursor/issues/263).
> Canonical gate: repo root `IMPLEMENTATION_PLAN.md` (APPROVED).
> Proposed release: **v1.84.0**.
> Rollback: `rollback/pre-xrv-readiness-assessor` @ `cb85c4a`.

## Operator surface

```bash
COMPASS_XRV_READINESS_ENABLED=1 \
  ./scripts/northstar assess readiness --repo .
```

## Pillars (repository readiness)

1. Style & validation  
2. Build systems  
3. Testing  
4. Documentation  
5. Development environments  
6. Code quality  
7. Observability  
8. Security & governance  

## Effectiveness (separate)

NorthStar control signals (EER schema/fixture, I6 schema, XRV docs, drift module).

Missing paths → **unscored** (never invented). Authority locks always false.
