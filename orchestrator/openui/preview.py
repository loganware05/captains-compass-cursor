"""Local OpenUI surface viewer — emit → HTML (no Node required)."""

from __future__ import annotations

import html
import re
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from orchestrator.openui.enabled import require_openui_gate
from orchestrator.openui.lang import OpenUILangError, validate_openui_lang

_STMT = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$")
_STRING_LIT = re.compile(r'"((?:\\.|[^"\\])*)"')
_CALL_NAME = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*\(")

SURFACES = ("plan", "tower", "scorecard", "closeout")


class PreviewError(ValueError):
    """Operator-facing preview errors."""


def ui_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "ui"


def surface_path(repo_root: Path, surface: str) -> Path:
    return ui_dir(repo_root) / f"{surface}.openui"


def list_persisted_surfaces(repo_root: Path) -> list[str]:
    root = ui_dir(repo_root)
    if not root.is_dir():
        return []
    found: list[str] = []
    for name in SURFACES:
        if (root / f"{name}.openui").is_file():
            found.append(name)
    return found


def load_surface_lang(repo_root: Path, surface: str) -> str:
    path = surface_path(repo_root, surface)
    if not path.is_file():
        raise PreviewError(
            f"missing {path} — run: northstar ui emit --surface {surface}"
        )
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PreviewError(str(exc)) from exc
    try:
        validate_openui_lang(text)
    except OpenUILangError as exc:
        raise PreviewError(f"fail-closed: invalid OpenUI Lang in {path}: {exc}") from exc
    return text


def parse_statements(lang: str) -> dict[str, str]:
    body = lang.strip()
    if body.startswith("```"):
        parts = body.split("\n", 1)
        body = parts[1] if len(parts) > 1 else ""
        if body.rstrip().endswith("```"):
            body = body.rstrip()[:-3].rstrip()
    statements: dict[str, str] = {}
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        m = _STMT.match(line)
        if m:
            statements[m.group(1)] = m.group(2).strip()
    return statements


def _unescape(value: str) -> str:
    return (
        value.replace("\\n", "\n")
        .replace("\\r", "\r")
        .replace('\\"', '"')
        .replace("\\\\", "\\")
    )


def extract_string_args(expr: str) -> list[str]:
    return [_unescape(m.group(1)) for m in _STRING_LIT.finditer(expr)]


def summarize_statement(ident: str, expr: str) -> dict[str, Any]:
    call = _CALL_NAME.match(expr)
    component = call.group(1) if call else None
    strings = extract_string_args(expr)
    return {
        "id": ident,
        "component": component,
        "expr": expr,
        "strings": strings,
    }


def _repo_version(repo_root: Path) -> str:
    path = Path(repo_root) / "VERSION"
    if path.is_file():
        return path.read_text(encoding="utf-8").strip() or "unknown"
    return "unknown"


def render_preview_html(
    repo_root: Path,
    *,
    surfaces: list[str] | None = None,
    active: str | None = None,
) -> str:
    """Build a self-contained HTML viewer for persisted OpenUI surfaces."""
    require_openui_gate()
    available = list_persisted_surfaces(repo_root)
    selected = surfaces or available
    if not selected:
        raise PreviewError(
            "no persisted OpenUI surfaces under .agent/ui/ — "
            "run: northstar ui emit --surface plan"
        )
    for name in selected:
        if name not in SURFACES:
            raise PreviewError(f"unknown surface: {name}")
        if name not in available:
            raise PreviewError(
                f"missing .agent/ui/{name}.openui — emit it first"
            )

    active_surface = active if active in selected else selected[0]
    version = _repo_version(repo_root)
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    nav_bits: list[str] = []
    sections: list[str] = []
    for name in selected:
        lang = load_surface_lang(repo_root, name)
        statements = parse_statements(lang)
        meta = validate_openui_lang(lang)
        nav_bits.append(
            f'<a class="nav{" active" if name == active_surface else ""}" '
            f'href="#{html.escape(name)}">{html.escape(name)}</a>'
        )
        cards: list[str] = []
        for ident, expr in statements.items():
            if ident == "root":
                continue
            summary = summarize_statement(ident, expr)
            title = summary["component"] or ident
            body_lines = summary["strings"] or [summary["expr"]]
            lis = "".join(
                f"<li>{html.escape(line)}</li>" for line in body_lines[:12]
            )
            cards.append(
                "<article class='card'>"
                f"<h3>{html.escape(str(title))} "
                f"<code>{html.escape(ident)}</code></h3>"
                f"<ul>{lis}</ul>"
                "</article>"
            )
        root_expr = statements.get("root", "")
        sections.append(
            f"<section id='{html.escape(name)}' class='surface'>"
            f"<h2>Surface: {html.escape(name)}</h2>"
            f"<p class='meta'>statements={meta['statement_count']} · "
            f"root=<code>{html.escape(root_expr)}</code></p>"
            f"<div class='cards'>{''.join(cards) or '<p>No child statements.</p>'}</div>"
            "<details><summary>Raw OpenUI Lang</summary>"
            f"<pre>{html.escape(lang)}</pre></details>"
            "</section>"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>NorthStar Open UI Viewer</title>
  <style>
    :root {{
      --ink: #0f172a;
      --muted: #475569;
      --line: #c5d0c8;
      --bg: linear-gradient(160deg, #f0f7f4 0%, #e8eef7 45%, #f7f3ea 100%);
      --card: rgba(255,255,255,0.72);
      --accent: #0f766e;
    }}
    body {{
      margin: 0;
      padding: 1.5rem;
      font-family: "IBM Plex Sans", "Source Sans 3", "Segoe UI", sans-serif;
      color: var(--ink);
      background: var(--bg);
      min-height: 100vh;
    }}
    h1, h2, h3 {{ font-family: Fraunces, Georgia, serif; letter-spacing: -0.02em; }}
    header {{ margin-bottom: 1rem; }}
    .badge {{
      display: inline-flex; gap: 0.55rem; align-items: baseline;
      border: 1px solid var(--line); border-radius: 12px;
      padding: 0.45rem 0.8rem; background: rgba(255,255,255,0.55);
      margin-bottom: 0.75rem;
    }}
    .nav-row {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0.75rem 0 1.25rem; }}
    .nav {{
      text-decoration: none; color: var(--ink);
      border: 1px solid var(--line); border-radius: 999px;
      padding: 0.35rem 0.85rem; background: rgba(255,255,255,0.5);
    }}
    .nav.active {{ background: #0f766e; color: #fff; border-color: #0f766e; }}
    .surface {{
      border: 1px solid var(--line); border-radius: 14px;
      padding: 1rem 1.15rem; margin-bottom: 1rem; background: var(--card);
    }}
    .meta {{ color: var(--muted); }}
    .cards {{ display: grid; gap: 0.65rem; }}
    .card {{
      border: 1px solid var(--line); border-radius: 12px;
      padding: 0.75rem 0.9rem; background: rgba(255,255,255,0.65);
    }}
    .card h3 {{ margin: 0 0 0.35rem; font-size: 1.05rem; }}
    .card code {{ font-size: 0.8rem; color: var(--muted); font-weight: 400; }}
    ul {{ margin: 0.25rem 0 0; padding-left: 1.1rem; color: var(--muted); }}
    pre {{
      overflow: auto; background: #0b1220; color: #e2e8f0;
      padding: 0.85rem; border-radius: 10px; font-size: 0.82rem;
    }}
    footer {{ color: var(--muted); font-size: 0.9rem; margin-top: 1.25rem; }}
  </style>
</head>
<body>
  <header>
    <div class="badge">
      <strong>NorthStar</strong>
      <span>v{html.escape(version)}</span>
      <span>Open UI Viewer</span>
    </div>
    <h1>Live Open UI surfaces</h1>
    <p class="meta">Generated {html.escape(generated)} from <code>.agent/ui/*.openui</code>.
      Static mock lives at <code>orchestrator/ui/preview.sample.html</code>.</p>
    <div class="nav-row">{''.join(nav_bits)}</div>
  </header>
  {''.join(sections)}
  <footer>
    Authority locks unchanged: never auto-approves.
    Approve still requires <code>COMPASS_CAPTAIN_APPROVE=1</code>.
  </footer>
</body>
</html>
"""


def write_preview(
    repo_root: Path,
    *,
    surfaces: list[str] | None = None,
    active: str | None = None,
    out_path: Path | None = None,
) -> Path:
    html_text = render_preview_html(
        repo_root, surfaces=surfaces, active=active
    )
    dest = out_path or (ui_dir(repo_root) / "preview.html")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html_text, encoding="utf-8")
    return dest


def serve_preview(
    repo_root: Path,
    *,
    surfaces: list[str] | None = None,
    active: str | None = None,
    host: str = "127.0.0.1",
    port: int = 8765,
    timeout_seconds: float | None = None,
) -> dict[str, Any]:
    """Serve ``.agent/ui/`` on localhost (127.0.0.1 only).

    Writes preview.html first. When ``timeout_seconds`` is set, shuts down after
    that many seconds (hermetic / smoke). Otherwise blocks until interrupted.
    """
    require_openui_gate()
    if host not in {"127.0.0.1", "localhost"}:
        raise PreviewError("serve host must be 127.0.0.1 or localhost")
    preview = write_preview(repo_root, surfaces=surfaces, active=active)
    directory = ui_dir(repo_root).resolve()

    class _Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, directory=str(directory), **kwargs)

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
            return

    server = ThreadingHTTPServer((host, port), _Handler)
    url = f"http://{host}:{port}/preview.html"
    if timeout_seconds is not None and timeout_seconds > 0:
        import threading

        def _shutdown() -> None:
            server.shutdown()

        timer = threading.Timer(timeout_seconds, _shutdown)
        timer.daemon = True
        timer.start()
        try:
            server.serve_forever(poll_interval=0.2)
        finally:
            timer.cancel()
            server.server_close()
        return {
            "status": "served",
            "url": url,
            "path": str(preview),
            "host": host,
            "port": port,
            "timeout_seconds": timeout_seconds,
            "authority_mutation": False,
            "auto_approved": False,
        }

    print(f"Serving {url} (Ctrl-C to stop)", flush=True)
    try:
        server.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return {
        "status": "stopped",
        "url": url,
        "path": str(preview),
        "host": host,
        "port": port,
        "authority_mutation": False,
        "auto_approved": False,
    }
