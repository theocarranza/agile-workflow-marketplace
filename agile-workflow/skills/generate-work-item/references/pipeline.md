# generate-work-item — Pipeline

Entry point for the skill reference library. Distinguish three layers:

| Layer | Location | What it is |
| --- | --- | --- |
| **Vault artifacts** | `<vault>/Specs/`, `<vault>/Tickets/` | Generated specs and ticket drafts (real output) |
| **Blueprints** | `./blueprints/` | Blank forms the skill fills to produce vault artifacts |
| **Enrichers** | `./enrichers/` | Full prompts — authoritative rules for ticket body prose |

```
INGEST → RESEARCH (Context7) → WRITE SPEC (blueprint) → GENERATE DRAFT (enricher) → GATE → AZURE
         │                        │                        │
         │                        ▼                        ▼
         │                 <vault>/Specs/           <vault>/Tickets/Ready/
         └─ read enricher context + Context7
```

## Type map

| `work_item_type` | Spec blueprint | Ticket authority | Ticket quick-ref |
| --- | --- | --- | --- |
| `epic` | `blueprints/spec-epic.md` | `enrichers/epic-enricher.prompt.md` | `blueprints/ticket-quickref.md` § Epic |
| `feature` | `blueprints/spec-feature.md` | `enrichers/feature-enricher.prompt.md` | `blueprints/ticket-quickref.md` § Feature |
| `user-story`, `bug` | `blueprints/spec-work-item.md` | `enrichers/work-item-enricher.prompt.md` | `blueprints/ticket-quickref.md` § User Story |
| `task` | `blueprints/spec-work-item.md` | `enrichers/work-item-enricher.prompt.md` | `blueprints/ticket-quickref.md` § Task |

Host vault enricher copies (prefer when present): `<vault>/assets/*-enricher.prompt.md`

## Vault output paths

**Spec** (PHASE 3): `<vault>/Specs/[<parent-id>-]<kebab-slug>-spec.md`

**Ticket draft** (PHASE 4): `<vault>/Tickets/Ready/<prefix>-<kebab-slug>.md`

Shared spec frontmatter:

```yaml
---
type: spec
work_item_type: <Epic|Feature|User Story|Bug|Task>
ticket: <parent-id or null>
area: <kebab-area>
stack: [<from-context7>]
tags: [spec]
created: <YYYY-MM-DD>
source: [context7, <urls>]
---
```

## Context7 research protocol

1. Extract tech-stack tokens from `idea`, `refs`, `spec` input, parent body, enricher context.
2. Up to **3 libraries**: `resolve-library-id` → `query-docs`.
3. Fold findings into blueprint **Tech stack** + **Research summary** — cite `libraryId`.
4. If Context7 unavailable: `source: [manual]`; proceed from refs only.

## Host enricher context

Enrichers may reference host monorepo docs (`docs/domain.md`, etc.). Read when available; skip
gracefully when absent (marketplace-only vault).

## Shared plugin references

- `../../references/decomposition-rules.md` — hierarchy, story-point heuristic
- `../../references/ticket-structure.md` — vault hook constraints
- `../../references/azure-mechanics.md` — Azure MCP calls + gotchas
