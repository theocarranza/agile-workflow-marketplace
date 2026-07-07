---
name: generate-work-item
description: >
  Generates a raw Epic, Feature, or User Story work item from a title and description: requirement
  bullets, acceptance criteria, Context7 research, a Specs note, and a Tickets/Ready draft; creates
  the Azure DevOps item after approval. Use when the user runs /generate-work-item, says "start
  ticket", "create a ticket", "create an issue", "create a user story", "create a feature",
  "create an epic", "generate a work item", or provides a work-item type plus a problem to turn
  into backlog work. For team-format enrichment (emoji sections, story-point drivers), use
  enrich-work-item instead.
license: MIT
compatibility: Requires Context7 MCP, Azure DevOps MCP, and an AI Codex vault with Specs/ and Tickets/ folders.
metadata:
  plugin: agile-workflow
  version: "0.5.0"
  orchestrator-manifest: "true"
  argument-hint: "--type <epic|feature|user-story> --title \"...\" --description \"...\" [--parent <id>] [--attachment <url|path>]"
allowed-tools: >
  Read Write Edit Glob Grep Bash
  mcp__azure-devops__wit_get_work_item
  mcp__azure-devops__wit_get_work_items_batch_by_ids
  mcp__azure-devops__wit_create_work_item
  mcp__azure-devops__wit_work_items_link
  mcp__azure-devops__wit_update_work_item
  CallMcpTool
---

# Generate Work Item

Conductor for turning a title + description into a **raw** spec, ledger draft, and (on approval)
Azure DevOps work item. Load references as each phase needs them — this file is the score, not the
textbook.

References (start at `./references/pipeline.md`):

- `./references/pipeline.md` — type map, vault paths, Context7 protocol.
- `./references/output-formats.md` — **uniform ticket body** (required before PHASE 5).
- `./references/canonical/` — **read-only shape contracts** (`canonical-epic.md`,
  `canonical-feature.md`, `canonical-user-story.md`). Do not edit these files; validate every draft
  against the matching template before presenting.
- `./references/blueprints/` — spec forms written to `<vault>/Specs/`:
  - `spec-epic.md`, `spec-feature.md`, `spec-work-item.md`
- `../../references/decomposition-rules.md` — hierarchy and parent rules.
- `../../references/ticket-structure.md` — vault hook constraints (frontmatter, filename).
- `../../references/azure-mechanics.md` — create/link MCP calls + gotchas.

Context7: read `context7-mcp` skill; server `plugin-context7-plugin-context7`.

**Not in scope:** enricher templates, emoji section layouts, or story-point driver tables — use the
`enrich-work-item` skill after drafting if the host team requires that format.

---

## PHASE 0 — COLLECT INPUTS

Gather inputs **one at a time** via the host UI. Each step: brief purpose, required vs optional.

| Input | Required | Purpose |
| --- | --- | --- |
| `title` | yes | Short work-item title |
| `description` | yes | Problem statement or scope in the author's words |
| `work_item_type` | yes | `epic` \| `feature` \| `user-story` |
| `parent` | when type ≠ epic | Parent id or Azure URL (Epic→Feature, Feature→Story) |
| `attachment` | no | Supporting doc URL or vault path |

Also accept flags from `/generate-work-item` or conversational inference (see Examples).

Normalize type → Azure `workItemType`:

| Input | Azure type | Parent required |
| --- | --- | --- |
| `epic` | Epic | no |
| `feature` | Feature | Epic id |
| `user-story` | User Story | Feature id |

If `parent` is missing when required: STOP and ask once. If parent type mismatches hierarchy: STOP
and report (see `decomposition-rules.md`).

Resolve vault from `.claude/codex-workflow.config.json` `codex.folder`, else glob `AI_Codex*/`.

---

## PHASE 1 — INGEST

1. Record normalized inputs.
2. If `parent` provided: `wit_get_work_item(id=<parent>, expand=relations)` — capture title,
   description, type, and chain. Verify parent type matches hierarchy.
3. If `attachment` is a path: read it. If URL: fetch or summarize. Note failures in spec References.

---

## PHASE 2 — RESEARCH (Context7)

**Always run before drafting.** Read `context7-mcp` skill, then:

1. Extract tech-stack tokens from `title`, `description`, `attachment`, and parent body.
2. Up to **3 libraries**: `resolve-library-id` → pick best match → `query-docs`.
3. If Context7 unavailable: proceed with `source: [manual]` and supplied refs only.

Output: research bundle for the spec blueprint.

---

## PHASE 3 — WRITE SPEC

Pick blueprint from `./references/blueprints/`:

| `work_item_type` | Blueprint |
| --- | --- |
| `epic` | `spec-epic.md` |
| `feature` | `spec-feature.md` |
| `user-story` | `spec-work-item.md` |

Write to `<vault>/Specs/<prefix>-<kebab-slug>-spec.md`. Populate all sections from inputs + research.
**Do not skip** — spec is the analysis ledger.

---

## PHASE 4 — GENERATE DRAFT

**Read `./references/output-formats.md` and the matching `./references/canonical/canonical-*.md`
first.** Every draft uses the **same** body shape (canonical templates are immutable — conform, do
not modify):

- `# <Title>`
- `[[Specs/<spec-basename>]]` wikilink under the title
- `## Requisitos` — requirement bullets (from `description`, parent context, attachment, research)
- `## Critérios de Aceite` — `- [ ]` checkboxes, testable, infinitive verbs

Path: `<vault>/Tickets/Ready/<prefix>-<kebab-slug>.md` only — never vault root or `Specs/`.

Frontmatter per `ticket-structure.md`: `type: ticket`, no `status:` key; filename regex
`^(\d+|tech-debt|bug|task|spike)-[a-z0-9-]+$` (prefix with parent Feature id until Azure assigns id).

Present title, requirements, acceptance criteria, spec path, and draft path in chat.

---

## PHASE 5 — GATE & DESTINATION

**── GATE —** WAIT for explicit approval (`proceed`, `create it`, `go ahead`) before any write.
Silence is not approval.

Then ask **where to persist** (if the user has not already chosen):

1. **Azure DevOps** — create work item + link parent.
2. **Codex Workflow AI Ledger** — keep vault spec + `Tickets/Ready/` draft only.
3. **Chat only** — formatted markdown ready to copy (no vault/Azure writes).

If the user named no destination and wants chat-only output, skip vault/Azure unless they approve
ledger persistence.

---

## PHASE 6 — CREATE (Azure DevOps)

When destination includes Azure, per `azure-mechanics.md`:

1. `wit_create_work_item` with matching `workItemType`; **Description in Markdown** (draft body).
2. If parent required: `wit_work_items_link` with **`type: "parent"`** explicit.
3. Set Story Points at creation for User Story when supported.

---

## PHASE 7 — VERIFY

When Azure was used:

1. `wit_get_work_item` read-back — assert `System.Parent == <expected parent>` when applicable.
2. Update vault draft: set `azure_id` in frontmatter; rename to `<azure-id>-<slug>.md`.
3. Update spec frontmatter `ticket` with new id when applicable.

On assertion failure: STOP and report — do not claim success.

Append checkpoint to open `Agent_Sessions/` record when the host keeps a session ledger.

---

## Operating rules

- **Raw ticket only** — uniform `# Title` + `## Requisitos` + `## Critérios de Aceite`; no enricher
  sections in this skill.
- **Spec before ticket** — PHASE 3 always runs; Context7 feeds the spec.
- **Tickets/Ready only** for drafts.
- **One gate** before persistence writes.
- **Hierarchy invariants** — never link Story to Epic; always pass `type: "parent"` on link.
- **Hook-safe drafts** — valid frontmatter and filename per `ticket-structure.md`.
- **Locale** — match the language of `description` for section labels and body prose.

## Examples

**Slash command:**

```
/generate-work-item --type user-story --parent 6869 --title "Login field validation" --description "Validate email and password with inline errors on the login form"
```

**Conversational trigger:**

> Start a feature ticket for OAuth2 login under epic 6800

→ Infer `work_item_type: feature`, `parent: 6800`, run full pipeline.

**Chat-only output:**

> Generate an epic for platform security — just show me the markdown

→ Run through PHASE 4, present body in chat; skip vault/Azure unless user approves ledger save.
