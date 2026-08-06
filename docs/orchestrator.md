# Orchestrator — deterministic skill runtime

The `agile-backlog-toolkit` plugin includes a Python orchestrator that enforces **Actor-Critic**
discipline for quality-gate skills. The LLM drafts artifacts; Python judges them with
rule-based checks — no LLM self-judgment on pass/fail.

## Architecture

```
bin/agile-backlog-toolkit CLI ──┐
MCP (plugin: orchestrator / installer: agile-backlog-toolkit-orchestrator) ──┤
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

**Recommended:** run the marketplace installer from the repo root (wires CLI, MCP, mailbox, and all detected agent hosts):

```bash
./install.sh
```

Registers **Claude Code**, **Cursor**, **Codex**, and **Antigravity** when their config directories are present. Use `--target cursor,codex` to limit hosts.

Or scaffold only the mailbox in an already-wired project:

```bash
./bin/agile-backlog-toolkit init
```

## CLI commands

| Command | Purpose |
| --- | --- |
| `validate --file <path> [--persist]` | Run rule-based critic; print report; optional artifacts path persist |
| `evaluate --skill <name> --file <path>` | Quality gate; writes `<skill>.error.log` on failure |
| `compile --skill <name> --file <path> [--mode novo\|correcao]` | Write compiled prompt to mailbox |
| `resume --skill <name> --file <path>` | `correcao` if error.log exists, else `novo` |
| `mcp` | Stdio JSON-RPC server for MCP clients |

Environment:

- `CODEX_PROJECT_ROOT` / `CURSOR_PROJECT_DIR` / `CLAUDE_PROJECT_DIR` — project root, in that
  precedence (default: cwd). Claude Code sets the third one itself, so a plugin install needs none
  of them configured.
- `ORCHESTRATOR_INTERACTIVE=1` — prompt for `IMPLEMENTATION APPROVED` on circuit breaker

## MCP setup

There are two channels. **Pick one** — running both wires the same orchestrator twice, under two
different tool namespaces.

### Claude Code: the plugin brings its own server

Nothing to configure. `.mcp.json` ships with the plugin and resolves its own path:

```json
{
  "mcpServers": {
    "orchestrator": {
      "command": "python3",
      "args": ["-m", "orchestrator_core", "mcp"],
      "env": {
        "PYTHONPATH": "${CLAUDE_PLUGIN_ROOT}"
      }
    }
  }
}
```

`claude plugin install agile-backlog-toolkit@agile-backlog-toolkit-marketplace` is the whole setup. Tools arrive
as `mcp__plugin_agile-backlog-toolkit_orchestrator__<tool>`; hook matchers and permission rules must use
that scoped form, and `mcp_tool` hooks take `plugin:agile-backlog-toolkit:orchestrator` as `server`.

### Cursor, Codex, or a manual install: wire it per project

The installer writes the entry for you (`./install.sh`). To do it by hand, add to the project's
`.mcp.json` — a local file, not committed if globally ignored:

```json
{
  "mcpServers": {
    "agile-backlog-toolkit-orchestrator": {
      "command": "python3",
      "args": ["-m", "orchestrator_core", "mcp"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/agile-backlog-toolkit",
        "CODEX_PROJECT_ROOT": "/absolute/path/to/your/project"
      }
    }
  }
}
```

`PYTHONPATH` points at the directory containing `orchestrator_core/`. Tools arrive unscoped, as
`mcp__agile-backlog-toolkit-orchestrator__<tool>`.

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
PYTHONPATH=. python3 -m unittest discover -s test -v
```

## Related

- [orchestrator-core feature note](../<artifacts>/Features/orchestrator-core.md)
- [validation-checks.md](../skills/validate-artifact/references/validation-checks.md)
