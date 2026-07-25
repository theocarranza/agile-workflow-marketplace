---
type: implementation-plan
feature: Features/generate-breakdown-work-items.md
skill: generate-breakdown-work-items
plugin: agile-workflow
status: active
created: 2026-07-25
branch_feature: feature/generate-breakdown-work-items
branch_base: main
---

# Implementation Plan — Generate Breakdown Work Items

> **For agentic workers:** Follow `feature-implementation` Phase 5 stacked workflow. One Feature integration branch; one short-lived Story branch each. Story PRs target the Feature branch only.

**Goal:** Ship the `generate-breakdown-work-items` skill so a team can turn a User Story's acceptance criteria into an Implementation Plan (ledger) plus atomic child Tasks (ledger and/or Azure), with Staging/Review/Breakdown conventions and Feature/Epic fan-out.

**Architecture:** New skill under `agile-workflow/skills/generate-breakdown-work-items/` — conductor `SKILL.md` plus skill-specific references. Reuse shared `agile-workflow/references/` (azure-mechanics, ticket-structure, decomposition-rules hierarchy). Register in plugin manifests, `skills.sh.json`, root `skills/` symlink, README/CHANGELOG as needed. No target-product application code — skill/markdown/plugin wiring only.

**Tech stack:** Markdown conductors + references; Azure DevOps MCP (`wit_get_work_item`, `wit_create_work_item` / `wit_add_child_work_items`, `wit_update_work_item`, `wit_work_items_link`); AI Codex vault (`Implementation_Plans/`, Tickets drafts).

## Confirmed conventions (Phase 0)

| Item | Value |
| --- | --- |
| Main work branch | `main` |
| Feature integration branch | `feature/generate-breakdown-work-items` |
| Story branch pattern | `feature/<nnn>-<kebab-description>` (always `feature/` for feature work) |
| US1 branch | `feature/001-intake-selection-ux` |
| US2 branch | `feature/002-implementation-plan-generation` |
| US3 branch | `feature/003-atomic-task-decomposition` |
| US4 branch | `feature/004-feature-epic-fanout` |

## Global constraints

- Do **not** invent or rewrite User Story acceptance criteria.
- Do **not** estimate story points at Feature level inside this skill.
- Implementation Plan **must** be saved to the vault **before** any Task is created.
- Default Tasks on every Story run: **Staging**, **Review**, then **Breakdown** last (assignee = Story assignee, state = Done).
- Language: `en` (default) or `pt-BR`.
- Destinations: filesystem/ledger, Azure Task board, or both.
- Selection UX: invariants/variants as selectable lists; variants include `all`; last option always `other (inform or describe)`; judgment calls put `Recommended` on the **first** option.
- Azure parent links: always `type: "parent"`; Task parent = User Story (not Feature).
- After Azure create/link: read-back assert parent and state.
- Shared references stay in `agile-workflow/references/` — never duplicate into the skill.
- Skill frontmatter: `name`, `description`, `allowed-tools`, `metadata.plugin`, version bump with release.

## File map (target)

| File | Stories | Responsibility |
| --- | --- | --- |
| `agile-workflow/skills/generate-breakdown-work-items/SKILL.md` | US1–US4 | Conductor: intake → plan → tasks → fan-out |
| `…/references/intake-ux.md` | US1 | Prompt order, invariant/variant lists, `all` / `other` / `Recommended` rules |
| `…/references/plan-generation.md` | US2 | Read Feature+Story, AC coverage, ledger path/naming for Implementation Plans |
| `…/references/atomic-tasks.md` | US3 | Atomic-commit task rules; Staging/Review/Breakdown; destination writers |
| `…/references/fan-out.md` | US4 | Feature/Epic child discovery; per-Story loop; failure isolation |
| `…/manifest.json` | US1+ | Skill manifest (match sibling skills) |
| `skills/generate-breakdown-work-items` → symlink | US1 or finalize | skills.sh / openskills discovery |
| `skills.sh.json`, plugin.json ×2, marketplace.json ×2 | finalize / US1 | Registry + descriptions |
| `README.md`, `CHANGELOG.md` | finalize | Document skill + version |

---

## Phase 5.0 — Feature branch setup

- [ ] Confirm worktree clean **or** approved safeguard for dirty Obsidian files
- [ ] `git fetch origin`
- [ ] Create `feature/generate-breakdown-work-items` from `origin/main`
- [ ] Push Feature branch with `-u`

---

## US1 — Intake and Selection UX (3 pts)

**Branch:** `feature/001-intake-selection-ux` off Feature  
**PR target:** `feature/generate-breakdown-work-items`

### Approach

Scaffold the skill directory and implement **PHASE 0 — INTAKE** only: collect work-item ref, destination, language; encode selection UX rules in `intake-ux.md`; stub later phases as "not yet implemented" gates so the skill is valid but incomplete until US2–US4 land.

### Tasks

- [ ] Create skill folder + `manifest.json` + stub `SKILL.md` skeleton (phases listed; only intake executable)
- [ ] Author `references/intake-ux.md` with:
  - Prompt sequence: work-item ID | URL | ledger path → destination → language
  - Invariant destination list: filesystem/ledger, Azure Task board, both, `other (inform or describe)`
  - Language list: `en` (default when omitted), `pt-BR`, `other…`
  - Variant multi-select rules (`all`, trailing `other…`)
  - `Recommended` tag rules (first option when judgment required)
- [ ] Wire intake phase in `SKILL.md` to STOP until selections confirmed; no Ledger/Azure writes
- [ ] Add root symlink + minimal registry entry if needed for local discovery (or defer full registry to Feature finalize — prefer register name early)
- [ ] Smoke: `./scripts/validate-skills.sh` includes / passes new skill if registered

### Git stages

1. Checkout Feature; pull latest  
2. Branch `feature/001-intake-selection-ux`  
3. Implement → commit → push  
4. Re-sync Feature into Story → push  
5. PR Story → Feature → merge  

### Acceptance mapping

| AC | Covered by |
| --- | --- |
| Prompt when no work-item ref | Intake phase gate |
| Destination selectable list + `other` | `intake-ux.md` + SKILL |
| Language defaults to `en` | Intake normalize |
| Lists end with `other…` | UX rules |
| `all` on variant multi-select | UX rules |
| `Recommended` on first judgment option | UX rules |

---

## US2 — Implementation Plan Generation (3 pts)

**Branch:** `feature/002-implementation-plan-generation` off Feature  
**PR target:** Feature

### Approach

Add **PHASE 1 — INGEST** (read Feature + Story) and **PHASE 2 — PLAN** (AC analysis → write `Implementation_Plans/` before any Task). Depends on US1 selections (ref + language).

### Tasks

- [ ] Author `references/plan-generation.md`:
  - Resolve parent Feature from Story relations or vault `parent_feature_vault`
  - Require AC list present; STOP if missing (do not invent ACs)
  - Plan must address **every** AC entry
  - Ledger path: `<vault>/Implementation_Plans/YYYY-MM-DD-<story-slug>.md` (or id-prefixed)
  - Frontmatter: `type: implementation-plan`, source story/feature refs, language, status
- [ ] Implement ingest + plan phases in `SKILL.md`
- [ ] Explicit guard: refuse Task creation until plan file exists on disk
- [ ] Optional: example plan shape / checklist template in references

### Git stages

Same Story→Feature loop as US1 (always re-sync Feature before PR).

### Acceptance mapping

| AC | Covered by |
| --- | --- |
| Read Feature + Story before plan | PHASE 1 |
| Plan addresses every AC | plan-generation rules |
| Plan saved to Ledger | write to Implementation_Plans/ |
| No Task before plan saved | hard stop guard |

---

## US3 — Atomic Task Decomposition and Attachment (5 pts)

**Branch:** `feature/003-atomic-task-decomposition` off Feature  
**PR target:** Feature

### Approach

Add **PHASE 3 — DECOMPOSE** and **PHASE 4 — PERSIST**: split saved plan into atomic Tasks; always append Staging + Review; append Breakdown (assignee = Story assignee, Done); write to ledger and/or Azure per destination.

### Tasks

- [ ] Author `references/atomic-tasks.md`:
  - Atomic-commit definition (one self-contained, unit-testable change)
  - Ordering: AC-derived tasks → Staging → Review → Breakdown (last)
  - Breakdown: copy Story `System.AssignedTo`; set state Done
  - Destination writers: vault Task drafts under Tickets (or skill-defined path) vs Azure `Task` children
  - Azure: create Task, link `type: "parent"` to Story, update state/assignee; read-back asserts
- [ ] Extend `azure-mechanics.md` (shared) **only if** Task create/state patterns are missing — prefer skill-local first, promote shared invariants if reusable
- [ ] Implement PHASE 3–4 in `SKILL.md` with destination branching
- [ ] Variant UX: present proposed Task list for multi-select (`all` / `other…`) before persist when judgment required
- [ ] Language: Task titles/bodies honor intake language

### Git stages

Same Story→Feature loop.

### Acceptance mapping

| AC | Covered by |
| --- | --- |
| Atomic, testable tasks | atomic-tasks rules |
| Staging + Review always | default append |
| Breakdown last, assignee, Done | Breakdown rules + Azure/ledger write |
| Children of User Story | parent link / vault parent ref |
| Destination(s) honored | persist branching |

---

## US4 — Feature / Epic Fan-out (3 pts)

**Branch:** `feature/004-feature-epic-fanout` off Feature  
**PR target:** Feature

### Approach

Add **PHASE 0 branch** when input is Feature/Epic: enumerate child User Stories, then run US2+US3 workflow per child using intake destination/language. Isolate failures so one Story error does not silently skip the rest.

### Tasks

- [ ] Author `references/fan-out.md`:
  - Resolve children via Azure relations or vault `parent_feature_vault` index
  - Epic: Stories under child Features (do not attach Tasks to Epic)
  - Ordered processing; per-Story success/failure report
  - On failure: record error, continue remaining Stories (no silent skip)
  - Reuse destination + language from intake (do not re-prompt unless `other` incomplete)
- [ ] Wire fan-out orchestration in `SKILL.md`
- [ ] Ensure intake accepts Feature/Epic refs (US1 already allows; confirm resolution paths)

### Git stages

Same Story→Feature loop.

### Acceptance mapping

| AC | Covered by |
| --- | --- |
| Identify all child Stories first | fan-out ingest |
| Full workflow per child | loop invokes plan + tasks |
| Failure does not silently skip others | continue + report |
| Reuse destination + language | intake context pass-through |

---

## Phase 5.2 — Feature finalize

- [ ] On Feature branch: complete registry (plugin.json ×2, marketplace.json ×2, skills.sh.json Backlog group, README, CHANGELOG, version bump if releasing)
- [ ] Catalog card / Knowledge update if repo convention requires
- [ ] `./scripts/validate-skills.sh` green
- [ ] Push Feature; open PR **Feature → `main`**
- [ ] Review → merge

## Delivery order rationale

US1 scaffolds intake + skill shell → US2 adds plan persistence (prerequisite for tasks) → US3 adds Task writers (highest integration risk) → US4 composes the prior workflow for parents.

## Out of scope (do not implement)

- Rewriting Story ACs  
- Feature-level story-point estimation  
- Implementing the product under breakdown (only plan + work items)
