# agile-backlog-toolkit

[![Release](https://img.shields.io/github/v/release/theocarranza/agile-backlog-toolkit?label=version&color=0e7c86)](https://github.com/theocarranza/agile-backlog-toolkit/releases)
[![License: MIT](https://img.shields.io/github/license/theocarranza/agile-backlog-toolkit)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-9-2563eb)](skills/)
[![Agent Skills](https://img.shields.io/badge/spec-agentskills.io-5C2D91)](https://agentskills.io/specification)
[![skills.sh](https://img.shields.io/badge/listed-skills.sh-000000)](https://skills.sh/)

[![Python](https://img.shields.io/badge/python-3.12+-3776AB?logo=python&logoColor=white)](agile-workflow/orchestrator_core/)
[![Bash](https://img.shields.io/badge/bash-install.sh-4EAA25?logo=gnubash&logoColor=white)](install.sh)
[![Markdown](https://img.shields.io/badge/format-SKILL.md-000000?logo=markdown)](https://agentskills.io/specification)
[![Azure DevOps](https://img.shields.io/badge/Azure%20DevOps-MCP-0078D4?logo=azuredevops&logoColor=white)](.mcp.json)
[![MCP](https://img.shields.io/badge/MCP-orchestrator%20%2B%20azure--devops-ff6b35)](docs/orchestrator.md)


A standalone multi-host plugin marketplace for vendor-neutral Agile backlog workflows.

Nine [Agent Skills](https://agentskills.io/specification)-compliant conductors plus a deterministic **Python orchestrator** for quality gates. Ships Claude Code, Cursor, Codex, and Antigravity (IDE and CLI) plugin manifests, and MCP wiring. For the current release see [`CHANGELOG.md`](CHANGELOG.md).

## Install

### Claude Code: the plugin alone (skills + MCP)

The plugin bundles the orchestrator's MCP server and resolves its own path, so this is the whole
setup — no clone, no installer, no per-project `.mcp.json` entry:

```text
/plugin marketplace add https://github.com/theocarranza/agile-backlog-toolkit
/plugin install agile-backlog-toolkit
```

Restart Claude Code afterwards. Orchestrator tools arrive as
`mcp__plugin_agile-backlog-toolkit-orchestrator__<tool>`.

This channel does not install the `agile-backlog-toolkit` CLI or the Azure DevOps MCP server. If you want
those, or you use Cursor, Codex, or Antigravity, use the installer below instead — but use **one or
the other**, since running both wires the orchestrator twice under two different names.

### Full stack, all hosts (MCP + orchestrator + CLI)

One command wires the plugin, orchestrator CLI, MCP servers, and project mailbox.
You only provide your Azure DevOps organization. Everything else is discovered on first use, and
where local artifacts go is asked for — never assumed.

```bash
git clone https://github.com/theocarranza/agile-backlog-toolkit.git
cd agile-backlog-toolkit
./install.sh
```

Non-interactive:

```bash
./install.sh -y --provider both --azure-org <org-slug> --linear-team <team> --project-dir /path/to/your/project
```

Remote bootstrap (no manual clone):

```bash
curl -fsSL https://raw.githubusercontent.com/theocarranza/agile-backlog-toolkit/main/install.sh \
  | bash -s -- -y --azure-org <org-slug> --project-dir /path/to/your/project
```

The installer auto-detects your agent hosts (Claude Code, Cursor, Codex, Antigravity) and wires:

- Plugin registration per host (skills + orchestrator + references)
- `azure-devops` + `agile-backlog-toolkit-orchestrator` MCP in project `.mcp.json` and `.cursor/mcp.json`
- Global `agile-backlog-toolkit` CLI at `~/.local/bin/`
- Project mailbox (`.agentic/workflow_prompts/`) and plugin state (`.agile-backlog-toolkit/`)

Restart your agent host(s) after install to load skills and MCP servers.

Limit to specific hosts:

```bash
./install.sh --target cursor,codex -y --azure-org <org> --project-dir .
```

### Skills only (registry install)

Root `skills/` symlinks expose the nine skills for [skills.sh](https://skills.sh/) and [openskills.cc](https://openskills.cc/skills) discovery:

```bash
npx skills add theocarranza/agile-workflow-marketplace
```

For agents that load `AGENTS.md` via [OpenSkills](https://www.npmjs.com/package/openskills):

```bash
npx openskills install theocarranza/agile-workflow-marketplace --universal
npx openskills sync -y
```

Skills-only install copies `SKILL.md` folders — it does **not** wire MCP or the orchestrator. Use `./install.sh` for the full stack.

## Orchestrator

Quality-gate skills use a **rule-based Python critic** — not LLM self-judgment. The orchestrator
implements the Actor-Critic pattern with circuit breaker and filesystem mailbox IPC.

```bash
./bin/agile-backlog-toolkit init
./bin/agile-backlog-toolkit validate --file path/to/draft.md --persist
./bin/agile-backlog-toolkit evaluate --skill validate-artifact --file path/to/draft.md
```

`bin/agile-backlog-toolkit` is the plugin-level **scripts** entrypoint (Agent Skills `scripts/` equivalent at marketplace root). Orchestrator-backed skills declare `metadata.orchestrator-skill` in their `SKILL.md`.

Full reference: [docs/orchestrator.md](docs/orchestrator.md).

## Estimation & capacity

Puts an hour estimate on **every Task under a User Story**, and checks it against **the assigned
person's capacity in the active sprint**.

It is not a separate tool you go and run. It is part of breaking a Story down — it fires when
`generate-breakdown-work-items` creates the Task list, and again when `amend-workitems` changes it.

### The problem it solves

Azure DevOps keeps two separate estimation systems, and they never talk to each other.

**Stories carry points** — a relative size, meaning "this feels twice as big as that". Points feed
velocity and forecasting.

**Tasks carry hours** — an absolute duration. Hours are the *only* thing the sprint capacity bar
and the burndown chart read.

Break a Story into Tasks without putting hours on them and nothing errors. The board looks healthy
and the hierarchy is correct, but the sprint tooling quietly reports an empty sprint:

```
   Story: 5 points ──► velocity ✓         forecasting works

   Task:  (no hours) ──► capacity bar ✗    the assignee's bar stays empty
                     └─► burndown     ✗    flat line, all sprint
```

The person doing the work finds out their sprint was over- or under-filled at the *end* of it.

### What it does

When a User Story is broken down into Tasks:

1. **Estimates each Task** — takes the Story's points, derives hours, and splits them across the
   Tasks in the list so the parts sum to the whole.
2. **Fetches the assignee's capacity** for the active sprint — their hours per day, minus their
   days off, team holidays and weekends.
3. **Checks the total against that capacity.** If it fits, the hours are written and every figure
   is reported. If it does not, the run stops and asks — split, reschedule, reassign, or reduce
   scope. The hours are never quietly scaled down to fit.
4. **Writes the hours onto the Tasks**, which is what makes them visible to the capacity bar and
   the burndown.

### When it runs

| Moment | Skill | What happens |
| --- | --- | --- |
| Breaking a Story into its Tasks | `generate-breakdown-work-items` | Each Task gets an estimate, checked against the assignee's sprint capacity |
| Amending an existing Task list | `amend-workitems` | The same, for Tasks added or changed |
| **Any change to the work a Story needs** | either | Estimates are recomputed and the Tasks updated, so hours never drift from the current breakdown |

That last row is the point: a Task list that changed but kept its old hours is worse than one with
no hours at all, because the burndown keeps charting a plan nobody is following any more.

### Checking by hand

The same engine is reachable directly, mostly for inspection:

```bash
./bin/agile-backlog-toolkit estimate --points 5                # suggested hours for a point value
./bin/agile-backlog-toolkit estimate --file path/to/draft.md   # …or read the points off a draft
./bin/agile-backlog-toolkit capacity --provider azure-devops --iteration <id>
```

`capacity` reports the whole sprint rather than one person, and exits non-zero when it is
overcommitted, so it works as a gate in a script.

### How the hours are worked out

**There is no formula for points → hours.** Points are deliberately unitless and team-relative, so
any universal constant is a guess. Instead the engine measures *your* team, and always states which
of three sources it used:

```
1. calibrated    from your team's own completed work  ← preferred
2. config        bands your team wrote down
3. seed-default  shipped starting point, explicitly not a measurement
```

Every suggestion is stamped with that source, so a shipped default is never mistaken for a fact
about your team:

```
5 pts -> 12h (8-16h, seed default -- NOT calibrated, confirm before use)
```

### Two safety rules

**Estimates are applied, and every change is reported.** Hours derive from the Story's points, so
there is nothing to approve item by item — they are written without asking. What is never optional
is telling you: every figure set or changed is named in the run summary, old value and new. Nothing
asked permission, so nothing moves silently.

**Capacity is a ceiling, and it is read-only.** When a Story's Tasks exceed the assignee's
remaining hours, the run stops and asks — split, reschedule, reassign, or reduce scope. The hours
are never scaled down to fit, because that would misrepresent how long the work takes. Your team's
capacity settings themselves are read to do the arithmetic and never modified.

Full reference: [agile-workflow/references/estimation.md](agile-workflow/references/estimation.md).

## Configuration

Four things the plugin needs to know about your setup, so no skill has to ask twice: which Azure
DevOps **organisation, project and team** to talk to, which **process** your project uses (Agile,
Scrum or CMMI — it decides which fields exist), and where you want local files written.

They live in `.agile-backlog-toolkit/config.json`, which holds no secrets and is safe to commit so your
team shares one setup. Authentication comes from the Azure DevOps MCP server using your signed-in
session.

```bash
./bin/agile-backlog-toolkit config --show                  # what is set, and where it came from
./bin/agile-backlog-toolkit config --set azure.team=<name> # set a value
```

You rarely type any of it. **Azure values are discovered** — the first skill that needs your
project or team lists the options through Azure, you pick one, and the answer is saved. `--show`
exits non-zero when something required is missing, so it also works as a precondition check.

**Where your files go is asked for, never assumed.** The plugin has no default location for your
work and creates no directory structure in your project. The only directory it owns is
`.agile-backlog-toolkit/` — its own config, reports, and memory.

Full reference: [agile-workflow/references/project-config.md](agile-workflow/references/project-config.md).

## Plugin: `agile-workflow`

### Skill: `decompose-backlog`

Takes a parent work item (Epic or Feature) and drives seven phases to produce correctly-parented,
audited child Stories in Azure DevOps:

1. **Ingest** the parent (verbatim text, acceptance criteria, parent chain).
2. **Decompose** into right-sized Stories (1 Story = 1 sprint = 1 PR). — _approval gate_
3. **Draft** each Story under the configured artifacts path.
4. **Enrich** to the team format (ASCII diagrams, de-duped, story points). — _approval gate_
5. **Create** in Azure DevOps, parented to the **Feature** (explicit link type).
6. **Verify** the Epic→Feature→Story hierarchy structurally.
7. **Audit** that every parent requirement maps to a Story (coverage report).

Self-contained: carries its own decomposition rules and Azure linking guardrails (the two linking
gotchas: always pass explicit link `type`; a Story's parent is its Feature, never the Epic).

Trigger: "decompose Feature N", "break this into stories", or supply a Feature/Epic id.

See `docs/design.md` for the full design and `docs/plans/` for the implementation plan.

### Skill: `validate-artifact`

Quality gate for a single agile artifact (Epic, Feature, or User Story). Accepts a local draft
path or live Azure DevOps work item ID. Runs all checks non-blocking and emits a terminal report
plus a persisted report. One artifact per invocation.

**Prefer the orchestrator critic:**

```bash
./bin/agile-backlog-toolkit validate --file <path> [--persist]
```

Four check categories:

1. **STRUCTURAL** — frontmatter keys, filename regex, required body sections.
2. **HIERARCHY** — parent chain validated against Azure (Story → Feature → Epic).
3. **CONTENT** — driver breakdown present, story points set, no machine paths or placeholder prose.
4. **DoR** (Definition of Ready) — title clarity, description present, points set, linked to Feature.

Trigger: "validate this story/feature/epic", "check this ticket", "is this artifact ready?", or
supply a file path or Azure work item ID.

### Skill: `split-story`

Lateral story-sizing skill. Takes a single User Story and determines whether to split it, how
many sub-stories to produce, and which split pattern to apply — then drafts the sub-stories and
hands them off. One story per invocation.

Five phases with two approval gates:

1. **INGEST** — normalize from a local draft, Azure ID, file system path, or raw text pasted inline.
2. **SCORE** — apply the 6-driver MAX heuristic (Escopo, Incerteza, Integrações, Dados, QA,
   Rollout); flag declared vs. calculated discrepancy for user resolution.
3. **ANALYZE** — Branch A (right-sized → stop), Branch B (Incerteza sole MAX → recommend Spike),
   Branch C (split → auto-select pattern, present plan). _Approval gate before drafting._
4. **DRAFT** — write local drafts; coverage check ensures every original AC maps to exactly one
   sub-story (orphans and duplicates stop the run).
5. **HANDOFF** — three options: keep as local drafts / create in Azure and link to parent Feature /
   discard.

Split patterns auto-detected from catalog: Workflow Step, Business Rule, Happy/Unhappy Path,
CRUD Operation, Data Variation.

Trigger: "split this story", "is this story too big?", "analyze this story for sizing", or supply
a file path / Azure ID / raw text.

### Skill: `auto-fix-artifact`

Validates a single agile artifact and offers an auto-fix workflow if issues are found. Uses
`validate-artifact` quality gates via the orchestrator critic, then applies fixes with user consent.

1. **INGEST AND VALIDATE** — orchestrator runs rule-based checks (`evaluate` CLI or MCP).
2. **DECISION GATE** — if issues found, show report and ask permission to fix.
3. **AUTO-FIX** — address each FAIL/WARN (frontmatter, sections, complexity, story points, hygiene).
4. **OUTPUT & PERSIST** — show corrected artifact; save to Azure or the artifacts path on approval.

Circuit breaker: 3 retries or identical critiques → human `IMPLEMENTATION APPROVED` to resume.

Trigger: "fix this artifact", "auto-fix the ticket", or supply a file path / Azure ID / raw text.

### Skill: `generate-work-item`

Generate an Epic, Feature, User Story, or Task from an idea: Context7 research → `Specs/`
note → **raw** ticket draft (uniform sections per `output-formats.md`) → optional handoff to
`enrich-work-item` or Azure DevOps on approval. Does **not** run enricher prompts.

Trigger: `/generate-work-item`, "create a ticket/story/feature/epic/task", or supply type +
description.

### Skill: `enrich-work-item`

Enrich an existing or freshly generated work item to the team format: type-specific enricher
prompts, canonical shape targets, ASCII diagrams, story-point hygiene, and Azure ingest
(attachments and description references). One item per invocation.

Trigger: `/enrich-work-item`, "enrich this story/feature/epic", or supply a file path / Azure ID /
raw draft.

### Skill: `generate-plain-language-documentation`

Turn technical source material into plain-language prose for humans — documentation, reports,
guides, and work-item narrative (`work-item-prose`). Uses the bundled skill glossary
(`references/assets/tech-glossary-en-pt-br.json`) for **pt-BR** translation and technical-term
verification. Sibling skills delegate prose passes here without a separate user gate (see
`references/integration-notes.md` in the skill package).

Trigger: `/generate-plain-language-documentation`, "document this in plain language", "rewrite for
the product team", or `--source` with optional `--audience`, `--language`, `--type`.

### Skill: `generate-breakdown-work-items`

From a User Story (or Feature/Epic fan-out), collect work-item reference, output destination, and
language; write an Implementation Plan to the artifacts path; attach atomic child Tasks — including
Staging, Review, and a Done Breakdown Task. Intake enforces selection UX rules (`Recommended`,
`all`, trailing `other…`). Fan-out runs the Story workflow per child without silently skipping
failures.

Trigger: `/generate-breakdown-work-items`, "break down this story into tasks", or supply a Story /
Feature / Epic id, URL, or file path.

### Skill: `amend-workitems`

Analyze user corrections against a complete Epic or Feature tree. The skill snapshots the full
Epic → Feature → Story → Task hierarchy, searches local artifacts when available, offers
single-select placement choices with `Other` last, and presents one approved change set before
delegating content updates to the existing enrichment, prose, breakdown, and validation skills.
Related Implementation Plans and Task child lists are reconciled without deleting existing Tasks
or changing hierarchy/state by default.

Trigger: `/amend-workitems`, "amend this work-item tree", or provide correction instructions and
an Epic/Feature id, URL, or file path.

Antigravity installs expose the plugin in both the IDE global directory and the separate CLI
directory (`~/.gemini/antigravity-cli/plugins/agile-workflow`); CLI skill links are also placed in
the host's native skills directory.


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
| `azure-mechanics.md` | MCP calls, linking gotchas, scheduling fields, rendering rules |
| `audit-checklist.md` | Coverage checking and audit rules |
| `estimation.md` | Points → hours, calibration, sprint capacity |
| `project-config.md` | Config schema, resolution order, discovery flow |

## Documentation

| Document | Contents |
| --- | --- |
| [docs/design.md](docs/design.md) | `decompose-backlog` skill design |
| [docs/orchestrator.md](docs/orchestrator.md) | Deterministic orchestrator runtime (v0.4.0+) |
| [agile-workflow/references/estimation.md](agile-workflow/references/estimation.md) | Estimation and sprint capacity |
| [agile-workflow/references/project-config.md](agile-workflow/references/project-config.md) | Per-project configuration |
| [CHANGELOG.md](CHANGELOG.md) | Release history |

## Development

```bash
PYTHONPATH=agile-workflow python3.12 -m pytest test/ -v
./scripts/validate-skills.sh
```
