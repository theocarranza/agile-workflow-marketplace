# generate-work-item — Output Formats

Uniform ticket body for **all** work-item types. This skill produces **raw** drafts — not enricher
layouts. For team emoji sections and complexity drivers, run `enrich-work-item` on the result.

## Canonical templates (read-only)

Shape contracts live in `./canonical/` — **do not edit** these files:

| Type | Template |
| --- | --- |
| `epic` | `canonical/canonical-epic.md` |
| `feature` | `canonical/canonical-feature.md` |
| `user-story` | `canonical/canonical-user-story.md` |

All three share the same skeleton. Validate every draft against the matching template before presenting.

## Ticket body (required shape)

Every draft — Epic, Feature, or User Story — uses the same markdown skeleton:

```markdown
# <Title>

[[Specs/<spec-basename>]]

## Requisitos

- <Requirement bullet — WHAT, not HOW>
- <Another requirement>

## Critérios de Aceite

- [ ] <Testable outcome — infinitive verb>
- [ ] <Another criterion>
```

### Rules

| Part | Rule |
| --- | --- |
| Title | Single `#` heading; objective-focused |
| Spec link | Obsidian wikilink to the spec written in PHASE 3 |
| Requisitos | Flat bullet list under `## Requisitos` for every type |
| Acceptance | `## Critérios de Aceite` with `- [ ]` checkboxes only |
| Diagrams | ASCII in requirements when helpful; no Mermaid in Azure-bound bodies |
| Locale | Match the language of the input `description` |

### Requirements quality

- Derive bullets from `description`, parent context, `attachment`, and Context7 research.
- State WHAT and observable behavior; avoid prescribing implementation unless the author did.
- Preserve technical names from the original description.
- Epic bullets: strategic outcomes. Feature bullets: scoped capability. Story bullets: one-sprint scope.

### Acceptance criteria quality

- Testable, user- or business-observable outcomes.
- No obvious criteria ("code compiles", "tests pass").
- Proportional count: simple items 3–5; moderate 5–7; complex up to 10.

## Type vs scope guard

If `description` describes multi-package / pipeline / multi-week work but `work_item_type` is
`user-story`, STOP — recommend `feature` or `epic` and ask once.

## Frontmatter and filename

Per `../../references/ticket-structure.md`:

```yaml
---
date: <YYYY-MM-DD>
type: ticket
work_item_type: <Epic|Feature|User Story>
parent_feature: <feature-id when applicable>
parent_epic: <epic-id when applicable>
tags: [ticket, <type>]
---
```

- No `status:` key.
- Filename: `^(\d+|tech-debt|bug|task|spike)-[a-z0-9-]+$`, lowercase.
- Until Azure assigns an id, prefix with parent Feature id (e.g. `6868-login-validation`).

## Azure description

The ticket **body** (below frontmatter) becomes the Azure work-item description verbatim when the
user chooses Azure persistence. Markdown format required (see `azure-mechanics.md`).
