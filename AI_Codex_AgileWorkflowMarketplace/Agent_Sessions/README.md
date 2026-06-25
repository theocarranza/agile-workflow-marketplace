# Agent Sessions

Operational journal of agent work sessions for this project.

## Protocol

Sessions form a **doubly-linked chain** — each record has `Previous Session` and `Next Session`
wikilinks. At session start, open the newest record; if still open, close it and open a new one.

## Record cadence

Each session file uses these headers, appended during work:

| Header | Trigger | Required? |
| --- | --- | --- |
| `## Implementation Checkpoint - <timestamp>` | End of every validated work unit | MUST |
| `## Pre-Operation Snapshot - <timestamp>` | Before any state-disrupting action | MUST |
| `## Pivot - <timestamp>` | Tranche transitions, scope shifts, subagent spawn | SHOULD |
| `## Heartbeat - <timestamp>` | If 30 min pass without any other entry | Safety net |

## Naming

Files follow `YYYY-MM-DD-HHMMSS-kebab-slug.md` — sortable by date, slug describes the session's
primary focus.

Required frontmatter:
```yaml
---
date: YYYY-MM-DD
type: agent-session
status: open | closed
---
```
