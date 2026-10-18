#!/usr/bin/env bash
# Open the writer desk in a browser. Leave this running.

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$ROOT/skin/app.py"
