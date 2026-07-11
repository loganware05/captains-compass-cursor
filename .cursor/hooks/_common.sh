# shellcheck shell=bash
# Shared helpers for Captain's Compass hooks. Source from other hook scripts.

compass_parse_input() {
  COMPASS_INPUT="$(cat)"
  COMPASS_COMMAND="$(printf '%s' "$COMPASS_INPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("command") or "")')"
  COMPASS_HOOK_CWD="$(printf '%s' "$COMPASS_INPUT" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("cwd") or d.get("working_directory") or d.get("workingDirectory") or "")')"
  COMPASS_CD_PATH="$(printf '%s' "$COMPASS_INPUT" | python3 -c '
import json,sys,re
command=json.load(sys.stdin).get("command") or ""
m=re.search(r"(?:^|[;&\n])\s*cd\s+(\"([^\"]+)\"|'\''([^'\'']+)'\''|(\S+))\s*(?:&&|;|\n)", command)
if not m:
    print("")
else:
    print(m.group(2) or m.group(3) or m.group(4) or "")
')"
}

compass_repo_dir() {
  if [[ -n "${COMPASS_CD_PATH:-}" ]]; then
    printf '%s' "$COMPASS_CD_PATH"
  elif [[ -n "${COMPASS_HOOK_CWD:-}" ]]; then
    printf '%s' "$COMPASS_HOOK_CWD"
  else
    pwd
  fi
}

compass_allow() { echo '{"permission":"allow"}'; exit 0; }

compass_deny() {
  python3 -c 'import json,sys; print(json.dumps({"permission":"deny","user_message":sys.argv[1],"agent_message":sys.argv[1]}))' "$1"
  exit 0
}

compass_branch() {
  local dir="$1"
  git -C "$dir" rev-parse --abbrev-ref HEAD 2>/dev/null || echo ""
}
