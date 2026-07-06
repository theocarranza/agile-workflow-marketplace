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
| **Install** | `git clone https://github.com/theocarranza/agile-workflow-marketplace.git && cd agile-workflow-marketplace && ./install.sh` |
| **Requires** | Azure DevOps MCP, AI Codex vault, optional Context7 MCP |
| **Standard** | [agentskills.io](https://agentskills.io/home) |
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

- [ ] Confirm repository `LICENSE` file (none at 2026-07-06 — add before listing)
- [ ] Run `./scripts/validate-skills.sh` — all pass
- [ ] Submit bundle or per-skill folders to target registry
- [ ] Link back to [[Agent Skills Adoption Notes]]

## Related

- [[Open Skills Marketplace]]
- [[Agent Skills Overview]]
