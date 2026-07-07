# generate-work-item — Pipeline

Entry point for the skill reference library.

```
COLLECT → INGEST → RESEARCH (Context7) → WRITE SPEC (blueprint) → GENERATE DRAFT → GATE → PERSIST
         │                              │                        │
         │                              ▼                        ▼
         │                       <vault>/Specs/           <vault>/Tickets/Ready/
         └─ parent + attachment context
```

## Type map

| `work_item_type` | Spec blueprint | Ticket body |
| --- | --- | --- |
| `epic` | `blueprints/spec-epic.md` | `canonical/canonical-epic.md` |
| `feature` | `blueprints/spec-feature.md` | `canonical/canonical-feature.md` |
| `user-story` | `blueprints/spec-work-item.md` | `canonical/canonical-user-story.md` |

Enrichment (emoji sections, drivers, host team format) is **`enrich-work-item`**, not this skill.

Prose polish for requirement bullets: **`generate-plain-language-documentation`** sub-pass in PHASE 4
(see `../generate-plain-language-documentation/references/integration-notes.md`).

## Vault output paths

**Spec** (PHASE 3): `<vault>/Specs/[<parent-id>-]<kebab-slug>-spec.md`

**Ticket draft** (PHASE 4): `<vault>/Tickets/Ready/<prefix>-<kebab-slug>.md`

Shared spec frontmatter:

```yaml
---
type: spec
work_item_type: <Epic|Feature|User Story>
ticket: <parent-id or null>
area: <kebab-area>
stack: [<from-context7>]
tags: [spec]
created: <YYYY-MM-DD>
source: [context7, <urls>]
---
```

## Context7 research protocol

1. Extract tech-stack tokens from `title`, `description`, `attachment`, parent body.
2. Up to **3 libraries**: `resolve-library-id` → `query-docs`.
3. Fold findings into blueprint **Tech stack** + **Research summary** — cite `libraryId`.
4. If Context7 unavailable: `source: [manual]`; proceed from supplied context only.

## Shared plugin references

- `../../references/decomposition-rules.md` — hierarchy, sizing heuristic
- `../../references/ticket-structure.md` — vault hook constraints
- `../../references/azure-mechanics.md` — Azure MCP calls + gotchas
