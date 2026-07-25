# Atomic Task Decomposition and Persist

Reference for `generate-breakdown-work-items` PHASE 3 (decompose) and PHASE 4 (persist).
Requires a saved Implementation Plan from `./plan-generation.md` (`plan_path` on disk).

## Preflight

1. Assert `plan_path` exists and is non-empty. If not → STOP:
   `Implementation Plan not saved; refusing Task creation.`
2. Re-read the plan and the Story's verbatim `acceptance_criteria`.
3. Reuse intake `destination` and `language`. Do not re-prompt unless a value is incomplete
   `other:…`.

## Atomic-commit definition

Each AC-derived Task must be:

- **Atomic** — one self-contained change to the project
- **Testable** — can be verified with a unit test (or an equally narrow automated check)
- **Scoped** — maps to a single delivery step from the Implementation Plan (or a clear sub-step)

Do not merge unrelated plan steps into one Task. Do not invent scope beyond the plan / ACs.

## Task list construction (PHASE 3)

Build an ordered list:

1. **AC / plan Tasks** — one Task per atomic plan step that delivers AC coverage  
2. **Staging** — always append (default)  
3. **Review** — always append (default)  
4. **Breakdown** — always last (default)

### Default Tasks

| Title | Required | Notes |
| --- | --- | --- |
| Staging | yes | Prepare/verify environment or staging for the Story's delivery |
| Review | yes | Review the Story's delivered work against acceptance criteria |
| Breakdown | yes (last) | Signals breakdown complete; see Breakdown rules below |

Titles may be localized when `language` is `pt-BR` (e.g. `Staging` / `Review` / `Breakdown` kept as
proper names, or host-preferred equivalents — stay consistent within a run). Descriptions follow
`language`.

### Breakdown rules

- Title: `Breakdown` (or localized equivalent; keep recognizable)
- **Assignee** = User Story assignee (`System.AssignedTo` on Azure; vault metadata if present).
  If the Story has no assignee → leave unassigned and note in the run summary; still set Done.
- **State** = Done (Azure: set `System.State` to the project's Done/Closed equivalent for Task;
  vault: mark status Done in the draft body/frontmatter convention used for Tasks)
- Always the **last** Task in the list

### Variant selection UX

Before persisting, present the proposed Task titles as a **variant multi-select** list
(see `./intake-ux.md`):

- Include `all` (Recommended when the full set is the default judgment)
- Include every proposed Task title
- End with `other (inform or describe)`

Wait for selection. If the user deselects Staging, Review, or Breakdown → WARN and re-add them
unless they explicitly confirm omission (defaults are mandatory per Feature ACs; prefer STOP and
re-prompt over silently dropping them).

---

## Persist (PHASE 4)

Write only the selected Tasks to intake `destination`.

### Filesystem / ledger

When `destination` is `filesystem` or `both`:

1. Write one markdown draft per Task under the vault (prefer `Tickets/Ready/` or a host Task folder).
2. Filename pattern per `../../references/ticket-structure.md`:
   `task-<kebab-title>` is invalid as a bare prefix — use `task-<slug>` only if the host regex
   allows `task-`; otherwise `<story-id-or-0000>-task-<slug>.md` matching
   `^(\d+|tech-debt|bug|task|spike)-[a-z0-9-]+`.
3. Frontmatter: `type: ticket`, `work_item_type: Task`, parent Story ref, `language`, no `status:`
   key in Tickets/ (lifecycle note for Breakdown Done can live in the body: `State: Done`).
4. Body: title heading + short description (WHAT for this atomic unit) + link/ref to `plan_path`
   and parent Story.

### Azure Task board

When `destination` is `azure` or `both`:

1. Parent must be the **User Story** id (never Feature/Epic).
2. Prefer `wit_add_child_work_items` with `workItemType: "Task"`, `parentId: <storyId>`,
   `items: [{ title, description, format: "Markdown" }, …]` for the AC/plan + Staging + Review
   batch when possible.
3. For **Breakdown** (or any Task needing assignee/state): create as child, then
   `wit_update_work_item` to set:
   - `/fields/System.AssignedTo` → Story assignee (when present)
   - `/fields/System.State` → Done (or project-specific completed state for Task)
4. Alternative: `wit_create_work_item` + `wit_work_items_link` with **`type: "parent"`**
   (Story is parent of Task). Never omit `type` (defaults to Related).
5. **Read-back** every created Task: assert parent is the Story id; for Breakdown assert Done and
   assignee match. Failed assertion → STOP.

### Shared Azure notes

Extend behavior from `../../references/azure-mechanics.md`. Parent of a Task is the **User Story**,
not the Feature. Description format: Markdown.

---

## Run summary

After persist, report:

- `plan_path`
- Task titles + destinations (vault paths and/or Azure ids)
- Breakdown assignee + state
- Any skipped `other:…` follow-ups still open
