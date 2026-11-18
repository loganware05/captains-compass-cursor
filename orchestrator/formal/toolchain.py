"""Locate and run the isolated Bend toolchain (Bend + Lean for ``--verdict``).

Search order for Bend: ``$COMPASS_BEND_BIN`` (explicit; never falls back),
``<root>/.agent/tools/bend/bin/bend``, then ``bend`` on PATH. Lean comes from
``$COMPASS_BEND_ELAN_HOME`` or ``<root>/.agent/tools/elan`` when present.

Hardening: commands run without a shell, in their own process group with a
timeout, with truncated output, and with an *allowlisted* environment (the
compiler is unaudited, so credentials in the caller's environment are never
forwarded). ``COMPASS_BEND_SHA256`` optionally pins the binary.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import signal
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

MAX_OUTPUT = 1_000_000
ENV_ALLOWLIST = (
    "PATH", "HOME", "USER", "LANG", "LC_ALL", "LC_CTYPE", "TMPDIR", "TERM",
    "ELAN_HOME", "BEND_HOME",
)


class ToolchainError(RuntimeError):
    """The toolchain is present but untrusted or unusable."""


def explicit_bin() -> str:
    return (os.environ.get("COMPASS_BEND_BIN") or "").strip()


def _clip(text: str | bytes | None) -> str:
    if text is None:
        return ""
    if isinstance(text, bytes):
        text = text.decode("utf-8", "replace")
    return text[:MAX_OUTPUT]


@dataclass
class Toolchain:
    bend: Path
    env: dict[str, str] = field(default_factory=dict)

    def run(self, args: list[str], *, cwd: Path, timeout: float = 600.0) -> dict[str, Any]:
        started = time.monotonic()
        proc = subprocess.Popen(
            [str(self.bend), *args],
            cwd=str(cwd),
            env=self.env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        try:
            out, err = proc.communicate(timeout=timeout)
            code = proc.returncode
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            out, err = proc.communicate()
            code = 124
            err = f"{_clip(err)}\ntimeout after {timeout}s"
        return {
            "command": [self.bend.name, *args],
            "exit_code": code,
            "stdout": _clip(out),
            "stderr": _clip(err),
            "seconds": round(time.monotonic() - started, 3),
        }

    def version(self) -> str:
        try:
            res = self.run(["version"], cwd=self.bend.parent, timeout=30)
        except OSError:
            return ""
        lines = (res["stdout"] or res["stderr"]).strip().splitlines()
        return lines[0] if res["exit_code"] == 0 and lines else ""

    def binary_sha256(self) -> str:
        return hashlib.sha256(self.bend.read_bytes()).hexdigest()

    def lean_version(self) -> str:
        lean = shutil.which("lean", path=self.env.get("PATH"))
        if not lean:
            return ""
        try:
            proc = subprocess.run(
                [lean, "--version"], env=self.env, capture_output=True, text=True,
                timeout=30, check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            return ""
        lines = (proc.stdout or "").strip().splitlines()
        return lines[0] if proc.returncode == 0 and lines else ""


def discover(root: Path) -> Toolchain | None:
    """Return the toolchain, or None when it is absent.

    An explicit ``COMPASS_BEND_BIN`` that is not executable is *not* silently
    replaced; callers can detect it with :func:`explicit_bin`.
    """
    explicit = explicit_bin()
    if explicit:
        candidates = [Path(explicit)]
    else:
        candidates = [root / ".agent" / "tools" / "bend" / "bin" / "bend"]
        on_path = shutil.which("bend")
        if on_path:
            candidates.append(Path(on_path))
    bend = next((c for c in candidates if c.is_file() and os.access(c, os.X_OK)), None)
    if bend is None:
        return None

    env = {k: os.environ[k] for k in ENV_ALLOWLIST if k in os.environ}
    env["BEND_NO_TELEMETRY"] = "1"
    elan = (os.environ.get("COMPASS_BEND_ELAN_HOME") or "").strip()
    elan_home = Path(elan) if elan else root / ".agent" / "tools" / "elan"
    if (elan_home / "bin" / "lean").exists():
        env["ELAN_HOME"] = str(elan_home)
        env["PATH"] = f"{elan_home / 'bin'}{os.pathsep}{env.get('PATH', '')}"
    tc = Toolchain(bend=bend, env=env)

    pin = (os.environ.get("COMPASS_BEND_SHA256") or "").strip().lower()
    if pin and tc.binary_sha256() != pin:
        raise ToolchainError(
            f"bend binary sha256 does not match COMPASS_BEND_SHA256 ({tc.binary_sha256()[:12]}…)"
        )
    return tc
