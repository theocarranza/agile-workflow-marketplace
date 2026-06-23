# `decompose-backlog` Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `agile-workflow` standalone marketplace plugin containing the self-contained `decompose-backlog` skill, which drives a parent work item (Epic/Feature) → correctly-parented, audited child Stories in Azure DevOps.

**Architecture:** A Claude Code plugin in its own marketplace repo (mirrors the sibling `spike-workflow-marketplace`). The skill is a thin conductor (`SKILL.md`) over 7 phases, with self-contained rule content split into four `references/*.md` files loaded on demand. No application code — deliverables are markdown + two JSON manifests. "Tests" are validation gates: JSON validity, plugin discoverability, and structural assertions against required content.

**Tech Stack:** Markdown (SKILL + references), JSON (`marketplace.json`, `plugin.json`), `jq`/`python3 -json.tool` for validation, `git`/`gh` for the repo.

**Validation philosophy:** Each task ends with a concrete check command and an expected result, then a commit. Because there is no runtime, the gates verify (a) machine-readable manifests parse, (b) required structural markers exist in each file, (c) cross-references between files resolve.

**Repo root for all paths below:** `~/Documents/Projects/Personal/agile-workflow-marketplace/`

---

## File Structure

```text
agile-workflow-marketplace/
├── .claude-plugin/marketplace.json          ← Task 2
├── README.md                                ← Task 8
├── .gitignore                               ← Task 1
├── docs/
│   ├── design.md                            ← exists (approved spec)
│   └── plans/2026-06-03-decompose-backlog.md ← this file
└── agile-workflow/
    ├── .claude-plugin/plugin.json           ← Task 3
    └── skills/decompose-backlog/
        ├── SKILL.md                         ← Task 7 (conductor; written last, references the refs)
        └── references/
            ├── decomposition-rules.md       ← Task 4
            ├── ticket-structure.md          ← Task 5
            ├── azure-mechanics.md           ← Task 6 (the gotchas)
            └── audit-checklist.md           ← Task 6
```

Responsibilities:

- **marketplace.json** — lists the one plugin; entry point for `/plugin marketplace add`.
- **plugin.json** — plugin identity + version.
- **decomposition-rules.md** — hierarchy, DoR, 1-Story=1-sprint=1-PR sizing, story-point heuristic.
- **ticket-structure.md** — vault draft section format + hook constraints (frontmatter, filename regex).
- **azure-mechanics.md** — create/link MCP calls, the two linking gotchas, ASCII-vs-Markdown rendering.
- **audit-checklist.md** — fidelity / coverage / DoR postflight checks.
- **SKILL.md** — the 7-phase conductor with two approval gates; loads the references.

---

## Task 1: Initialize repo + .gitignore

**Files:**

- Create: `.gitignore`

- [ ] **Step 1: Init the git repo**

Run:

```bash
cd ~/Documents/Projects/Personal/agile-workflow-marketplace && git init
```

Expected: `Initialized empty Git repository in .../agile-workflow-marketplace/.git/`

- [ ] **Step 2: Write `.gitignore`**

Create `.gitignore`:

```gitignore
.DS_Store
*.log
.idea/
.vscode/
node_modules/
```

- [ ] **Step 3: Verify the repo is clean and docs/ is already present**

Run:

```bash
cd ~/Documents/Projects/Personal/agile-workflow-marketplace && git status --short && ls docs/
```

Expected: `.gitignore` and `docs/` show as untracked; `docs/` lists `design.md` and `plans/`.

- [ ] **Step 4: Commit**

```bash
cd ~/Documents/Projects/Personal/agile-workflow-marketplace
git add .gitignore docs/
git commit -m "chore: initialize agile-workflow-marketplace repo with design + plan"
```

---

## Task 2: Marketplace manifest

**Files:**

- Create: `.claude-plugin/marketplace.json`

- [ ] **Step 1: Write the marketplace manifest**

Create `.claude-plugin/marketplace.json`:

```json
{
  "name": "agile-workflow-marketplace",
  "owner": {
    "name": "Théo Carranza"
  },
  "plugins": [
    {
      "name": "agile-workflow",
      "source": "./agile-workflow",
      "description": "Agile backlog workflow skills for Azure DevOps. First skill, decompose-backlog: takes a parent work item (Epic/Feature), splits it into right-sized Stories (1 Story = 1 sprint = 1 PR), drafts and enriches them, creates them in Azure DevOps correctly parented to the Feature, then audits requirement coverage. Self-contained decomposition rules + Azure linking guardrails.",
      "version": "0.1.0"
    }
  ]
}
```

- [ ] **Step 2: Validate JSON parses**

Run:

```bash
cd ~/Documents/Projects/Personal/agile-workflow-marketplace && python3 -m json.tool .claude-plugin/marketplace.json > /dev/null && echo VALID
```

Expected: `VALID`

- [ ] **Step 3: Assert the plugin source path will exist**

Run:

```bash
cd ~/Documents/Projects/Personal/agile-workflow-marketplace && python3 -c "import json;d=json.load(open('.claude-plugin/marketplace.json'));print(d['plugins'][0]['source'])"
```

Expected: `./agile-workflow` (the dir is created in Task 3)

- [ ] **Step 4: Commit**

```bash
cd ~/Documents/Projects/Personal/agile-workflow-marketplace
git add .claude-plugin/marketplace.json
git commit -m "feat: add marketplace manifest listing agile-workflow plugin"
```

---

## Task 3: Plugin manifest

**Files:**

- Create: `agile-workflow/.claude-plugin/plugin.json`

- [ ] **Step 1: Write the plugin manifest**

Create `agile-workflow/.claude-plugin/plugin.json`:

```json
{
  "name": "agile-workflow",
  "version": "0.1.0",
  "description": "Agile backlog workflow skills for Azure DevOps. decompose-backlog: parent work item (Epic/Feature) → right-sized, enriched, correctly-parented Stories, with requirement-coverage audit. Self-contained rules + Azure linking guardrails.",
  "author": {
    "name": "Théo Carranza"
  }
}
```

- [ ] **Step 2: Validate JSON parses**

Run:

```bash
cd ~/Documents/Projects/Personal/agile-workflow-marketplace && python3 -m json.tool agile-workflow/.claude-plugin/plugin.json > /dev/null && echo VALID
```

Expected: `VALID`

- [ ] **Step 3: Assert version parity with marketplace entry**

Run:

```bash
cd ~/Documents/Projects/Personal/agile-workflow-marketplace
python3 -c "
import json
m=json.load(open('.claude-plugin/marketplace.json'))['plugins'][0]['version']
p=json.load(open('agile-workflow/.claude-plugin/plugin.json'))['version']
assert m==p, f'version mismatch: marketplace={m} plugin={p}'
print('PARITY', p)
"
```

Expected: `PARITY 0.1.0`

- [ ] **Step 4: Commit**

```bash
cd ~/Documents/Projects/Personal/agile-workflow-marketplace
git add agile-workflow/.claude-plugin/plugin.json
git commit -m "feat: add agile-workflow plugin manifest"
```

---

## Task 4: Reference — decomposition-rules.md

**Files:**

- Create: `agile-workflow/skills/decompose-backlog/references/decomposition-rules.md`

- [ ] **Step 1: Write the decomposition rules (self-contained)**

Create `agile-workflow/skills/decompose-backlog/references/decomposition-rules.md`:

```markdown
# Decomposition Rules

Self-contained rules for splitting a parent work item into Stories. These travel with the skill
so it needs no host-repo docs to function.

## Backlog hierarchy
```

Epic
└─ Feature
└─ Story (User Story / Bug / Tech Debt / Spike) ← the unit you create here
└─ Task

```

- A **Story** is executable work that fits one sprint and yields exactly **1 Pull Request**.
  "Story" covers User Story, Bug, Tech Debt, Spike — same backlog rules.
- A Story's parent is its **Feature**, never the Epic directly.

## The sizing rule (the core judgment)

**1 Story = 1 sprint = 1 PR.** Split the parent so each Story honors this. If a candidate Story
would exceed the team's story-point ceiling (default ceiling: **5 points** — confirm with the host
team), split it further, or stage it into phases and carry later phases as separate Stories.

Each Story must trace to a **verbatim slice of the parent text**. If a slice has no Story, it is a
dropped requirement (caught in AUDIT). If a Story has no parent slice, it is scope creep.

## Story-point heuristic (6-driver MAX)

Score each driver 1/2/3/5; the Story's points = the **MAX** across drivers (not the sum). This keeps
one hard dimension from being diluted by easy ones.

| Driver       | 1                | 2                  | 3                       | 5                          |
|--------------|------------------|--------------------|-------------------------|----------------------------|
| Escopo       | one tiny change  | one area           | multiple artifacts/area | multiple areas             |
| Incerteza    | known            | mostly known       | some unknowns           | significant unknowns       |
| Integrações  | none             | one stable         | a couple to integrate   | many / unstable            |
| Dados        | none             | trivial            | some shaping            | complex modeling/migration |
| QA           | trivial          | unit-level         | a flow                  | multi-screen E2E journey   |
| Rollout      | none             | flag/simple        | coordinated             | risky/irreversible         |

Record the per-driver scores and the MAX in the Story's Complexity section so the estimate is
auditable, e.g. `5 pts — driver: QA=5 (multi-screen E2E); Escopo=5; rest ≤3`.

## Definition of Ready (each Story must meet)

- [ ] Title states a clear objective (describe the need, not the solution; for Bugs, the defect).
- [ ] Detailed description (behaviors, scenarios, technical specs, affected areas).
- [ ] Story points set.
- [ ] Linked to a Feature.

## Parent-type branch

- Parent is a **Feature** → decompose straight into Stories.
- Parent is an **Epic** → STOP and ask: create the intervening Feature(s) first, or target an
  existing child Feature. Never attach a Story directly to an Epic.

## Provenance

Distilled from the originating team's `development-process.md` (hierarchy, DoR, story points) and
backlog-strategy guides. Values marked "default" / "confirm with host team" are tunable seams.
```

- [ ] **Step 2: Assert the file carries the non-negotiable markers**

Run:

```bash
cd ~/Documents/Projects/Personal/agile-workflow-marketplace
f=agile-workflow/skills/decompose-backlog/references/decomposition-rules.md
for marker in "1 Story = 1 sprint = 1 PR" "never the Epic" "6-driver MAX" "Definition of Ready"; do
  grep -qF "$marker" "$f" && echo "OK: $marker" || { echo "MISSING: $marker"; exit 1; }
done
```

Expected: four `OK:` lines, no `MISSING`.

- [ ] **Step 3: Commit**

```bash
cd ~/Documents/Projects/Personal/agile-workflow-marketplace
git add agile-workflow/skills/decompose-backlog/references/decomposition-rules.md
git commit -m "feat: add self-contained decomposition rules reference"
```

---

## Task 5: Reference — ticket-structure.md

**Files:**

- Create: `agile-workflow/skills/decompose-backlog/references/ticket-structure.md`

- [ ] **Step 1: Write the ticket structure + hook constraints**

Create `agile-workflow/skills/decompose-backlog/references/ticket-structure.md`:

````markdown
# Ticket Structure & Draft Constraints

How each Story draft is written so it (a) passes the host vault's hooks and (b) carries the
enriched body that becomes the exact Azure work-item description.

## Draft location (configurable seam)

Default: `Tickets/Ready/` in the host vault. If the host organizes drafts elsewhere, adapt — this
is a default, not a hard requirement.

## Frontmatter (hook-validated)

```yaml
---
date: <YYYY-MM-DD>
type: ticket # REQUIRED — the frontmatter hook rejects drafts missing `type`
work_item_type: User Story
parent_feature: <feature-id>
parent_epic: <epic-id>
azure_id: <assigned-after-creation>
tags: [ticket, user-story, ...]
---
```
````

**Hard constraint:** do NOT include a `status:` key — the originating vault's hook forbids `status`
in `Tickets/`. Lifecycle lives in Azure, not in frontmatter.

## Filename (hook-validated)

Regex: `^(\d+|tech-debt|bug|task|spike)-[a-z0-9-]+`, all lowercase.

Until Azure assigns the real id, prefix with the **parent Feature id** (e.g.
`6868-us1-...`). After creation, rename to the **Azure-assigned id** (e.g. `6870-...`) and set
`azure_id` in frontmatter. Never use `FINAL`, `us1` is fine only as a mid-name token, not a prefix.

## Body sections (order)

The body is written once and becomes the Azure description verbatim. Section labels follow the host
team's language (originating team uses pt-BR):

1. **🎯 O quê** — what, as descriptive sentences, one idea per line.
2. **💡 Por quê** — why this Story exists.
3. **📋 Comportamento esperado** — expected behavior; ASCII diagrams here (see azure-mechanics.md).
4. **✅ Critérios de Aceite** — acceptance criteria as checkboxes.
5. **🔧 Notas Técnicas** — technical notes; areas/modules, not invented implementation.
6. **📊 Complexidade** — story points + the per-driver MAX justification (decomposition-rules.md).
7. **📄 Descrição Original** — the verbatim parent slice this Story traces to.

## Content hygiene

- State each fact ONCE, in its natural section. No repetition across sections.
- No machine-specific paths or local-only / spike folder references; the project repo is the
  canonical root.
- Locale-correct technical vocabulary; no calques from English.
- No decision-making/meta in the body. An unresolved choice becomes an `@TODO (decide in breakdown)`
  annotation, never prose pretending to be a requirement.
- Focus on the WHAT and WHERE (area/module), never invent the HOW.

````

- [ ] **Step 2: Assert hook constraints are present**

Run:
```bash
cd ~/Documents/Projects/Personal/agile-workflow-marketplace
f=agile-workflow/skills/decompose-backlog/references/ticket-structure.md
for marker in "forbids \`status\`" "^(\\d+|tech-debt|bug|task|spike)" "type: ticket" "Descrição Original"; do
  grep -qF "$marker" "$f" && echo "OK: $marker" || { echo "MISSING: $marker"; exit 1; }
done
````

Expected: four `OK:` lines.

- [ ] **Step 3: Commit**

```bash
cd ~/Documents/Projects/Personal/agile-workflow-marketplace
git add agile-workflow/skills/decompose-backlog/references/ticket-structure.md
git commit -m "feat: add ticket-structure reference with hook constraints"
```

---

## Task 6: References — azure-mechanics.md + audit-checklist.md

**Files:**

- Create: `agile-workflow/skills/decompose-backlog/references/azure-mechanics.md`
- Create: `agile-workflow/skills/decompose-backlog/references/audit-checklist.md`

- [ ] **Step 1: Write azure-mechanics.md (the two gotchas)**

Create `agile-workflow/skills/decompose-backlog/references/azure-mechanics.md`:

```markdown
# Azure DevOps Mechanics

The exact MCP calls and the traps that bite if you skip them. These are invariant — not seams.

## Create a Story

Use `wit_create_work_item` (project = host's Azure project; repo context as needed):

- `workItemType: "User Story"` (or Bug/Tech Debt/Spike).
- **Description in Markdown format** — Markdown descriptions render fenced ASCII diagrams. Plain-text
  format mangles them.
- Set Story Points and tags at creation when supported.

## Link to parent — TWO GOTCHAS

### Gotcha 1 — always pass an explicit `type`

`wit_work_items_link` **defaults to `type: "related"`.** Omitting `type` silently creates a wrong
**Related** link instead of a parent link. ALWAYS pass `type: "parent"` explicitly.

### Gotcha 2 — a Story's parent is its FEATURE, not the Epic

Link the Story to the **Feature id**, never the Epic id. Skipping the Feature level breaks the
Epic→Feature→Story chain. If you have been handling the Epic id all session, do not reflexively reuse
it here — the parent is the Feature.

Fix sequence if a wrong link was made:
```

wit_work_item_unlink id=<story> type=related # remove the stray Related link
wit_work_item_unlink id=<story> type=parent # remove a wrong parent (e.g. → Epic)
wit_work_items_link id=<story> linkToId=<feature> type=parent

```

## Rendering rules

- Work-item **description** bodies: **ASCII diagrams only.** Mermaid does NOT render in work-item
  descriptions (it renders only in the Wiki). Inline SVG is unsupported.
- Keep parentheses inside ASCII diagram boxes; outside diagrams, prefer one sentence per line.

## Verify (read-back, every time)
After creating + linking, read the item back and assert `System.Parent == <feature id>` and that the
sole hierarchy relation is Parent → the Feature. A failed assertion STOPS the run.
```

- [ ] **Step 2: Write audit-checklist.md (Phase 7)**

Create `agile-workflow/skills/decompose-backlog/references/audit-checklist.md`:

```markdown
# Audit Checklist (Phase 7)

Run AFTER all Stories are created and structurally verified. Retrieve each work item **fresh from
Azure** (not the local draft) — the draft is what you meant to send; the Azure item is what landed.

## a) Fidelity

- [ ] The Azure description matches the approved enriched draft (no truncation, no MCP re-encoding).
- [ ] ASCII diagrams render intact.
- [ ] Story points and tags persisted.

## b) Coverage (the safeguard against silent requirement loss)

Build a parent-requirement → Story map:

- [ ] Every requirement / acceptance criterion in the PARENT text maps to ≥1 child Story.
- [ ] Flag any **orphan requirement** (in the parent, in no Story) — a dropped requirement.
- [ ] Flag any **unanchored Story scope** (in a Story, not in the parent) — scope creep.

Emit the map as a requirement-by-requirement pass/gap report.

## c) Definition of Ready

For each Story:

- [ ] Clear-objective title.
- [ ] Detailed description.
- [ ] Story points set.
- [ ] Parented to the Feature.

## Outcome

- All pass → report the coverage map and stop.
- Any gap → STOP and report; do not patch silently.
```

- [ ] **Step 3: Assert both files carry their non-negotiable markers**

Run:

```bash
cd ~/Documents/Projects/Personal/agile-workflow-marketplace
a=agile-workflow/skills/decompose-backlog/references/azure-mechanics.md
b=agile-workflow/skills/decompose-backlog/references/audit-checklist.md
grep -qF 'defaults to `type: "related"`' "$a" && echo "OK gotcha1" || { echo MISSING gotcha1; exit 1; }
grep -qF "FEATURE, not the Epic" "$a" && echo "OK gotcha2" || { echo MISSING gotcha2; exit 1; }
grep -qF "ASCII diagrams only" "$a" && echo "OK render" || { echo MISSING render; exit 1; }
grep -qF "fresh from" "$b" && echo "OK fresh" || { echo MISSING fresh; exit 1; }
grep -qF "orphan requirement" "$b" && echo "OK coverage" || { echo MISSING coverage; exit 1; }
```

Expected: five `OK` lines.

- [ ] **Step 4: Commit**

```bash
cd ~/Documents/Projects/Personal/agile-workflow-marketplace
git add agile-workflow/skills/decompose-backlog/references/azure-mechanics.md \
        agile-workflow/skills/decompose-backlog/references/audit-checklist.md
git commit -m "feat: add azure-mechanics + audit-checklist references"
```

---

## Task 7: SKILL.md — the conductor

**Files:**

- Create: `agile-workflow/skills/decompose-backlog/SKILL.md`

- [ ] **Step 1: Write SKILL.md**

Create `agile-workflow/skills/decompose-backlog/SKILL.md`:

```markdown
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
disable-model-invocation: true
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

References (in `references/`):

- `decomposition-rules.md` — hierarchy, sizing (1 Story = 1 sprint = 1 PR), story-point heuristic, DoR.
- `ticket-structure.md` — draft format + vault hook constraints (frontmatter, filename regex).
- `azure-mechanics.md` — create/link MCP calls + the two linking gotchas + rendering rules.
- `audit-checklist.md` — fidelity / coverage / DoR postflight.

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

Per approved stub, write a vault draft per `ticket-structure.md` — hook-valid frontmatter (`type`, no
`status`), filename regex with the Feature-id prefix, the 7 body sections. Content hygiene applies.

### 4. ENRICH

Tighten each draft to the team format: WHAT not HOW, ASCII diagrams, de-dup (each fact once),
story-point justification with the per-driver MAX. The enriched body IS the exact Azure description.
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
```

- [ ] **Step 2: Validate frontmatter parses as YAML**

Run:

```bash
cd ~/Documents/Projects/Personal/agile-workflow-marketplace
python3 -c "
import sys
t=open('agile-workflow/skills/decompose-backlog/SKILL.md').read()
assert t.startswith('---'), 'no frontmatter'
fm=t.split('---',2)[1]
try:
    import yaml; d=yaml.safe_load(fm); print('YAML OK; name=',d['name'])
except ImportError:
    assert 'name: decompose-backlog' in fm; print('yaml module absent; name line present')
"
```

Expected: `YAML OK; name= decompose-backlog` (or the fallback line).

- [ ] **Step 3: Assert every reference file named in SKILL.md exists**

Run:

```bash
cd ~/Documents/Projects/Personal/agile-workflow-marketplace
d=agile-workflow/skills/decompose-backlog
for ref in decomposition-rules ticket-structure azure-mechanics audit-checklist; do
  grep -qF "$ref.md" "$d/SKILL.md" && test -f "$d/references/$ref.md" \
    && echo "OK $ref" || { echo "BROKEN REF $ref"; exit 1; }
done
```

Expected: four `OK` lines — every reference mentioned resolves to a file.

- [ ] **Step 4: Assert the 7 phases and 2 gates are present**

Run:

```bash
cd ~/Documents/Projects/Personal/agile-workflow-marketplace
f=agile-workflow/skills/decompose-backlog/SKILL.md
for p in INGEST DECOMPOSE DRAFT ENRICH CREATE VERIFY AUDIT "GATE 1" "GATE 2"; do
  grep -qF "$p" "$f" && echo "OK $p" || { echo "MISSING $p"; exit 1; }
done
```

Expected: nine `OK` lines.

- [ ] **Step 5: Commit**

```bash
cd ~/Documents/Projects/Personal/agile-workflow-marketplace
git add agile-workflow/skills/decompose-backlog/SKILL.md
git commit -m "feat: add decompose-backlog SKILL.md conductor (7 phases, 2 gates)"
```

---

## Task 8: README + final repo validation

**Files:**

- Create: `README.md`

- [ ] **Step 1: Write the README**

Create `README.md`:

```markdown
# agile-workflow-marketplace

A standalone Claude Code plugin marketplace for Agile backlog workflows against Azure DevOps.

## Install
```

/plugin marketplace add <path-or-git-url-to-this-repo>
/plugin install agile-workflow

```

## Plugin: `agile-workflow`

### Skill: `decompose-backlog`

Takes a parent work item (Epic or Feature) and drives seven phases to produce correctly-parented,
audited child Stories in Azure DevOps:

1. **Ingest** the parent (verbatim text, acceptance criteria, parent chain).
2. **Decompose** into right-sized Stories (1 Story = 1 sprint = 1 PR). — *approval gate*
3. **Draft** each Story in the vault (hook-valid).
4. **Enrich** to the team format (ASCII diagrams, de-duped, story points). — *approval gate*
5. **Create** in Azure DevOps, parented to the **Feature** (explicit link type).
6. **Verify** the Epic→Feature→Story hierarchy structurally.
7. **Audit** that every parent requirement maps to a Story (coverage report).

Self-contained: carries its own decomposition rules and Azure linking guardrails (the two linking
gotchas: always pass explicit link `type`; a Story's parent is its Feature, never the Epic).

Trigger: "decompose Feature N", "break this into stories", or supply a Feature/Epic id.

See `docs/design.md` for the full design and `docs/plans/` for the implementation plan.
```

- [ ] **Step 2: Full-repo validation — all JSON valid, all skill files present**

Run:

```bash
cd ~/Documents/Projects/Personal/agile-workflow-marketplace
python3 -m json.tool .claude-plugin/marketplace.json > /dev/null && \
python3 -m json.tool agile-workflow/.claude-plugin/plugin.json > /dev/null && \
test -f agile-workflow/skills/decompose-backlog/SKILL.md && \
ls agile-workflow/skills/decompose-backlog/references/*.md | wc -l
```

Expected: prints `4` (four reference files), no JSON errors.

- [ ] **Step 3: Assert the marketplace `source` dir actually contains a plugin manifest**

Run:

```bash
cd ~/Documents/Projects/Personal/agile-workflow-marketplace
src=$(python3 -c "import json;print(json.load(open('.claude-plugin/marketplace.json'))['plugins'][0]['source'])")
test -f "$src/.claude-plugin/plugin.json" && echo "SOURCE OK: $src"
```

Expected: `SOURCE OK: ./agile-workflow`

- [ ] **Step 4: Commit**

```bash
cd ~/Documents/Projects/Personal/agile-workflow-marketplace
git add README.md
git commit -m "docs: add marketplace README"
```

---

## Task 9: Live install smoke test (manual gate)

**Files:** none — this is an environment validation.

- [ ] **Step 1: Add the marketplace locally**

In Claude Code:

```
/plugin marketplace add ~/Documents/Projects/Personal/agile-workflow-marketplace
```

Expected: marketplace `agile-workflow-marketplace` registers, listing one plugin `agile-workflow`.

- [ ] **Step 2: Install the plugin**

```
/plugin install agile-workflow
```

Expected: install succeeds; no manifest errors.

- [ ] **Step 3: Confirm the skill is discoverable**

Expected: `decompose-backlog` appears in the skill list. (It has `disable-model-invocation: true`, so
it is user-invoked, matching spike-workflow's pattern.)

- [ ] **Step 4: Tag the release**

```bash
cd ~/Documents/Projects/Personal/agile-workflow-marketplace
git tag v0.1.0
git log --oneline
```

Expected: clean linear history of the commits above; `v0.1.0` tag on the tip.

---

## Self-Review

**Spec coverage** (design.md → tasks):

- Purpose / self-contained rules → Tasks 4–6 (references), Task 7 (conductor). ✓
- 7 phases + 2 gates → Task 7 SKILL.md, asserted in Task 7 Step 4. ✓
- Guardrails (both linking gotchas, hook constraints, rendering, hygiene) → Task 5 + Task 6, asserted. ✓
- Inputs/outputs + Epic/Feature branch → Task 7 INGEST + decomposition-rules.md (Task 4). ✓
- AUDIT (fidelity/coverage/DoR, fresh retrieval) → Task 6 audit-checklist.md + Task 7 phase 7. ✓
- Packaging (marketplace mirror of spike-workflow) → Tasks 1–3, 8; install gate Task 9. ✓
- Portability note (configurable seams) → encoded in references as "default/seam" wording (Tasks 4,5). ✓

**Placeholder scan:** no TBD/TODO left as plan instructions; the only `@TODO` is _content of a rule_
(how to annotate unresolved ticket choices), which is intended. ✓

**Type/name consistency:** plugin name `agile-workflow`, skill `decompose-backlog`, four reference
filenames, and the MCP tool names (`wit_create_work_item`, `wit_work_items_link`,
`wit_work_item_unlink`, `wit_get_work_item`) are identical across marketplace.json, plugin.json,
SKILL.md `allowed-tools`, and the validation greps. ✓

**Note on validation medium:** there is no runtime under test, so steps use JSON-parse + structural
grep + a live `/plugin install` gate instead of unit tests — appropriate for a markdown/manifest
deliverable.

```

```
