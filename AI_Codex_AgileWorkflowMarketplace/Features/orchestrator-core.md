---
type: feature
skill: orchestrator
plugin: agile-workflow
shipped: 2026-07-02
---

# orchestrator-core

Deterministic Python orchestrator for agile-workflow skills. Ports the event-sourced Actor-Critic pattern from codex-workflows-plugin and the filesystem mailbox from agentic-e2e-test-workflow.

## Components

| Path | Role |
|------|------|
| `agile-workflow/orchestrator_core/` | Stream, reducers, rule-based critic, reflection engine, MCP server |
| `bin/agile-workflow` | CLI entry (`init`, `validate`, `evaluate`, `compile`, `resume`, `mcp`) |
| `.agentic/workflow_prompts/` | Harness-agnostic mailbox (prompt + error.log) |
| `AI_Codex_AgileWorkflowMarketplace/_mistakes/` | Circuit-breaker learning store |

## Pattern

- **Actor:** LLM agent (SKILL.md) drafts or fixes artifacts.
- **Critic:** `artifact_validator.py` — regex/structure checks from `validation-checks.md`.
- **Circuit breaker:** 3 retries or identical critiques → `BLOCKED_REQUIRES_REVIEW`.
- **Recovery:** Human token `IMPLEMENTATION APPROVED` resets state.

## Wired skills

- `validate-artifact` — read-only critic + report persistence
- `auto-fix-artifact` — reflection loop with `correcao` mode via error.log

## MCP

`.mcp.json` → `agile-workflow-orchestrator` (stdio JSON-RPC).
