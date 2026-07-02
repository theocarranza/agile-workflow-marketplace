from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .engine import OrchestratorEngine
from .init_scaffold import scaffold_workspace
from .ingest import ingest_vault_file
from .mailbox import read_error_log
from .report_formatter import format_terminal_report, persist_report
from .artifact_validator import validate_artifact


def _default_skills_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "skills"


def _project_root() -> Path:
    for key in ("CODEX_PROJECT_ROOT", "CURSOR_PROJECT_DIR", "CLAUDE_PROJECT_DIR"):
        value = os.environ.get(key, "").strip()
        if value:
            return Path(value)
    return Path.cwd()


def _vault_dir(project_root: Path) -> Path:
    folder = os.environ.get("CODEX_VAULT_FOLDER", "AI_Codex_AgileWorkflowMarketplace").strip()
    return project_root / folder


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Agile Workflow deterministic orchestrator")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("init", help="Scaffold .agentic/workflow_prompts mailbox")

    validate_p = sub.add_parser("validate", help="Validate a vault artifact (rule-based critic)")
    validate_p.add_argument("--file", required=True, help="Path to vault draft markdown")
    validate_p.add_argument("--persist", action="store_true", help="Write report to Agent_Reports/")
    validate_p.add_argument(
        "--hierarchy-parent-is-feature",
        choices=("true", "false"),
        help="Optional Azure hierarchy assertion for stories",
    )

    eval_p = sub.add_parser("evaluate", help="Quality gate CLI (writes error.log on failure)")
    eval_p.add_argument("--skill", default="validate-artifact")
    eval_p.add_argument("--file", required=True)

    compile_p = sub.add_parser("compile", help="Compile skill prompt to mailbox")
    compile_p.add_argument("--skill", required=True)
    compile_p.add_argument("--file", required=True)
    compile_p.add_argument("--mode", default="novo", choices=("novo", "correcao", "atualizacao"))

    resume_p = sub.add_parser("resume", help="Route skill: compile prompt if error.log or new work")
    resume_p.add_argument("--skill", required=True)
    resume_p.add_argument("--file", required=True)

    mcp_p = sub.add_parser("mcp", help="Run MCP stdio server")

    args = parser.parse_args(argv)
    project_root = _project_root()
    skills_dir = Path(os.environ.get("ORCHESTRATOR_SKILLS_DIR", str(_default_skills_dir())))
    vault_dir = _vault_dir(project_root)
    engine = OrchestratorEngine(
        skills_dir,
        project_root=project_root,
        vault_dir=vault_dir,
        interactive=bool(os.environ.get("ORCHESTRATOR_INTERACTIVE")),
    )

    if args.command == "init":
        scaffold_workspace(project_root)
        return 0

    if args.command == "validate":
        path = Path(args.file)
        record = ingest_vault_file(path)
        hierarchy = None
        if args.hierarchy_parent_is_feature == "true":
            hierarchy = True
        elif args.hierarchy_parent_is_feature == "false":
            hierarchy = False
        results = validate_artifact(record, hierarchy_parent_is_feature=hierarchy)
        report = format_terminal_report(record, results)
        print(report)
        if args.persist:
            out = persist_report(record, report, vault_dir=vault_dir)
            print(f"\n[+] Report persisted: {out}")
        return 1 if any(r.result == "FAIL" for r in results) else 0

    if args.command == "evaluate":
        ok, report = engine.evaluate_file(Path(args.file), skill_name=args.skill)
        print(report)
        return 0 if ok else 1

    if args.command == "compile":
        out = engine.compile_mailbox(args.skill, file_path=args.file, mode=args.mode)
        print(f"[+] Prompt written: {out}")
        return 0

    if args.command == "resume":
        mode = "correcao" if read_error_log(project_root, args.skill) else "novo"
        out = engine.compile_mailbox(args.skill, file_path=args.file, mode=mode)
        print(f"[+] Resume mode={mode} prompt: {out}")
        return 0

    if args.command == "mcp":
        from . import mcp_server

        mcp_server.main()
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
