# Design — `validate-artifact` skill (`agile-workflow` plugin)

## Purpose

A **standalone quality gate** that checks a single agile artifact (Epic, Feature, or User Story)
against the full rule set embedded in the `agile-workflow` plugin. It can be invoked at any point
in the artifact lifecycle — before creation, after enrichment, or as an ad-hoc audit — from either
a vault draft or a live Azure DevOps work item.

It is complementary to `decompose-backlog`: where that skill runs an audit only as its final phase
and only on newly created Stories, `validate-artifact` is type-agnostic, source-agnostic, and
invocable at any time.

## Scope

**In:**
- Validating vault drafts (by file path) and live Azure work items (by ID)
- All three artifact types: Epic, Feature, User Story
- Four check categories: structural, hierarchy, content quality, Definition of Ready
- Terminal report + persisted vault note

**Out:**
- Batch validation (one artifact per invocation)
- Auto-fixing findings — report only, no mutations to the artifact
- Sprint planning or estimation ceremony

## Classification

A **process skill** — rigid on which checks run and the report format, flexible on judgment calls
within content-quality checks (e.g., flagging potential hygiene issues as WARN rather than FAIL).

## Phases

The skill is a thin conductor over four ordered phases. All checks are non-blocking: a failure in
one check does not skip subsequent checks. The full finding set is collected before any output is
emitted.

```
1. INGEST     Determine source type from the invocation argument:
                vault draft  → read the markdown file; parse frontmatter + body sections.
                Azure ID     → fetch work item via wit_get_work_item MCP call.
              Detect artifact type from work_item_type (frontmatter) or Azure System.WorkItemType.
              Normalize into a unified artifact record:
                { type, title, body, story_points, parent_id, source, raw }
              → normalized artifact record.

2. VALIDATE   Run all four check categories. Each check emits { name, result, detail }.
              Results: PASS | FAIL | WARN. Failures do not halt sibling or subsequent checks.

              a) STRUCTURAL
                 Vault draft only:
                   - Frontmatter contains `type:` key                          (FAIL if absent)
                   - Frontmatter does NOT contain `status:` key                (FAIL if present)
                   - Filename matches regex ^(\d+|tech-debt|bug|task|spike)-[a-z0-9-]+
                                                                               (FAIL if no match)
                 All sources:
                   User Story → all 7 body sections present:
                     🎯 O quê / 💡 Por quê / 📋 Comportamento esperado /
                     ✅ Critérios de Aceite / 🔧 Notas Técnicas /
                     📊 Complexidade / 📄 Descrição Original               (FAIL per missing section)
                   Feature / Epic → title and non-empty description present    (FAIL if absent)

              b) HIERARCHY   (requires Azure MCP; failures logged, validation continues)
                 User Story  → parent must be a Feature (not an Epic, not missing)
                 Feature     → parent must be an Epic
                 Epic        → must have no direct Story children
                 Each assertion: fetch parent via wit_get_work_item, check WorkItemType field.

              c) CONTENT     (User Story only for points/traceability; hygiene applies to all)
                 - Complexidade section contains per-driver MAX breakdown      (FAIL if absent/empty)
                 - Story points field is set (> 0)                             (FAIL if unset)
                 - Descrição Original is non-empty                             (FAIL if empty)
                 - No machine-specific paths in body (heuristic: absolute path pattern scan)
                                                                               (WARN if found)
                 - No `status:` meta prose in body sections                    (WARN if found)

              d) DoR         (Definition of Ready — all artifact types)
                 □ Title states a clear objective (non-empty, > 5 words)       (FAIL if not met)
                 □ Detailed description present (non-empty body / description) (FAIL if not met)
                 □ Story points set (User Story only)                          (FAIL if not met)
                 □ Linked to a Feature (User Story only — hierarchy check result reused)

3. REPORT     Print findings to terminal:
                Header:  Validating <type> — "<title>" [<source>]
                Body:    grouped by category (STRUCTURAL / HIERARCHY / CONTENT / DoR)
                         each line:  [PASS|FAIL|WARN]  <check name>  —  <detail>
                Footer:  Summary — X passed, Y failed, Z warnings
                         Overall outcome: PASS (zero failures) | FAIL (≥1 failure)

4. PERSIST    Write report as a vault note:
                Path:      AI_Codex_AgileWorkflowMarketplace/Agent_Reports/
                Filename:  YYYY-MM-DD-validate-<artifact-id-or-slug>.md
                Frontmatter:
                  ---
                  date: <YYYY-MM-DD>
                  type: report
                  artifact: <id or filename>
                  artifact_type: <Epic|Feature|User Story>
                  source: <vault|azure>
                  outcome: <pass|fail>
                  ---
                Body: the same report printed in step 3, as markdown.
```

## Shared references (plugin level)

Rules are maintained once at the plugin level and read by both skills. They are not duplicated
inside `validate-artifact/references/` — only skill-specific reference files live there.

```
agile-workflow/
├── references/                         ← shared, single source of truth
│   ├── decomposition-rules.md          ← hierarchy, DoR, sizing, story-point heuristic
│   ├── ticket-structure.md             ← body sections, frontmatter constraints, hygiene
│   ├── azure-mechanics.md              ← MCP calls, linking gotchas, rendering rules
│   └── audit-checklist.md             ← fidelity, coverage, DoR check definitions
└── skills/
    ├── decompose-backlog/
    │   └── SKILL.md                    ← updated paths: ../../references/
    └── validate-artifact/
        ├── SKILL.md                    ← references ../../references/ + ./references/
        └── references/
            ├── validation-checks.md    ← full check catalog per artifact type + category
            └── report-format.md        ← terminal output template + vault note template
```

**Portability:** when extracting a skill for standalone distribution, a packaging step copies the
relevant shared reference files into the skill's `references/` directory. The skill itself does not
change.

## Inputs / outputs

**Inputs**
- Required: one of — a vault draft file path OR an Azure work item ID
- Implicit context: Azure project + repo; vault `Agent_Reports/` location

**Outputs**
1. Terminal report — findings grouped by category, overall outcome line
2. Vault note — `Agent_Reports/YYYY-MM-DD-validate-<id>.md`, frontmatter-valid

## Relationship to `decompose-backlog`

| Dimension          | `decompose-backlog`                   | `validate-artifact`             |
|--------------------|---------------------------------------|---------------------------------|
| Artifact types     | User Story only                       | Epic, Feature, User Story       |
| When it runs       | Phase 7, after Azure creation         | Any time, any lifecycle stage   |
| Source             | Azure (reads back created items)      | Vault draft or Azure ID         |
| Mutations          | Creates + links work items            | None — report only              |
| Hierarchy check    | Asserts Story → Feature post-create   | Validates all three levels      |

## Non-goals / YAGNI

- No batch mode (multiple artifacts per run).
- No auto-fix — findings are reported, not corrected.
- No severity tiers (ERROR / WARNING / INFO distinction beyond FAIL / WARN) — can be added later.
- No CI integration.
