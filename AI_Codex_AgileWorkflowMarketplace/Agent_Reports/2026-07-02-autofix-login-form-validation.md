---
date: 2026-07-02
type: report
artifact: 6869-login-form-validation
artifact_type: User Story
source: vault
outcome: pass
skill: auto-fix-artifact
---

# auto-fix-artifact exercise — vault draft `6869-login-form-validation`

Demonstration of the `auto-fix-artifact` skill workflow on a deliberately flawed vault draft.
Azure MCP was unavailable in this session; exercise used a vault filesystem source.

## Pre-fix input (simulated ingest)

Source file content before auto-fix (not persisted — vault hooks reject invalid frontmatter):

```yaml
---
date: 2026-07-02
status: draft          # forbidden key
work_item_type: User Story
parent_feature: 6869
# type: missing
---
```

Body had 4 of 7 required sections; title was 3 words; `TBD — to be defined` placeholder present; no story_points or Complexidade block.

## Phase 1 — Validation report (pre-fix)

```
Validating User Story — "Login form validation" [vault]
============================================================

STRUCTURAL
  [FAIL]  frontmatter-type-present  —  `type:` key missing
  [FAIL]  frontmatter-status-absent  —  `status: draft` found in frontmatter
  [PASS]  filename-regex  —  matches ^(\d+|tech-debt|bug|task|spike)-[a-z0-9-]+
  [FAIL]  body-section-missing: 🔧 Notas Técnicas
  [FAIL]  body-section-missing: 📊 Complexidade
  [FAIL]  body-section-missing: 📄 Descrição Original

HIERARCHY
  [WARN]  hierarchy-skipped-no-azure-id  —  no azure_id in frontmatter, hierarchy checks skipped

CONTENT
  [FAIL]  content-complexidade-breakdown  —  📊 Complexidade section absent
  [FAIL]  content-story-points-set  —  story_points not set in frontmatter
  [FAIL]  content-descricao-original-present  —  section absent
  [WARN]  content-no-meta-prose  —  found: TBD — to be defined during breakdown

DoR
  [FAIL]  dor-title-clear  —  3 words (minimum 6)
  [PASS]  dor-description-present  —  partial body present
  [FAIL]  dor-story-points-set  —  story points not set
  [FAIL]  dor-linked-to-feature  —  hierarchy-story-parent-is-feature skipped (no azure_id)

------------------------------------------------------------
Summary: 2 passed · 10 failed · 2 warnings
Outcome: FAIL
```

## Phase 2 — Decision gate

User approved auto-fix (exercise mode — implicit approval for demo).

## Phase 3 — Fixes applied

| Check | Fix |
|-------|-----|
| `frontmatter-type-present` | Added `type: ticket` |
| `frontmatter-status-absent` | Removed `status: draft` |
| `body-section-missing` (×3) | Added Notas Técnicas, Complexidade (with 6-driver table), Descrição Original |
| `content-complexidade-breakdown` | Populated drivers; MAX=3 (Escopo=3) |
| `content-story-points-set` | Set `story_points: 3` in frontmatter |
| `content-descricao-original-present` | Added verbatim parent slice |
| `content-no-meta-prose` | Replaced TBD with concrete behavior bullets |
| `dor-title-clear` | Expanded title to 7 words (pt-BR) |

Hierarchy and `dor-linked-to-feature` remain WARN/SKIP — no `azure_id`; acceptable for vault-only draft.

## Phase 4 — Post-fix validation

```
Validating User Story — "Validação de campos do formulário de login" [vault]
============================================================

STRUCTURAL
  [PASS]  frontmatter-type-present
  [PASS]  frontmatter-status-absent
  [PASS]  filename-regex
  [PASS]  body-sections  —  all 7 required sections present

HIERARCHY
  [WARN]  hierarchy-skipped-no-azure-id  —  no azure_id in frontmatter

CONTENT
  [PASS]  content-complexidade-breakdown
  [PASS]  content-story-points-set  —  3 points
  [PASS]  content-descricao-original-present
  [PASS]  content-no-machine-paths
  [PASS]  content-no-meta-prose

DoR
  [PASS]  dor-title-clear  —  7 words
  [PASS]  dor-description-present
  [PASS]  dor-story-points-set  —  3 points
  [SKIP]  dor-linked-to-feature  —  hierarchy skipped (no azure_id)

------------------------------------------------------------
Summary: 11 passed · 0 failed · 1 warning
Outcome: PASS
```

**Persist:** Corrected draft saved to `Tickets/Ready/6869-login-form-validation.md`.
**Azure:** Not applicable (vault source, no azure_id).
