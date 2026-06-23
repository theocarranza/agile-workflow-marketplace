# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-06-03

### Added
- Standalone Claude Code plugin marketplace configuration ([marketplace.json](file:///.claude-plugin/marketplace.json)).
- `agile-workflow` plugin directory with manifest listing ([plugin.json](file:///agile-workflow/.claude-plugin/plugin.json)).
- `decompose-backlog` skill with a structured conductor ([SKILL.md](file:///agile-workflow/skills/decompose-backlog/SKILL.md)) outlining the 7 agile decomposition phases and 2 approval gates (INGEST, DECOMPOSE, DRAFT, ENRICH, CREATE, VERIFY, AUDIT).
- Self-contained reference guides for backlog decomposition:
  - [decomposition-rules.md](file:///agile-workflow/skills/decompose-backlog/references/decomposition-rules.md): rules for sizing and story-point estimation.
  - [ticket-structure.md](file:///agile-workflow/skills/decompose-backlog/references/ticket-structure.md): rules for drafting stories, frontmatter schemas, and vault hook validation constraints.
  - [azure-mechanics.md](file:///agile-workflow/skills/decompose-backlog/references/azure-mechanics.md): guides for creating and linking work items in Azure DevOps.
  - [audit-checklist.md](file:///agile-workflow/skills/decompose-backlog/references/audit-checklist.md): coverage checking and audit rules.
- Design documentation ([design.md](file:///docs/design.md)) and implementation roadmap ([2026-06-03-decompose-backlog.md](file:///docs/plans/2026-06-03-decompose-backlog.md)).
- Project [README.md](file:///README.md) with installation instructions and plugin overview.
