---
type: reference
tags: [reference, agent-skills, agile-workflow]
area: agile-workflow-marketplace
created: 2026-07-06
---

# Agent Skills Adoption Notes

Gap checklist for aligning `agile-workflow` with the [Agent Skills open standard](https://agentskills.io/specification). See [[Agent Skills Overview]] and [[Open Skills Marketplace]].

## Plugin posture

`agile-workflow` is a **skill bundle** (marketplace plugin) shipping five spec-shaped skills plus shared runtime (orchestrator, references, installer). The format shell is standard; the moat is Azure DevOps + vault ledger + deterministic critic.

## Per-skill checklist

| Skill | `name` = dir | `<500` lines | `metadata` | `compatibility` | `skills-ref validate` | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `decompose-backlog` | yes | yes (80) | yes | yes | pass | Conductor; explicit-only via metadata |
| `validate-artifact` | yes | yes (201) | yes | yes | pass | Orchestrator critic preferred |
| `auto-fix-artifact` | yes | yes (106) | yes | yes | pass | Reflection loop + circuit breaker |
| `split-story` | yes | yes (261) | yes | yes | pass | Two approval gates |
| `generate-work-item` | yes | yes (203) | yes | yes | pass | Auto-trigger; Context7 + enrichers |

Validate locally:

```bash
npx skills-ref validate agile-workflow/skills/<skill-name>
```

## Spec-aligned frontmatter (2026-07-06)

Host-specific keys moved under `metadata` so `skills-ref` passes:

- `disable-model-invocation` → `metadata.disable-model-invocation: "true"` (four conductors)
- `argument-hint` → `metadata.argument-hint` (`generate-work-item` only)

Added to all skills:

```yaml
compatibility: <MCP and vault requirements>
metadata:
  plugin: agile-workflow
  version: "0.4.0"
```

## Intentional extensions (keep)

| Extension | Location | Rationale |
| --- | --- | --- |
| `manifest.json` | per skill | Orchestrator input/output schemas — not in base spec |
| Plugin `references/` | `agile-workflow/references/` | Shared Azure mechanics, ticket structure — DRY across skills |
| `../../references/` links | SKILL.md bodies | One hop from skill root; document as plugin convention |
| Marketplace manifests | `.claude-plugin`, `.codex-plugin` | Multi-host distribution via `install.sh` |
| Python orchestrator | `orchestrator_core/` | Deterministic quality gates — plugin-level `scripts/` equivalent |
| `generate-work-item` auto-trigger | no `disable-model-invocation` | Description-driven discovery per user request |

## Remaining gaps (optional)

| Item | Priority | Action |
| --- | --- | --- |
| `license` frontmatter | low | Add `license: MIT` (or repo license) to each SKILL.md |
| Per-skill `scripts/` | low | Document `bin/agile-workflow` as plugin script root in README |
| `skills-ref to-prompt` | low | Evaluate bundling skill metadata for non-Cursor hosts |
| Open Skills listing | medium | Publish catalog cards on [openskills.cc](https://openskills.cc/) |
| `metadata.orchestrator-skill` | low | Link skills with `manifest.json` to orchestrator handlers |

## Directory layout (current vs spec)

```
agile-workflow/
├── skills/<name>/          # spec: skill folder
│   ├── SKILL.md            # required
│   ├── references/         # optional (generate-work-item, split-story, validate-artifact)
│   └── manifest.json       # extension (orchestrator)
├── references/             # plugin-shared (documented exception)
├── orchestrator_core/      # plugin runtime
└── .claude-plugin/         # marketplace packaging
```

## Progressive disclosure compliance

| Stage | Implementation |
| --- | --- |
| Discovery | Host loads `name` + `description` from each SKILL.md |
| Activation | Full SKILL.md on explicit invoke or description match |
| Execution | `references/`, enrichers, `../../references/`, orchestrator CLI on demand |

All skills under 500 lines. Detailed catalogs live in `references/` (split-patterns, validation-checks, blueprints, enrichers).

## Related

- [[Agent Skills Overview]]
- [[Open Skills Marketplace]]
- Feature: [[orchestrator-core]]
