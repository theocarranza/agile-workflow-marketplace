#!/usr/bin/env bash
# Validate all agile-workflow skills against the Agent Skills open standard.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# Root skills/ is the discovery surface for skills.sh and openskills.cc; symlinks to agile-workflow/skills/.
SKILLS_DIR="$ROOT/skills"
if [[ ! -d "$SKILLS_DIR" ]]; then
  SKILLS_DIR="$ROOT/agile-workflow/skills"
fi
FAILED=0
for skill in "$SKILLS_DIR"/*/; do
  name="$(basename "$skill")"
  printf 'validating %s ... ' "$name"
  if npx --yes skills-ref@0.1.5 validate "$skill" >/dev/null 2>&1; then
    echo "ok"
  else
    echo "FAIL"
    npx --yes skills-ref@0.1.5 validate "$skill" 2>&1 || true
    FAILED=1
  fi
done
exit "$FAILED"
