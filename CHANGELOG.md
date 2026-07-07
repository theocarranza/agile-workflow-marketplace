# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.0] - 2026-07-07

### Added

- **`enrich-work-item` skill**: Standalone enrichment conductor (Epic / Feature / User Story) with
  type-specific enricher prompts, canonical shape examples, and Azure ingest (attachments plus
  description references). Complements `generate-work-item` after the generate/enrich split.
- **Canonical templates** (`references/canonical/` per skill): Read-only shape contracts wired
  into `SKILL.md` for `decompose-backlog`, `generate-work-item`, `enrich-work-item`,
  `split-story`, and `validate-artifact`.
- **`orchestrator_core/output_formats.py`**: Structural validators for raw ticket drafts,
  spikes, and validation reports.
- Unit tests: `test/test_output_formats.py` (24 structural compliance cases; 46 tests total in
  `test/`).
- Vault feature notes: `Features/generate-work-item.md`, `Features/enrich-work-item.md`.

### Changed

- **`generate-work-item` reboot**: Emits uniform **raw** ticket bodies via `output-formats.md`
  and slim spec blueprints; enricher prompts removed (moved to `enrich-work-item`).
- **`azure-mechanics.md`**: Shared rules for Azure read paths, attachments, and description
  reference handling used by enrich and ingest flows.
- Agent Skills registry: six skills in `skills.sh.json`, root `skills/enrich-work-item`
  symlink, and marketplace/plugin manifests listing `enrich-work-item`.
- Plugin version bumped to **0.6.0**.

## [0.5.0] - 2026-07-06

### Added

- **`generate-work-item` skill**: Context7 research → vault `Specs/` note → enriched ticket draft →
  Azure DevOps on approval (Epic / Feature / User Story / Task). Bundled enricher prompts and
  type-specific spec blueprints.
- **`./install.sh` installer**: wires Claude Code, Cursor, Codex, and Antigravity plugins; Azure
  DevOps MCP, orchestrator MCP, global CLI, project mailbox, and vault mistakes repo.
  Auto-detects agent hosts; non-interactive mode via `-y --azure-org --project-dir`.
- **Agent Skills registry layout**: MIT `LICENSE`, root `skills/` symlinks to
  `agile-workflow/skills/`, and `skills.sh.json` for [skills.sh](https://skills.sh/) discovery.
- **`scripts/validate-skills.sh`**: batch `skills-ref validate` across all five skills.
- **Codex plugin manifests** (`.codex-plugin/`, `agile-workflow/.codex-plugin/`).
- Unit tests: `test/test_install.py`, `test/test_validate_skills.py`, `test/test_skills_discovery.py`.

### Changed

- All five `SKILL.md` files aligned with [agentskills.io](https://agentskills.io/specification):
  `compatibility`, `license: MIT`, host-specific keys under `metadata`.
- Orchestrator-backed skills declare `metadata.orchestrator-skill` (validate-artifact,
  auto-fix-artifact) or `metadata.orchestrator-manifest` (generate-work-item).
- README documents full-plugin, skills-only (`npx skills add`), and OpenSkills install paths.
- Plugin version bumped to **0.5.0**.

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
