# Adversarial review remediation — M35 / C2

Reviewer findings addressed on control branch before PR #166:

1. **Status SHIPPED → PARTIAL** — AC#2 open until product PR exists.
2. **Evidence integrity** — clean reinstall at VERSION 1.38.0; patch SHA `0b7bb96`
   matches inventory; scrubbed `install.log.txt` committed (not `*.log`).
3. **Bare `./scripts/` in product Skills/docs** — `install.sh` rewrites to
   `$CONTROL/scripts/`; hermetic test asserts zero bare refs.
4. **INDEX sandbox hard-code** — learn example uses `--repo "$(pwd)"`.
5. **Secrets** — `SECRETS_SCAN.md` documents clean high-signal scan.

Residual: product push 403 (expected; APPLY.md for Captain).
