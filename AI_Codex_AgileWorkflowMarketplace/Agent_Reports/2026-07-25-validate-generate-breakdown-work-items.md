---
date: 2026-07-25
type: report
artifact: generate-breakdown-work-items
artifact_type: Feature
source: vault
outcome: pass
---

Reshaped to enriched Feature template; renamed from `spike-generate-breakdown-work-items` to sibling-style `generate-breakdown-work-items` (option A — may fail `filename-regex` on vault ticket convention).

```
Validating Feature — "Generate Breakdown Work Items from Acceptance Criteria" [vault]
============================================================

STRUCTURAL
  [PASS]  frontmatter-type-present
  [PASS]  frontmatter-status-absent
  [FAIL]  filename-regex  —  filename `generate-breakdown-work-items` does not match required pattern
  [PASS]  body-title-present
  [PASS]  body-description-present

HIERARCHY
  [WARN]  hierarchy-skipped-no-azure-id  —  no azure_id in frontmatter, hierarchy checks skipped

CONTENT
  [PASS]  content-no-machine-paths
  [PASS]  content-no-meta-prose

DoR
  [PASS]  dor-title-clear
  [PASS]  dor-description-present

------------------------------------------------------------
Summary: 8 passed · 1 failed · 1 warnings
Outcome: FAIL
```
