#!/usr/bin/env bash
# Block commits and pushes that mutate protected base branches.
# Parses git -C, push refspecs, and does NOT short-circuit on checkout -b substrings.
set -euo pipefail

input="$(cat)"
export COMPASS_HOOK_INPUT="$input"

python3 - <<'PY'
import json, os, re, subprocess, sys

PROTECTED = {"main", "master", "develop", "release", "production"}


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


d = load()
command = str(d.get("command") or "")
hook_cwd = str(
    d.get("cwd") or d.get("working_directory") or d.get("workingDirectory") or ""
)

if not re.search(r"(?i)(^|[\s;|&])git(\s|$)", command):
    allow()

# Only interested in mutating git verbs (anywhere in the command string).
if not re.search(
    r"(?i)(^|[\s;|&])git(\s+\-C\s+\S+)?\s+(commit|push|merge|rebase)\b",
    command,
):
    allow()


def unquote(tok: str) -> str:
    if len(tok) >= 2 and tok[0] == tok[-1] and tok[0] in "'\"":
        return tok[1:-1]
    return tok


def tokenize(cmd: str) -> list[str]:
    # Lightweight shell-ish split for git argv inspection (handles quotes).
    return re.findall(r'"(?:\\.|[^"])*"|\'(?:\\.|[^\'])*\'|\S+', cmd)


def branch_of(repo: str) -> str:
    try:
        proc = subprocess.run(
            ["git", "-C", repo, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return ""
    return (proc.stdout or "").strip()


def is_protected_ref(name: str) -> bool:
    n = name.strip()
    if not n:
        return False
    n = n.removeprefix("+")
    # refspec dest side: src:dst
    if ":" in n:
        n = n.split(":", 1)[1]
    n = n.removeprefix("refs/heads/")
    n = n.removeprefix("refs/remotes/")
    if "/" in n and not n.startswith("refs/"):
        # remote-tracking style origin/main → main when second part protected
        parts = n.split("/")
        if parts[-1] in PROTECTED:
            n = parts[-1]
    return n in PROTECTED


def leading_cd(cmd: str) -> str | None:
    m = re.search(
        r"(?:^|[;&\n])\s*cd\s+(\"[^\"]+\"|'[^']+'|\S+)\s*(?:&&|;|\n|$)",
        cmd,
    )
    if not m:
        return None
    return unquote(m.group(1))


# Split on shell separators while keeping git invocations discoverable
segments = re.split(r"[;&\n]|&&|\|\|", command)
default_repo = leading_cd(command) or hook_cwd or os.getcwd()

for seg in segments:
    seg = seg.strip()
    if not seg:
        continue
    # Strip env assignments: FOO=1 git ...
    seg = re.sub(r"^(?:\w+=\S+\s+)+", "", seg)
    if not re.search(r"(?i)^git\b", seg):
        continue
    tokens = [unquote(t) for t in tokenize(seg)]
    if not tokens or tokens[0] != "git":
        continue

    repo = default_repo
    i = 1
    # git global options before verb: -C, -c, --git-dir, --work-tree
    while i < len(tokens):
        t = tokens[i]
        if t == "-C" and i + 1 < len(tokens):
            repo = tokens[i + 1]
            i += 2
            continue
        if t.startswith("-C") and len(t) > 2:
            repo = t[2:]
            i += 1
            continue
        if t in {"-c", "--git-dir", "--work-tree"} and i + 1 < len(tokens):
            i += 2
            continue
        if t.startswith("-"):
            i += 1
            continue
        break

    if i >= len(tokens):
        continue
    verb = tokens[i].lower()
    args = tokens[i + 1 :]

    if verb not in {"commit", "push", "merge", "rebase"}:
        continue

    if verb == "push":
        # Collect refspecs (non-option tokens after optional remote)
        positionals = [a for a in args if not a.startswith("-")]
        refspecs = positionals[1:] if positionals else []
        # Flags that push protected branches without naming them
        joined = " ".join(args).lower()
        if re.search(r"(?i)(^|\s)--all(\s|$)|(^|\s)--mirror(\s|$)", joined):
            deny(
                "Protected-branch hook: refusing git push --all/--mirror "
                f"(may update protected branches) in {repo}."
            )
        for spec in refspecs:
            if is_protected_ref(spec):
                deny(
                    "Protected-branch hook: refusing push refspec "
                    f"'{spec}' targeting protected branch in {repo}."
                )
        # No refspecs → pushes current HEAD
        if not refspecs:
            br = branch_of(repo)
            if br in PROTECTED:
                deny(
                    "Protected-branch hook: refusing git push on protected "
                    f"branch '{br}' in {repo}."
                )
        continue

    if verb in {"commit", "merge", "rebase"}:
        br = branch_of(repo)
        if br in PROTECTED:
            deny(
                "Protected-branch hook: refusing git "
                f"{verb} on protected branch '{br}' in {repo}."
            )
        # merge/rebase onto protected remote-tracking names in args
        if verb in {"merge", "rebase"}:
            for a in args:
                if a.startswith("-"):
                    continue
                if is_protected_ref(a) or a in PROTECTED:
                    # merging *from* main into feature is OK; only deny if HEAD protected (above).
                    pass

allow()
PY
