#!/usr/bin/env bash
# serve-northstar-ingress.sh — stdlib GitHub webhook ingress for NorthStar (M22)
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: serve-northstar-ingress.sh [options]

Starts the NorthStar GitHub webhook ingress (stdlib HTTP).

Options:
  --repo <path>              Repo root (default: cwd)
  --mode fixtures|live       Default: fixtures (webhooks return 503)
  --bind <host>              Default: 127.0.0.1
  --port <port>              Default: 8787
  --product-repo <slug>      Must be sandbox allowlist (default)
  --webhook-secret-env <VAR> Env var holding HMAC secret (default NORTHSTAR_GITHUB_WEBHOOK_SECRET)
  -h, --help

Live mode requires the webhook secret env var to be set. Never commit secrets.
USAGE
}

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="."
MODE="fixtures"
BIND="127.0.0.1"
PORT="8787"
PRODUCT_REPO="loganware05/captain-compass-sandbox"
SECRET_ENV="NORTHSTAR_GITHUB_WEBHOOK_SECRET"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="$2"; shift 2 ;;
    --mode) MODE="$2"; shift 2 ;;
    --bind) BIND="$2"; shift 2 ;;
    --port) PORT="$2"; shift 2 ;;
    --product-repo) PRODUCT_REPO="$2"; shift 2 ;;
    --webhook-secret-env) SECRET_ENV="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

REPO="$(cd "$REPO" && pwd)"

if [[ "$MODE" == "live" ]]; then
  if [[ -z "${!SECRET_ENV:-}" ]]; then
    echo "error: live ingress requires ${SECRET_ENV} to be set" >&2
    exit 2
  fi
fi

export NORTHSTAR_GITHUB_WEBHOOK_SECRET="${!SECRET_ENV:-}"

PYTHONPATH="$ROOT" python3 - "$REPO" "$MODE" "$BIND" "$PORT" "$PRODUCT_REPO" <<'PY'
import sys
from pathlib import Path

from orchestrator.integrations.ingress.server import run_ingress_forever

repo, mode, bind, port, product_repo = sys.argv[1:6]
print(
    f"NorthStar ingress mode={mode} bind={bind}:{port} product={product_repo}",
    flush=True,
)
run_ingress_forever(
    repo_root=Path(repo),
    host=bind,
    port=int(port),
    mode=mode,
    product_repository=product_repo,
)
PY
