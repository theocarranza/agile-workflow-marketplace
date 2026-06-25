# validate-artifact Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the `validate-artifact` skill and promote shared reference files to the plugin level so both skills read from a single source of truth.

**Architecture:** Four ordered phases (INGEST → VALIDATE → REPORT → PERSIST). All checks are non-blocking — every check runs and the full finding set is emitted at the end. Two new skill-specific reference files carry the check catalog and report templates; four existing reference files move up from `decompose-backlog/references/` to `agile-workflow/references/`.

**Tech Stack:** Markdown conductor files (SKILL.md), YAML frontmatter, Azure DevOps MCP (`mcp__azure-devops__*`).

## Global Constraints

- All new markdown files must be valid YAML frontmatter + CommonMark body.
- No `status:` key in any frontmatter that lands in `Tickets/` or `Agent_Reports/`.
- SKILL.md files are exempt from the workspace markdown allowlist — use the Read/Edit tools on them directly.
- Reference files under `agile-workflow/references/` are NOT in the allowlist — use `bash cat` (not the Read tool) to verify their contents after writing.
- Commit message style: `feat:` for new files, `refactor:` for moves/path updates. Conventional commits, atomic per task.
- US English throughout.

---

### Task 1: Promote shared references to plugin level

Move the four shared reference files from `agile-workflow/skills/decompose-backlog/references/` to `agile-workflow/references/` using `git mv` so history is preserved.

**Files:**
- Move: `agile-workflow/skills/decompose-backlog/references/decomposition-rules.md` → `agile-workflow/references/decomposition-rules.md`
- Move: `agile-workflow/skills/decompose-backlog/references/ticket-structure.md` → `agile-workflow/references/ticket-structure.md`
- Move: `agile-workflow/skills/decompose-backlog/references/azure-mechanics.md` → `agile-workflow/references/azure-mechanics.md`
- Move: `agile-workflow/skills/decompose-backlog/references/audit-checklist.md` → `agile-workflow/references/audit-checklist.md`

**Interfaces:**
- Produces: `agile-workflow/references/` with 4 files; `agile-workflow/skills/decompose-backlog/references/` now empty (directory can remain).

- [ ] **Step 1: Create the shared references directory and move files**

```bash
mkdir -p agile-workflow/references
git mv agile-workflow/skills/decompose-backlog/references/decomposition-rules.md agile-workflow/references/decomposition-rules.md
git mv agile-workflow/skills/decompose-backlog/references/ticket-structure.md agile-workflow/references/ticket-structure.md
git mv agile-workflow/skills/decompose-backlog/references/azure-mechanics.md agile-workflow/references/azure-mechanics.md
git mv agile-workflow/skills/decompose-backlog/references/audit-checklist.md agile-workflow/references/audit-checklist.md
```

- [ ] **Step 2: Verify files exist at new location**

```bash
ls agile-workflow/references/
```

Expected output (order may vary):
```
audit-checklist.md
azure-mechanics.md
decomposition-rules.md
ticket-structure.md
```

- [ ] **Step 3: Verify old location is empty**

```bash
ls agile-workflow/skills/decompose-backlog/references/
```

Expected: empty output (directory exists but no files).

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "refactor: promote shared references to plugin level

Move decomposition-rules, ticket-structure, azure-mechanics, audit-checklist
from decompose-backlog/references/ to agile-workflow/references/ — single
source of truth for both skills."
```

---

### Task 2: Update decompose-backlog SKILL.md reference paths

The `References` prose block in `decompose-backlog/SKILL.md` currently says `references/` (relative to the skill directory). Update it to `../../references/` to point to the new plugin-level location.

**Files:**
- Modify: `agile-workflow/skills/decompose-backlog/SKILL.md` (line 29 area — the References block)

**Interfaces:**
- Consumes: moved files from Task 1 at `agile-workflow/references/`
- Produces: updated SKILL.md with correct paths

- [ ] **Step 1: Read the current References block**

Use the Read tool on `agile-workflow/skills/decompose-backlog/SKILL.md` (SKILL.md files are allowlist-exempt). Confirm the block reads:

```
References (in `references/`):
- `decomposition-rules.md` — ...
- `ticket-structure.md` — ...
- `azure-mechanics.md` — ...
- `audit-checklist.md` — ...
```

- [ ] **Step 2: Update the References block**

Replace the old block with:

```
References (in `../../references/`):
- `decomposition-rules.md` — hierarchy, sizing (1 Story = 1 sprint = 1 PR), story-point heuristic, DoR.
- `ticket-structure.md` — draft format + vault hook constraints (frontmatter, filename regex).
- `azure-mechanics.md` — create/link MCP calls + the two linking gotchas + rendering rules.
- `audit-checklist.md` — fidelity / coverage / DoR postflight.
```

- [ ] **Step 3: Verify no old path remains**

```bash
grep "references/" agile-workflow/skills/decompose-backlog/SKILL.md
```

Expected: one line, `../../references/`.

- [ ] **Step 4: Commit**

```bash
git add agile-workflow/skills/decompose-backlog/SKILL.md
git commit -m "refactor: update decompose-backlog reference paths to plugin level"
```

---

### Task 3: Create validation-checks.md

Write the full check catalog for `validate-artifact`. This is the single source of truth for what checks run, per artifact type and category.

**Files:**
- Create: `agile-workflow/skills/validate-artifact/references/validation-checks.md`

**Interfaces:**
- Produces: check catalog consumed by `validate-artifact/SKILL.md` (Task 5)

- [ ] **Step 1: Create directory**

```bash
mkdir -p agile-workflow/skills/validate-artifact/references
```

- [ ] **Step 2: Write validation-checks.md**

Create `agile-workflow/skills/validate-artifact/references/validation-checks.md` with this exact content:

```markdown
# Validation Check Catalog

Full set of checks run by the `validate-artifact` skill, organized by category and artifact type.
Each check emits: `{ name, result: PASS|FAIL|WARN, detail }`.

## a) STRUCTURAL

### Vault draft only

| Check | Condition | Result |
|---|---|---|
| `frontmatter-type-present` | `type:` key exists in frontmatter | FAIL if absent |
| `frontmatter-status-absent` | `status:` key NOT present in frontmatter | FAIL if present |
| `filename-regex` | Filename matches `^(\d+|tech-debt|bug|task|spike)-[a-z0-9-]+` | FAIL if no match |

### All sources — body sections

**User Story** — all 7 sections must be present. Emit one `body-section-missing: <name>` FAIL per absent section.

Required sections (detect by emoji + label heading):
- `🎯 O quê`
- `💡 Por quê`
- `📋 Comportamento esperado`
- `✅ Critérios de Aceite`
- `🔧 Notas Técnicas`
- `📊 Complexidade`
- `📄 Descrição Original`

**Feature / Epic** — title non-empty AND description non-empty. FAIL if either absent.

## b) HIERARCHY

Requires Azure MCP (`wit_get_work_item`). If `azure_id` is null and source is vault, emit
`WARN hierarchy-skipped-no-azure-id` and skip the entire category.

Failures are logged and validation continues to the next check.

| Artifact | Assertion | Check name | Result |
|---|---|---|---|
| User Story | `System.Parent` exists and its `WorkItemType == "Feature"` | `hierarchy-story-parent-is-feature` | FAIL if parent is Epic or missing |
| Feature | `System.Parent` exists and its `WorkItemType == "Epic"` | `hierarchy-feature-parent-is-epic` | FAIL if missing or wrong type |
| Epic | No child items with `WorkItemType == "User Story"` | `hierarchy-epic-no-direct-stories` | FAIL if any direct Story children found |

## c) CONTENT

### User Story only

| Check | Condition | Result |
|---|---|---|
| `content-complexidade-breakdown` | `📊 Complexidade` section contains per-driver scores — keywords: Escopo, Incerteza, Integrações, Dados, QA, Rollout | FAIL if absent |
| `content-story-points-set` | Story points field > 0 (frontmatter `story_points` or Azure `Microsoft.VSTS.Scheduling.StoryPoints`) | FAIL if unset or 0 |
| `content-descricao-original-present` | `📄 Descrição Original` section is non-empty | FAIL if empty |

### All artifact types

| Check | Condition | Result |
|---|---|---|
| `content-no-machine-paths` | Body does not contain absolute filesystem paths — pattern: `/home/`, `/Users/`, `C:\`, `D:\` | WARN if found |
| `content-no-meta-prose` | Body does not contain `TBD`, `to be defined`, or `a definir` outside `@TODO` annotation context | WARN if found |

## d) DoR (Definition of Ready)

Applied to all artifact types unless noted.

| Check | Condition | Result |
|---|---|---|
| `dor-title-clear` | Title non-empty and word count > 5 | FAIL if not met |
| `dor-description-present` | Body / description field non-empty | FAIL if not met |
| `dor-story-points-set` *(User Story only)* | Story points > 0 | FAIL if not met |
| `dor-linked-to-feature` *(User Story only)* | Reuses result of `hierarchy-story-parent-is-feature` — no extra MCP call | FAIL if that check failed |
```

- [ ] **Step 3: Verify file was written**

```bash
bash -c 'wc -l agile-workflow/skills/validate-artifact/references/validation-checks.md'
```

Expected: > 60 lines.

- [ ] **Step 4: Commit**

```bash
git add agile-workflow/skills/validate-artifact/references/validation-checks.md
git commit -m "feat: add validate-artifact validation-checks reference"
```

---

### Task 4: Create report-format.md

Write the output templates for the terminal report and the vault note.

**Files:**
- Create: `agile-workflow/skills/validate-artifact/references/report-format.md`

**Interfaces:**
- Produces: templates consumed by `validate-artifact/SKILL.md` phases 3 and 4 (Task 5)

- [ ] **Step 1: Write report-format.md**

Create `agile-workflow/skills/validate-artifact/references/report-format.md` with this exact content:

````markdown
# Report Format

## Terminal output template

```
Validating <type> — "<title>" [<source: vault|azure>]
============================================================

STRUCTURAL
  [PASS]  frontmatter-type-present
  [FAIL]  frontmatter-status-absent — `status: active` found in frontmatter
  [SKIP]  filename-regex — source is Azure, not a vault draft

HIERARCHY
  [PASS]  hierarchy-story-parent-is-feature — parent #6868 is Feature "Payment Flow"
  [WARN]  hierarchy-skipped-no-azure-id — no azure_id in frontmatter, hierarchy checks skipped

CONTENT
  [PASS]  content-complexidade-breakdown
  [FAIL]  content-story-points-set — story_points not set in frontmatter
  [PASS]  content-descricao-original-present
  [WARN]  content-no-machine-paths — found: /home/user/projects/repo

DoR
  [PASS]  dor-title-clear
  [PASS]  dor-description-present
  [FAIL]  dor-story-points-set — story points not set
  [FAIL]  dor-linked-to-feature — hierarchy-story-parent-is-feature failed

------------------------------------------------------------
Summary: 5 passed · 4 failed · 2 warnings
Outcome: FAIL
```

Rules:
- Every check that ran appears as one line: `  [PASS|FAIL|WARN|SKIP]  <check-name>  —  <detail>`
- SKIP: check was intentionally not run (wrong artifact type, missing azure_id). Include reason.
- Detail field: omit for PASS unless the detail adds value (e.g., confirming a parent id).
- Separator line: 60 `=` characters (header) and 60 `-` characters (before summary).

## Vault note frontmatter

```yaml
---
date: <YYYY-MM-DD>
type: report
artifact: <azure-id or vault-filename>
artifact_type: <Epic|Feature|User Story>
source: <vault|azure>
outcome: <pass|fail>
---
```

Do NOT include `status:` — the vault hook forbids it in `Agent_Reports/`.

## Vault note body

Reproduce the terminal output from the Report phase verbatim as a fenced code block:

```
(terminal output here)
```

No reformatting. What was printed is what is stored.
````

- [ ] **Step 2: Verify file was written**

```bash
bash -c 'wc -l agile-workflow/skills/validate-artifact/references/report-format.md'
```

Expected: > 50 lines.

- [ ] **Step 3: Commit**

```bash
git add agile-workflow/skills/validate-artifact/references/report-format.md
git commit -m "feat: add validate-artifact report-format reference"
```

---

### Task 5: Create validate-artifact/SKILL.md

Write the four-phase conductor. This is the entry point the skill runner loads.

**Files:**
- Create: `agile-workflow/skills/validate-artifact/SKILL.md`

**Interfaces:**
- Consumes: `../../references/` (4 shared files from Task 1), `./references/validation-checks.md` (Task 3), `./references/report-format.md` (Task 4)
- Produces: the deployable skill

- [ ] **Step 1: Write SKILL.md**

Create `agile-workflow/skills/validate-artifact/SKILL.md` with this exact content:

```markdown
---
name: validate-artifact
description: >
  Validate a single agile artifact (Epic, Feature, or User Story) against the agile-workflow
  rule set. Use when the user asks to "validate this story/feature/epic", "check this ticket",
  "is this artifact ready?", or provides a vault draft path or Azure work item ID and wants a
  quality report. Accepts a vault draft (file path) or a live Azure DevOps work item (ID). Runs
  all checks non-blocking and emits a terminal report + persisted vault note. One artifact per
  invocation.
allowed-tools: >
  Read Write Edit Glob Grep Bash
  mcp__azure-devops__wit_get_work_item
  mcp__azure-devops__wit_get_work_items_batch_by_ids
  mcp__azure-devops__search_workitem
---

# validate-artifact

Quality gate for a single agile artifact. Load reference files as each phase needs them.

References (shared, in `../../references/`):
- `decomposition-rules.md` — hierarchy, DoR, sizing, story-point heuristic.
- `ticket-structure.md` — body sections, frontmatter constraints, content hygiene.
- `azure-mechanics.md` — MCP calls, linking mechanics, rendering rules.
- `audit-checklist.md` — fidelity, coverage, DoR check definitions.

References (skill-specific, in `./references/`):
- `validation-checks.md` — full check catalog per artifact type + category.
- `report-format.md` — terminal output template + vault note template.

---

## PHASE 1 — INGEST

**Input:** one of — a vault draft file path OR an Azure work item ID.

Determine source from the argument:

**If vault draft (file path argument):**
1. Read the markdown file. Parse frontmatter: extract `work_item_type`, `parent_feature`,
   `azure_id`, `story_points`. Parse body: identify sections by emoji + label headings.
2. Derive artifact type from `work_item_type` frontmatter value.

**If Azure ID (numeric argument):**
1. Call `wit_get_work_item(id=<id>, expand=relations)`.
2. Extract: `System.WorkItemType`, `System.Title`, `System.Description`,
   `Microsoft.VSTS.Scheduling.StoryPoints`, `System.Parent`.
3. Artifact type = `System.WorkItemType`.

Normalize into a unified artifact record:

```
{
  type:         "Epic" | "Feature" | "User Story"
  title:        string
  body:         string  (full description / body text)
  story_points: number | null
  parent_id:    number | null
  source:       "vault" | "azure"
  filename:     string | null   (vault only — basename without path)
  azure_id:     number | null
  raw:          original parsed content
}
```

If artifact type cannot be determined: STOP and report —
`"Cannot detect artifact type — check work_item_type frontmatter (vault) or System.WorkItemType (Azure)."`

If given multiple IDs or paths: process only the first and warn —
`"validate-artifact processes one artifact per invocation."`

---

## PHASE 2 — VALIDATE

Read `./references/validation-checks.md` for the complete check definitions, conditions, and
FAIL/WARN thresholds before running checks.

Run all four categories in order. Each check emits `{ name, result, detail }`.
No check halts sibling or subsequent checks on failure. Collect all findings.

### a) STRUCTURAL

**Vault draft only:**
- `frontmatter-type-present` — FAIL if `type:` key absent from frontmatter.
- `frontmatter-status-absent` — FAIL if `status:` key present in frontmatter.
- `filename-regex` — FAIL if filename does not match `^(\d+|tech-debt|bug|task|spike)-[a-z0-9-]+`.
  If source is Azure (no filename): emit SKIP.

**All sources:**
- If User Story: check each of the 7 required sections present in body.
  Emit `body-section-missing: <section name>` FAIL for each absent section.
- If Feature or Epic: check title non-empty AND description non-empty. FAIL if either absent.

### b) HIERARCHY

If `azure_id` is null and source is vault: emit `WARN hierarchy-skipped-no-azure-id` and skip
this entire category.

**User Story:**
1. `wit_get_work_item(id=artifact.parent_id)`. Assert `System.WorkItemType == "Feature"`.
2. Check `hierarchy-story-parent-is-feature` — FAIL if parent is Epic or missing.

**Feature:**
1. `wit_get_work_item(id=artifact.parent_id)`. Assert `System.WorkItemType == "Epic"`.
2. Check `hierarchy-feature-parent-is-epic` — FAIL if missing or wrong type.

**Epic:**
1. Fetch children via `search_workitem` or relations from the ingested item.
   Assert no child has `System.WorkItemType == "User Story"`.
2. Check `hierarchy-epic-no-direct-stories` — FAIL if direct Story children found.

If an MCP call fails (network / permission): emit `SKIP <check> — MCP unavailable: <error>` and
continue. Do not abort the run.

### c) CONTENT

**User Story only:**
- `content-complexidade-breakdown` — scan `📊 Complexidade` section for driver keywords
  (Escopo, Incerteza, Integrações, Dados, QA, Rollout). FAIL if absent.
- `content-story-points-set` — assert `story_points > 0`. FAIL if unset or 0.
- `content-descricao-original-present` — assert `📄 Descrição Original` section non-empty.
  FAIL if empty.

**All artifact types:**
- `content-no-machine-paths` — scan body for `/home/`, `/Users/`, `C:\`, `D:\`.
  WARN if found; include the matched path in detail.
- `content-no-meta-prose` — scan body for `TBD`, `to be defined`, `a definir` outside
  `@TODO` annotation context. WARN if found.

### d) DoR (Definition of Ready)

- `dor-title-clear` — assert title non-empty and word count > 5. FAIL if not met.
- `dor-description-present` — assert body / description non-empty. FAIL if not met.
- `dor-story-points-set` *(User Story only)* — assert `story_points > 0`. FAIL if not met.
- `dor-linked-to-feature` *(User Story only)* — reuse result of `hierarchy-story-parent-is-feature`;
  no extra MCP call. FAIL if that check failed or was skipped.

---

## PHASE 3 — REPORT

Read `./references/report-format.md` for the exact output template before printing.

Print to terminal:
1. Header: `Validating <type> — "<title>" [<source>]`
2. Separator: 60 `=` characters.
3. Findings grouped by category (STRUCTURAL / HIERARCHY / CONTENT / DoR).
   Each line: `  [PASS|FAIL|WARN|SKIP]  <check-name>  —  <detail>`
4. Separator: 60 `-` characters.
5. Summary: `Summary: X passed · Y failed · Z warnings`
6. Outcome: `Outcome: PASS` (zero FAILs) or `Outcome: FAIL` (≥1 FAIL)

---

## PHASE 4 — PERSIST

Read `./references/report-format.md` for the vault note frontmatter template.

Path: `AI_Codex_AgileWorkflowMarketplace/Agent_Reports/`

Filename: `<YYYY-MM-DD>-validate-<id-or-slug>.md`
- Use `azure_id` if available.
- Otherwise: derive slug from vault filename (strip extension) or from title (lowercase, spaces → hyphens, max 40 chars).

Frontmatter:
```yaml
---
date: <YYYY-MM-DD>
type: report
artifact: <azure-id or vault-filename>
artifact_type: <Epic|Feature|User Story>
source: <vault|azure>
outcome: <pass|fail>
---
```

Body: reproduce the full terminal output from Phase 3 verbatim inside a fenced code block.

Do NOT include `status:` in frontmatter.

---

## Guardrails

- **No mutations.** This skill reads and reports only. Never write, update, or link work items.
- **Non-blocking.** Every check runs regardless of prior failures in the same category.
- **SKIP over ERROR.** If an Azure MCP call fails, log SKIP with reason and continue.
- **One artifact per run.** Process only the first argument if multiple are given.
```

- [ ] **Step 2: Verify frontmatter is valid YAML**

```bash
bash -c "head -20 agile-workflow/skills/validate-artifact/SKILL.md"
```

Expected: `---` on line 1, `name: validate-artifact` on line 2, closing `---` present.

- [ ] **Step 3: Verify all four phases are present**

```bash
grep "^## PHASE" agile-workflow/skills/validate-artifact/SKILL.md
```

Expected:
```
## PHASE 1 — INGEST
## PHASE 2 — VALIDATE
## PHASE 3 — REPORT
## PHASE 4 — PERSIST
```

- [ ] **Step 4: Verify reference paths**

```bash
grep "references/" agile-workflow/skills/validate-artifact/SKILL.md
```

Expected lines include `../../references/` (shared) and `./references/` (skill-specific). No bare `references/` path.

- [ ] **Step 5: Commit**

```bash
git add agile-workflow/skills/validate-artifact/
git commit -m "feat: add validate-artifact skill (4-phase conductor + references)"
```

---

## Final verification

- [ ] **Confirm full file tree**

```bash
find agile-workflow -type f | sort
```

Expected tree:
```
agile-workflow/references/audit-checklist.md
agile-workflow/references/azure-mechanics.md
agile-workflow/references/decomposition-rules.md
agile-workflow/references/ticket-structure.md
agile-workflow/skills/decompose-backlog/SKILL.md
agile-workflow/skills/decompose-backlog/references/   (empty)
agile-workflow/skills/validate-artifact/SKILL.md
agile-workflow/skills/validate-artifact/references/report-format.md
agile-workflow/skills/validate-artifact/references/validation-checks.md
```

- [ ] **Confirm no broken paths in decompose-backlog**

```bash
grep "references/" agile-workflow/skills/decompose-backlog/SKILL.md
```

Expected: `../../references/` — no bare `references/` path remaining.
