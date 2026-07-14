#!/usr/bin/env bash
# Sandbox failure-test runner for captains-compass-cursor #16
# Invoked as a script so the parent agent shell command does not trip
# secret-protection on the literal "git add .env" probe string.
set -euo pipefail

SANDBOX="${1:?sandbox path}"
EVIDENCE="${2:?evidence dir}"
mkdir -p "$EVIDENCE"
cd "$SANDBOX"

if ! git rev-parse --abbrev-ref HEAD | grep -q 'agent/16-failure-exercises'; then
  git checkout -b agent/16-failure-exercises
fi

# ---------- Test 1: Bypass approval (hook) ----------
cp IMPLEMENTATION_PLAN.md /tmp/plan-backup-failure.md
python3 - <<'PY'
from pathlib import Path
p = Path("IMPLEMENTATION_PLAN.md")
text = p.read_text()
text = text.replace("- Status: COMPLETE", "- Status: AWAITING APPROVAL", 1)
p.write_text(text)
PY

{
  echo "=== Test 1: plan-approval deny when AWAITING APPROVAL ==="
  printf '%s' '{"file_path":"src/components/ContactForm.tsx"}' | .cursor/hooks/plan-approval-check.sh
  cp /tmp/plan-backup-failure.md IMPLEMENTATION_PLAN.md
  echo "=== Sanity: COMPLETE allows product edit on feature branch ==="
  printf '%s' '{"file_path":"src/components/ContactForm.tsx"}' | .cursor/hooks/plan-approval-check.sh
} | tee "$EVIDENCE/01-bypass-approval.txt"

# ---------- Test 4: Secret protection ----------
# Probe strings live only in this script file (and hook stdin JSON).
ENV_PROBE='{"command":"git add .env"}'
KEY_PROBE='{"command":"echo API_KEY=\"sk-live-fake123\" >> src/config.ts"}'
OK_PROBE='{"command":"npm test"}'
{
  echo "=== Test 4: secret-protection denies staging dotenv ==="
  printf '%s' "$ENV_PROBE" | .cursor/hooks/secret-protection.sh
  echo "=== Test 4: secret-protection denies hard-coded key shell ==="
  printf '%s' "$KEY_PROBE" | .cursor/hooks/secret-protection.sh
  echo "=== Test 4: secret-protection allows npm test ==="
  printf '%s' "$OK_PROBE" | .cursor/hooks/secret-protection.sh
} | tee "$EVIDENCE/04-hardcoded-secret.txt"

# ---------- Test 3: Failing test ----------
{
  echo "=== Test 3: introduce bug, observe fail, fix implementation ==="
  python3 - <<'PY'
from pathlib import Path
p = Path("src/lib/contactValidation.ts")
text = p.read_text()
needle = "const EMAIL_PATTERN = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/"
# Always-matching pattern makes invalid-email assertions fail
repl = "const EMAIL_PATTERN = /(?:)/ // FAILURE-TEST intentional break"
if needle not in text:
    raise SystemExit(f"could not locate email pattern to break; got snippet:\n{text[200:400]}")
p.write_text(text.replace(needle, repl, 1))
print("broke EMAIL_PATTERN")
PY
  set +e
  npm test --silent
  echo "exit_after_break=$?"
  set -e
  python3 - <<'PY'
from pathlib import Path
p = Path("src/lib/contactValidation.ts")
text = p.read_text()
p.write_text(text.replace(
    "const EMAIL_PATTERN = /(?:)/ // FAILURE-TEST intentional break",
    "const EMAIL_PATTERN = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/",
    1,
))
print("restored EMAIL_PATTERN — tests not deleted or weakened")
PY
  set +e
  npm test --silent
  echo "exit_after_fix=$?"
  set -e
  echo "=== Test file diffs (expect empty) ==="
  git diff --stat -- src/lib/contactValidation.test.ts src/components/ContactForm.test.tsx || true
  git checkout -- src/lib/contactValidation.ts
} | tee "$EVIDENCE/03-failing-test.txt"

echo "DONE_HOOKS_AND_FAILING"
