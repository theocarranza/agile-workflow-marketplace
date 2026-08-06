#!/usr/bin/env python3
"""Wire project MCP servers (orchestrator + optional Azure/Linear) without reinstalling the plugin."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from install import (
    INSTALL_DIR,
    ensure_azure_mcp_installed,
    parse_targets,
    read_azure_org_from_mcp,
    resolve_tool_paths,
    validate_azure_org,
    wire_project_mcp,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Wire agile-backlog-toolkit orchestrator (and optional providers) into a project.",
    )
    parser.add_argument("--project-dir", default=".", help="Project directory to wire (default: cwd)")
    parser.add_argument(
        "--install-dir",
        default=str(INSTALL_DIR),
        help=f"Plugin install location (default: {INSTALL_DIR})",
    )
    parser.add_argument(
        "--provider",
        choices=("local", "azure", "linear", "both"),
        default="local",
        help="Integration mode to wire (default: local)",
    )
    parser.add_argument("--azure-org", help="Azure DevOps organization slug")
    parser.add_argument(
        "--target",
        default="all-agents",
        help="Comma-separated hosts: claude,cursor,codex or all-agents",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    project_dir = Path(args.project_dir).expanduser().resolve()
    install_dir = Path(args.install_dir).expanduser().resolve()
    try:
        targets = parse_targets(args.target, non_interactive=True)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    provider = args.provider
    enable_azure = provider in {"azure", "both"}
    enable_linear = provider in {"linear", "both"}
    azure_org = None
    if enable_azure:
        default_org = read_azure_org_from_mcp(project_dir / ".mcp.json") or args.azure_org
        if not default_org:
            print("error: --azure-org is required when provider includes azure", file=sys.stderr)
            return 1
        azure_org = validate_azure_org(default_org if args.azure_org is None else args.azure_org)
        ensure_azure_mcp_installed(npm_path=__import__("shutil").which("npm"), quiet=False)

    try:
        resolve_tool_paths("python3", *(("npx",) if enable_azure else ()))
        wire_project_mcp(
            project_dir,
            install_dir=install_dir,
            azure_org=azure_org,
            targets=targets,
            enable_azure=enable_azure,
            enable_linear=enable_linear,
        )
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print("wire-project-mcp ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
