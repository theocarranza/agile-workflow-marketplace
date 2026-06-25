# AI Codex — Agile Workflow Marketplace

Archetype: `software-project` | Created: 2026-06-25

This vault is the cross-session knowledge ledger for the `agile-workflow-marketplace` project.
Agents read it at session start; humans browse it in Obsidian. See [[Knowledge/Agent Orientation]]
for operating instructions.

## Vault Taxonomy

- **Knowledge/** — Permanent distilled knowledge notes (patterns, domains, references) + the knowledge MOC
- **Tickets/Active/** — In-flight ticket ledgers
- **Tickets/Ready/** — Groomed, ready-to-start tickets
- **Tickets/Closed/** — Merged/closed, awaiting release
- **Tickets/Resolved/** — Shipped/archived ticket ledgers
- **Features/** — Feature specifications and implementation detail
- **Architecture/** — High-level architecture overviews (subfolders below for ADRs/patterns/etc.)
- **Architecture/ADR/** — Architecture Decision Records
- **Architecture/Patterns/** — Recurring design patterns
- **Architecture/Infrastructure/** — Structural/infra definitions
- **Architecture/Agent-Governance/** — Agent governance protocols and directives
- **Architecture/Protocols/** — Operational protocols
- **Agent_Sessions/** — Operational journal of agent sessions (doubly-linked chain)
- **Agent_Reports/** — Formal agent-generated reports
- **assets/** — Images and binary attachments
- **Meta/** — Templates, scripts, and vault plumbing

## Naming Conventions

| Folder | Pattern | Example |
| --- | --- | --- |
| `Agent_Sessions/` | `YYYY-MM-DD-HHMMSS-kebab-slug` | `2026-06-25-143000-init-vault` |
| `Agent_Reports/` | `YYYY-MM-DD-kebab-slug` | `2026-06-25-scaffold-summary` |
| `Tickets/` | `<id-or-type>-kebab-slug` | `feat-marketplace-routing` |
| `Features/` | `[<id>-]kebab-slug` | `workflow-canvas-builder` |
| `Knowledge/` | Natural Title Case | `Agent Orientation` |
| `Architecture/ADR/` | `NNNN-kebab-title` | `0001-use-firebase-backend` |
| `Architecture/` | Natural Title Case | `System Overview` |
| Default | `kebab-case` | `my-note` |

## Required Frontmatter (per folder)

| Folder | Required | Forbidden |
| --- | --- | --- |
| `Tickets/` | `type` | `status` (encoded by lane folder) |
| `Features/` | `type` | `status` |
| `Agent_Sessions/` | `date`, `type` | — |
| `Knowledge/` | `type` | — |
| `Architecture/` | `type` | — |

## Slash Commands

| Command | Purpose |
| --- | --- |
| `/codex-workflow:codex-init-workspace` | Scaffold the CLAUDE.md tree. |
| `/codex-workflow:codex-init-vault` | Scaffold this vault skeleton. |
| `/codex-workflow:codex-init-rules` | Drop starter `.agent/rules/*.md` templates. |
| `/codex-workflow:codex-mine-bases` | Backfill frontmatter + Base dashboards (software-project). |
| `/codex-workflow:codex-query-vault` | Read-only live query of the vault via the Obsidian CLI. |
| `/codex-workflow:codex-canvas-map` | Generate an Architecture Canvas relationship map. |
| `/codex-workflow:codex-research-ingest` | Ingest a URL into a source-stamped reference note. |
| `/codex-workflow:codex-vault-lint` | Audit the vault against its archetype spec. |
