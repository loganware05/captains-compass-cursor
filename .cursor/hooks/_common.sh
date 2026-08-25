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

# Soft-hook skips: process env, command-string assignment, repo skip-env file, or marker.
# Usage: compass_soft_skip FORMAT|TESTS|PR_EVIDENCE
compass_soft_skip() {
  local kind="$1"
  local env_var=""
  local cmd_pat=""
  case "$kind" in
    FORMAT)
      env_var="COMPASS_SKIP_FORMAT"
      cmd_pat='COMPASS_SKIP_FORMAT=1'
      ;;
    TESTS)
      env_var="COMPASS_SKIP_TESTS"
      cmd_pat='COMPASS_SKIP_TESTS=1'
      ;;
    PR_EVIDENCE)
      env_var="COMPASS_SKIP_PR_EVIDENCE"
      cmd_pat='COMPASS_SKIP_PR_EVIDENCE=1'
      ;;
    *)
      return 1
      ;;
  esac
  if [[ "${!env_var:-}" == "1" ]]; then
    return 0
  fi
  if echo "${COMPASS_COMMAND:-}" | grep -Fq "$cmd_pat"; then
    return 0
  fi
  local repo
  repo="$(compass_repo_dir)"
  # Env inheritance file — when Cursor does not forward process env to hooks.
  # Lines like COMPASS_SKIP_FORMAT=1 (no secrets). Prefer gitignored local file.
  local skip_env="$repo/.agent/compass-skip.env"
  if [[ -f "$skip_env" ]] && grep -Eq "^[[:space:]]*${env_var}=1([[:space:]]|#|$)" "$skip_env"; then
    return 0
  fi
  if [[ -f "$repo/.agent/COMPASS_SKIP_HOOKS" ]]; then
    return 0
  fi
  return 1
}

compass_branch() {
  local dir="$1"
  git -C "$dir" rev-parse --abbrev-ref HEAD 2>/dev/null || echo ""
}
