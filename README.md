# agile-workflow-marketplace

A standalone Claude Code plugin marketplace for Agile backlog workflows against Azure DevOps.

## Install

```text
/plugin marketplace add <path-or-git-url-to-this-repo>
/plugin install agile-workflow
```

## Plugin: `agile-workflow`

### Skill: `decompose-backlog`

Takes a parent work item (Epic or Feature) and drives seven phases to produce correctly-parented,
audited child Stories in Azure DevOps:

1. **Ingest** the parent (verbatim text, acceptance criteria, parent chain).
2. **Decompose** into right-sized Stories (1 Story = 1 sprint = 1 PR). — _approval gate_
3. **Draft** each Story in the vault (hook-valid).
4. **Enrich** to the team format (ASCII diagrams, de-duped, story points). — _approval gate_
5. **Create** in Azure DevOps, parented to the **Feature** (explicit link type).
6. **Verify** the Epic→Feature→Story hierarchy structurally.
7. **Audit** that every parent requirement maps to a Story (coverage report).

Self-contained: carries its own decomposition rules and Azure linking guardrails (the two linking
gotchas: always pass explicit link `type`; a Story's parent is its Feature, never the Epic).

Trigger: "decompose Feature N", "break this into stories", or supply a Feature/Epic id.

See `docs/design.md` for the full design and `docs/plans/` for the implementation plan.

### Skill: `validate-artifact`

Quality gate for a single agile artifact (Epic, Feature, or User Story). Accepts a vault draft
path or live Azure DevOps work item ID. Runs all checks non-blocking and emits a terminal report
plus a persisted vault note. One artifact per invocation.

Four check categories:

1. **STRUCTURAL** — frontmatter keys, filename regex, required body sections.
2. **HIERARCHY** — parent chain validated against Azure (Story → Feature → Epic).
3. **CONTENT** — driver breakdown present, story points set, no machine paths or placeholder prose.
4. **DoR** (Definition of Ready) — title clarity, description present, points set, linked to Feature.

Trigger: "validate this story/feature/epic", "check this ticket", "is this artifact ready?", or
supply a vault path or Azure work item ID.

### Skill: `split-story`

Lateral story-sizing skill. Takes a single User Story and determines whether to split it, how
many sub-stories to produce, and which split pattern to apply — then drafts the sub-stories and
hands them off. One story per invocation.

Five phases with two approval gates:

1. **INGEST** — normalize from vault draft, Azure ID, file system path, or raw text pasted inline.
2. **SCORE** — apply the 6-driver MAX heuristic (Escopo, Incerteza, Integrações, Dados, QA,
   Rollout); flag declared vs. calculated discrepancy for user resolution.
3. **ANALYZE** — Branch A (right-sized → stop), Branch B (Incerteza sole MAX → recommend Spike),
   Branch C (split → auto-select pattern, present plan). _Approval gate before drafting._
4. **DRAFT** — write vault drafts; coverage check ensures every original AC maps to exactly one
   sub-story (orphans and duplicates stop the run).
5. **HANDOFF** — three options: keep as vault drafts / create in Azure and link to parent Feature /
   discard.

Split patterns auto-detected from catalog: Workflow Step, Business Rule, Happy/Unhappy Path,
CRUD Operation, Data Variation.

Trigger: "split this story", "is this story too big?", "analyze this story for sizing", or supply
a vault path / Azure ID / file path / raw text.

## Shared references

All skills share a common reference library at `agile-workflow/references/`:

| File | Purpose |
| --- | --- |
| `decomposition-rules.md` | 6-driver MAX heuristic, story-point ceiling, DoR, hierarchy rules |
| `ticket-structure.md` | Body sections, frontmatter constraints, content hygiene |
| `azure-mechanics.md` | MCP calls, linking gotchas, rendering rules |
| `audit-checklist.md` | Coverage checking and audit rules |
