# Orchestrator — deterministic skill runtime (v0.4.0)

The `agile-workflow` plugin includes a Python orchestrator that enforces **Actor-Critic**
discipline for quality-gate skills. The LLM drafts artifacts; Python judges them with
rule-based checks — no LLM self-judgment on pass/fail.

## Architecture

```
bin/agile-workflow CLI ──┐
MCP (agile-workflow-orchestrator) ──┤
                                    ▼
                          OrchestratorEngine
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            artifact_validator   OrchestratorStream   mailbox
            (rule-based critic)  (event + reducers)   (.agentic/workflow_prompts/)
```

| Layer | Responsibility |
| --- | --- |
| **Actor** | LLM agent following `SKILL.md` — drafts or revises artifacts |
| **Critic** | `artifact_validator.py` — implements `validation-checks.md` |
| **Stream** | `OrchestratorStream` — immutable state, pure reducers, queued dispatch |
| **Circuit breaker** | 3 retries or identical critiques → `BLOCKED_REQUIRES_REVIEW` |
| **Recovery** | Human types `IMPLEMENTATION APPROVED` to reset retries |
| **Mailbox** | Compiled prompts + error logs for harness-agnostic IPC |

## Bootstrap

```bash
./bin/agile-workflow init
```

Creates `.agentic/workflow_prompts/` and `AI_Codex_AgileWorkflowMarketplace/_mistakes/`.

## CLI commands

| Command | Purpose |
| --- | --- |
| `validate --file <path> [--persist]` | Run rule-based critic; print report; optional vault persist |
| `evaluate --skill <name> --file <path>` | Quality gate; writes `<skill>.error.log` on failure |
| `compile --skill <name> --file <path> [--mode novo\|correcao]` | Write compiled prompt to mailbox |
| `resume --skill <name> --file <path>` | `correcao` if error.log exists, else `novo` |
| `mcp` | Stdio JSON-RPC server for MCP clients |

Environment:

- `CODEX_PROJECT_ROOT` / `CURSOR_PROJECT_DIR` — project root (default: cwd)
- `CODEX_VAULT_FOLDER` — vault name (default: `AI_Codex_AgileWorkflowMarketplace`)
- `ORCHESTRATOR_INTERACTIVE=1` — prompt for `IMPLEMENTATION APPROVED` on circuit breaker

## MCP setup

Add to your project's `.mcp.json` (local file — not committed if globally ignored):

```json
{
  "mcpServers": {
    "agile-workflow-orchestrator": {
      "command": "python3",
      "args": ["-m", "orchestrator_core", "mcp"],
      "env": {
        "PYTHONPATH": "agile-workflow",
        "CODEX_VAULT_FOLDER": "AI_Codex_AgileWorkflowMarketplace"
      }
    }
  }
}
```

Run from the marketplace repo root (or set `PYTHONPATH` to the installed plugin path).

## Wired skills

### `validate-artifact`

MCP tool / CLI runs the full check catalog (STRUCTURAL, HIERARCHY, CONTENT, DoR).
Hierarchy checks accept optional `hierarchy_parent_is_feature` when Azure MCP is unavailable.

### `auto-fix-artifact`

Reflection loop: Actor submits `draft_content` → critic evaluates → critiques injected
into next prompt via mailbox `correcao` mode. On circuit breaker trip, flaws are appended
to `_mistakes/mistakes.json`.

## Tests

```bash
PYTHONPATH=agile-workflow python3 -m unittest discover -s test -v
```

## Related

- [orchestrator-core feature note](../AI_Codex_AgileWorkflowMarketplace/Features/orchestrator-core.md)
- [validation-checks.md](../agile-workflow/skills/validate-artifact/references/validation-checks.md)
