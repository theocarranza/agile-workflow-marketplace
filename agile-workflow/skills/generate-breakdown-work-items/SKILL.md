---
name: generate-breakdown-work-items
description: >
  From a User Story (or Feature/Epic with child Stories), generate an Implementation Plan in the
  AI Codex Ledger and atomic child Tasks aligned to acceptance criteria — including Staging,
  Review, and a Done Breakdown Task. Use when the user runs /generate-breakdown-work-items, says
  "break down this story into tasks", "create tasks from acceptance criteria", "breakdown work
  items", or provides a Story/Feature/Epic id, URL, or vault path and wants plan + Task children
  for delivery. Does not invent acceptance criteria or implement product code.
license: MIT
compatibility: Requires Azure DevOps MCP for Azure destinations and an AI Codex vault with Implementation_Plans/ for ledger writes.
metadata:
  plugin: agile-workflow
  version: "0.1.0"
  argument-hint: "--ref <id|url|path> [--destination filesystem|azure|both] [--language en|pt-BR]"
allowed-tools: >
  Read Write Edit Glob Grep Bash
  mcp__azure-devops__wit_get_work_item
  mcp__azure-devops__wit_get_work_items_batch_by_ids
  mcp__azure-devops__wit_create_work_item
  mcp__azure-devops__wit_add_child_work_items
  mcp__azure-devops__wit_update_work_item
  mcp__azure-devops__wit_work_items_link
  CallMcpTool
---

# Generate Breakdown Work Items

Conductor for turning Story acceptance criteria into a ledger Implementation Plan and atomic
child Tasks. Load references as each phase needs them — this file is the score, not the textbook.

References (skill-specific, in `./references/`):

- `./references/intake-ux.md` — prompt order, invariant/variant lists, `all` / `other` / `Recommended`
- `./references/plan-generation.md` — **US2 — not yet shipped**
- `./references/atomic-tasks.md` — **US3 — not yet shipped**
- `./references/fan-out.md` — **US4 — not yet shipped**

Shared references (in `../../references/`):

- `azure-mechanics.md` — MCP calls, linking gotchas, URL→id
- `ticket-structure.md` — vault draft constraints
- `decomposition-rules.md` — hierarchy (Epic → Feature → Story → Task)

Resolve vault from `.claude/codex-workflow.config.json` `codex.folder`, else glob `AI_Codex*/`.

**Not in scope:** inventing or rewriting acceptance criteria; Feature-level story-point estimation;
implementing the product under breakdown — only plan + work-item persistence.

---

## PHASE 0 — INTAKE (selection only)

Read `./references/intake-ux.md` before prompting. Gather inputs **one at a time**.

| Input | Required | Purpose |
| --- | --- | --- |
| `work_item_ref` | yes | Azure ID, URL, or vault/filesystem path to Story, Feature, or Epic |
| `destination` | yes | `filesystem` \| `azure` \| `both` \| `other:…` |
| `language` | no | `en` (default when omitted) \| `pt-BR` \| `other:…` |

Also accept flags from `/generate-breakdown-work-items` or conversational inference.

### Rules (must follow `intake-ux.md`)

1. If `work_item_ref` is missing → STOP and ask before continuing.
2. If `destination` is missing → show the invariant destination list (with `other…` last; apply
   `Recommended` when judgment requires it).
3. If `language` is missing → set `en` (do not force a prompt).
4. Every selectable list ends with `other (inform or describe)`.
5. Variant multi-select lists include `all`.
6. Judgment calls: first option tagged `Recommended`.

### Confirmation gate

Present the normalized intake record and **WAIT** for explicit confirmation. Do **not** read
work-item bodies, write the Ledger, or call Azure write APIs in this phase.

```text
{
  work_item_ref:   string
  source_kind:     "id" | "url" | "path"
  destination:     "filesystem" | "azure" | "both" | "other:<text>"
  language:        "en" | "pt-BR" | "other:<text>"
}
```

On confirmation, proceed to PHASE 1 when that phase is implemented; until then STOP with the
confirmed record and note that plan generation / task decomposition / fan-out land in later Stories.

---

## PHASE 1 — INGEST (stub — US2)

**Not implemented yet.** Will read Feature + User Story bodies (or enumerate children for
Feature/Epic). Do not invent acceptance criteria. If invoked before US2 ships: STOP and report
that plan generation is not available.

---

## PHASE 2 — IMPLEMENTATION PLAN (stub — US2)

**Not implemented yet.** Will analyze acceptance criteria, write
`<vault>/Implementation_Plans/…`, and refuse Task creation until the plan file exists.

---

## PHASE 3 — DECOMPOSE TASKS (stub — US3)

**Not implemented yet.** Will split the saved plan into atomic Tasks plus Staging, Review, and
Breakdown (assignee = Story assignee, state = Done).

---

## PHASE 4 — PERSIST (stub — US3)

**Not implemented yet.** Will attach Tasks as children and write to `destination`
(filesystem, Azure, or both).

---

## PHASE 5 — FAN-OUT (stub — US4)

**Not implemented yet.** When the resolved work item is a Feature or Epic, will run the User
Story workflow for each child Story, reusing intake `destination` and `language`, without
silently skipping failures.

---

## Examples

```text
/generate-breakdown-work-items --ref 12345
→ ask destination → language defaults to en → confirm intake → (later phases when shipped)

/generate-breakdown-work-items --ref Features/foo.md --destination both --language pt-BR
→ confirm intake record → (later phases when shipped)
```
