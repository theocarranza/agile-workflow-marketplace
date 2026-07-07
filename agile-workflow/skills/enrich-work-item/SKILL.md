---
name: enrich-work-item
description: >
  Enriches an existing Epic, Feature, or User Story into the host team's structured format using
  type-specific enricher prompts (emoji sections, scope blocks, complexity drivers, ASCII diagrams).
  Use when the user runs /enrich-work-item, asks to "enrich a ticket", "enrich this issue",
  "format this user story", "polish this feature", "structure this epic", or provides a path, URL,
  or pasted text plus work-item type. For raw title + requirement bullets from scratch, use
  generate-work-item instead. For plain-language narrative inside enricher sections, this skill
  delegates a sub-pass to generate-plain-language-documentation after enricher assembly.
license: MIT
compatibility: Requires Azure DevOps MCP and an AI Codex vault when persisting to the ledger.
metadata:
  plugin: agile-workflow
  version: "0.6.0"
  argument-hint: "--type <epic|feature|user-story> --source <url|path|text> [--parent <id>] [--attachment <url|path>]"
allowed-tools: >
  Read Write Edit Glob Grep Bash
  mcp__azure-devops__wit_get_work_item
  mcp__azure-devops__wit_get_work_items_batch_by_ids
  mcp__azure-devops__wit_get_work_item_attachment
  mcp__azure-devops__wit_create_work_item
  mcp__azure-devops__wit_work_items_link
  mcp__azure-devops__wit_update_work_item
  CallMcpTool
---

# Enrich Work Item

Conductor for applying the **enricher pattern** to an existing work-item description. Load references
as each phase needs them.

References (start at `./references/pipeline.md`):

- `./references/pipeline.md` — type map, enricher routing, vault paths.
- `./references/azure-ingest.md` — Azure URL/id ingest: work item, attachments, description refs.
- `./references/output-formats.md` — per-type output contracts (points to enrichers).
- `./references/canonical/` — **read-only shape contracts** (`canonical-epic.md`,
  `canonical-feature.md`, `canonical-user-story.md`). Do not edit these files; validate enriched
  output against the matching template before presenting.
- `./references/enrichers/` — **authoritative** prose rules:
  - `epic-enricher.prompt.md`, `feature-enricher.prompt.md`, `work-item-enricher.prompt.md`
- `./references/blueprints/` — spec forms for optional analysis ledger in `<vault>/Specs/`.
- `./references/examples/` — illustrative dummy outputs (content reference only; shape contract is
  `./references/canonical/`).
- `<vault>/assets/*-enricher.prompt.md` — host vault copies (**prefer when present**).
- `../../references/decomposition-rules.md` — hierarchy, story-point heuristic.
- `../../references/ticket-structure.md` — vault hook constraints.
- `../../references/azure-mechanics.md` — create/update MCP calls + gotchas.
- `../generate-plain-language-documentation/references/integration-notes.md` — prose polish sub-pass
  (PHASE 4).

**Not in scope:** generating a raw work item from a title alone — use `generate-work-item` first.

---

## PHASE 0 — COLLECT INPUTS

Gather inputs **one at a time** via the host UI. Each step: brief purpose, required vs optional.

| Input | Required | Purpose |
| --- | --- | --- |
| `source` | yes | `url` \| vault `path` \| pasted `text` — the material to enrich |
| `work_item_type` | yes | `epic` \| `feature` \| `user-story` |
| `parent` | when type ≠ epic | Parent id or Azure URL for hierarchy context |
| `attachment` | no | Extra doc URL or path |

Accept `/enrich-work-item` flags or conversational inference (see Examples).

Normalize type → enricher + Azure `workItemType` per `pipeline.md`.

Resolve vault from `.claude/codex-workflow.config.json` `codex.folder`, else glob `AI_Codex*/`.

---

## PHASE 1 — INGEST

Read `./references/azure-ingest.md` when `source` is an Azure DevOps URL or numeric id.

1. Load `source`:
   - **Azure URL or id** — per `azure-ingest.md`: parse id, `wit_get_work_item(expand=relations)`,
     enumerate `AttachedFile` relations, parse description for linked docs/URLs/paths, fetch attachment
     and referenced content into `supplementary_context`. Set **Descrição Original** from
     `System.Description` verbatim.
   - **path** — read vault or filesystem markdown; capture body verbatim.
   - **url** (non-Azure) — fetch external doc; capture description verbatim.
   - **text** — treat pasted content as the description to enrich.
2. If `parent` provided: `wit_get_work_item` — capture parent chain for context and filename prefix.
   When `source` is Azure and `parent` omitted, use `System.Parent` from the fetched item.
3. If `attachment` provided: read or fetch; fold into enricher context (dedupe against Azure
   attachments already ingested).
4. Preserve **Descrição Original** text exactly for the enricher output section.

---

## PHASE 2 — ROUTE ENRICHER

Read `./references/output-formats.md` and the matching enricher:

| `work_item_type` | Enricher |
| --- | --- |
| `epic` | `enrichers/epic-enricher.prompt.md` |
| `feature` | `enrichers/feature-enricher.prompt.md` |
| `user-story` | `enrichers/work-item-enricher.prompt.md` |

Prefer `<vault>/assets/<type>-enricher.prompt.md` when it exists.

Follow enricher **Contexto Obrigatório** when host monorepo docs exist; skip gracefully when absent.

For user-story sources, classify Bug vs User Story per enricher §1 keywords when applicable.

---

## PHASE 3 — WRITE SPEC (optional ledger)

When the user will persist to the Codex ledger, fill the matching `./references/blueprints/spec-*.md`
into `<vault>/Specs/[<parent-id>-]<kebab-slug>-spec.md`. Skip when destination is chat-only.

---

## PHASE 4 — ENRICH

Apply the enricher rules to produce the **exact** output format defined in enricher §4 (Epic/Feature) or
§6 (work item). The enriched body IS the deliverable — emoji sections, scope blocks, complexity
drivers, ASCII diagrams as the enricher specifies.

**Plain-language sub-pass:** Read
`../generate-plain-language-documentation/references/integration-notes.md` § enrich-work-item; polish
narrative paragraphs inside sections (not emoji headings; not **Descrição Original**). Glossary-verify
when locale is pt-BR.

Run the enricher **Checklist de Auto-Revisão** before presenting.

Compare shape against `./references/canonical/canonical-<type>.md` (read-only contract; do not
edit). Use `./references/examples/example-<type>.md` only for illustrative content patterns.

Present the enriched markdown in chat. Suggest a title outside the markdown block when the enricher
requires it (work-item enricher).

---

## PHASE 5 — GATE & DESTINATION

**── GATE —** WAIT for explicit approval before any write. Silence is not approval.

Then ask **where to persist** (if not already chosen):

1. **Azure DevOps** — create or update work item with enriched body as Description (Markdown).
2. **Codex Workflow AI Ledger** — write/update vault draft under `Tickets/Ready/` (or host path).
3. **Chat only** — formatted markdown ready to copy.

If no destination was named and the user wants chat-only, skip vault/Azure unless they approve ledger
save.

---

## PHASE 6 — PERSIST (Azure / ledger)

**Azure** — per `azure-mechanics.md`:

- **Create** when no existing Azure id: `wit_create_work_item` + `wit_work_items_link` with
  `type: "parent"` when parent required.
- **Update** when source was an Azure id or draft with `azure_id`: `wit_update_work_item`.

**Ledger** — frontmatter per `ticket-structure.md`; hook-valid filename; enriched body verbatim.

---

## PHASE 7 — VERIFY

When Azure was used: read-back parent link and description fidelity. Update vault `azure_id` and
rename file when creating new items.

On failure: STOP and report.

Append checkpoint to open `Agent_Sessions/` record when the host keeps a session ledger.

---

## Operating rules

- **Enricher is authoritative** — output matches enricher § output format, not generate-work-item's
  uniform three-part layout.
- **Verbatim original** — always include Descrição Original from ingest (work-item description only;
  attachment text feeds enrichment context, not Descrição Original).
- **WHAT not HOW** — per enricher quality rules.
- **One gate** before persistence writes.
- **Locale** — Português BR for host-team enrichers unless the source is clearly another language.

## Examples

**Slash command:**

```
/enrich-work-item --type feature --source Tickets/Ready/6800-oauth-login.md --parent 6800
```

**Conversational trigger:**

> Enrich this user story — [pasted description]

→ Infer `work_item_type: user-story`, `source: text`, run enricher pipeline.

**Azure source:**

> Format issue 6871 in the team template

→ `source: url` (Azure), resolve per `azure-ingest.md` (work item + attachments + description refs),
enrich, present for approval.
