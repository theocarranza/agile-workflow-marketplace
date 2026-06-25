---
type: feature
skill: split-story
plugin: agile-workflow
shipped: 2026-06-25
---

# split-story

Lateral story-sizing skill. Takes a single User Story, scores it with the 6-driver MAX heuristic, determines whether to split it (or recommend a Spike), auto-selects a split pattern, drafts sub-stories with coverage validation, and hands them off to the vault or Azure DevOps.

## Links

- Design spec: [[docs/superpowers/specs/2026-06-25-split-story-design]]
- Implementation plan: [[docs/superpowers/plans/2026-06-25-split-story]]
- Session record: [[Agent_Sessions/2026-06-25-160000-split-story-design]]

## Key decisions

- **4 input sources:** vault draft path, Azure work item ID, file system path, or raw text pasted inline — normalized into a single artifact record in INGEST.
- **Spike detection:** `Incerteza == 5` AND sole MAX driver → recommend Spike, not scope split.
- **Discrepancy handling:** declared vs. calculated point mismatch always surfaces to user — never auto-resolved.
- **Gate 1:** explicit user approval of split plan before any vault files are written.
- **Coverage check:** every original AC must map to exactly one sub-story's `📄 Descrição Original` — orphans and duplicates stop the run.
- **HANDOFF menu:** 3 options (keep / Azure / discard) — no auto-push without user consent.
- **Azure safety:** `wit_work_items_link` uses explicit `type: "parent"`; read-back asserts `System.Parent == feature_id` AND no stray `System.LinkTypes.Related` links.

## Sibling skills

- `decompose-backlog` — Feature → Stories (upstream)
- `validate-artifact` — quality gate on any artifact (lateral)
- `split-story` — Story → Stories (this skill)
