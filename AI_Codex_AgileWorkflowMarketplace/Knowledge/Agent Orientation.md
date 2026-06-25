---
type: orientation
---

# Agent Orientation

Entry point for agents arriving in the `agile-workflow-marketplace` AI Codex vault.

## Vault purpose

This vault is the persistent knowledge ledger for the `agile-workflow-marketplace` project —
a marketplace of agile workflow skills and tooling. It stores architectural decisions, ticket
ledgers, feature specs, and operational session logs that survive context resets.

## Session bootstrap

1. Read this file.
2. Read the two newest records in `Agent_Sessions/` for continuity.
3. If the newest session is still open, close it and open a new one.
4. Proceed with the user's task.

## Slash commands

| Command                                 | Purpose                                            |
| --------------------------------------- | -------------------------------------------------- |
| `/codex-workflow:codex-init-workspace`  | Scaffold the CLAUDE.md tree.                       |
| `/codex-workflow:codex-init-vault`      | Scaffold this vault skeleton.                      |
| `/codex-workflow:codex-init-rules`      | Drop starter `.agent/rules/*.md` templates.        |
| `/codex-workflow:codex-mine-bases`      | Backfill frontmatter + Base dashboards.            |
| `/codex-workflow:codex-query-vault`     | Read-only live query via the Obsidian CLI.         |
| `/codex-workflow:codex-canvas-map`      | Generate an Architecture Canvas relationship map.  |
| `/codex-workflow:codex-research-ingest` | Ingest a URL into a source-stamped reference note. |
| `/codex-workflow:codex-vault-lint`      | Audit the vault against its archetype spec.        |

## Related

- [[README]] — vault map and naming conventions
- [[Agent_Sessions/README]] — session linking protocol
