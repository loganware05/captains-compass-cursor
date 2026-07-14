#!/usr/bin/env bash
# Failing-test exercise only (sandbox failure-test #3)
set -euo pipefail
SANDBOX="${1:?sandbox path}"
EVIDENCE="${2:?evidence dir}"
mkdir -p "$EVIDENCE"
cd "$SANDBOX"

{
  echo "=== Test 3: introduce bug, observe fail, fix implementation ==="
  python3 - <<'PY'
from pathlib import Path
p = Path("src/lib/contactValidation.ts")
text = p.read_text()
old = "const EMAIL_PATTERN = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/"
new = "const EMAIL_PATTERN = /.^/ // FAILURE-TEST intentional break (matches nothing useful)"
# Actually we want ALWAYS match so invalid emails pass validation → tests that expect errors fail
new = "const EMAIL_PATTERN = /(?:)/ // FAILURE-TEST intentional break"
if old not in text:
    raise SystemExit("pattern not found:\n" + repr(text.splitlines()[7]))
p.write_text(text.replace(old, new, 1))
print("broke EMAIL_PATTERN to always-match")
PY
  set +e
  npm test --silent
  echo "exit_after_break=$?"
  set -e
  python3 - <<'PY'
from pathlib import Path
p = Path("src/lib/contactValidation.ts")
text = p.read_text()
old = "const EMAIL_PATTERN = /(?:)/ // FAILURE-TEST intentional break"
new = "const EMAIL_PATTERN = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/"
if old not in text:
    raise SystemExit("broken marker missing")
p.write_text(text.replace(old, new, 1))
print("restored EMAIL_PATTERN — test files not modified")
PY
  set +e
  npm test --silent
  echo "exit_after_fix=$?"
  set -e
  echo "=== Test file diffs (expect empty) ==="
  git diff --stat -- src/lib/contactValidation.test.ts src/components/ContactForm.test.tsx || true
  git checkout -- src/lib/contactValidation.ts
  echo "DONE_TEST_3"
} | tee "$EVIDENCE/03-failing-test.txt"
