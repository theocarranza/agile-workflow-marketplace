# Ticket Structure & Draft Constraints

How each Story draft is written so it (a) passes the host vault's hooks and (b) carries the
enriched body that becomes the exact Azure work-item description.

## Draft location (configurable seam)

Default: `Tickets/Ready/` in the host vault. If the host organizes drafts elsewhere, adapt — this
is a default, not a hard requirement.

## Frontmatter (hook-validated)

```yaml
---
date: <YYYY-MM-DD>
type: ticket            # REQUIRED — the frontmatter hook rejects drafts missing `type`
work_item_type: User Story
parent_feature: <feature-id>
parent_epic: <epic-id>
azure_id: <assigned-after-creation>
tags: [ticket, user-story, ...]
---
```

**Hard constraint:** do NOT include a `status:` key — the originating vault's hook forbids `status`
in `Tickets/`. Lifecycle lives in Azure, not in frontmatter.

## Filename (hook-validated)

Regex: `^(\d+|tech-debt|bug|task|spike)-[a-z0-9-]+`, all lowercase.

Until Azure assigns the real id, prefix with the **parent Feature id** (e.g.
`6868-us1-...`). After creation, rename to the **Azure-assigned id** (e.g. `6870-...`) and set
`azure_id` in frontmatter. Never use `FINAL`, `us1` is fine only as a mid-name token, not a prefix.

## Body sections (order)

The body is written once and becomes the Azure description verbatim. Section labels follow the host
team's language (originating team uses pt-BR):

1. **🎯 O quê** — what, as descriptive sentences, one idea per line.
2. **💡 Por quê** — why this Story exists.
3. **📋 Comportamento esperado** — expected behavior; ASCII diagrams here (see azure-mechanics.md).
4. **✅ Critérios de Aceite** — acceptance criteria as checkboxes.
5. **🔧 Notas Técnicas** — technical notes; areas/modules, not invented implementation.
6. **📊 Complexidade** — story points + the per-driver MAX justification (decomposition-rules.md).
7. **📄 Descrição Original** — the verbatim parent slice this Story traces to.

## Content hygiene

- State each fact ONCE, in its natural section. No repetition across sections.
- No machine-specific paths or local-only / spike folder references; the project repo is the
  canonical root.
- Locale-correct technical vocabulary; no calques from English.
- No decision-making/meta in the body. An unresolved choice becomes an `@TODO (decide in breakdown)`
  annotation, never prose pretending to be a requirement.
- Focus on the WHAT and WHERE (area/module), never invent the HOW.
