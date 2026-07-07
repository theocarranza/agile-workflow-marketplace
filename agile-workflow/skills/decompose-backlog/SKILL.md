---
name: decompose-backlog
description: >
  Decompose a parent Azure DevOps work item into correctly-parented, audited child Stories.
  Use when the user asks to "break down this Feature", "decompose Epic/Feature N into stories",
  "create the user stories for <feature>", "groom this backlog item", or provides a Feature/Epic id
  and wants Stories drafted and created in Azure DevOps. Drives 7 phases: ingest the parent, split
  into right-sized Stories (1 Story = 1 sprint = 1 PR), draft them in the vault, enrich to the team
  format, create them in Azure DevOps parented to the FEATURE, verify the hierarchy, and audit that
  every parent requirement has a home. Self-contained rules; two approval gates before any write.
  For plain-language scope lines and story narrative, delegates sub-passes to
  generate-plain-language-documentation in DRAFT and ENRICH phases.
license: MIT
compatibility: Requires Azure DevOps MCP and an AI Codex vault. Designed for Claude Code and Cursor.
metadata:
  plugin: agile-workflow
  version: "0.5.0"
  disable-model-invocation: "true"
allowed-tools: >
  Read Write Edit Glob Grep
  mcp__azure-devops__wit_get_work_item
  mcp__azure-devops__wit_get_work_items_batch_by_ids
  mcp__azure-devops__wit_create_work_item
  mcp__azure-devops__wit_work_items_link
  mcp__azure-devops__wit_work_item_unlink
  mcp__azure-devops__wit_update_work_item
  mcp__azure-devops__search_workitem
---

# Decompose Backlog

Conductor for turning a parent work item into child Stories in Azure DevOps. Load the reference files
as each phase needs them — they carry the self-contained rules so this file stays a score, not a
textbook.

References (in `../../references/`):

- `decomposition-rules.md` — hierarchy, sizing (1 Story = 1 sprint = 1 PR), story-point heuristic, DoR.
- `ticket-structure.md` — draft format + vault hook constraints (frontmatter, filename regex).
- `azure-mechanics.md` — create/link MCP calls + the two linking gotchas + rendering rules.
- `audit-checklist.md` — fidelity / coverage / DoR postflight.

References (skill-specific, in `./references/`):

- `canonical/canonical-user-story.md` — **read-only shape contract** for enriched Story drafts (seven
  emoji sections per `ticket-structure.md`). Do not edit; validate every draft against this template.
- `../generate-plain-language-documentation/references/integration-notes.md` — prose polish sub-pass
  in DRAFT and ENRICH phases.

## Input

A parent work item **id** (Epic or Feature). Optional: target iteration, story-point ceiling override.

## Phases

### 1. INGEST

Read the parent via `wit_get_work_item` (expand relations). Capture the original text VERBATIM, its
acceptance criteria, and the parent chain. Read any linked spike/wiki. Determine parent type.
**Branch:** if the parent is an **Epic**, STOP and ask whether to create intervening Feature(s) first
or target an existing child Feature (see decomposition-rules.md → Parent-type branch). Stories never
attach to an Epic.

### 2. DECOMPOSE

Apply the sizing rule and story-point heuristic from `decomposition-rules.md`. Produce an ordered list
of Story stubs (title + one-line scope + dependencies), each tracing to a verbatim slice of the parent.
**── GATE 1 —** present the split and WAIT for explicit approval before drafting anything.

### 3. DRAFT

Per approved stub, write a vault draft per `ticket-structure.md` and
`./references/canonical/canonical-user-story.md` — hook-valid frontmatter (`type`, no `status`),
filename regex with the Feature-id prefix, the 7 body sections in canonical order. Content hygiene
applies.

**Plain-language sub-pass:** Read
`../generate-plain-language-documentation/references/integration-notes.md` § decompose-backlog; run a
`generate-plain-language-documentation` pass on scope lines and section prose (glossary-verify via
`../generate-plain-language-documentation/references/assets/tech-glossary-en-pt-br.json` when locale
is pt-BR).

### 4. ENRICH

Tighten each draft to the team format: WHAT not HOW, ASCII diagrams, de-dup (each fact once),
story-point justification with the per-driver MAX. The enriched body IS the exact Azure description.

**Plain-language sub-pass:** Read
`../generate-plain-language-documentation/references/integration-notes.md` § decompose-backlog; polish
narrative paragraphs inside sections (not emoji headings; not story-point driver tables).
Glossary-verify via `../generate-plain-language-documentation/references/assets/tech-glossary-en-pt-br.json`
when locale is pt-BR.
**── GATE 2 —** show the final body and WAIT for thumbs-up before any Azure write.

### 5. CREATE

Per `azure-mechanics.md`: `wit_create_work_item` with **Markdown** description; then
`wit_work_items_link` with **explicit `type: "parent"`** to the **FEATURE id**. Honor both gotchas.

### 6. VERIFY (structural)

Read each created item back; assert `System.Parent == <feature id>` and the Epic→Feature→Story chain.
Reconcile vault frontmatter with the Azure-assigned id (rename file, set `azure_id`). A failed
assertion STOPS the run.

### 7. AUDIT (content + coverage)

Run `audit-checklist.md`: retrieve each item FRESH from Azure; check fidelity, build the
parent-requirement → Story coverage map (flag orphans and scope creep), confirm DoR. Emit the coverage
report. Any gap STOPS and reports — no silent patching.

## Operating rules

- Two hard gates (after DECOMPOSE, after ENRICH). Never write to the vault or Azure without the
  matching approval.
- Every Azure-mutating step is followed by a read-back assertion.
- If the host repo keeps a session ledger, write a checkpoint after CREATE and after AUDIT.
