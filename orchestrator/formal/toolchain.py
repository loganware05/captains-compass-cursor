"""Locate and run the isolated Bend toolchain (Bend + Lean for ``--verdict``).

Search order for Bend: ``$COMPASS_BEND_BIN``, ``<root>/.agent/tools/bend/bin/bend``,
then ``bend`` on PATH. Lean comes from ``$COMPASS_BEND_ELAN_HOME`` or
``<root>/.agent/tools/elan`` when present, else the ambient PATH. Commands are
always run without a shell, with a timeout, and with telemetry disabled.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Toolchain:
    bend: Path
    env: dict[str, str] = field(default_factory=dict)

    def run(
        self,
        args: list[str],
        *,
        cwd: Path,
        timeout: float = 600.0,
    ) -> dict[str, Any]:
        started = time.monotonic()
        try:
            proc = subprocess.run(
                [str(self.bend), *args],
                cwd=str(cwd),
                env=self.env,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            code, out, err = proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired as exc:
            code = 124
            out = (exc.stdout or b"").decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            err = f"timeout after {timeout}s"
        return {
            "command": [self.bend.name, *args],
            "exit_code": code,
            "stdout": out,
            "stderr": err,
            "seconds": round(time.monotonic() - started, 3),
        }

    def version(self) -> str:
        res = self.run(["version"], cwd=self.bend.parent, timeout=30)
        return (res["stdout"] or res["stderr"]).strip().splitlines()[0] if res["exit_code"] == 0 else ""

    def binary_sha256(self) -> str:
        return hashlib.sha256(self.bend.read_bytes()).hexdigest()

    def lean_version(self) -> str:
        lean = shutil.which("lean", path=self.env.get("PATH"))
        if not lean:
            return ""
        proc = subprocess.run(
            [lean, "--version"], env=self.env, capture_output=True, text=True, timeout=30, check=False
        )
        return proc.stdout.strip().splitlines()[0] if proc.returncode == 0 and proc.stdout else ""


def discover(root: Path) -> Toolchain | None:
    explicit = (os.environ.get("COMPASS_BEND_BIN") or "").strip()
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit))
    else:
        candidates.append(root / ".agent" / "tools" / "bend" / "bin" / "bend")
        on_path = shutil.which("bend")
        if on_path:
            candidates.append(Path(on_path))
    bend = next((c for c in candidates if c.is_file() and os.access(c, os.X_OK)), None)
    if bend is None:
        return None

    env = dict(os.environ)
    env["BEND_NO_TELEMETRY"] = "1"
    elan = (os.environ.get("COMPASS_BEND_ELAN_HOME") or "").strip()
    elan_home = Path(elan) if elan else root / ".agent" / "tools" / "elan"
    if (elan_home / "bin" / "lean").exists():
        env["ELAN_HOME"] = str(elan_home)
        env["PATH"] = f"{elan_home / 'bin'}{os.pathsep}{env.get('PATH', '')}"
    return Toolchain(bend=bend, env=env)
