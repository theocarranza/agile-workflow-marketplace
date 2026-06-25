---
type: feature
skill: auto-fix-artifact
plugin: agile-workflow
shipped: 2026-06-25
---

# auto-fix-artifact

Validates a single agile artifact and offers an auto-fix workflow if issues are found. Builds on `validate-artifact` quality gates and applies fixes based on the same reference rules. Accepts Azure work item ID, vault draft path, file system path, or raw text pasted inline.

## Links

- Session record: [[Agent_Sessions/2026-06-25-200000-validate-artifact-run]]

## Key decisions

- **Read-then-ask gate:** runs the full validation silently first, shows the report, then asks permission before touching anything — user is always in control.
- **Shares validate-artifact references:** reads `../validate-artifact/references/validation-checks.md` and `report-format.md` directly — no duplication.
- **Azure mutations use `wit_update_work_item`:** only called in PHASE 4, only after explicit user approval.
- **Traceability guardrail:** when updating Azure items, adds a comment noting the AI Codex applied automated quality fixes.
- **All-or-nothing persist:** user can discard after seeing the corrected diff — no partial saves.

## Sibling skills

- `validate-artifact` — read-only quality gate (upstream)
- `auto-fix-artifact` — validate + auto-correct (this skill)
- `split-story` — lateral sizing (downstream)
