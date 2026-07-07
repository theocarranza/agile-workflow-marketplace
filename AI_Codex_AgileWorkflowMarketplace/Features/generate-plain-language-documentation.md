---
type: feature
skill: generate-plain-language-documentation
plugin: agile-workflow
---

# Generate Plain-Language Documentation

**Inputs:**
- source: one of text | path | url
- audience: string (optional; default feature owner)
- language: one of en | pt-br (optional; default en)
- document_type: one of general | report | guide | work-item-prose (optional)

## Description

Writes and rewrites human-facing prose in plain language — documentation, reports, guides, proposals,
and work-item narrative. Uses the vault tech glossary (`assets/tech-glossary-en-pt-br.json`) for
pt-BR translation and technical-term verification. When the artifact is ready, present persistence
options:

1. Vault Knowledge note (or user-named path)
2. Chat only — formatted markdown ready to copy

Sibling skills invoke this skill as a sub-pass for requirement bullets and narrative sections without
a separate user gate:

- `generate-work-item` — PHASE 4 (`## Requisitos`, `## Critérios de Aceite`)
- `enrich-work-item` — PHASE 4 (narrative inside enricher sections)
- `decompose-backlog` — PHASE 3 DRAFT (scope lines, section prose) and PHASE 4 ENRICH (story body
  narrative; preserves emoji headings and story-point driver tables)

## Outputs

Plain-language markdown document per `document_type`, or polished prose sections when invoked as a
sub-skill.

## Implementation notes

1. Skill package: `agile-workflow/skills/generate-plain-language-documentation/` (SKILL.md, manifest,
   references/, evals/).
2. Hard rules and quality gate live in `references/plain-language-principles.md` (derived from this
   feature spec's writing standard).
3. Glossary protocol in `references/glossary-usage.md` — exact, alias, substring, and reverse lookup.
4. Inputs obtained one at a time via host UI with brief purpose per field.
5. Standalone runs require explicit approval before vault writes; sub-skill mode defers to caller gate.
