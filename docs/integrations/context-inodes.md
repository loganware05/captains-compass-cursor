# Filesystem-Gated Context & Dependency Architecture (M40)

Operating-system filesystem patterns applied to NorthStar's orchestrator:
directory-style context routing, inode-style metadata decoupling,
hard/symlinked dependency graphs, and per-subagent `pwd` isolation.

## Why

Flat memory files and naive top-N retrieval scale with project history, not
with the task ("lost in the middle"). Task-graph dependencies were ordering
strings with no contract semantics, and `northstar review` never checked calls
crossing module boundaries. M40 adds the missing structural layer.

## Components

| Component | Path | Purpose |
|---|---|---|
| Inode store | `orchestrator/context/inodes.py` → `.agent/inodes/` | Content-addressed structural metadata (exports, signatures, declared complexity); never file contents |
| Extractors | `orchestrator/context/extract.py` | Python via stdlib `ast`; TypeScript/TSX parser-lite (conservative, line-oriented) |
| Context tree + walker | `orchestrator/context/walker.py` → `.agent/context/` | Derived `domain/module` nodes; sequential route walking returns inode pointers only |
| Dependency graph | `orchestrator/dependency_graph.py` | Module edges from inode imports: named-symbol import = **hard** (contract recorded), side-effect import = **symlink**; cross-boundary flagged |
| Typed task links | `orchestrator/planner/decompose.py` + `task.schema.json` | `dependencies` accept strings (ordering) or `{target, link, contract?, paths?}` |
| Boundary gate | `orchestrator/review/boundary.py` | Cross-boundary checks: unknown symbol (high), arity mismatch (medium), complexity amplification vs declared `@complexity` (medium) |
| Skill inodes | `orchestrator/registry/inodes.py` → `.cursor/skills/inodes/` | Content-addressed Skill identity; reputation carry-over on edit requires `--captain-approved` |
| Manifest pwd | `orchestrator/assembler/manifest.py` | `working_context`: scoped route + inode refs + scope allow/deny per subagent |

## Commands

```bash
./scripts/build-context-inodes.sh [--repo-root PATH]   # build store + tree (deterministic)
./scripts/build-context-inodes.sh --check              # fail closed when stale
./scripts/walk-context-route.sh --route src/lib        # sequential route walk
./scripts/build-skill-inodes.sh [--check] [--captain-approved]
./scripts/northstar context build --repo PATH
./scripts/northstar context walk --repo PATH --route domain/module
./scripts/northstar review --repo PATH [--no-boundary-check]
```

## Safety posture

- Hermetic and deterministic: stdlib only, no network, no model; identical
  sources produce byte-identical stores.
- The boundary gate **skips with an explicit note** when the inode store is
  absent or stale — it never reviews against untrusted metadata.
- `doctor.sh` fails closed on stale committed Skill inodes and on a stale
  built context store.
- Complexity is **declared** via `@complexity O(...)` annotations, never
  inferred. The complexity check is a declared-contract mismatch detector,
  not a static analysis oracle.
- `working_context` isolation is advisory-by-construction (the manifest
  declares scope); hard runtime enforcement is a Cursor-platform concern.
- All M27–M33 review locks unchanged: evidence-only default, no auto-apply,
  no auto-merge, Captain gates intact.

## Validation

- `tests/orchestrator/test_m40_*.py` (35 tests) — extractors, store
  determinism, staleness, walker, typed links, dependency graph, boundary
  precision (1.0 on fixtures), manifest isolation invariant
- `tests/evals/run.sh` M40 sensors — determinism, sequential walk, boundary
  precision, isolation, measured payload reduction
- Sandbox evidence: `.agent/evidence/m40-filesystem-gated-context/`
