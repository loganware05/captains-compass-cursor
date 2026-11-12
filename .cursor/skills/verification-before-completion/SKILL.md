---
name: verification-before-completion
description: Use before claiming work is complete, fixed, or passing — require fresh verification command output in-session before any success claim
---

# Verification Before Completion

Patterns inspired by [obra/superpowers](https://github.com/obra/superpowers)
`verification-before-completion` (DISCOVERED inspiration — not a plugin install).

Aligns with always-on rule `03-validation-definition-of-done`.

## Use this Skill when

- About to claim tests pass, a bug is fixed, build succeeds, or work is complete
- Before committing “validation done”, opening a PR, or declaring Definition of Done

## Iron law

```text
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you have not run the verification command in this turn (or attached its fresh
output), you cannot claim it passes.

## Inputs

- The exact claim you want to make
- Project test / doctor / build commands from `TESTING.md`

## Procedure

1. **IDENTIFY** the command that proves the claim.
2. **RUN** the full command fresh (not a remembered earlier result).
3. **READ** exit code and full relevant output; count failures.
4. **VERIFY** the output actually supports the claim.
5. **ONLY THEN** state the claim **with** evidence (command + result summary).
6. Store transcripts under `.agent/evidence/` when this is a plan closeout.

| Claim | Requires | Not sufficient |
|---|---|---|
| Tests pass | Test command: 0 failures | “Should pass”, prior run |
| Doctor clean | `./scripts/doctor.sh` exit 0 | Partial check |
| Bug fixed | Repro or failing test now passes | Code changed only |
| Agent finished | Diff / evidence matches acceptance | Agent said “done” |

## Output

Claim paired with fresh command evidence, or an honest failure report.

## Prohibited actions

- Do not claim green without a fresh run in-session
- Do not weaken, delete, or skip failing tests to force a pass
- Do not treat chat memory of an older run as evidence
