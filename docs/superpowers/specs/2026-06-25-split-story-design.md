# Design — `split-story` skill (`agile-workflow` plugin)

## Purpose

A lateral sizing skill that takes a single User Story and determines whether it should be
split, how many sub-stories it should become, and what split pattern to use — then drafts the
sub-stories and hands them off. It operates at the Story-to-Story level, complementing
`decompose-backlog` (Feature → Stories) and `validate-artifact` (quality gate on any artifact).

## Scope

**In:**

- Vault draft (file path), live Azure work item (ID), arbitrary file system path, or raw text pasted inline as input
- Point calculation using the 6-driver MAX heuristic (Escopo, Incerteza, Integrações, Dados, QA, Rollout)
- Discrepancy detection: if declared points differ from calculated, flag and ask user which to trust
- Spike detection: if Incerteza is the dominant driver, recommend a Spike instead of a scope split
- Auto-selection of split pattern from a defined catalog
- Approval gate before drafting
- Coverage check: sub-stories must collectively cover all original acceptance criteria
- Handoff menu: keep drafts / create in Azure / discard

**Out:**

- Splitting Epics or Features (Story level only)
- Batch processing multiple stories per run
- Sprint planning or velocity tracking
- Auto-selecting iteration/sprint for sub-stories

## Classification

A **process skill** — rigid on the scoring heuristic, the coverage assertion, and the Azure
linking mechanics; flexible on judgment calls within pattern detection and story wording.

## Phases

The skill is a conductor over five ordered phases. Two hard gates protect the vault and Azure
from unapproved writes.

```text
1. INGEST     Determine source from the argument:
                vault draft      → read the markdown file; parse frontmatter + body.
                Azure ID         → fetch via wit_get_work_item (expand relations).
                file system path → read the file from disk; parse as markdown.
                raw text         → use the pasted content directly.
              Normalize into a unified artifact record:
                { title, body, story_points, acceptance_criteria,
                  parent_feature, azure_id, source }
              If story_points absent: mark as "not declared."

2. SCORE      Apply 6-driver MAX heuristic per decomposition-rules.md.
              Score each driver 1/2/3/5; calculated_points = MAX across all drivers.
              Record per-driver scores for display.

              If story_points declared:
                Compare declared vs. calculated.
                If they agree: proceed with declared value.
                If they differ: STOP. Show both values with full driver breakdown.
                  Ask: "Use declared (<X> pts) or calculated (<Y> pts)?"
                  Wait for user choice. Proceed with chosen value.

              active_points = user-chosen or calculated value.

3. ANALYZE    Branch A — No split needed:
                If active_points ≤ ceiling (default 5, overridable):
                  Report "story is right-sized" with score breakdown. Stop.
                  No vault files written.

              Branch B — Spike recommended:
                If Incerteza driver == 5 AND is the sole MAX driver:
                  Present spike rationale (uncertainty dominates; splitting scope
                  doesn't reduce risk — investigation does).
                  Ask user to confirm before drafting a Spike stub.

              Branch C — Split:
                split_count = ceil(active_points / ceiling).
                Auto-select split pattern from split-patterns.md:
                  - Workflow step     — sequential steps detected in body or AC
                  - Business rule     — multiple distinct rules/conditions in AC
                  - Happy/unhappy path — success + error/edge flows present
                  - CRUD operation    — create/read/update/delete operations present
                  - Data variation    — different entity types or input variations

                Show pattern reasoning: one sentence per candidate pattern
                considered; one winner with justification.

              ── GATE 1: present split plan to user ──
                - Pattern chosen and why
                - Number of sub-stories
                - Proposed title + one-line scope per sub-story
                - Estimated point value per sub-story
                WAIT for explicit approval before drafting.

4. DRAFT      Per approved sub-story, write a vault draft to Tickets/Ready/
              following ticket-structure.md:
                - Hook-valid frontmatter: type present, status absent,
                  filename regex with parent Feature id prefix.
                - All 7 body sections: O quê / Por quê / Comportamento esperado /
                  Critérios de Aceite / Notas Técnicas / Complexidade /
                  Descrição Original.
                - Descrição Original traces to the exact slice of the original
                  story's AC that this sub-story covers.

              Coverage check (before reporting done):
                - Every AC item in the original story must appear in exactly
                  one sub-story's Descrição Original.
                - Flag orphan AC (in original, in no sub-story) → dropped requirement.
                - Flag duplicate coverage (in two or more sub-stories) → ambiguous scope.
                - Any gap or duplicate STOPS and reports — no silent patching.

5. HANDOFF    Present drafted sub-stories summary (title + point estimate per sub-story).
              Show options:
                1. Keep as vault drafts — done; user continues manually or
                   via decompose-backlog's ENRICH/CREATE/VERIFY phases.
                2. Create in Azure and link to parent Feature — calls
                   wit_create_work_item (Markdown description) then
                   wit_work_items_link (explicit type=parent to Feature id)
                   per azure-mechanics.md; reads back each item to assert
                   System.Parent == feature_id. A failed assertion stops the run.
                3. Discard drafts — delete vault files, stop.
```

## Shared references (plugin level)

Read from `../../references/` — not duplicated in this skill:

- `decomposition-rules.md` — 6-driver MAX heuristic, story-point ceiling, DoR, hierarchy rules
- `ticket-structure.md` — body sections, frontmatter constraints, content hygiene
- `azure-mechanics.md` — MCP calls, linking gotchas, rendering rules

## Skill-specific references

New files under `./references/`:

- `split-patterns.md` — catalog of split patterns with detection signals and example applications
- `scoring-guide.md` — 6-driver scoring table, ceiling logic, spike detection rule, discrepancy handling

## Inputs / outputs

### Inputs

- Required: one of — vault draft path, Azure work item ID, file system path, or raw text pasted inline
- Optional: story-point ceiling override (default 5)
- Implicit context: Azure project + repo; vault `Tickets/Ready/` location

### Outputs

1. Score report — driver breakdown, calculated vs. declared (if applicable), active points used
2. Split plan — pattern, reasoning, count, titles + scope (shown at Gate 1)
3. Vault drafts in `Tickets/Ready/` — hook-valid, all 7 sections, coverage-verified
4. Azure work items (HANDOFF option 2) — created, linked to Feature, hierarchy verified

## Relationship to sibling skills

| Dimension      | `decompose-backlog`      | `validate-artifact`  | `split-story`            |
| -------------- | ------------------------ | -------------------- | ------------------------ |
| Direction      | Feature → Stories        | Any artifact, r/o    | Story → Stories          |
| Scoring        | DoR check only           | DoR check            | Full 6-driver calculation |
| Split patterns | N/A                      | N/A                  | Auto-detected            |
| Azure writes   | Yes (core flow)          | Never                | Optional (HANDOFF)       |
| Gates          | 2 (decompose, enrich)    | None                 | 2 (split plan, handoff)  |

## File layout

```text
agile-workflow/
├── references/                          ← shared (existing)
│   ├── decomposition-rules.md
│   ├── ticket-structure.md
│   ├── azure-mechanics.md
│   └── audit-checklist.md
└── skills/
    ├── decompose-backlog/SKILL.md
    ├── validate-artifact/...
    └── split-story/
        ├── SKILL.md                     ← conductor (5 phases, 2 gates)
        └── references/
            ├── split-patterns.md        ← pattern catalog with detection rules
            └── scoring-guide.md         ← driver table, ceiling, spike rule
```

## Non-goals / YAGNI

- No batch mode (one story per run).
- No auto-push without user choice at HANDOFF.
- No sprint/iteration assignment.
- No story-point *auto-accept* — discrepancies always surface to the user.
