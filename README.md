# agile-workflow-marketplace

[![Release](https://img.shields.io/github/v/release/theocarranza/agile-workflow-marketplace?label=version&color=0e7c86)](https://github.com/theocarranza/agile-workflow-marketplace/releases)
[![License: MIT](https://img.shields.io/github/license/theocarranza/agile-workflow-marketplace)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-7-2563eb)](skills/)
[![Agent Skills](https://img.shields.io/badge/spec-agentskills.io-5C2D91)](https://agentskills.io/specification)
[![skills.sh](https://img.shields.io/badge/listed-skills.sh-000000)](https://skills.sh/)

[![Python](https://img.shields.io/badge/python-3.10+-3776AB?logo=python&logoColor=white)](agile-workflow/orchestrator_core/)
[![Bash](https://img.shields.io/badge/bash-install.sh-4EAA25?logo=gnubash&logoColor=white)](install.sh)
[![Markdown](https://img.shields.io/badge/format-SKILL.md-000000?logo=markdown)](https://agentskills.io/specification)
[![Azure DevOps](https://img.shields.io/badge/Azure%20DevOps-MCP-0078D4?logo=azuredevops&logoColor=white)](.mcp.json)
[![Obsidian](https://img.shields.io/badge/Obsidian-AI%20Codex%20vault-7C3AED&logo=obsidian)](AI_Codex_AgileWorkflowMarketplace/)
[![MCP](https://img.shields.io/badge/MCP-orchestrator%20%2B%20azure--devops-ff6b35)](docs/orchestrator.md)


A standalone multi-host plugin marketplace for Agile backlog workflows against **Azure DevOps**.

Seven [Agent Skills](https://agentskills.io/specification)-compliant conductors plus a deterministic **Python orchestrator** for quality gates. Ships Claude Code, Cursor, Codex, and Antigravity plugin manifests, MCP wiring, and an Obsidian vault ledger.

## Install

### Full plugin (MCP + orchestrator + vault)

One command wires the plugin, orchestrator CLI, MCP servers, and project mailbox.
You only provide your Azure DevOps org, project path, and vault folder name.

```bash
git clone https://github.com/theocarranza/agile-workflow-marketplace.git
cd agile-workflow-marketplace
./install.sh
```

Non-interactive:

```bash
./install.sh -y --azure-org <org-slug> --project-dir /path/to/your/project
```

Remote bootstrap (no manual clone):

```bash
curl -fsSL https://raw.githubusercontent.com/theocarranza/agile-workflow-marketplace/master/install.sh \
  | bash -s -- -y --azure-org <org-slug> --project-dir /path/to/your/project
```

The installer auto-detects your agent hosts (Claude Code, Cursor, Codex, Antigravity) and wires:

- Plugin registration per host (skills + orchestrator + references)
- `azure-devops` + `agile-workflow-orchestrator` MCP in project `.mcp.json` and `.cursor/mcp.json`
- Global `agile-workflow` CLI at `~/.local/bin/`
- Project mailbox (`.agentic/workflow_prompts/`) and vault `_mistakes/` repo

Restart your agent host(s) after install to load skills and MCP servers.

Limit to specific hosts:

```bash
./install.sh --target cursor,codex -y --azure-org <org> --project-dir .
```

Manual / Claude-only alternative:

```text
/plugin marketplace add <path-or-git-url-to-this-repo>
/plugin install agile-workflow
```

### Skills only (registry install)

Root `skills/` symlinks expose the seven skills for [skills.sh](https://skills.sh/) and [openskills.cc](https://openskills.cc/skills) discovery:

```bash
npx skills add theocarranza/agile-workflow-marketplace
```

For agents that load `AGENTS.md` via [OpenSkills](https://www.npmjs.com/package/openskills):

```bash
npx openskills install theocarranza/agile-workflow-marketplace --universal
npx openskills sync -y
```

Skills-only install copies `SKILL.md` folders — it does **not** wire MCP, orchestrator, or vault. Use `./install.sh` for the full stack.

## Orchestrator (v0.4.0+)

Quality-gate skills use a **rule-based Python critic** — not LLM self-judgment. The orchestrator
implements the Actor-Critic pattern with circuit breaker and filesystem mailbox IPC.

```bash
./bin/agile-workflow init
./bin/agile-workflow validate --file path/to/draft.md --persist
./bin/agile-workflow evaluate --skill validate-artifact --file path/to/draft.md
```

`bin/agile-workflow` is the plugin-level **scripts** entrypoint (Agent Skills `scripts/` equivalent at marketplace root). Orchestrator-backed skills declare `metadata.orchestrator-skill` in their `SKILL.md`.

Full reference: [docs/orchestrator.md](docs/orchestrator.md).

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

**Prefer the orchestrator critic:**

```bash
./bin/agile-workflow validate --file <path> [--persist]
```

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

### Skill: `auto-fix-artifact`

Validates a single agile artifact and offers an auto-fix workflow if issues are found. Uses
`validate-artifact` quality gates via the orchestrator critic, then applies fixes with user consent.

1. **INGEST AND VALIDATE** — orchestrator runs rule-based checks (`evaluate` CLI or MCP).
2. **DECISION GATE** — if issues found, show report and ask permission to fix.
3. **AUTO-FIX** — address each FAIL/WARN (frontmatter, sections, complexity, story points, hygiene).
4. **OUTPUT & PERSIST** — show corrected artifact; save to Azure or vault on approval.

Circuit breaker: 3 retries or identical critiques → human `IMPLEMENTATION APPROVED` to resume.

Trigger: "fix this artifact", "auto-fix the ticket", or supply a vault path / Azure ID / file path / raw text.

### Skill: `generate-work-item`

Generate an Epic, Feature, User Story, or Task from an idea: Context7 research → vault `Specs/`
note → **raw** ticket draft (uniform sections per `output-formats.md`) → optional handoff to
`enrich-work-item` or Azure DevOps on approval. Does **not** run enricher prompts.

Trigger: `/generate-work-item`, "create a ticket/story/feature/epic/task", or supply type +
description.

### Skill: `enrich-work-item`

Enrich an existing or freshly generated work item to the team format: type-specific enricher
prompts, canonical shape targets, ASCII diagrams, story-point hygiene, and Azure ingest
(attachments and description references). One item per invocation.

Trigger: `/enrich-work-item`, "enrich this story/feature/epic", or supply vault path / Azure ID /
raw draft.

### Skill: `generate-plain-language-documentation`

Turn technical source material into plain-language prose for humans — documentation, reports,
guides, and work-item narrative (`work-item-prose`). Uses the bundled skill glossary
(`references/assets/tech-glossary-en-pt-br.json`) for **pt-BR** translation and technical-term
verification. Sibling skills delegate prose passes here without a separate user gate (see
`references/integration-notes.md` in the skill package).

Trigger: `/generate-plain-language-documentation`, "document this in plain language", "rewrite for
the product team", or `--source` with optional `--audience`, `--language`, `--type`.


## Agent Skills compliance

Each skill may ship `references/canonical/` templates (read-only shape
contracts) alongside skill-specific blueprints and pipelines.

Each skill follows the [Agent Skills open standard](https://agentskills.io/specification): root `skills/<name>/SKILL.md` (symlinked to `agile-workflow/skills/`) with `name`, `description`, `license`, optional `references/`, and progressive disclosure. Repo page grouping: `skills.sh.json`. Licensed under [MIT](LICENSE).

Validate all skills:

```bash
./scripts/validate-skills.sh
```

## Shared references

All skills share a common reference library at `agile-workflow/references/`:

| File | Purpose |
| --- | --- |
| `decomposition-rules.md` | 6-driver MAX heuristic, story-point ceiling, DoR, hierarchy rules |
| `ticket-structure.md` | Body sections, frontmatter constraints, content hygiene |
| `azure-mechanics.md` | MCP calls, linking gotchas, rendering rules |
| `audit-checklist.md` | Coverage checking and audit rules |

## Documentation

| Document | Contents |
| --- | --- |
| [docs/design.md](docs/design.md) | `decompose-backlog` skill design |
| [docs/orchestrator.md](docs/orchestrator.md) | Deterministic orchestrator runtime (v0.4.0+) |
| [CHANGELOG.md](CHANGELOG.md) | Release history |

## Development

```bash
PYTHONPATH=agile-workflow python3.12 -m pytest test/ -v
./scripts/validate-skills.sh
```
