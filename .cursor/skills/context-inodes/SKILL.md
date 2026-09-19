---
name: context-inodes
description: Builds and walks the content-addressed inode metadata store and derived context tree for filesystem-gated, module-scoped agent context
---

# Context Inodes & Route Walking (M40)

Use this Skill when planning or reviewing work that touches module boundaries,
when subagent context needs scoping to a module, or when the inode store is
stale/missing.

## Concepts

- **Inode** — `.agent/inodes/<sha256>.json`: structural metadata for one source
  file (exported interfaces, function signatures with param optionality, I/O
  types, declared complexity), content-addressed and decoupled from raw source.
  Inodes never contain file contents.
- **Context tree** — `.agent/context/<domain>/<module>/node.json`: derived from
  the source tree (never hand-authored). Each node carries a summary, child
  segments, and the inode refs for its subtree.
- **Route walk** — sequential segment-by-segment resolution
  (`src/lib` → load `src/node.json`, then `src/lib/node.json`). Walks return
  inode *pointers*; callers page in source explicitly only when needed.

## Declared complexity convention

Complexity is **declared, never inferred**. Annotate with `@complexity`:

```python
def process(records: list[dict]) -> list[dict]:
    """@complexity O(N)"""
```

```ts
/** @complexity O(N) */
export function validateForm(fields: InputProps[]): string[] { ... }
```

## Commands

```bash
# Build/refresh the inode store + context tree (deterministic)
./scripts/build-context-inodes.sh [--repo-root PATH]

# Fail (exit 1) when indexed sources are stale
./scripts/build-context-inodes.sh --check

# Walk a context route (prints steps + in-scope inode refs)
./scripts/walk-context-route.sh --route orchestrator/review

# Via the launcher
./scripts/northstar context build --repo /path/to/repo
./scripts/northstar context walk --repo /path/to/repo --route src/lib
```

## Gates and invariants

- `doctor.sh` fails closed when `.agent/inodes/` exists but is stale
  (rebuild hint), and when committed Skill inodes are stale.
- The `northstar review` boundary gate **skips with an explicit note** when the
  inode store is absent or stale — it never reviews against untrusted
  metadata. See Skill `code-reviewer` for the boundary checks.
- Subagent manifests carry `working_context` (context root, inode refs, scope
  allow/deny) — see Skill `capability-planning`.
