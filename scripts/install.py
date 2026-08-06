#!/usr/bin/env python3
"""Install and wire agile-backlog-toolkit with minimal prompts."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

INSTALL_DIR = Path.home() / ".agile-backlog-toolkit"
PLUGIN_NAME = "agile-backlog-toolkit"
MARKETPLACE_NAME = "agile-backlog-toolkit"
PLUGIN_SOURCE_DIR = "agile-backlog-toolkit"
PLUGIN_BUNDLE_DIRS = ("common", "skills", "references", "orchestrator_core")
ALL_TARGETS = ("claude", "cursor", "codex", "antigravity")
LINEAR_MCP_URL = "https://mcp.linear.app/mcp"

PROJECT_HOST_PLUGIN_DIRS = {
    "claude": Path(".claude") / "plugins" / PLUGIN_NAME,
    "codex": Path(".codex") / "plugins" / PLUGIN_NAME,
    "cursor": Path(".cursor") / "plugins" / PLUGIN_NAME,
}

LEGACY_INSTALL_DIRS = (
    Path.home() / ".agile-workflow-marketplace",
    Path.home() / ".agile-workflow",
)
LEGACY_PROJECT_PATHS = (
    Path(".agile-workflow"),
    Path(".agile-workflow.install.json"),
)

_COPY_IGNORE = shutil.ignore_patterns(
    ".git",
    "__pycache__",
    "*.pyc",
    ".superpowers",
    ".agentic",
    "node_modules",
    ".obsidian",
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + f"{datetime.now(timezone.utc).microsecond // 1000:03d}Z"


def _prompt(text: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    while True:
        try:
            value = input(f"{text}{suffix}: ").strip()
        except EOFError:
            value = ""
        if value:
            return value
        if default is not None:
            return default
        print("  (required)")


def _yes_no(text: str, default: bool = True) -> bool:
    hint = "Y/n" if default else "y/N"
    try:
        value = input(f"{text} [{hint}]: ").strip().lower()
    except EOFError:
        value = ""
    if not value:
        return default
    return value in {"y", "yes"}


def detect_hosts() -> list[str]:
    home = Path.home()
    hosts: list[str] = []
    if (home / ".claude").is_dir():
        hosts.append("claude")
    if (home / ".cursor").is_dir():
        hosts.append("cursor")
    if (home / ".agents").is_dir() or (home / ".codex-plugins").is_dir():
        hosts.append("codex")
    if (home / ".gemini").is_dir():
        hosts.append("antigravity")
    return hosts


def parse_targets(raw: str | None, *, non_interactive: bool) -> list[str]:
    if raw in (None, "", "all-agents", "all"):
        detected = detect_hosts()
        return detected if detected else list(ALL_TARGETS)
    targets = [part.strip().lower() for part in raw.split(",") if part.strip()]
    unknown = [t for t in targets if t not in ALL_TARGETS]
    if unknown:
        raise ValueError(f"Unknown target(s): {', '.join(unknown)}. Use: {', '.join(ALL_TARGETS)}")
    return targets


def read_azure_org_from_mcp(mcp_path: Path) -> str | None:
    if not mcp_path.is_file():
        return None
    try:
        data = json.loads(mcp_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    servers = data.get("mcpServers", {})
    for key in ("azure-devops", "Azure DevOps", "azure_devops"):
        entry = servers.get(key)
        if not isinstance(entry, dict):
            continue
        args = entry.get("args", [])
        if isinstance(args, list) and args:
            return str(args[-1])
    return None


def validate_source_package(source_root: Path) -> tuple[str, ...]:
    """Validate a staged package before any installed state is removed."""
    proot = source_root / PLUGIN_SOURCE_DIR
    required = (
        proot / ".claude-plugin" / "plugin.json",
        proot / ".codex-plugin" / "plugin.json",
        proot / ".mcp.json",
        proot / "common" / "artifact-schema.json",
        proot / "skills",
        proot / "orchestrator_core" / "__init__.py",
    )
    errors = tuple(f"missing package resource: {path}" for path in required if not path.exists())
    if errors:
        return errors
    try:
        manifests = (
            json.loads((proot / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")),
            json.loads((proot / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")),
        )
        schema = json.loads((proot / "common" / "artifact-schema.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return (f"invalid staged package JSON: {exc}",)
    identities = {(manifest.get("name"), manifest.get("version")) for manifest in manifests}
    if len(identities) != 1 or next(iter(identities))[0] != PLUGIN_NAME:
        return ("Claude and Codex manifests must share the agile-backlog-toolkit identity and version",)
    if schema.get("title") is None:
        return ("artifact schema has no title",)
    return ()


def _managed_registration_present(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return False
    return any(name in text for name in ("agile-workflow", "agile-backlog-toolkit"))


def managed_state(project_dir: Path, install_dir: Path, source_root: Path) -> tuple[str, ...]:
    home = Path.home()
    paths = [
        *LEGACY_INSTALL_DIRS,
        project_dir / ".agile-backlog-toolkit",
        project_dir / ".agile-backlog-toolkit.install.json",
        *(project_dir / relpath for relpath in LEGACY_PROJECT_PATHS),
        *(project_dir / relpath for relpath in PROJECT_HOST_PLUGIN_DIRS.values()),
        home / ".codex" / "plugins" / PLUGIN_NAME,
        home / ".codex-plugins" / "agile-workflow",
        home / ".local" / "bin" / "agile-workflow",
        home / ".local" / "bin" / PLUGIN_NAME,
    ]
    if install_dir.resolve() != source_root.resolve():
        paths.append(install_dir)
    registrations = (
        home / ".claude" / "plugins" / "installed_plugins.json",
        home / ".claude" / "plugins" / "known_marketplaces.json",
        home / ".agents" / "plugins" / "marketplace.json",
        project_dir / ".mcp.json",
        project_dir / ".cursor" / "mcp.json",
    )
    found = [str(path) for path in paths if path.exists() or path.is_symlink()]
    found.extend(f"registration:{path}" for path in registrations if _managed_registration_present(path))
    return tuple(sorted(set(found)))


def _remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink(missing_ok=True)
    elif path.is_dir():
        shutil.rmtree(path)


def _remove_json_entries(path: Path, *, mcp: bool = False) -> None:
    if not path.is_file():
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    names = {"agile-workflow", "agile-workflow-marketplace", PLUGIN_NAME, MARKETPLACE_NAME}
    if mcp:
        servers = data.get("mcpServers")
        if isinstance(servers, dict):
            for key in tuple(servers):
                if key in {"azure-devops", "agile-workflow-orchestrator", "agile-backlog-toolkit-orchestrator", "linear"}:
                    servers.pop(key, None)
    plugins = data.get("plugins")
    if isinstance(plugins, dict):
        for key in tuple(plugins):
            if any(name in key for name in names):
                plugins.pop(key, None)
    elif isinstance(plugins, list):
        data["plugins"] = [entry for entry in plugins if not isinstance(entry, dict) or entry.get("name") not in names]
    for key in tuple(data):
        if key in names:
            data.pop(key, None)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def remove_managed_state(project_dir: Path, install_dir: Path, source_root: Path) -> None:
    home = Path.home()
    paths = [
        *LEGACY_INSTALL_DIRS,
        project_dir / ".agile-backlog-toolkit",
        project_dir / ".agile-backlog-toolkit.install.json",
        *(project_dir / relpath for relpath in LEGACY_PROJECT_PATHS),
        *(project_dir / relpath for relpath in PROJECT_HOST_PLUGIN_DIRS.values()),
        project_dir / ".cursor" / "bin" / "azure-devops-mcp.sh",
        home / ".codex" / "plugins" / PLUGIN_NAME,
        home / ".codex-plugins" / "agile-workflow",
        home / ".local" / "bin" / "agile-workflow",
        home / ".local" / "bin" / PLUGIN_NAME,
    ]
    if install_dir.resolve() != source_root.resolve():
        paths.append(install_dir)
    for path in paths:
        _remove_path(path)
    _remove_json_entries(home / ".claude" / "plugins" / "installed_plugins.json")
    _remove_json_entries(home / ".claude" / "plugins" / "known_marketplaces.json")
    _remove_json_entries(home / ".agents" / "plugins" / "marketplace.json")
    _remove_json_entries(project_dir / ".mcp.json", mcp=True)
    _remove_json_entries(project_dir / ".cursor" / "mcp.json", mcp=True)


def replacement_choice() -> bool:
    print("Older plugin-managed installation state was detected.")
    print("  Proceed: remove plugin-managed state and perform a fresh installation.")
    print("  Abort: leave everything unchanged.")
    return _prompt("Choose Proceed or Abort").strip().lower() == "proceed"


def install_marketplace(source_root: Path, install_dir: Path) -> None:
    if source_root.resolve() == install_dir.resolve():
        return
    if install_dir.exists():
        shutil.rmtree(install_dir)
    install_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_root, install_dir, ignore=_COPY_IGNORE)


def plugin_root(install_dir: Path) -> Path:
    """Repository package location; the public plugin id is intentionally independent."""
    return install_dir / PLUGIN_SOURCE_DIR


def plugin_version(install_dir: Path) -> str:
    for manifest in (
        plugin_root(install_dir) / ".claude-plugin" / "plugin.json",
        plugin_root(install_dir) / ".codex-plugin" / "plugin.json",
    ):
        if manifest.is_file():
            try:
                return json.loads(manifest.read_text(encoding="utf-8")).get("version", "0.0.0")
            except (OSError, json.JSONDecodeError):
                continue
    return "0.0.0"


def _load_plugin_manifest(proot: Path) -> dict:
    for manifest in (
        proot / ".claude-plugin" / "plugin.json",
        proot / ".codex-plugin" / "plugin.json",
    ):
        if manifest.is_file():
            return json.loads(manifest.read_text(encoding="utf-8"))
    return {"name": PLUGIN_NAME, "version": "0.0.0", "description": ""}


def copy_plugin_bundle(
    proot: Path,
    dest: Path,
    *,
    include_claude_plugin: bool = False,
    include_codex_plugin: bool = False,
) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)
    for dirname in PLUGIN_BUNDLE_DIRS:
        src = proot / dirname
        if src.is_dir():
            shutil.copytree(src, dest / dirname, ignore=_COPY_IGNORE)
    mcp_config = proot / ".mcp.json"
    if mcp_config.is_file():
        shutil.copy2(mcp_config, dest / ".mcp.json")
    if include_claude_plugin:
        src = proot / ".claude-plugin"
        if src.is_dir():
            shutil.copytree(src, dest / ".claude-plugin", ignore=_COPY_IGNORE)
    if include_codex_plugin:
        src = proot / ".codex-plugin"
        if src.is_dir():
            shutil.copytree(src, dest / ".codex-plugin", ignore=_COPY_IGNORE)


def assemble_host_tree(proot: Path, destination: Path, target: str) -> Path:
    """Materialize a host-owned, self-contained plugin tree without symlinks."""
    manifests = {
        "claude": (True, False),
        "cursor": (True, False),
        "codex": (False, True),
        "antigravity": (False, True),
    }
    include_claude_plugin, include_codex_plugin = manifests[target]
    copy_plugin_bundle(
        proot,
        destination,
        include_claude_plugin=include_claude_plugin,
        include_codex_plugin=include_codex_plugin,
    )
    return destination


def link_cli_skills(proot: Path, destination: Path) -> bool:
    """Expose every bundled skill through a host CLI's native skills directory."""
    skills = proot / "skills"
    if not skills.is_dir():
        return False
    destination.mkdir(parents=True, exist_ok=True)
    linked = False
    for skill in sorted(path for path in skills.iterdir() if path.is_dir()):
        target = destination / skill.name
        shutil.copytree(skill, target, ignore=_COPY_IGNORE, dirs_exist_ok=True)
        linked = True
    return linked


def register_claude_plugin(install_dir: Path) -> bool:
    proot = plugin_root(install_dir)
    manifest = _load_plugin_manifest(proot)
    version = manifest.get("version", "0.0.0")
    cache_dir = (
        Path.home() / ".claude" / "plugins" / "cache" / MARKETPLACE_NAME / PLUGIN_NAME / version
    )
    copy_plugin_bundle(proot, cache_dir, include_claude_plugin=True)

    plugin_meta = {k: manifest[k] for k in ("name", "description", "version", "author") if k in manifest}
    (cache_dir / ".claude-plugin").mkdir(exist_ok=True)
    (cache_dir / ".claude-plugin" / "plugin.json").write_text(
        json.dumps(plugin_meta, indent=2) + "\n",
        encoding="utf-8",
    )

    registry_path = Path.home() / ".claude" / "plugins" / "installed_plugins.json"
    registry: dict = {"version": 2, "plugins": {}}
    if registry_path.is_file():
        try:
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass

    plugin_key = f"{PLUGIN_NAME}@{MARKETPLACE_NAME}"
    now = _now_iso()
    existing = registry.setdefault("plugins", {}).get(plugin_key, [])
    installed_at = existing[0].get("installedAt", now) if existing else now
    registry["plugins"][plugin_key] = [
        {
            "scope": "user",
            "installPath": str(cache_dir),
            "version": version,
            "installedAt": installed_at,
            "lastUpdated": now,
        }
    ]
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    return True


def register_known_marketplace(install_dir: Path) -> bool:
    path = Path.home() / ".claude" / "plugins" / "known_marketplaces.json"
    data: dict = {}
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
    data[MARKETPLACE_NAME] = {
        "source": {"source": "local", "path": str(install_dir / ".claude-plugin" / "marketplace.json")},
        "installLocation": str(install_dir),
        "lastUpdated": _now_iso(),
        "autoUpdate": False,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return True


def register_cursor_plugin(install_dir: Path) -> bool:
    if not (Path.home() / ".cursor").is_dir():
        return False
    proot = plugin_root(install_dir)
    manifest = _load_plugin_manifest(proot)
    version = manifest.get("version", "0.0.0")

    marketplace_link = Path.home() / ".cursor" / "plugins" / "marketplaces" / "local" / MARKETPLACE_NAME
    marketplace_link.parent.mkdir(parents=True, exist_ok=True)
    if marketplace_link.is_symlink():
        marketplace_link.unlink()
    shutil.copytree(install_dir, marketplace_link, dirs_exist_ok=True)

    cache_dir = (
        Path.home()
        / ".cursor"
        / "plugins"
        / "cache"
        / "local"
        / MARKETPLACE_NAME
        / PLUGIN_NAME
        / version
    )
    copy_plugin_bundle(proot, cache_dir, include_claude_plugin=True)
    plugin_meta = {k: manifest[k] for k in ("name", "description", "version", "author") if k in manifest}
    (cache_dir / ".claude-plugin").mkdir(exist_ok=True)
    (cache_dir / ".claude-plugin" / "plugin.json").write_text(
        json.dumps(plugin_meta, indent=2) + "\n",
        encoding="utf-8",
    )
    # Cursor CLI discovers native skills independently of plugin cache loading.
    link_cli_skills(proot, Path.home() / ".cursor" / "skills")
    return True


def register_codex_plugin(install_dir: Path) -> bool:
    proot = plugin_root(install_dir)
    manifest = _load_plugin_manifest(proot)
    version = manifest.get("version", "0.0.0")

    codex_plugins = Path.home() / ".codex" / "plugins" / PLUGIN_NAME
    copy_plugin_bundle(proot, codex_plugins, include_codex_plugin=True)
    clean_manifest = {k: manifest[k] for k in ("name", "version", "description", "author") if k in manifest}
    (codex_plugins / "plugin.json").write_text(json.dumps(clean_manifest, indent=2) + "\n", encoding="utf-8")
    (codex_plugins / "installed_version.json").write_text(
        json.dumps({"version": version}) + "\n",
        encoding="utf-8",
    )

    marketplace_path = Path.home() / ".agents" / "plugins" / "marketplace.json"
    marketplace: dict = {
        "name": "personal",
        "interface": {"displayName": "Personal"},
        "plugins": [],
    }
    if marketplace_path.is_file():
        try:
            marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass

    marketplace.setdefault("name", "personal")
    marketplace.setdefault("interface", {"displayName": "Personal"})
    plugins = marketplace.setdefault("plugins", [])
    plugins[:] = [p for p in plugins if p.get("name") not in {PLUGIN_NAME, MARKETPLACE_NAME}]
    plugins.append(
        {
            "name": PLUGIN_NAME,
            "source": {"source": "local", "path": str(proot)},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Productivity",
        }
    )

    marketplace_path.parent.mkdir(parents=True, exist_ok=True)
    marketplace_path.write_text(json.dumps(marketplace, indent=2) + "\n", encoding="utf-8")
    return True


def register_antigravity_plugin(install_dir: Path) -> bool:
    proot = plugin_root(install_dir)
    manifest = _load_plugin_manifest(proot)
    version = manifest.get("version", "0.0.0")
    description = manifest.get("description", "")
    author = manifest.get("author", {}).get("name", "local") if isinstance(manifest.get("author"), dict) else "local"
    ok = False

    config_plugins = Path.home() / ".gemini" / "config" / "plugins"
    if config_plugins.is_dir():
        plugin_dir = config_plugins / PLUGIN_NAME
        copy_plugin_bundle(proot, plugin_dir, include_codex_plugin=True)
        clean_manifest = {k: manifest[k] for k in ("name", "version", "description", "author") if k in manifest}
        (plugin_dir / "plugin.json").write_text(json.dumps(clean_manifest, indent=2) + "\n", encoding="utf-8")
        (plugin_dir / "installed_version.json").write_text(
            json.dumps({"version": version}) + "\n",
            encoding="utf-8",
        )
        ok = True

    ide_plugins = Path.home() / ".gemini" / "antigravity-ide" / "plugins"
    if ide_plugins.is_dir():
        plugin_dir = ide_plugins / f"{author}.{PLUGIN_NAME}.{PLUGIN_NAME}"
        if plugin_dir.exists():
            shutil.rmtree(plugin_dir)
        plugin_dir.mkdir(parents=True, exist_ok=True)
        shutil.copytree(proot / "skills", plugin_dir / "skills", ignore=_COPY_IGNORE)
        (plugin_dir / "plugin.json").write_text(
            json.dumps({"name": PLUGIN_NAME, "description": description, "disabled": False}),
            encoding="utf-8",
        )
        ok = True

    # Antigravity CLI has a separate plugin root from the IDE global root.
    cli_plugins = Path.home() / ".gemini" / "antigravity-cli" / "plugins"
    cli_plugin_dir = cli_plugins / PLUGIN_NAME
    copy_plugin_bundle(proot, cli_plugin_dir, include_codex_plugin=False)
    cli_plugin_dir.joinpath("plugin.json").write_text(
        json.dumps({"name": PLUGIN_NAME, "description": description}, indent=2) + "\n",
        encoding="utf-8",
    )
    cli_plugin_dir.joinpath("installed_version.json").write_text(
        json.dumps({"version": version}) + "\n",
        encoding="utf-8",
    )
    link_cli_skills(proot, Path.home() / ".gemini" / "antigravity-cli" / "skills")
    ok = True

    return ok


def register_hosts(install_dir: Path, targets: list[str]) -> list[str]:
    registered: list[str] = []
    handlers = {
        "claude": lambda: register_claude_plugin(install_dir) and register_known_marketplace(install_dir),
        "cursor": lambda: register_cursor_plugin(install_dir),
        "codex": lambda: register_codex_plugin(install_dir),
        "antigravity": lambda: register_antigravity_plugin(install_dir),
    }
    labels = {
        "claude": "Claude Code",
        "cursor": "Cursor",
        "codex": "Codex",
        "antigravity": "Antigravity",
    }
    for target in targets:
        handler = handlers.get(target)
        if handler is None:
            continue
        print(f"[*] Registering {labels[target]} …")
        if handler():
            print(f"    ✓ {labels[target]}")
            registered.append(target)
        else:
            print(f"    ! {labels[target]} skipped (host not present or registration failed)", file=sys.stderr)
    return registered


def materialize_project_hosts(project_dir: Path, proot: Path, targets: list[str]) -> list[Path]:
    """Create independent project-local plugin copies for the three required hosts."""
    written: list[Path] = []
    for target in targets:
        relpath = PROJECT_HOST_PLUGIN_DIRS.get(target)
        if relpath is None:
            continue
        destination = project_dir / relpath
        written.append(assemble_host_tree(proot, destination, target))
    return written


def merge_json_mcp(path: Path, servers: dict[str, dict]) -> None:
    existing: dict = {"mcpServers": {}}
    if path.is_file():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {"mcpServers": {}}
    merged = existing.setdefault("mcpServers", {})
    merged.update(servers)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")


# Hosts that read Claude/Codex-style project `.mcp.json` (not Cursor's `.cursor/mcp.json`).
_MCP_JSON_HOSTS = frozenset({"claude", "codex", "antigravity"})


def resolve_tool_paths(*names: str) -> dict[str, str]:
    """Resolve executables to absolute paths (via PATH lookup)."""
    required = names or ("python3", "npx")
    resolved: dict[str, str] = {}
    missing: list[str] = []
    for name in required:
        path = shutil.which(name)
        if path:
            resolved[name] = path
        else:
            missing.append(name)
    if missing:
        raise ValueError(
            "Required executable(s) not found on PATH: "
            + ", ".join(missing)
            + ". Install them and retry."
        )
    return resolved


AZURE_MCP_PACKAGE = "@azure-devops/mcp@2.7.0"
AZURE_MCP_HOME = Path.home() / ".local" / "share" / "azure-devops-mcp"
AZURE_MCP_ENTRYPOINT = AZURE_MCP_HOME / "node_modules" / "@azure-devops" / "mcp" / "dist" / "index.js"


def azure_mcp_entrypoint() -> Path | None:
    """The pinned MCP entrypoint, when it has been installed."""
    return AZURE_MCP_ENTRYPOINT if AZURE_MCP_ENTRYPOINT.is_file() else None


def ensure_azure_mcp_installed(*, npm_path: str | None, quiet: bool = False) -> Path | None:
    """Install the Azure DevOps MCP server to a fixed location, best effort.

    Launching a pinned `node <path>` beats `npx` twice over: npx re-resolves the package on
    every start, and it is the piece that breaks when a host leaks a truncated PATH into
    stdio servers. Failure here is not fatal -- the caller falls back to npx.
    """
    existing = azure_mcp_entrypoint()
    if existing:
        return existing
    if not npm_path:
        return None

    AZURE_MCP_HOME.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            [npm_path, "install", "--prefix", str(AZURE_MCP_HOME), AZURE_MCP_PACKAGE],
            check=True,
            capture_output=True,
            timeout=300,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
        if not quiet:
            print(f"    ! could not pre-install {AZURE_MCP_PACKAGE} ({exc.__class__.__name__}); using npx")
        return None
    return azure_mcp_entrypoint()


def azure_mcp_launch(
    *,
    azure_org: str,
    node_path: str | None,
    npx_path: str,
    entrypoint: Path | None,
) -> tuple[str, list[str]]:
    """Command and args for launching the Azure DevOps MCP server.

    Prefers the pinned entrypoint; falls back to npx when it is unavailable.
    """
    if entrypoint and node_path:
        return node_path, [str(entrypoint), azure_org]
    return npx_path, ["-y", AZURE_MCP_PACKAGE, azure_org]


def write_cursor_azure_wrapper(
    project_dir: Path,
    *,
    azure_org: str,
    npx_path: str,
    node_path: str | None = None,
    entrypoint: Path | None = None,
) -> Path:
    """Project-local wrapper so Cursor stdio MCP gets a sane PATH (no bare `npx`).

    Uses the pinned entrypoint when one exists, for the same reason the Claude wiring does.
    """
    bin_dir = project_dir / ".cursor" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    script = bin_dir / "azure-devops-mcp.sh"
    env_script = Path.home() / ".local" / "bin" / "cursor-mcp" / "cursor-mcp-env.sh"
    env_block = (
        f'source "{env_script}"\n'
        if env_script.is_file()
        else "unset ELECTRON_RUN_AS_NODE\n"
    )
    command, args = azure_mcp_launch(
        azure_org=azure_org, node_path=node_path, npx_path=npx_path, entrypoint=entrypoint
    )
    quoted = " ".join(f'"{arg}"' for arg in args)
    script.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f"{env_block}"
        f'exec "{command}" {quoted} "$@"\n',
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script


def _mcp_server_payloads(
    *,
    proot: Path,
    project_dir: Path,
    azure_org: str | None,
    tool_paths: dict[str, str],
    enable_azure: bool,
    enable_linear: bool,
    cursor_azure_wrapper: Path | None = None,
) -> tuple[dict[str, dict], dict[str, dict]]:
    python3 = tool_paths["python3"]
    # No artifacts location here: the plugin resolves that from .agile-backlog-toolkit/config.json
    # at runtime, and has no default to inject.
    orchestrator_env = {
        "PYTHONPATH": str(proot),
        "CODEX_PROJECT_ROOT": str(project_dir.resolve()),
    }
    claude_servers: dict[str, dict] = {
        "agile-backlog-toolkit-orchestrator": {
            "command": python3,
            "args": ["-m", "orchestrator_core", "mcp"],
            "env": orchestrator_env,
        },
    }
    cursor_servers: dict[str, dict] = {
        "agile-backlog-toolkit-orchestrator": {
            "type": "stdio",
            "command": python3,
            "args": ["-m", "orchestrator_core", "mcp"],
            "env": orchestrator_env,
        },
    }
    if enable_azure and azure_org:
        npx = tool_paths["npx"]
        node_path = tool_paths.get("node") or shutil.which("node")
        azure_cmd, azure_cmd_args = azure_mcp_launch(
            azure_org=azure_org,
            node_path=node_path,
            npx_path=npx,
            entrypoint=azure_mcp_entrypoint(),
        )
        claude_servers["azure-devops"] = {"command": azure_cmd, "args": azure_cmd_args}
        cursor_servers["azure-devops"] = {
            "type": "stdio",
            "command": str(cursor_azure_wrapper) if cursor_azure_wrapper else azure_cmd,
            "args": [] if cursor_azure_wrapper else list(azure_cmd_args),
            "env": {},
        }
    if enable_linear:
        linear = {"url": LINEAR_MCP_URL}
        claude_servers["linear"] = linear
        cursor_servers["linear"] = {"type": "http", **linear}
    return claude_servers, cursor_servers


def wire_project_mcp(
    project_dir: Path,
    *,
    install_dir: Path,
    azure_org: str | None,
    targets: list[str],
    enable_azure: bool,
    enable_linear: bool = False,
) -> None:
    proot = plugin_root(install_dir).resolve()
    required_tools = ("python3", "npx") if enable_azure else ("python3",)
    tool_paths = resolve_tool_paths(*required_tools)
    node_path = shutil.which("node")
    entrypoint = None
    if enable_azure and azure_org:
        entrypoint = ensure_azure_mcp_installed(npm_path=shutil.which("npm"))
        if entrypoint:
            print(f"    ✓ Azure DevOps MCP pinned at {entrypoint}")
    else:
        print("    ↷ Azure MCP skipped (provider not selected)")
    cursor_wrapper: Path | None = None
    if enable_azure and azure_org and "cursor" in targets:
        cursor_wrapper = write_cursor_azure_wrapper(
            project_dir,
            azure_org=azure_org,
            npx_path=tool_paths["npx"],
            node_path=node_path,
            entrypoint=entrypoint,
        )
    claude_servers, cursor_servers = _mcp_server_payloads(
        proot=proot,
        project_dir=project_dir,
        azure_org=azure_org,
        tool_paths=tool_paths,
        enable_azure=enable_azure,
        enable_linear=enable_linear,
        cursor_azure_wrapper=cursor_wrapper,
    )

    if _MCP_JSON_HOSTS.intersection(targets):
        merge_json_mcp(project_dir / ".mcp.json", claude_servers)
        print("    ✓ project .mcp.json")

    if "cursor" in targets:
        merge_json_mcp(project_dir / ".cursor" / "mcp.json", cursor_servers)
        print("    ✓ project .cursor/mcp.json")
        if cursor_wrapper:
            print("    ✓ project .cursor/bin/azure-devops-mcp.sh")


def install_cli(install_dir: Path) -> Path:
    bin_dir = Path.home() / ".local" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    target = bin_dir / "agile-backlog-toolkit"
    proot = plugin_root(install_dir).resolve()
    python3 = resolve_tool_paths("python3")["python3"]
    script = f"""#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="{proot}"${{PYTHONPATH:+:$PYTHONPATH}}
exec {python3!r} -m orchestrator_core "$@"
"""
    target.write_text(script, encoding="utf-8")
    target.chmod(0o755)
    return target


def scaffold_project(project_dir: Path) -> None:
    """Create only what the plugin owns.

    The installer never creates a directory structure for the user's artifacts. Where those
    go is the user's decision, captured as `artifacts_path` and asked for on first use.
    """
    mailbox = project_dir / ".agentic" / "workflow_prompts"
    mailbox.mkdir(parents=True, exist_ok=True)
    gitkeep = mailbox / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.write_text("", encoding="utf-8")
    (project_dir / ".agile-backlog-toolkit").mkdir(parents=True, exist_ok=True)


def write_install_manifest(
    project_dir: Path,
    *,
    install_dir: Path,
    provider_mode: str,
    azure_org: str | None,
    version: str,
    hosts: list[str],
) -> Path:
    path = project_dir / ".agile-backlog-toolkit.install.json"
    payload = {
        "marketplace": MARKETPLACE_NAME,
        "plugin": PLUGIN_NAME,
        "version": version,
        "provider_mode": provider_mode,
        "install_dir": str(install_dir.resolve()),
        "hosts": hosts,
        "installed_at": _now_iso(),
    }
    if azure_org:
        payload["azure_devops_org"] = azure_org
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def write_project_config(
    project_dir: Path,
    *,
    provider_mode: str,
    azure_org: str | None,
    azure_project: str | None,
    azure_team: str | None,
    azure_process: str | None,
    linear_team: str | None = None,
    artifacts_path: str | None = None,
) -> Path:
    """Write `.agile-backlog-toolkit/config.json`, the runtime config skills and the CLI read.

    Only the org is required here. Project, team, and process may be filled in later by the
    skill that first needs them -- see `orchestrator_core/project_config.py`.
    """
    path = project_dir / ".agile-backlog-toolkit" / "config.json"
    path.parent.mkdir(parents=True, exist_ok=True)

    existing: dict = {}
    if path.is_file():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                existing = loaded
        except (OSError, json.JSONDecodeError):
            existing = {}

    existing["provider_mode"] = provider_mode

    if azure_org:
        azure = existing.get("azure") if isinstance(existing.get("azure"), dict) else {}
        azure["org"] = azure_org
        for key, value in (("project", azure_project), ("team", azure_team), ("process", azure_process)):
            if value:
                azure[key] = value
        existing["azure"] = azure
    elif "azure" in existing and not isinstance(existing.get("azure"), dict):
        existing.pop("azure", None)

    if linear_team:
        linear = existing.get("linear") if isinstance(existing.get("linear"), dict) else {}
        linear["team"] = linear_team
        existing["linear"] = linear

    if artifacts_path:
        existing["artifacts_path"] = artifacts_path
    path.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
    return path


def validate_azure_org(org: str) -> str:
    org = org.strip()
    if not org or re.search(r"\s", org):
        raise ValueError("Azure DevOps org must be a single slug (no spaces).")
    return org


def run_install(
    *,
    source_root: Path,
    install_dir: Path,
    project_dir: Path,
    provider_mode: str,
    azure_org: str | None,
    targets: list[str],
    artifacts_path: str | None = None,
    azure_project: str | None = None,
    azure_team: str | None = None,
    azure_process: str | None = None,
    linear_team: str | None = None,
    skip_copy: bool = False,
) -> int:
    print(f"\n[*] Installing marketplace → {install_dir}")
    if not skip_copy:
        install_marketplace(source_root, install_dir)

    version = plugin_version(install_dir)
    print(f"[*] Plugin version: {version}")
    print(f"[*] Agent targets: {', '.join(targets)}")

    hosts = register_hosts(install_dir, targets)
    host_bundles = materialize_project_hosts(project_dir, plugin_root(install_dir), targets)
    for bundle in host_bundles:
        print(f"    ✓ host bundle {bundle}")

    print(f"[*] Wiring MCP servers for {project_dir} …")
    wire_project_mcp(
        project_dir,
        install_dir=install_dir,
        azure_org=azure_org,
        targets=targets,
        enable_azure=provider_mode in {"azure", "both"},
        enable_linear=provider_mode in {"linear", "both"},
    )

    cli_path = install_cli(install_dir)
    print(f"[*] CLI installed → {cli_path}")

    print("[*] Scaffolding project workspace …")
    scaffold_project(project_dir)
    print("    ✓ .agentic/workflow_prompts/")
    print("    ✓ .agile-backlog-toolkit/")

    manifest = write_install_manifest(
        project_dir,
        install_dir=install_dir,
        provider_mode=provider_mode,
        azure_org=azure_org,
        version=version,
        hosts=hosts,
    )
    print(f"[*] Install manifest → {manifest}")

    config = write_project_config(
        project_dir,
        provider_mode=provider_mode,
        azure_org=azure_org,
        azure_project=azure_project,
        azure_team=azure_team,
        azure_process=azure_process,
        linear_team=linear_team,
        artifacts_path=artifacts_path,
    )
    print(f"[*] Project config → {config}")
    if provider_mode in {"azure", "both"} and not azure_project:
        print("    (project/team unset — the first skill that needs them will ask and save)")

    print("\n========================================")
    print(" Installation complete")
    print("========================================")
    print(f"  Marketplace : {install_dir}")
    print(f"  Project     : {project_dir}")
    print(f"  Provider    : {provider_mode}")
    print(f"  Azure org   : {azure_org or '(unset)'}")
    print(f"  Artifacts   : {artifacts_path or '(unset — asked on first use)'}")
    print(f"  Hosts       : {', '.join(hosts) if hosts else '(none)'}")
    print(f"  CLI         : agile-backlog-toolkit")
    print("\nNext steps:")
    print("  1. Restart your agent host(s) to load skills and MCP servers.")
    print("  2. Run: agile-backlog-toolkit config --show")
    if "codex" in hosts:
        print("  3. Codex: codex plugin add agile-backlog-toolkit@personal  (if not already installed)")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install and wire agile-backlog-toolkit (plugin + orchestrator + MCP).",
    )
    parser.add_argument(
        "--install-dir",
        default=str(INSTALL_DIR),
        help=f"Marketplace install location (default: {INSTALL_DIR})",
    )
    parser.add_argument("--project-dir", help="Project directory to wire (default: prompt or cwd)")
    parser.add_argument("--azure-org", help="Azure DevOps organization slug")
    parser.add_argument(
        "--provider",
        choices=("local", "azure", "linear", "both"),
        help="Integration mode to wire. Defaults to local when omitted.",
    )
    parser.add_argument(
        "--azure-project",
        help="Azure DevOps project name. Optional -- skills discover and save it on first use.",
    )
    parser.add_argument(
        "--azure-team",
        help="Azure DevOps team name, needed for sprint capacity. Optional; discovered on first use.",
    )
    parser.add_argument(
        "--azure-process",
        choices=("agile", "scrum", "cmmi"),
        help="Azure process template. Decides whether Original Estimate exists. Optional.",
    )
    parser.add_argument(
        "--linear-team",
        help="Linear team slug or identifier to record in the install manifest and config.",
    )
    parser.add_argument(
        "--artifacts-path",
        help="Where local artifacts should be written. Optional; asked for on first use. "
        "The installer never creates this directory.",
    )
    parser.add_argument(
        "--target",
        default="all-agents",
        help=f"Comma-separated hosts to register: {', '.join(ALL_TARGETS)}, or all-agents (default)",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Non-interactive; fail if required values are missing",
    )
    parser.add_argument(
        "--from-source",
        action="store_true",
        help="Use the repository checkout as install dir (skip copy to ~/.agile-backlog-toolkit)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source_root = Path(__file__).resolve().parent.parent
    install_dir = source_root if args.from_source else Path(args.install_dir).expanduser().resolve()
    project_dir = Path(args.project_dir).expanduser().resolve() if args.project_dir else Path.cwd().resolve()

    print("========================================")
    print(" agile-backlog-toolkit installer")
    print("========================================\n")

    stage_parent = Path(tempfile.mkdtemp(prefix="agile-backlog-toolkit-stage-"))
    staged_root = stage_parent / "package"
    try:
        shutil.copytree(source_root, staged_root, ignore=_COPY_IGNORE)
    except OSError as exc:
        print(f"error: could not stage package: {exc}", file=sys.stderr)
        _remove_path(stage_parent)
        return 1
    stage_errors = validate_source_package(staged_root)
    if stage_errors:
        for error in stage_errors:
            print(f"error: {error}", file=sys.stderr)
        _remove_path(stage_parent)
        return 1

    try:
        targets = parse_targets(args.target, non_interactive=args.yes)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    default_org = read_azure_org_from_mcp(project_dir / ".mcp.json")
    if not default_org:
        default_org = read_azure_org_from_mcp(Path.home() / ".cursor" / "mcp.json")
    if not default_org:
        default_org = read_azure_org_from_mcp(source_root / ".mcp.json")

    provider_mode = (args.provider or "").strip().lower() if args.provider else ""
    if not provider_mode:
        if args.azure_org:
            provider_mode = "azure"
        elif args.linear_team:
            provider_mode = "linear"
        else:
            provider_mode = "local" if args.yes else _prompt(
                "Integration (local, azure, linear, or both)", "local"
            ).strip().lower()
    if provider_mode not in {"local", "azure", "linear", "both"}:
        print("error: integration must be local, azure, linear, or both", file=sys.stderr)
        _remove_path(stage_parent)
        return 1

    if args.yes:
        if provider_mode in {"azure", "both"} and not (args.azure_org or default_org):
            print("error: --azure-org is required when Azure is selected with -y", file=sys.stderr)
            return 1
        azure_org = (
            validate_azure_org(args.azure_org or default_org)
            if provider_mode in {"azure", "both"} and (args.azure_org or default_org)
            else None
        )
    else:
        detected = detect_hosts()
        if detected:
            print(f"Detected agent hosts: {', '.join(detected)}\n")
        project_input = args.project_dir or _prompt("Project directory to wire", str(project_dir))
        project_dir = Path(project_input).expanduser().resolve()
        if (
            not args.project_dir
            and project_dir.resolve() == source_root.resolve()
            and not _yes_no(
                "Project directory is the marketplace checkout itself. Wire MCP here?",
                default=False,
            )
        ):
            print("error: specify --project-dir to your application monorepo.", file=sys.stderr)
            return 1
        azure_org = None
        if provider_mode in {"azure", "both"}:
            azure_org = validate_azure_org(
                args.azure_org or _prompt("Azure DevOps organization slug", default_org or "")
            )
        if provider_mode in {"linear", "both"} and not args.linear_team:
            args.linear_team = _prompt("Linear team identifier (optional)", "") or None
        if not args.from_source and install_dir.resolve() != source_root.resolve():
            if not _yes_no(f"Install marketplace copy to {install_dir}?", default=True):
                install_dir = source_root
                print(f"    → Using source checkout: {install_dir}")

    azure_org_for_install = azure_org if provider_mode in {"azure", "both"} else None

    old_state = managed_state(project_dir, install_dir, source_root)
    if old_state:
        print("Detected plugin-managed state:")
        for entry in old_state:
            print(f"  - {entry}")
        if args.yes:
            print(
                "error: an older installation requires an interactive clean replacement",
                file=sys.stderr,
            )
            _remove_path(stage_parent)
            return 1
        if not replacement_choice():
            print("Installation aborted; no managed state was changed.")
            _remove_path(stage_parent)
            return 0
        remove_managed_state(project_dir, install_dir, source_root)

    try:
        result = run_install(
            azure_project=args.azure_project,
            azure_team=args.azure_team,
            azure_process=args.azure_process,
            linear_team=args.linear_team,
            source_root=source_root if args.from_source else staged_root,
            install_dir=install_dir,
            project_dir=project_dir,
            provider_mode=provider_mode,
            azure_org=azure_org_for_install,
            artifacts_path=args.artifacts_path,
            targets=targets,
            skip_copy=args.from_source or install_dir.resolve() == source_root.resolve(),
        )
        _remove_path(stage_parent)
        return result
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        remove_managed_state(project_dir, install_dir, source_root)
        _remove_path(stage_parent)
        print(f"error: fresh installation failed and partial managed state was removed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
