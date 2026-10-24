# Supply chain — @openuidev packages

| Package | Version | Notes |
|---|---|---|
| `@openuidev/react-lang` | 1.0.1 | Pinned; Open UI React runtime |
| `@openuidev/lang-core` | 1.0.1 | Pinned; prompt + parser |
| `zod` | ^4 | Peer/schema for defineComponent |
| `react` / `react-dom` | ^19 | Dev/peer for orchestrator/ui only |

## Risk notes

- Open UI ecosystem is young; Captain approved via plan `openui-control-plane`.
- Packages live only under control `orchestrator/ui` — not installed into product repos by default.
- Lockfile: `orchestrator/ui/package-lock.json`.
- No Thesys API keys required for hermetic Python emitters or fixture parse tests.
- `@openuidev/lang-core` declares an install script (`postinstall.cjs`, telemetry-oriented).
  Operators may use `npm ci --ignore-scripts` in CI if install-time scripts are undesired;
  hermetic Python emitters do not require running that postinstall.

## Audit

```bash
cd orchestrator/ui && npm audit --omit=dev 2>&1 | tee ../../.agent/evidence/openui-control-plane/npm-audit.txt || true
```
