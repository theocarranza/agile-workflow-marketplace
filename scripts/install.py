#!/usr/bin/env python3
"""Install and wire agile-workflow-marketplace with minimal prompts."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

INSTALL_DIR = Path.home() / ".agile-workflow-marketplace"
PLUGIN_NAME = "agile-workflow"
MARKETPLACE_NAME = "agile-workflow-marketplace"
DEFAULT_VAULT = "AI_Codex_AgileWorkflowMarketplace"
PLUGIN_BUNDLE_DIRS = ("skills", "references", "orchestrator_core")
ALL_TARGETS = ("claude", "cursor", "codex", "antigravity")

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


def detect_vault_folder(project_dir: Path) -> str | None:
    if not project_dir.is_dir():
        return None
    for path in sorted(project_dir.iterdir()):
        if path.is_dir() and path.name.startswith("AI_Codex"):
            return path.name
    return None


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


def install_marketplace(source_root: Path, install_dir: Path) -> None:
    if source_root.resolve() == install_dir.resolve():
        return
    if install_dir.exists():
        shutil.rmtree(install_dir)
    install_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_root, install_dir, ignore=_COPY_IGNORE)


def plugin_root(install_dir: Path) -> Path:
    return install_dir / "agile-workflow"


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
    if include_claude_plugin:
        src = proot / ".claude-plugin"
        if src.is_dir():
            shutil.copytree(src, dest / ".claude-plugin", ignore=_COPY_IGNORE)
    if include_codex_plugin:
        src = proot / ".codex-plugin"
        if src.is_dir():
            shutil.copytree(src, dest / ".codex-plugin", ignore=_COPY_IGNORE)


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
    if marketplace_link.is_symlink() or marketplace_link.exists():
        if marketplace_link.is_symlink():
            marketplace_link.unlink()
        elif marketplace_link.is_dir():
            shutil.rmtree(marketplace_link)
    marketplace_link.symlink_to(install_dir.resolve())

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
    return True


def register_codex_plugin(install_dir: Path) -> bool:
    proot = plugin_root(install_dir)
    manifest = _load_plugin_manifest(proot)
    version = manifest.get("version", "0.0.0")

    codex_plugins = Path.home() / ".codex-plugins" / PLUGIN_NAME
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
            "name": MARKETPLACE_NAME,
            "source": {"source": "local", "path": str(install_dir)},
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


def write_cursor_azure_wrapper(project_dir: Path, *, azure_org: str, npx_path: str) -> Path:
    """Project-local wrapper so Cursor stdio MCP gets a sane PATH (no bare `npx`)."""
    bin_dir = project_dir / ".cursor" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    script = bin_dir / "azure-devops-mcp.sh"
    env_script = Path.home() / ".local" / "bin" / "cursor-mcp" / "cursor-mcp-env.sh"
    env_block = (
        f'source "{env_script}"\n'
        if env_script.is_file()
        else "unset ELECTRON_RUN_AS_NODE\n"
    )
    script.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f"{env_block}"
        f'exec "{npx_path}" -y "@azure-devops/mcp@2.7.0" "{azure_org}" "$@"\n',
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script


def _mcp_server_payloads(
    *,
    proot: Path,
    project_dir: Path,
    azure_org: str,
    vault_folder: str,
    tool_paths: dict[str, str],
    cursor_azure_wrapper: Path | None = None,
) -> tuple[dict[str, dict], dict[str, dict]]:
    python3 = tool_paths["python3"]
    npx = tool_paths["npx"]
    orchestrator_env = {
        "PYTHONPATH": str(proot),
        "CODEX_VAULT_FOLDER": vault_folder,
        "CODEX_PROJECT_ROOT": str(project_dir.resolve()),
    }
    claude_servers = {
        "azure-devops": {
            "command": npx,
            "args": ["-y", "@azure-devops/mcp@2.7.0", azure_org],
        },
        "agile-workflow-orchestrator": {
            "command": python3,
            "args": ["-m", "orchestrator_core", "mcp"],
            "env": orchestrator_env,
        },
    }
    azure_command = str(cursor_azure_wrapper) if cursor_azure_wrapper else npx
    azure_args: list[str] = [] if cursor_azure_wrapper else ["-y", "@azure-devops/mcp@2.7.0", azure_org]
    cursor_servers = {
        "azure-devops": {
            "type": "stdio",
            "command": azure_command,
            "args": azure_args,
            "env": {},
        },
        "agile-workflow-orchestrator": {
            "type": "stdio",
            "command": python3,
            "args": ["-m", "orchestrator_core", "mcp"],
            "env": orchestrator_env,
        },
    }
    return claude_servers, cursor_servers


def wire_project_mcp(
    project_dir: Path,
    *,
    install_dir: Path,
    azure_org: str,
    vault_folder: str,
    targets: list[str],
) -> None:
    proot = plugin_root(install_dir).resolve()
    tool_paths = resolve_tool_paths("python3", "npx")
    cursor_wrapper: Path | None = None
    if "cursor" in targets:
        cursor_wrapper = write_cursor_azure_wrapper(
            project_dir,
            azure_org=azure_org,
            npx_path=tool_paths["npx"],
        )
    claude_servers, cursor_servers = _mcp_server_payloads(
        proot=proot,
        project_dir=project_dir,
        azure_org=azure_org,
        vault_folder=vault_folder,
        tool_paths=tool_paths,
        cursor_azure_wrapper=cursor_wrapper,
    )

    if _MCP_JSON_HOSTS.intersection(targets):
        merge_json_mcp(project_dir / ".mcp.json", claude_servers)
        print("    ✓ project .mcp.json")

    if "cursor" in targets:
        merge_json_mcp(project_dir / ".cursor" / "mcp.json", cursor_servers)
        print("    ✓ project .cursor/mcp.json")
        print("    ✓ project .cursor/bin/azure-devops-mcp.sh")


def install_cli(install_dir: Path) -> Path:
    bin_dir = Path.home() / ".local" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    target = bin_dir / "agile-workflow"
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


def scaffold_project(project_dir: Path, vault_folder: str) -> None:
    mailbox = project_dir / ".agentic" / "workflow_prompts"
    mailbox.mkdir(parents=True, exist_ok=True)
    gitkeep = mailbox / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.write_text("", encoding="utf-8")
    mistakes = project_dir / vault_folder / "_mistakes"
    mistakes.mkdir(parents=True, exist_ok=True)


def write_install_manifest(
    project_dir: Path,
    *,
    install_dir: Path,
    azure_org: str,
    vault_folder: str,
    version: str,
    hosts: list[str],
) -> Path:
    path = project_dir / ".agile-workflow.install.json"
    payload = {
        "marketplace": MARKETPLACE_NAME,
        "plugin": PLUGIN_NAME,
        "version": version,
        "install_dir": str(install_dir.resolve()),
        "azure_devops_org": azure_org,
        "vault_folder": vault_folder,
        "hosts": hosts,
        "installed_at": _now_iso(),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
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
    azure_org: str,
    vault_folder: str,
    targets: list[str],
    skip_copy: bool = False,
) -> int:
    print(f"\n[*] Installing marketplace → {install_dir}")
    if not skip_copy:
        install_marketplace(source_root, install_dir)

    version = plugin_version(install_dir)
    print(f"[*] Plugin version: {version}")
    print(f"[*] Agent targets: {', '.join(targets)}")

    hosts = register_hosts(install_dir, targets)

    print(f"[*] Wiring MCP servers for {project_dir} …")
    wire_project_mcp(
        project_dir,
        install_dir=install_dir,
        azure_org=azure_org,
        vault_folder=vault_folder,
        targets=hosts,
    )

    cli_path = install_cli(install_dir)
    print(f"[*] CLI installed → {cli_path}")

    print("[*] Scaffolding project workspace …")
    scaffold_project(project_dir, vault_folder)
    print("    ✓ .agentic/workflow_prompts/")
    print(f"    ✓ {vault_folder}/_mistakes/")

    manifest = write_install_manifest(
        project_dir,
        install_dir=install_dir,
        azure_org=azure_org,
        vault_folder=vault_folder,
        version=version,
        hosts=hosts,
    )
    print(f"[*] Install manifest → {manifest}")

    print("\n========================================")
    print(" Installation complete")
    print("========================================")
    print(f"  Marketplace : {install_dir}")
    print(f"  Project     : {project_dir}")
    print(f"  Azure org   : {azure_org}")
    print(f"  Vault       : {vault_folder}")
    print(f"  Hosts       : {', '.join(hosts) if hosts else '(none)'}")
    print(f"  CLI         : agile-workflow")
    print("\nNext steps:")
    print("  1. Restart your agent host(s) to load skills and MCP servers.")
    print("  2. Run: agile-workflow validate --file <vault-draft.md>")
    if "codex" in hosts:
        print("  3. Codex: codex plugin add agile-workflow@personal  (if not already installed)")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install and wire agile-workflow-marketplace (plugin + orchestrator + MCP).",
    )
    parser.add_argument(
        "--install-dir",
        default=str(INSTALL_DIR),
        help=f"Marketplace install location (default: {INSTALL_DIR})",
    )
    parser.add_argument("--project-dir", help="Project directory to wire (default: prompt or cwd)")
    parser.add_argument("--azure-org", help="Azure DevOps organization slug")
    parser.add_argument("--vault-folder", help=f"Vault folder name (default: {DEFAULT_VAULT})")
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
        help="Use the repository checkout as install dir (skip copy to ~/.agile-workflow-marketplace)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source_root = Path(__file__).resolve().parent.parent
    install_dir = source_root if args.from_source else Path(args.install_dir).expanduser().resolve()
    project_dir = Path(args.project_dir).expanduser().resolve() if args.project_dir else Path.cwd().resolve()

    print("========================================")
    print(" agile-workflow-marketplace installer")
    print("========================================\n")

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

    default_vault = detect_vault_folder(project_dir) or DEFAULT_VAULT

    if args.yes:
        if not args.azure_org:
            print("error: --azure-org is required with -y", file=sys.stderr)
            return 1
        azure_org = validate_azure_org(args.azure_org)
        vault_folder = args.vault_folder or default_vault
    else:
        detected = detect_hosts()
        if detected:
            print(f"Detected agent hosts: {', '.join(detected)}\n")
        print("Only three values are needed — everything else is wired automatically.\n")
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
        azure_org = validate_azure_org(
            args.azure_org or _prompt("Azure DevOps organization slug", default_org or "")
        )
        vault_folder = args.vault_folder or _prompt("Vault folder name", default_vault)
        if not args.from_source and install_dir.resolve() != source_root.resolve():
            if not _yes_no(f"Install marketplace copy to {install_dir}?", default=True):
                install_dir = source_root
                print(f"    → Using source checkout: {install_dir}")

    try:
        return run_install(
            source_root=source_root,
            install_dir=install_dir,
            project_dir=project_dir,
            azure_org=azure_org,
            vault_folder=vault_folder,
            targets=targets,
            skip_copy=args.from_source or install_dir.resolve() == source_root.resolve(),
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
