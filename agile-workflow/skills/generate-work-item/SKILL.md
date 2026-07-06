---
name: generate-work-item
description: >
  Generate an Epic, Feature, User Story, or Task with a title, requirement bullets, and acceptance
  criteria; research the tech stack via Context7, save a spec to the vault Specs folder and a
  draft to the ledger, then create the work item in Azure DevOps after user confirmation. Use when
  the user runs /generate-work-item, asks to "create a ticket", "create a user story", "create a
  feature", "create an epic", "create a task", or "generate a work item", or provides a work item
  type plus a problem description to turn into a backlog item.
license: MIT
compatibility: Requires Azure DevOps MCP, Context7 MCP, and an AI Codex vault with Specs/ and Tickets/ folders.
metadata:
  plugin: agile-workflow
  version: "0.5.0"
  orchestrator-manifest: "true"
  argument-hint: "--type <epic|feature|user-story|task> --idea \"...\" [--parent <id>] [--refs <url>...] [--spec <path|text>]"
allowed-tools: >
  Read Write Edit Glob Grep Bash
  mcp__azure-devops__wit_get_work_item
  mcp__azure-devops__wit_get_work_items_batch_by_ids
  mcp__azure-devops__wit_create_work_item
  mcp__azure-devops__wit_work_items_link
  mcp__azure-devops__wit_update_work_item
  CallMcpTool
---

# generate-work-item

Conductor for turning an idea into a spec + ledger draft + Azure DevOps work item. Load references
as each phase needs them.

References (start at `./references/pipeline.md`):
- `./references/pipeline.md` — entry point: type map, vault paths, Context7 protocol.
- `./references/blueprints/` — blank forms filled into `<vault>/Specs/` and ticket layout quick-ref:
  - `spec-epic.md`, `spec-feature.md`, `spec-work-item.md` — spec blueprints
  - `ticket-quickref.md` — ticket section layouts (extracts from enrichers)
- `./references/enrichers/` — **canonical enricher prompts** (authoritative ticket prose rules):
  - `epic-enricher.prompt.md`, `feature-enricher.prompt.md`, `work-item-enricher.prompt.md`
- `<vault>/assets/*-enricher.prompt.md` — host vault copies (prefer when present).
- `../../references/decomposition-rules.md` — hierarchy, parent rules, story-point heuristic.
- `../../references/ticket-structure.md` — vault hook constraints (frontmatter, filename).
- `../../references/azure-mechanics.md` — create/link MCP calls + gotchas.

Context7 (read `context7-mcp` skill): `resolve-library-id` → `query-docs` via Context7 MCP server
`plugin-context7-plugin-context7`.

---

## Arguments

Parse from `$ARGUMENTS`, flags, or conversational input:

| Argument | Required | Description |
| --- | --- | --- |
| `work_item_type` | yes | `epic` \| `feature` \| `user-story` \| `task` |
| `idea` | yes | Problem statement or general description |
| `parent` | when type ≠ epic | Parent work item id (Epic→Feature, Feature→Story, Story→Task) |
| `refs` | no | External docs/URLs (comma-separated or repeated flag) |
| `spec` | no | Existing spec path or inline spec text to incorporate |

Normalize type → Azure `workItemType`:

| Input | Azure type | Parent required |
| --- | --- | --- |
| `epic` | Epic | no |
| `feature` | Feature | Epic id |
| `user-story` | User Story | Feature id |
| `task` | Task | Story id |

If `parent` is missing when required: STOP and ask once. If parent type mismatches hierarchy: STOP
and report (see decomposition-rules.md).

Resolve vault folder from `.claude/codex-workflow.config.json` `codex.folder`, else glob `AI_Codex*/`.

---

## PHASE 1 — INGEST

1. Record normalized inputs.
2. If `parent` provided: `wit_get_work_item(id=<parent>, expand=relations)` — capture title,
   description, type, and chain. Verify parent type matches hierarchy.
3. If `spec` is a path: read it. If inline text: treat as supplemental context.
4. If `refs` provided: fetch or summarize each (web docs, vault paths). Do not block on fetch
   failures — note unavailable refs in the spec's References section.

---

## PHASE 2 — RESEARCH (Context7 hook)

**Always run before drafting.** Read `context7-mcp` skill, then:

1. Load the matching enricher (`enrichers/<type>-enricher.prompt.md` or `work-item-enricher` for
   user-story/task/bug) — follow its **Contexto Obrigatório** when host docs exist.
2. Extract tech-stack tokens from `idea`, `refs`, `spec`, parent body, and enricher project hints.
3. Up to **3 libraries**: `resolve-library-id` → pick best match → `query-docs`.
4. If Context7 unavailable: proceed with `source: [manual]` and supplied refs only.

Output: research bundle + classification (epic/feature type, bug vs story, implicit requirements).

---

## PHASE 3 — WRITE SPEC (mandatory)

Pick the spec blueprint from `./references/blueprints/`:

| `work_item_type` | Blueprint |
| --- | --- |
| `epic` | `spec-epic.md` |
| `feature` | `spec-feature.md` |
| `user-story`, `task` | `spec-work-item.md` |

Write to `<vault>/Specs/<prefix>-<slug>-spec.md`. Populate all sections from template + research
bundle. For user-story inputs, classify Bug vs User Story per enricher §1 keywords.

**Do not skip** — spec is the analysis ledger; ticket is the enriched deliverable.

---

## PHASE 4 — GENERATE DRAFT

**Read the full enricher prompt** for the type. Apply its quality rules, concision limits, and
checklist before writing.

| Type | Enricher | Word limit | Output section |
| --- | --- | --- | --- |
| Epic | `epic-enricher.prompt.md` | 400 | §4 |
| Feature | `feature-enricher.prompt.md` | 300 | §4 |
| User Story / Bug / Task | `work-item-enricher.prompt.md` | 200 | §6 |

Derive from spec + enricher:

- **Title** — suggest outside the markdown block (enricher convention); objective-focused.
- **Body** — exact section structure from enricher output format (see `blueprints/ticket-quickref.md`).
- **Story points** — 6-driver MAX per work-item-enricher §7–7.2 (User Story/Bug only).

Write vault draft to `<vault>/Tickets/Ready/<prefix>-<kebab-slug>.md`:

- Frontmatter per `blueprints/ticket-quickref.md` + `ticket-structure.md` hook rules.
- Filename regex: `^(\d+|tech-debt|bug|task|spike)-[a-z0-9-]+$`.
- Wikilink spec: `[[Specs/<spec-basename>]]`.

Run enricher **Checklist de Auto-Revisão** mentally before presenting to user.

Present **title**, **requirements**, **acceptance criteria**, spec path, and draft path to the user.

**── GATE —** WAIT for explicit approval (`proceed`, `create it`, `go ahead`) before Azure writes.
Silence is not approval.

---

## PHASE 5 — CREATE (Azure DevOps)

Per `azure-mechanics.md`:

1. `wit_create_work_item` with `workItemType` matching normalized type; **Description in Markdown**.
2. If parent required: `wit_work_items_link` with **`type: "parent"`** explicit — parent id per
   hierarchy (Story→Feature, not Epic).
3. Set Story Points at creation for User Story when supported.

---

## PHASE 6 — VERIFY

1. `wit_get_work_item` read-back — assert `System.Parent == <expected parent>` when applicable.
2. Update vault draft: set `azure_id` in frontmatter; **rename file** to `<azure-id>-<slug>.md`.
3. Update spec frontmatter `ticket` with new id if applicable.
4. Optionally run `bin/agile-workflow validate --file <draft>` for User Story drafts.

On assertion failure: STOP and report — do not claim success.

---

## PHASE 7 — PERSIST REPORT

Append checkpoint to the open `Agent_Sessions/` record (if session ledger exists):

- Spec path, draft path (final name), Azure id, parent link verified.

---

## Operating rules

- **Enricher-driven output** — ticket body MUST follow the matching `*-enricher.prompt.md` §output
  format; spec MUST follow the matching `blueprints/spec-*.md` blueprint.
- **Spec before ticket** — PHASE 3 always runs; Context7 research feeds the spec.
- **One gate** before Azure — show draft, wait for approval.
- **Hierarchy invariants** — never link Story to Epic; always pass `type: "parent"` on link.
- **Hook-safe drafts** — `type: ticket` in frontmatter, no `status:` key, valid filename regex.
- **Locale** — match the language of `idea` for section labels and body prose.

## Examples

**Explicit command:**

```
/generate-work-item --type user-story --parent 6869 --idea "Validate login form fields with inline errors" --refs https://flutter.dev/docs/cookbook/forms/validation
```

**Conversational trigger:**

> Create a feature for OAuth2 login under epic 6800

→ Infer `work_item_type: feature`, `parent: 6800`, run full pipeline.

**With existing spec:**

```
/generate-work-item --type task --parent 6870 --spec Specs/6869-login-form-validation-spec.md --idea "Add widget tests for email validation"
```
