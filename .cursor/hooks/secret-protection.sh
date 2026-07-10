#!/usr/bin/env bash
# Block shell commands that stage/commit common secret files or echo obvious secrets.
set -euo pipefail

input="$(cat)"
command="$(python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("command") or "")' <<<"$input")"

deny() {
  local msg="$1"
  python3 -c 'import json,sys; print(json.dumps({"permission":"deny","user_message":sys.argv[1],"agent_message":sys.argv[1]}))' "$msg"
  exit 0
}

# Dangerous path patterns in git add/commit/mv
if echo "$command" | grep -Eqi '(^|[[:space:]])git[[:space:]]+(add|commit|mv|cp).*(\.env([^\.]|$)|secrets/|\.pem|\.key|credentials\.json|id_rsa)'; then
  deny "Secret protection hook: refusing to stage/commit likely secret files (.env, keys, credentials)."
fi

# Explicit hard-code patterns in shell one-liners
if echo "$command" | grep -Eqi '(api[_-]?key|secret[_-]?key|private[_-]?key)[[:space:]]*=[[:space:]]*['\''\"][^'\''\"]+['\''\"]'; then
  deny "Secret protection hook: refusing commands that hard-code API/secret keys."
fi

echo '{"permission":"allow"}'
exit 0
