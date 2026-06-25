---
type: feature
skill: validate-artifact
plugin: agile-workflow
shipped: 2026-06-25
---

# validate-artifact

Standalone quality gate that checks a single agile artifact (Epic, Feature, or User Story) against the full `agile-workflow` rule set. Complements [[decompose-backlog]] — where that skill audits only newly created Stories at the end of its flow, this skill is type-agnostic, source-agnostic, and invocable at any point in the artifact lifecycle.

## What it does

Accepts either a vault draft (file path) or a live Azure DevOps work item (ID). Runs all checks non-blocking — every check fires regardless of prior failures — and emits a terminal report plus a persisted vault note in `Agent_Reports/`.

## Phases

| Phase | What happens |
| --- | --- |
| INGEST | Reads the artifact from vault or Azure; detects type; normalizes into a unified record |
| VALIDATE | Runs four check categories (STRUCTURAL, HIERARCHY, CONTENT, DoR); collects all findings |
| REPORT | Prints findings grouped by category with PASS/FAIL/WARN/SKIP per check; summary line |
| PERSIST | Writes the report as a vault note to `Agent_Reports/` |

## Check categories

- **STRUCTURAL** — frontmatter compliance (type present, status absent, filename regex); required body sections per artifact type
- **HIERARCHY** — parent chain via Azure MCP (Story → Feature, Feature → Epic, Epic has no direct Story children); failures logged, validation continues
- **CONTENT** — story-point driver breakdown, Descrição Original traceability, hygiene (no machine paths, no placeholder prose)
- **DoR** — Definition of Ready: clear title, description present, story points set, linked to Feature

## Key design decisions

- **Non-blocking checks** — all checks run; the full finding set is collected before any output
- **Either source** — vault draft or Azure ID; hierarchy checks skip gracefully if no `azure_id` is present
- **Report only** — no mutations; never writes or links work items
- **One artifact per run** — YAGNI; no batch mode

## Files

```
agile-workflow/skills/validate-artifact/
├── SKILL.md                        ← conductor (4 phases, guardrails)
└── references/
    ├── validation-checks.md        ← full check catalog per type + category
    └── report-format.md            ← terminal output + vault note templates
```

Shared rules live at `agile-workflow/references/` and are read by both this skill and [[decompose-backlog]].

## Design spec

[[docs/superpowers/specs/2026-06-25-validate-artifact-design]]

## Related

- [[decompose-backlog]] — sibling skill; AUDIT phase (Phase 7) covers similar ground post-creation
- [[Agent_Sessions/2026-06-25-143000-validate-artifact-skill]] — session record for this feature's implementation
