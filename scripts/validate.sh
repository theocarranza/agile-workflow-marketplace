#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python3 - <<'PY'
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(".").resolve()
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
PLUGIN = json.loads((ROOT / ".plugin" / "plugin.json").read_text(encoding="utf-8"))
NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9.-]{0,62}[a-z0-9])?$")
PORTABLE_FM = frozenset({"name", "description", "license"})
REQUIRED_SKILLS = (
    "amend-workitems",
    "auto-fix-artifact",
    "decompose-backlog",
    "enrich-work-item",
    "generate-breakdown-work-items",
    "generate-plain-language-documentation",
    "generate-work-item",
    "split-story",
    "validate-artifact",
)


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


match PLUGIN.get("name"):
    case name if isinstance(name, str) and NAME_RE.fullmatch(name) and "--" not in name and ".." not in name:
        pass
    case other:
        fail(f"invalid plugin name: {other!r}")

match PLUGIN.get("version"):
    case version if version == VERSION:
        pass
    case other:
        fail(f".plugin/plugin.json version {other!r} != VERSION {VERSION!r}")

for relative in (
    Path(".claude-plugin") / "marketplace.json",
    Path(".cursor-plugin") / "marketplace.json",
    Path(".agents") / "plugins" / "marketplace.json",
):
    marketplace = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    match marketplace.get("plugins", [{}])[0].get("version"):
        case version if version == VERSION:
            pass
        case other:
            fail(f"{relative.as_posix()} plugin version {other!r} != VERSION {VERSION!r}")

for relative in (
    Path(".cursor-plugin") / "plugin.json",
    Path(".claude-plugin") / "plugin.json",
):
    host_plugin = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    match host_plugin.get("version"):
        case version if version == VERSION:
            pass
        case other:
            fail(f"{relative.as_posix()} version {other!r} != VERSION {VERSION!r}")

match (ROOT / ".codex-plugin").exists():
    case True:
        fail(".codex-plugin must not exist; Codex uses .agents/plugins/marketplace.json")
    case False:
        pass

for host in ("cursor", "claude", "codex"):
    manifest = json.loads((ROOT / "adapters" / host / "plugin.template.json").read_text(encoding="utf-8"))
    match (manifest.get("name"), manifest.get("version")):
        case (name, version) if name == PLUGIN["name"] and version == VERSION:
            pass
        case pair:
            fail(f"adapters/{host}/plugin.template.json name/version mismatch: {pair!r}")

mcp = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))
server = mcp["mcpServers"]["orchestrator"]
match server.get("env", {}).get("PYTHONPATH"):
    case "${PLUGIN_ROOT}":
        pass
    case other:
        fail(f".mcp.json PYTHONPATH must be ${{PLUGIN_ROOT}}, got {other!r}")

for skill_name in REQUIRED_SKILLS:
    skill = ROOT / "skills" / skill_name / "SKILL.md"
    match skill.is_file():
        case False:
            fail(f"missing skill: {skill}")
        case True:
            text = skill.read_text(encoding="utf-8")
            match text.startswith("---\n"):
                case False:
                    fail(f"{skill.as_posix()} missing frontmatter")
                case True:
                    end = text.find("\n---", 4)
                    match end:
                        case -1:
                            fail(f"{skill.as_posix()} frontmatter not closed")
                        case _:
                            fm = text[4:end]
                            keys = {
                                line.split(":", 1)[0].strip()
                                for line in fm.splitlines()
                                if line.strip() and not line.startswith(" ") and not line.startswith("#") and ":" in line
                            }
                            extras = keys - PORTABLE_FM
                            match extras:
                                case set() as empty if not empty:
                                    pass
                                case leftover:
                                    fail(
                                        f"{skill_name} frontmatter has non-portable keys: "
                                        f"{', '.join(sorted(leftover))}"
                                    )
                            name_match = re.search(r"(?m)^name:\s*(.+)$", fm)
                            match name_match.group(1).strip() if name_match else None:
                                case name if name == skill_name:
                                    pass
                                case other:
                                    fail(f"{skill_name} name must match directory, got {other!r}")
                            match bool(re.search(r"(?m)^description:\s*", fm)):
                                case True:
                                    pass
                                case False:
                                    fail(f"{skill_name} missing description")
                            match bool(re.search(r"(?m)^license:\s*", fm)):
                                case True:
                                    pass
                                case False:
                                    fail(f"{skill_name} missing license")

for required in (
    ROOT / "orchestrator_core" / "__init__.py",
    ROOT / "references" / "decomposition-rules.md",
    ROOT / "common" / "artifact-schema.json",
    ROOT / "bin" / "agile-backlog-toolkit",
):
    match required.exists():
        case False:
            fail(f"missing required path: {required}")
        case True:
            pass

print(f"validate ok: {PLUGIN['name']}@{VERSION}")
PY
