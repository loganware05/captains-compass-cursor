# Structural test examples

Computational architecture feedback complements markdown conventions.
Copy patterns into product repos; Compass does not force a single tool.

## TypeScript / JavaScript — dependency-cruiser

Example config: [`dependency-cruiser.cjs`](./dependency-cruiser.cjs)

```bash
npm install --save-dev dependency-cruiser
npx depcruise --config dependency-cruiser.cjs src
```

Typical rules: forbid `ui` importing `db` directly; forbid circular deps.

## Other stacks (notes)

| Stack | Example tools |
|---|---|
| JVM | ArchUnit |
| Python | import-linter |
| Go | `go-arch-lint` / custom package tests |

Wire structural checks into `pre-push` / CI in the **product** repo once chosen.
Compass soft `pre-push-tests` only runs `npm test` when that script exists.
