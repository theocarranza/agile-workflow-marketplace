# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `./install.sh` interactive installer: wires Claude Code, Cursor, Codex, and Antigravity plugins;
  Azure DevOps MCP, orchestrator MCP, global CLI, project mailbox, and vault mistakes repo.
  Auto-detects installed agent hosts; prompts only for Azure org, project path, and vault folder.

## [0.4.0] - 2026-07-02

### Added

- **Deterministic orchestrator** (`agile-workflow/orchestrator_core/`): event-sourced runtime
  with rule-based Actor-Critic validation, circuit breaker (3 retries), and
  `IMPLEMENTATION APPROVED` recovery gate. See [docs/orchestrator.md](docs/orchestrator.md).
- **`bin/agile-workflow` CLI**: `init`, `validate`, `evaluate`, `compile`, `resume`, `mcp`.
- **Filesystem mailbox** (`.agentic/workflow_prompts/`): harness-agnostic prompts and error logs
  for `correcao` resume after quality-gate failures.
- **Mistakes repo** (`AI_Codex_AgileWorkflowMarketplace/_mistakes/mistakes.json`): persists
  circuit-breaker flaws for cross-session avoidance.
- Skill **manifests** for `validate-artifact` and `auto-fix-artifact` (MCP input/output schemas).
- Unit tests (`test/test_orchestrator.py`, `test/test_stream.py`).

### Changed

- `validate-artifact` and `auto-fix-artifact` SKILL.md now prefer the Python critic over
  LLM self-judgment for validation.
- Plugin version bumped to **0.4.0**.

## [0.3.0] - 2026-06-25

### Added

- `auto-fix-artifact` skill: validates a single agile artifact and offers an auto-fix workflow if issues are found. Applies fixes based on `validate-artifact` quality gates (e.g., adding missing sections, fixing titles, calculating story points, etc.). Accepts an Azure workitem ID, ledger document, filesystem reference, or pasted string.

## [0.2.0] - 2026-06-25

### Added

- `validate-artifact` skill: non-mutating quality gate for a single Epic, Feature, or User Story.
  Accepts vault draft path or Azure work item ID. Runs four check categories (STRUCTURAL,
  HIERARCHY, CONTENT, DoR) non-blocking and emits a terminal report + vault note in
  `Agent_Reports/`.
- `split-story` skill: lateral story-sizing conductor (5 phases, 2 gates). Takes a single User
  Story from any of four input sources (vault draft, Azure ID, file system path, raw text),
  scores it with the 6-driver MAX heuristic, determines split pattern, drafts sub-stories with
  AC coverage validation, and hands off via a 3-option HANDOFF menu.

### Changed

- Promoted shared references from `decompose-backlog/references/` to `agile-workflow/references/`
  so all skills share one copy of `decomposition-rules.md`, `ticket-structure.md`,
  `azure-mechanics.md`, and `audit-checklist.md`.
- Updated `decompose-backlog/SKILL.md` reference paths from `./references/` to `../../references/`
  to point to the new shared location.

## [0.1.0] - 2026-06-25

### Added

- Standalone Claude Code plugin marketplace configuration.
- `agile-workflow` plugin with `decompose-backlog` skill (7 phases, 2 approval gates).
- Shared reference library: decomposition rules, ticket structure, Azure mechanics, audit checklist.
- Design documentation and implementation roadmap.
