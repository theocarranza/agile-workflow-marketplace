from __future__ import annotations

from pathlib import Path


def scaffold_workspace(project_root: Path) -> None:
    mailbox = project_root / ".agentic" / "workflow_prompts"
    mailbox.mkdir(parents=True, exist_ok=True)
    gitkeep = mailbox / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.write_text("", encoding="utf-8")
    mistakes = project_root / "AI_Codex_AgileWorkflowMarketplace" / "_mistakes"
    mistakes.mkdir(parents=True, exist_ok=True)
    print(f"[+] Scaffolded mailbox: {mailbox}")
    print(f"[+] Scaffolded mistakes repo: {mistakes}")
