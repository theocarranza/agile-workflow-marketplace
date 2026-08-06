# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.11.0] - 2026-08-05

### Added

- **The plugin bundles the orchestrator as an MCP server.** `agile-backlog-toolkit/.mcp.json` declares an
  `orchestrator` server whose `PYTHONPATH` is `${CLAUDE_PLUGIN_ROOT}`, so installing the plugin in
  Claude Code is now sufficient on its own — no `install.sh` copy on the side, and no per-project
  `.mcp.json` entry pointing at an absolute path in the user's home directory. The project root
  still resolves without configuration: `CODEX_PROJECT_ROOT` already falls back to
  `CLAUDE_PROJECT_DIR`, which Claude Code sets for every session.

  Tools from this server are scoped as `mcp__plugin_agile-workflow_orchestrator__<tool>`, not the
  `mcp__agile-workflow-orchestrator__<tool>` names the installer's wiring produces. Hook matchers
  and permission rules written against the installer names do not match the plugin's.

  The installer is unchanged and remains the path for Cursor and Codex, which have no equivalent
  mechanism. Claude Code users should pick one channel: running both wires the same orchestrator
  twice under two different names.

### Fixed

- **`plugin.json` and `marketplace.json` both reported `0.9.0` at the `v0.10.0` tag**, so an install
  of v0.10.0 landed in a cache directory named `0.9.0` and `claude plugin list` reported a version
  the code had not been for a release. The manifests now carry the release version, and the
  hardcoded `(v0.9.0)` inside the plugin description — a second copy of the same number, drifting
  independently — is gone.

## [0.10.0] - 2026-07-28

### Removed

- **The plugin no longer creates, detects, or depends on a knowledge artifacts path anywhere.** It previously
  created `<project>/<artifacts path>/_mistakes/` in the client's project — hardcoded to the marketplace's own
  artifacts path name in `init_scaffold.py`, and derived from a first-alphabetical `<artifacts>*` glob in the
  installer. That glob picked the wrong directory in a project with more than one, so plugin output
  went somewhere nobody was looking.

  Gone: `detect_artifacts path_folder`, the `--artifacts path-folder` flag, the `CODEX_VAULT_FOLDER` environment
  variable and its hardcoded default, `artifacts path_folder` in the install manifest, and every `<artifacts>`
  string in shipped code and prose.

### Changed

- **Where artifacts go is now the user's answer, not the plugin's assumption.** `artifacts_path` in
  `.agile-backlog-toolkit/config.json` is user-supplied and has **no default**. When unset, local output is
  unavailable and skills must ask — the filesystem provider returns an explanatory refusal rather
  than writing somewhere nobody chose. What lives at that path is not the plugin's concern.
- **Plugin-owned state moved to `.agile-backlog-toolkit/`**, cleanly separated from user artifacts:
  validation reports to `reports/` (was `<artifacts path>/Agent_Reports/`), the retry-loop mistakes artifacts to
  `mistakes.json` (was `<artifacts path>/_mistakes/`), and estimation bands to `estimation.json` (was
  `<artifacts path>/Meta/`). `artifacts path_dir` is `state_dir` throughout the runtime.
- `ArtifactsProvider` is now `FilesystemProvider`, reading whatever directory the user nominated.
- `agile-workflow init` and the installer create only `.agentic/workflow_prompts/` and
  `.agile-backlog-toolkit/`. Nothing else, ever.
- Older installs that recorded a path under `artifacts path_folder` still resolve: the value is read as
  `artifacts_path`, treated as nothing more than a path a user once supplied.

### Added

- **Estimation and capacity core** (`orchestrator_core/estimation/`, `orchestrator_core/capacity/`):
  provider-agnostic, I/O-free engines that suggest effort hours from story points and compare a
  sprint's available hours against what it has taken on. Hours resolve as calibrated (from the
  team's own completed work) → config → seed default, and every suggestion carries that provenance
  so a shipped default is never mistaken for a measurement.
- **Provider adapter seam** (`orchestrator_core/providers/`): `CapacityProvider` and
  `WorkItemWriter` protocols with a `PROVIDERS` registry, shipping a filesystem adapter and an
  Azure DevOps adapter. Adding another backlog system needs no change to the estimation or capacity code.
- **Azure DevOps adapter**: reads iteration capacity, days off, and work items; centralises
  `Microsoft.VSTS.*` reference names in `providers/azure_devops/fields.py` (previously only in
  markdown). Guards `OriginalEstimate` behind a process check, since Scrum projects lack it.
  Capacity is read-only — the adapter never writes capacity settings.
- `estimate` and `capacity` CLI subcommands; `capacity` exits non-zero when overcommitted so it
  works as a gate. New `plan-capacity` orchestrator handler.
- `content-effort-hours-plausible` validator check — advisory only: `SKIP` when unestimated,
  `WARN` when a figure contradicts its own story points, never `FAIL`.
- `effort_hours`, `activity`, and `iteration` frontmatter keys, plus the previously undocumented
  `story_points`, in the ticket-structure contract. New `references/estimation.md`.
- **HTTP-level tests for the Azure client** (`test/test_azure_client_http.py`): a real server on
  localhost exercises URL construction, the Basic auth header, and every error branch (401, 404,
  500, malformed body, connection refused, timeout) without network access or credentials. Includes
  a live read-only smoke test, skipped unless `ADO_PAT` and an org are set.
- **Contract tests for the Azure mappers** (`test/test_azure_contract.py`): asserts the mappers
  degrade rather than raise on payloads that differ from Microsoft's documented examples — full
  identity objects, unknown fields, numbers as strings, nulls, and malformed dates.
- **First CI workflow** (`.github/workflows/test.yml`): pytest on Python 3.12, skill manifest
  validation, and a CLI exit-code smoke test. The suite previously had nothing running it.
- **Project configuration** (`.agile-backlog-toolkit/config.json`, `orchestrator_core/project_config.py`):
  one runtime source of truth for the artifacts path and the Azure organisation, project, team, and
  process. Resolves through a fallback chain — environment, then the canonical file, then the
  install receipt, then the org parsed out of MCP wiring — so
  projects set up by earlier versions keep working. Read it with `agile-workflow config --show`,
  which exits non-zero when a required value is missing.
- **Lazy fill for Azure identity.** Project, team, and process no longer have to be typed: a skill
  discovers the options through the MCP server (`core_list_projects`, `core_list_project_teams`,
  `wit_list_backlogs`), the user picks, and `agile-workflow config --set azure.<key>=<value>`
  persists the answer. Installer flags `--azure-project`, `--azure-team`, and `--azure-process`
  cover the unattended path.
- Installer now pins the Azure DevOps MCP server to a `node` invocation against a fixed entrypoint,
  installing it once under `~/.local/share/azure-devops-mcp`, and falls back to `npx` when that is
  unavailable. Pinning avoids re-resolving the package on every start and sidesteps the truncated
  `PATH` that breaks stdio servers under some hosts. The Cursor wrapper uses the same launch.
- `references/project-config.md` documents the schema, the resolution order, and the discovery flow.

### Fixed

Three mapping defects, all found by running against a real organisation and all silent — each
produced a plausible-looking but wrong capacity report rather than an error.

- **Capacity payloads mapped to zero members.** The Azure DevOps MCP server returns capacity under
  a `teamMembers` key, not the `{count, value}` envelope the REST reference documents. Every real
  capacity read produced an empty team and zero available hours. The unwrapper now understands both
  envelopes, and `reported_daily_total()` cross-checks the mapped sum against Azure's own
  `totalCapacityPerDay`.
- **`workingDays` arrived as integers, not day names**, using JavaScript's Sunday-is-0 numbering.
  The mapper only understood strings, so it silently ignored the setting and assumed a Saturday
  and Sunday weekend. A team working a six-day week would have had its capacity computed wrong.
- Azure work-item mapping discarded an explicit `0` story-point value and fell through to another
  process's size field, because the `or` chain treated a legitimate zero as absent. A Story with
  `StoryPoints: 0` and `Effort: 5` on an Agile project reported 5 points.
- `.claude/codex-workflow.config.json` was named by five skills as the way to resolve a storage location, but
  nothing ever wrote it and no code ever read it — while the Python side resolved the artifacts path from an
  environment variable with a hardcoded default. The two mechanisms now meet: the skills point at
  `agile-workflow config --show`.

### Changed (continued)

- **Story-point scale reconciled across all three sources.** Drivers now score 1/2/3/5/8 in
  `scoring-guide.md`, `decomposition-rules.md`, and `work-item-enricher.prompt.md`, under a pure
  MAX rule. The enricher's contradicting non-MAX exception ("Dois drivers = 5 → 8 pontos") is
  removed; the rule is encoded in `estimation/scales.py` as the single source of truth.
- `generate-breakdown-work-items` now writes `RemainingWork`, `OriginalEstimate` (Agile/CMMI only),
  `Activity`, and an explicit `IterationPath` on generated Tasks — closing the gap that left
  broken-down Stories invisible to sprint capacity bars and the burndown chart. Hours are only ever
  written after a human confirms them, and declined estimates are named in the run summary.

## [0.9.0] - 2026-07-28

### Added

- **`amend-workitems` skill**: UI intake, complete-tree backup and scan, keyword-ranked placement
  choices, approval-gated content amendments, Implementation Plan updates, and non-destructive
  Task-child reconciliation.
- Antigravity IDE and Antigravity CLI installation targets for the plugin bundle.

### Changed

- Agent Skills registry, manifests, README, and plugin version updated to nine skills (`0.9.0`).

### Fixed

- Codex plugin metadata now uses the host-compatible `defaultPrompt` array shape.
- `amend-workitems` declares the Azure attachment-read tool required for complete tree backups.

## [0.8.1] - 2026-07-25

### Fixed

- **`install.sh` curl|bash bootstrap**: Piped installs no longer resolve `scripts/install.py`
  relative to the current working directory (which produced
  `python3: can't open file '…/scripts/install.py'`). When not run from a checkout, the
  script shallow-clones the repo and runs the installer from that clone.
- README remote install URL now uses the `main` branch (not `master`).

## [0.8.0] - 2026-07-25

### Added

- **`generate-breakdown-work-items` skill**: Intake UX, Implementation Plan generation to the
  artifacts, atomic Task decomposition (Staging / Review / Breakdown), and Feature/Epic fan-out.
  Registered in `skills.sh.json`, plugin/marketplace descriptions, and root `skills/` symlink.
- Skill package under `agile-backlog-toolkit/skills/generate-breakdown-work-items/` with
  `intake-ux.md`, `plan-generation.md`, `atomic-tasks.md`, and `fan-out.md` references.
- Artifacts feature, child Stories, and Implementation Plan under
  `<artifacts>/`.

### Changed

- Agent Skills registry: eighth skill in `skills.sh.json`, root
  `skills/generate-breakdown-work-items` symlink, marketplace/plugin manifests, and README.
- Plugin version bumped to **0.8.0**.

## [0.7.3] - 2026-07-24

### Changed

- **`enrich-work-item` enricher prompts**: Synced `references/enrichers/*.prompt.md` with the
  upstream host-team source — Contexto Obrigatório now routes through a single `../../AGENTS.md`
  router (dropping the separate `AGENTS_RULES.md` lookup) and the Feature enricher consolidates
  plan/feature-flag guidance into `domain.md` (dropping the standalone
  `plans-and-subscriptions.md` reference). Epic enricher's Dependências e Riscos Estratégicos
  heading emoji changed 🔗 → 🚧 to match upstream.

### Removed

- Stale duplicate copies of the enricher prompts and the pt-BR tech glossary under
  `<artifacts>/assets/`, left over from before the 0.7.1 bundled-assets
  migration. The artifacts path's `assets/` folder is documented for images/binary attachments only; the
  bundled copies inside each skill's own `references/` are the single source of truth.

## [0.7.1] - 2026-07-07

### Changed

- **Bundled skill assets policy**: Runtime inputs (glossary, enricher prompts) ship inside the
  plugin skill packages. Skills no longer read from `<artifacts path>/assets/` for bundled artifacts.
- **`generate-plain-language-documentation`**: Tech glossary copied to
  `references/assets/tech-glossary-en-pt-br.json` within the skill package.
- **`enrich-work-item`**: Bundled `./references/enrichers/*.prompt.md` is authoritative; removed
  artifacts path override pattern.

## [0.7.0] - 2026-07-07

### Added

- **`generate-plain-language-documentation` skill**: Plain-language conductor for documentation,
  reports, guides, and `work-item-prose` (requirement bullets and acceptance criteria). Six-phase
  pipeline with glossary verification for `pt-br` via
  `<artifacts>/assets/tech-glossary-en-pt-br.json`.
- **Sibling prose hooks**: `generate-work-item`, `enrich-work-item`, and `decompose-backlog` delegate
  narrative polishing to the plain-language skill per `integration-notes.md`.
- Unit tests: `test/test_generate_plain_language_documentation.py`,
  `test/test_plain_language_skill_integration.py`, and `test/plain_language_helpers.py` (76 tests in
  `test/` with `PYTHONPATH=agile-backlog-toolkit`).
- Artifacts feature note: `Features/generate-plain-language-documentation.md`.

### Changed

- Agent Skills registry: seventh skill in `skills.sh.json`, root
  `skills/generate-plain-language-documentation` symlink, and marketplace/plugin manifests.
- Plugin version bumped to **0.7.0**.

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
- Artifacts feature notes: `Features/generate-work-item.md`, `Features/enrich-work-item.md`.

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

- **`generate-work-item` skill**: Context7 research → artifacts path `Specs/` note → enriched ticket draft →
  Azure DevOps on approval (Epic / Feature / User Story / Task). Bundled enricher prompts and
  type-specific spec blueprints.
- **`./install.sh` installer**: wires Claude Code, Cursor, Codex, and Antigravity plugins; Azure
  DevOps MCP, orchestrator MCP, global CLI, project mailbox, and artifacts path mistakes repo.
  Auto-detects agent hosts; non-interactive mode via `-y --azure-org --project-dir`.
- **Agent Skills registry layout**: MIT `LICENSE`, root `skills/` symlinks to
  `agile-backlog-toolkit/skills/`, and `skills.sh.json` for [skills.sh](https://skills.sh/) discovery.
- **`scripts/validate-skills.sh`**: batch `skills-ref validate` across all five skills.
- **Codex plugin manifests** (`.codex-plugin/`, `agile-backlog-toolkit/.codex-plugin/`).
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

- **Deterministic orchestrator** (`agile-backlog-toolkit/orchestrator_core/`): event-sourced runtime
  with rule-based Actor-Critic validation, circuit breaker (3 retries), and
  `IMPLEMENTATION APPROVED` recovery gate. See [docs/orchestrator.md](docs/orchestrator.md).
- **`bin/agile-workflow` CLI**: `init`, `validate`, `evaluate`, `compile`, `resume`, `mcp`.
- **Filesystem mailbox** (`.agentic/workflow_prompts/`): harness-agnostic prompts and error logs
  for `correcao` resume after quality-gate failures.
- **Mistakes repo** (`<artifacts>/_mistakes/mistakes.json`): persists
  circuit-breaker flaws for cross-session avoidance.
- Skill **manifests** for `validate-artifact` and `auto-fix-artifact` (MCP input/output schemas).
- Unit tests (`test/test_orchestrator.py`, `test/test_stream.py`).

### Changed

- `validate-artifact` and `auto-fix-artifact` SKILL.md now prefer the Python critic over
  LLM self-judgment for validation.
- Plugin version bumped to **0.4.0**.

## [0.3.0] - 2026-06-25

### Added

- `auto-fix-artifact` skill: validates a single agile artifact and offers an auto-fix workflow if issues are found. Applies fixes based on `validate-artifact` quality gates (e.g., adding missing sections, fixing titles, calculating story points, etc.). Accepts an Azure workitem ID, artifacts document, filesystem reference, or pasted string.

## [0.2.0] - 2026-06-25

### Added

- `validate-artifact` skill: non-mutating quality gate for a single Epic, Feature, or User Story.
  Accepts local draft path or Azure work item ID. Runs four check categories (STRUCTURAL,
  HIERARCHY, CONTENT, DoR) non-blocking and emits a terminal report + report in
  `Agent_Reports/`.
- `split-story` skill: lateral story-sizing conductor (5 phases, 2 gates). Takes a single User
  Story from any of four input sources (local draft, Azure ID, file system path, raw text),
  scores it with the 6-driver MAX heuristic, determines split pattern, drafts sub-stories with
  AC coverage validation, and hands off via a 3-option HANDOFF menu.

### Changed

- Promoted shared references from `decompose-backlog/references/` to `agile-backlog-toolkit/references/`
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
