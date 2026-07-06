---
type: reference
source: https://openskills.cc/
domain: openskills.cc
retrieved: 2026-07-06
tags: [reference, research, agent-skills, marketplace]
area: agile-workflow-marketplace
---

# Open Skills Marketplace

> [!info] Source
> Ingested from [openskills.cc](https://openskills.cc/) on 2026-07-06. Marketplace landing page snapshot — not the full skill catalog.

## What it is

[Open Skills](https://openskills.cc/) is a **public discovery directory** for open-source Agent Skills — 1800+ listed at time of ingest. It promotes the same folder format as [agentskills.io](https://agentskills.io/home):

```
my-skill/
├── SKILL.md          # Required
├── scripts/
├── references/
└── assets/
```

Users browse by category (Product Design, Development Tools, Document Processing, Persona, …), view download/popularity signals, and install with one click or copy a command (e.g. for OpenClaw).

## Value proposition (from site)

| Audience | Benefit |
| --- | --- |
| Skill authors | Build once, deploy across agent products |
| Compatible agents | End users add capabilities without custom wiring |
| Teams / enterprises | Portable, version-controlled knowledge packages |

## Lifecycle model (same as agentskills.io)

1. **Discovery** — metadata at startup
2. **Activation** — full instructions when task matches
3. **Execution** — scripts/references/assets on demand

## Relation to agentskills.io

- **agentskills.io** — open **standard**, specification, client implementation guides.
- **openskills.cc** — **distribution/discovery** layer on top of the same format (Anthropic-origin standard).

## Implications for agile-workflow-marketplace

A marketplace plugin could list on Open Skills for discoverability while staying spec-compliant. Our differentiator is not the folder shape (already aligned) but **domain workflows** (Azure DevOps, vault ledger, orchestrator critic) bundled as a plugin marketplace rather than loose skills.
