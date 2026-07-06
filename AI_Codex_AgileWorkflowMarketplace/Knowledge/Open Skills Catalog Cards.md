---
type: reference
tags: [reference, agent-skills, marketplace, openskills]
area: agile-workflow-marketplace
created: 2026-07-06
source: https://openskills.cc/
---

# Open Skills Catalog Cards

Copy-paste listing drafts for [openskills.cc](https://openskills.cc/) / OpenClaw-compatible registries. Install command points at this repo via `./install.sh`.

## Bundle card — `agile-workflow`

| Field | Value |
| --- | --- |
| **Name** | agile-workflow |
| **Category** | Development Tools / Productivity |
| **Description** | Azure DevOps backlog workflow skills: decompose Features into Stories, validate and auto-fix artifacts, split oversized stories, generate Epics/Features/Stories/Tasks with Context7-backed specs. Deterministic Python orchestrator for quality gates. |
| **Install (full plugin)** | `./install.sh -y --azure-org <org> --project-dir <path>` |
| **Install (skills only)** | `npx skills add theocarranza/agile-workflow-marketplace` |
| **Install (AGENTS.md agents)** | `npx openskills install theocarranza/agile-workflow-marketplace --universal && npx openskills sync -y` |
| **Install (Claude Code)** | `/plugin install agile-workflow@agile-workflow-marketplace` |
| **Requires** | Azure DevOps MCP, AI Codex vault, optional Context7 MCP |
| **Standard** | [agentskills.io](https://agentskills.io/home) |
| **License** | MIT |
| **Skills** | 5 |

## Per-skill cards

### decompose-backlog

Decompose a parent Azure DevOps Epic or Feature into correctly-parented, audited child Stories. Seven phases, two approval gates, vault drafts, Azure create + hierarchy verify + coverage audit.

**Triggers:** "decompose Feature N", "break this into stories", Feature/Epic id.

### validate-artifact

Non-mutating quality gate for a single Epic, Feature, or User Story. Vault draft or Azure ID. Rule-based orchestrator critic; terminal report + vault `Agent_Reports/` note.

**Triggers:** "validate this story", "check this ticket", "is this artifact ready?"

### auto-fix-artifact

Validate then auto-fix a draft with circuit-breaker reflection. Uses validate-artifact gates; persists corrections to vault or Azure with user consent.

**Triggers:** "fix this artifact", "auto-fix the ticket".

### split-story

Lateral story-sizing: 6-driver MAX score, split pattern detection, sub-story drafts, coverage check, three-option handoff.

**Triggers:** "split this story", "is this story too big?"

### generate-work-item

Research tech stack (Context7), write `Specs/` note, draft enriched ticket, create Azure work item after approval. Epic / Feature / User Story / Task.

**Triggers:** "create a user story", `/generate-work-item`, type + idea.

## Publication checklist

- [x] Confirm repository `LICENSE` file — MIT (2026-07-06)
- [x] Root `skills/` discovery layout — symlinks to `agile-workflow/skills/`
- [x] `skills.sh.json` grouping for [skills.sh](https://skills.sh/) repo page
- [x] Run `./scripts/validate-skills.sh` — all pass (2026-07-06)
- [ ] Tag release `v0.5.0` and push to GitHub
- [ ] First `npx skills add theocarranza/agile-workflow-marketplace` install (triggers skills.sh indexing)
- [ ] Wait for [openskills.cc](https://openskills.cc/skills) crawler to index public repo
- [ ] Link back to [[Agent Skills Adoption Notes]]

## Related

- [[Open Skills Marketplace]]
- [[Agent Skills Overview]]
