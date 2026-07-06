---
type: reference
tags: [reference, vault]
created: 2026-07-06
---

# Frontmatter Convention

Property schema for this vault. **Status is encoded by folder; frontmatter encodes what location cannot.**

## Core principle

A fact lives in exactly one place:

- **Status → folder.** A ticket under `Tickets/Ready/` is ready. Never write `status` in ticket frontmatter.
- **Identity/classification → frontmatter.** Ticket number, note type, area, stack — these go in YAML.

## Property schema

| Property | Type | Example | Notes |
| --- | --- | --- | --- |
| `ticket` | number/str | `6869` | Tracker id. Omit for non-ticket notes. |
| `type` | enum | `feature` | Tickets: `feature` \| `tech-debt` \| `bug` \| `task` \| `ticket`. Features: `feature`. Sessions: `agent-session`. Reports: `report`. Knowledge: `knowledge` \| `orientation` \| `reference`. |
| `area` | string | `quality-gates` | Functional domain. Stable kebab-case. |
| `stack` | list | `[python, mcp]` | Tech surfaces touched. |
| `tags` | list | `[ticket, demo]` | Obsidian tags. |
| `created` | date | `2026-07-06` | Authoring date (`YYYY-MM-DD`). |

## Bases formula gotchas

1. **No `.last()` on lists.** Derive ticket status lane with `file.folder.replace("Tickets/", "")`, not `split().last()`.
2. **Duration needs `.days`.** Use `(now() - file.ctime).days`, not bare subtraction.

## Related

- [[Agent Orientation]] — session bootstrap and slash commands
- `Tickets.base`, `Features.base`, `Agent_Sessions.base` — dashboards querying this schema
