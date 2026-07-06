#!/usr/bin/env bash
# Agile Workflow Marketplace — one-shot installer
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$ROOT/scripts/install.py" "$@"
