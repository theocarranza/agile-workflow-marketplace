#!/usr/bin/env bash
# Agile Backlog Toolkit — one-shot installer
# Works from a local checkout OR when piped:
#   curl -fsSL …/install.sh | bash -s -- -y --azure-org <org> --project-dir <path>
set -euo pipefail

REPO_URL="${AGILE_BACKLOG_TOOLKIT_REPO:-https://github.com/theocarranza/agile-backlog-toolkit.git}"
REPO_REF="${AGILE_BACKLOG_TOOLKIT_REF:-main}"

resolve_local_root() {
  local src dir
  src="${BASH_SOURCE[0]:-}"
  # curl|bash -s: no real script path on disk
  if [[ -z "$src" || "$src" == "bash" || "$src" == "-" || ! -f "$src" ]]; then
    return 1
  fi
  dir="$(cd "$(dirname "$src")" && pwd)"
  if [[ -f "$dir/scripts/install.py" ]]; then
    printf '%s\n' "$dir"
    return 0
  fi
  return 1
}

if ROOT="$(resolve_local_root)"; then
  exec python3 "$ROOT/scripts/install.py" "$@"
fi

# Remote bootstrap: shallow-clone, run installer, then remove the temp checkout
if ! command -v git >/dev/null 2>&1; then
  echo "error: git is required for curl|bash install (or clone the repo and run ./install.sh)" >&2
  exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "error: python3 is required" >&2
  exit 1
fi

TMP="$(mktemp -d "${TMPDIR:-/tmp}/agile-backlog-toolkit-install.XXXXXX")"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

echo "[*] Bootstrapping from ${REPO_URL}@${REPO_REF} …"
git clone --depth 1 --branch "$REPO_REF" "$REPO_URL" "$TMP/repo"
python3 "$TMP/repo/scripts/install.py" "$@"
