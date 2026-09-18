#!/usr/bin/env bash
# Before Write/StrReplace on product source, require a *committed* APPROVED plan.
# Writing APPROVED into IMPLEMENTATION_PLAN.md requires COMPASS_CAPTAIN_APPROVE=1
# so the agent cannot self-serve the fail-closed gate by editing the exempt plan file.
set -euo pipefail

input="$(cat)"
export COMPASS_HOOK_INPUT="$input"

python3 - <<'PY'
import json, os, re, subprocess, sys

PROTECTED = {"main", "master", "develop", "release", "production"}
APPROVED_RE = re.compile(
    r"(?i)\b(APPROVED|IN PROGRESS|VALIDATING|COMPLETE)\b"
)
PLACEHOLDER_BY = re.compile(
    r"(?i)^(tbd|todo|n/?a|none|unknown|<\s*captain\s*>|your name|changeme|\s*)$"
)
PLACEHOLDER_DATE = re.compile(
    r"(?i)^(tbd|todo|n/?a|none|unknown|yyyy-mm-dd|\s*)$"
)


def allow():
    print(json.dumps({"permission": "allow"}))
    sys.exit(0)


def deny(msg: str):
    print(json.dumps({
        "permission": "deny",
        "user_message": msg,
        "agent_message": msg,
    }))
    sys.exit(0)


def load() -> dict:
    raw = os.environ.get("COMPASS_HOOK_INPUT") or ""
    try:
        return json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        return {}


def tool_path(d: dict) -> str:
    path = (
        d.get("file_path")
        or d.get("path")
        or (d.get("tool_input") or {}).get("path")
        or (d.get("input") or {}).get("path")
        or ""
    )
    args = d.get("arguments")
    if not path and isinstance(args, dict):
        path = args.get("path") or args.get("file_path") or ""
    return str(path or "")


def tool_payload(d: dict) -> str:
    """Best-effort new file contents from Write / StrReplace hook payloads."""
    ti = d.get("tool_input") if isinstance(d.get("tool_input"), dict) else {}
    inp = d.get("input") if isinstance(d.get("input"), dict) else {}
    args = d.get("arguments") if isinstance(d.get("arguments"), dict) else {}
    for blob in (d, ti, inp, args):
        for key in ("contents", "content", "new_string", "new_str", "text"):
            val = blob.get(key)
            if isinstance(val, str) and val.strip():
                return val
    return ""


def shell_command(d: dict) -> str:
    return str(
        d.get("command")
        or d.get("cmd")
        or (d.get("tool_input") or {}).get("command")
        or (d.get("input") or {}).get("command")
        or ""
    )


_PLAN_FILE = r"IMPLEMENTATION_PLAN\.md"
# Redirects / tee / dd / cp that target the plan file.
_FORGE_WRITE = re.compile(
    rf"(?:>>|>)\s*[\"']?(?:\./)?{_PLAN_FILE}\b"
    rf"|(?:\btee(?:\s+-a)?\s+[\"']?(?:\./)?{_PLAN_FILE}\b)"
    rf"|(?:\bof=[\"']?(?:\./)?{_PLAN_FILE}\b)"
    rf"|(?:\b(?:cp|mv|install)\b[^\n;|&]{{0,160}}[\"']?(?:\./)?{_PLAN_FILE}\b)"
    rf"|(?:\b(?:cat|printf|echo|sed|awk|sponge)\b[^\n;|&]{{0,200}}(?:>>|>)\s*[\"']?(?:\./)?{_PLAN_FILE}\b)",
    re.I,
)
_PROMOTE = re.compile(
    r"(?i)(\|\s*Status\s*\|\s*(APPROVED|IN PROGRESS|VALIDATING|COMPLETE)\s*\|"
    r"|Status:\s*(APPROVED|IN PROGRESS|VALIDATING|COMPLETE)"
    r"|\b(APPROVED|IN PROGRESS|VALIDATING|COMPLETE)\b)",
)


def shell_forges_plan(cmd: str) -> bool:
    if not cmd or not re.search(_PLAN_FILE, cmd, re.I):
        return False
    if _FORGE_WRITE.search(cmd):
        return True
    if re.search(
        rf"(?:<<|<<-)\s*\S+[^\n]*\n[^\0]{{0,4000}}(?:>>|>)\s*[\"']?(?:\./)?{_PLAN_FILE}\b"
        rf"|(?:<<|<<-)\s*\S+.*?(?:>>|>)\s*[\"']?(?:\./)?{_PLAN_FILE}\b",
        cmd,
        re.I | re.S,
    ):
        return True
    if re.search(
        rf"(?:open|Path\(|write_text|write\()\s*\([^\)]*{_PLAN_FILE}",
        cmd,
        re.I,
    ):
        return True
    return False


def shell_promotes(cmd: str) -> bool:
    return bool(_PROMOTE.search(cmd))


def parse_status(text: str) -> str:
    # Prefer metadata table: | Status | VALUE |
    m = re.search(
        r"(?im)^\|\s*Status\s*\|\s*([^|]+?)\s*\|",
        text,
    )
    if m:
        return m.group(1).strip()
    m = re.search(r"(?im)^-\s*Status:\s*(.+)$", text)
    if m:
        return m.group(1).strip()
    m = re.search(r"(?im)^\*\*?Status\*\*?\s*[:=]\s*(.+)$", text)
    if m:
        return m.group(1).strip()
    return ""


def parse_field(text: str, names: tuple[str, ...]) -> str:
    for name in names:
        m = re.search(
            rf"(?im)^\|\s*{re.escape(name)}\s*\|\s*([^|]+?)\s*\|",
            text,
        )
        if m:
            return m.group(1).strip()
        m = re.search(rf"(?im)^-\s*{re.escape(name)}:\s*(.+)$", text)
        if m:
            return m.group(1).strip()
    return ""


def is_approved_status(status: str) -> bool:
    return bool(status and APPROVED_RE.search(status))


def approval_record_ok(text: str) -> bool:
    by = parse_field(text, ("Approved by", "Approved By"))
    date = parse_field(text, ("Approval date", "Approval Date"))
    if not by or PLACEHOLDER_BY.match(by.strip()):
        return False
    if not date or PLACEHOLDER_DATE.match(date.strip()):
        return False
    # Heading alone (shipped template) is not enough — fields must be filled.
    if not re.search(r"(?im)^##\s+Approval Record\b", text):
        # Allow metadata-table-only plans if by/date are real.
        pass
    return True


def git_show_plan() -> str | None:
    try:
        proc = subprocess.run(
            ["git", "show", "HEAD:IMPLEMENTATION_PLAN.md"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout


def current_branch() -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return ""
    return (proc.stdout or "").strip()


d = load()
cmd = shell_command(d)
path = tool_path(d)

# M38 — beforeShellExecution: deny shell writes that forge IMPLEMENTATION_PLAN.md
# without Captain. Opaque redirects are fail-closed (cannot prove Status is safe).
if cmd and shell_forges_plan(cmd):
    captain = os.environ.get("COMPASS_CAPTAIN_APPROVE", "") == "1"
    if re.search(r"(?:^|[\s;])COMPASS_CAPTAIN_APPROVE=1\b", cmd):
        captain = True
    if captain:
        allow()
    if shell_promotes(cmd):
        deny(
            "Plan-approval hook: refusing shell forge that promotes "
            "IMPLEMENTATION_PLAN.md Status (APPROVED/IN PROGRESS/VALIDATING/"
            "COMPLETE). Captain must set COMPASS_CAPTAIN_APPROVE=1 "
            "(M38 shell forge gate)."
        )
    deny(
        "Plan-approval hook: refusing opaque shell write to "
        "IMPLEMENTATION_PLAN.md without COMPASS_CAPTAIN_APPROVE=1 "
        "(cannot prove Status is not being forged). Use Write/StrReplace "
        "with an inspectable payload, or set COMPASS_CAPTAIN_APPROVE=1."
    )

if not path:
    allow()

rel = path[2:] if path.startswith("./") else path
rel = rel.lstrip("/")

# Memory / workflow exemptions (plan file handled specially below)
if rel in {
    "AGENTS.md",
    "PROJECT_CONTEXT.md",
    "DECISIONS.md",
    "PROGRESS.md",
    "TESTING.md",
    "CHANGELOG.md",
    "README.md",
    "LICENSE",
    "VERSION",
    ".gitignore",
    ".cursorignore",
}:
    allow()

if rel.startswith((".cursor/", ".agent/", "docs/", "templates/", "scripts/", "tests/")):
    allow()

if rel == "IMPLEMENTATION_PLAN.md":
    payload = tool_payload(d)
    captain = os.environ.get("COMPASS_CAPTAIN_APPROVE", "") == "1"
    if not payload:
        # Fail closed on opaque plan writes — cannot prove they do not self-approve.
        deny(
            "Plan-approval hook: refusing opaque Write/StrReplace on "
            "IMPLEMENTATION_PLAN.md (no contents visible). Captain must set "
            "COMPASS_CAPTAIN_APPROVE=1 to promote Status to APPROVED, or edit "
            "with a payload the hook can inspect."
        )
    new_status = parse_status(payload)
    # Also catch approval promotion via new_string fragments without full table
    promotes = is_approved_status(new_status) or bool(
        re.search(
            r"(?i)(\|\s*Status\s*\|\s*(APPROVED|IN PROGRESS|VALIDATING|COMPLETE)\s*\|"
            r"|Status:\s*(APPROVED|IN PROGRESS|VALIDATING|COMPLETE))",
            payload,
        )
    )
    if promotes and not captain:
        deny(
            "Plan-approval hook: refusing self-serve approval of "
            "IMPLEMENTATION_PLAN.md. Captain must set COMPASS_CAPTAIN_APPROVE=1 "
            "in the environment before writing an APPROVED/IN PROGRESS/"
            "VALIDATING/COMPLETE status (agents must not forge the gate)."
        )
    allow()

# Non-product markdown elsewhere
if rel.endswith(".md"):
    allow()

# Only gate common product source / config extensions
if not re.search(
    r"\.(ts|tsx|js|jsx|mjs|cjs|py|go|rs|swift|java|kt|css|scss|sass|html|vue|"
    r"svelte|json|yml|yaml|toml|sql|prisma)$",
    rel,
):
    allow()

committed = git_show_plan()
if committed is None:
    deny(
        f"Plan-approval hook: committed IMPLEMENTATION_PLAN.md missing on HEAD. "
        f"Captain must commit an APPROVED plan before changing product files ({rel})."
    )

status = parse_status(committed)
if not is_approved_status(status):
    deny(
        f"Plan-approval hook: committed IMPLEMENTATION_PLAN.md is not APPROVED "
        f"(found Status: {status or 'none'}). Working-tree edits to the plan do "
        f"not unlock product files — commit Captain approval first before editing {rel}."
    )

if not approval_record_ok(committed):
    deny(
        f"Plan-approval hook: committed plan lacks a real Approval Record "
        f"(Approved by + Approval date must be filled, not placeholders) before "
        f"editing {rel}."
    )

branch = current_branch()
if branch in PROTECTED:
    deny(
        f"Plan-approval hook: refuse product edits on protected branch '{branch}'. "
        f"Create a feature/fix branch first."
    )

allow()
PY
