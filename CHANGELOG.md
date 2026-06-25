# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-06-25

### Added

- `auto-fix-artifact` skill: validates a single agile artifact and offers an auto-fix workflow if issues are found. Applies fixes based on `validate-artifact` quality gates (e.g., adding missing sections, fixing titles, calculating story points, etc.). Accepts an Azure workitem ID, ledger document, filesystem reference, or pasted string.

## [0.2.0] - 2026-06-25

### Added

- `validate-artifact` skill: non-mutating quality gate for a single Epic, Feature, or User Story.
  Accepts vault draft path or Azure work item ID. Runs four check categories (STRUCTURAL,
  HIERARCHY, CONTENT, DoR) non-blocking and emits a terminal report + vault note in
  `Agent_Reports/`. See [2026-06-25-validate-artifact-design.md](file:///docs/superpowers/specs/2026-06-25-validate-artifact-design.md).
  - [validation-checks.md](file:///agile-workflow/skills/validate-artifact/references/validation-checks.md): full check catalog with PASS/FAIL/WARN/SKIP thresholds.
  - [report-format.md](file:///agile-workflow/skills/validate-artifact/references/report-format.md): terminal output template and vault note frontmatter template.
- `split-story` skill: lateral story-sizing conductor (5 phases, 2 gates). Takes a single User
  Story from any of four input sources (vault draft, Azure ID, file system path, raw text),
  scores it with the 6-driver MAX heuristic, determines split pattern, drafts sub-stories with
  AC coverage validation, and hands off via a 3-option HANDOFF menu.
  See [2026-06-25-split-story-design.md](file:///docs/superpowers/specs/2026-06-25-split-story-design.md).
  - [split-patterns.md](file:///agile-workflow/skills/split-story/references/split-patterns.md): catalog of 5 split patterns with detection signals and auto-selection decision tree.
  - [scoring-guide.md](file:///agile-workflow/skills/split-story/references/scoring-guide.md): 6-driver scoring table, ceiling logic (default 5 pts), spike detection rule, discrepancy-handling protocol.

### Changed

- Promoted shared references from `decompose-backlog/references/` to `agile-workflow/references/`
  so all skills share one copy of `decomposition-rules.md`, `ticket-structure.md`,
  `azure-mechanics.md`, and `audit-checklist.md`.
- Updated `decompose-backlog/SKILL.md` reference paths from `./references/` to `../../references/`
  to point to the new shared location.

## [0.1.0] - 2026-06-25

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
