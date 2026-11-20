# Wave 0 — Toolchain provenance & feasibility (bend-policy-proof-spike, #278)

Date: 2026-11-18 · Host: macOS 26.5 (darwin 25.5.0), arm64 · Result: **PASS**

## Pin (deviation from plan, recorded)

The plan pinned `bendlang/bend@9c586f0` (main, 45 commits past the last release). Wave 0 uses the
**released** build instead, which is the supported install path and has an independently checkable digest:

| Item | Value |
|---|---|
| Bend release | `v2.0.40` (tag commit `624dd9f4607cd29b0871a9b96d413bfb11e92f52`, published 2026-11-06) |
| Archive | `bend-2.0.40-darwin-arm64.tar.gz` |
| Archive sha256 | `b2be003b041eb6cfc65326be18f79eb2e0bae2189be79a18c507e661b4b6900b` |
| Digest cross-check | Matches the digest in `install.sh` **and** the GitHub release asset digest (two origins) |
| Installed `bin/bend` sha256 | `c362cdac355d84f51278db97cb29a3b2e0be084d59b76a5cff013199b3513539` |
| `install.sh` sha256 (as fetched) | `dd10f1f62ca14a068d4b19e664cc5c5c48cceed660bb8d3b21b45e9332c11970` |
| Lean (for `--verdict`) | `leanprover/lean4:v4.34.0`, via elan `v4.3.0` |
| elan archive sha256 | `214c1b610222cf21c76b2b9e31020cfab3bae90e21826f4aac4901c6aa0922b0` (matches GitHub release digest; installed directly, not via the unverified `elan-init.sh`) |
| License | Apache-2.0 |

## Supply-chain review (Skill: dependency-supply-chain)

- `install.sh` read in full before running: downloads one archive over HTTPS (TLS ≥1.2), verifies sha256,
  installs under `$BEND_HOME`, no sudo, no shell-rc edits. Ran with `BEND_HOME` inside the repo and
  `BEND_NO_TELEMETRY=1` (daily version check disabled).
- Everything is under `.agent/tools/` (git-ignored). Nothing installed globally; PATH untouched.
- Risk accepted and recorded: prebuilt binary, unaudited compiler (README: ~99% AI-written). Mitigated by
  `--verdict` kernel recheck, mutation controls (Wave B), and never making Bend a sole gate.
- Source clone used only for reading the guide (`/tmp`, not retained).

## Feasibility results

| Check | Result |
|---|---|
| `bend PROOF.bend` (smoke law `add_zero`) | `ALL PROOFS CHECK`, exit 0, ~0.15 s |
| `bend PROOF.bend --verdict` first run (builds Lean kernel) | `ALL PROOFS CHECK`, exit 0, ~54 s wall |
| `--verdict` cached run | `ALL PROOFS CHECK`, exit 0, ~0.18 s |
| Negative control (proof case replaced with `?TODO`) | `SOME PROOFS FAIL`, **exit 1** |
| Open law (LAWS only) | `SOME PROOFS FAIL` |

Exit codes are usable as an automated gate (0 pass / 1 fail). Smoke files: `formal/bend/smoke/`
(`LAWS.bend` sha256 `25cfad19…`, `PROOF.bend` sha256 `89ae09c2…`).

## Notes for later waves

- Bend convention is `LAWS.bend` (human-written laws) + `PROOF.bend` (proofs, `def Laws.<name>`), imported with
  `import ./LAWS.bend as Laws`. Plan text said `Proofs.bend`; use `PROOF.bend` to match Bend tooling.
- `--verdict` needs `lean` on `PATH` (project-local `ELAN_HOME`) — the opt-in runner must set both.
- First `--verdict` run costs ~1 min (kernel build); later runs are sub-second. Relevant to CI cost metric.

## Budget

Implementation loops used: 1 of 8. Wall time ≈ 0.4 h. No cost beyond local compute.
