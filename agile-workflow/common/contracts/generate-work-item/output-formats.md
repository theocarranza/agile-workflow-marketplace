# generate-work-item — Output Formats

Uniform ticket body for **all** work-item types. This skill produces **raw** drafts — not enricher
layouts. For team emoji sections and complexity drivers, run `enrich-work-item` on the result. For
plain-language requirement and acceptance-criteria wording, run
`generate-plain-language-documentation` (work-item-prose sub-pass) before presenting.

## Canonical templates (read-only)

Shape contracts live in `./canonical/` — **do not edit** these files:

| Type | Template |
| --- | --- |
| `epic` | `canonical/canonical-epic.md` |
| `feature` | `canonical/canonical-feature.md` |
| `user-story` | `canonical/canonical-user-story.md` |
| `task` | `canonical/canonical-task.md` |

All four share the same skeleton. Validate every draft against the matching template before presenting.

## Ticket body (required shape)

Every draft — Epic, Feature, User Story, or Task — uses the same markdown skeleton:

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
  Task bullets: one atomic implementation outcome.

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
work_item_type: <Epic|Feature|User Story|Task>
provider: <local|azure-devops|linear>
provider_id: "<provider identifier; omit before provider creation>"
parent_id: "<immediate parent identifier; omit for Epic>"
tags: [ticket, <type>]
---
```

- No `status:` key.
- Filename: `^(\d+|tech-debt|bug|task|spike)-[a-z0-9-]+$`, lowercase.
- Until a provider assigns an id, prefix with the immediate parent id.

## Provider description

The ticket **body** becomes the Azure DevOps or Linear item description verbatim. Use Markdown.
