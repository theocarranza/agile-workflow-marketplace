---
type: reference
source: https://agentskills.io/home
domain: agentskills.io
retrieved: 2026-07-06
tags: [reference, research, agent-skills, standards]
area: agile-workflow-marketplace
---

# Agent Skills Overview

> [!info] Source
> Ingested from [agentskills.io](https://agentskills.io/home) on 2026-07-06. Cleaned from fetched markdown — verify against the [specification](https://agentskills.io/specification) before relying on specifics.

## What are Agent Skills?

Agent Skills are a **lightweight, open format** for extending AI agent capabilities with specialized knowledge and workflows. Originally developed by Anthropic, released as an open standard, adopted by Cursor, Claude Code, Codex, VS Code, Gemini CLI, and many others.

At minimum, a skill is a **folder containing `SKILL.md`** with YAML frontmatter (`name`, `description`) plus markdown instructions. Optional directories:

```
my-skill/
├── SKILL.md          # Required: metadata + instructions
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
├── assets/           # Optional: templates, resources
```

## Progressive disclosure (three stages)

1. **Discovery** — At startup, agents load only `name` and `description` for each skill (~100 tokens each).
2. **Activation** — When a task matches the description, the agent reads the full `SKILL.md` body (<5000 tokens recommended; <500 lines).
3. **Execution** — Agent follows instructions; loads `scripts/`, `references/`, `assets/` on demand.

## Specification highlights ([agentskills.io/specification](https://agentskills.io/specification))

### Required frontmatter

| Field | Constraints |
| --- | --- |
| `name` | 1–64 chars; lowercase `a-z`, `0-9`, hyphens; must match parent directory name; no leading/trailing `--` |
| `description` | 1–1024 chars; what + when; keywords for trigger matching |

### Optional frontmatter

| Field | Purpose |
| --- | --- |
| `license` | License name or bundled file reference |
| `compatibility` | Environment requirements (product, packages, network) |
| `metadata` | Arbitrary string key-value map (`author`, `version`, …) |
| `allowed-tools` | Space-separated pre-approved tools (experimental) |

### Authoring guidance

- Body: step-by-step instructions, examples, edge cases — no strict schema.
- Reference files **one level deep** from `SKILL.md`; avoid deep chains.
- Split long content into `references/` for on-demand loading.
- Validate with `skills-ref validate ./my-skill`.

## Why it matters for teams

- **Domain expertise** — procedural knowledge in version-controlled packages.
- **Repeatable workflows** — multi-step tasks as auditable procedures.
- **Cross-product reuse** — build once, run on any compatible agent host.

## Related docs index

Full doc map: [agentskills.io/llms.txt](https://agentskills.io/llms.txt)

- [Specification](https://agentskills.io/specification)
- [Quickstart](https://agentskills.io/skill-creation/quickstart)
- [Best practices for skill creators](https://agentskills.io/skill-creation/best-practices)
- [Optimizing skill descriptions](https://agentskills.io/skill-creation/optimizing-descriptions)
- [Adding skills support to your agent](https://agentskills.io/client-implementation/adding-skills-support)
