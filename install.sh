#!/usr/bin/env bash
# Prefer host adapters (Open Plugins marketplace builds). Legacy flags are forwarded
# to scripts/install.py. Project MCP-only wiring: scripts/wire-project-mcp.py.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
REPO="${PLUGIN_INSTALL_REPO:-theocarranza/agile-workflow-marketplace}"
REF="${PLUGIN_INSTALL_REF:-main}"

usage() {
  cat <<EOF
Install agile-backlog-toolkit via a host adapter:

  # Cursor
  curl -fsSL https://raw.githubusercontent.com/${REPO}/${REF}/adapters/cursor/install.sh \\
    | bash -s -- --repo ${REPO} --ref ${REF}

  # Claude Code
  curl -fsSL https://raw.githubusercontent.com/${REPO}/${REF}/adapters/claude/install.sh \\
    | bash -s -- --repo ${REPO} --ref ${REF}

  # Codex
  curl -fsSL https://raw.githubusercontent.com/${REPO}/${REF}/adapters/codex/install.sh \\
    | bash -s -- --repo ${REPO} --ref ${REF}

From a local checkout:

  bash ${ROOT}/adapters/cursor/install.sh
  bash ${ROOT}/adapters/claude/install.sh
  bash ${ROOT}/adapters/codex/install.sh

Optional project MCP wiring (Azure/Linear + orchestrator env):

  python3 ${ROOT}/scripts/wire-project-mcp.py --project-dir /path/to/project --provider local

Legacy full installer (host registration + project wiring; accepts --azure-org, -y, …):

  python3 ${ROOT}/scripts/install.py --help
  # or: bash install.sh --azure-org <org> -y …
EOF
}

case "${1:-}" in
  -h|--help|"")
    usage
    ;;
  cursor|claude|codex)
    host="$1"
    shift
    exec bash "${ROOT}/adapters/${host}/install.sh" "$@"
    ;;
  -*)
    exec python3 "${ROOT}/scripts/install.py" "$@"
    ;;
  *)
    echo "error: unknown host '${1}'. Use cursor, claude, or codex (or --help)." >&2
    usage >&2
    exit 2
    ;;
esac
