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
