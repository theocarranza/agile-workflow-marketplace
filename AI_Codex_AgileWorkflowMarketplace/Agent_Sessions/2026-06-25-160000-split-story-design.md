---
date: 2026-06-25
type: agent-session
status: open
---

# Session: split-story skill design

**Previous Session:** [[2026-06-25-143000-validate-artifact-skill]]
**Next Session:** (none yet)

**Scope:** Brainstorm and spec the `split-story` skill — lateral story sizing, split pattern detection, scoring, coverage check, and handoff menu.

---

## Implementation Checkpoint - 2026-06-25T16:00

**Scope:** Design spec — `split-story` skill.

**Changes:**

- Wrote `docs/superpowers/specs/2026-06-25-split-story-design.md` (179 lines).
- Committed: `6ddded3 docs: add split-story skill design spec`.

**Design decisions:**

- Five-phase conductor: INGEST → SCORE → ANALYZE → DRAFT → HANDOFF.
- Input: vault draft OR Azure ID.
- Point discrepancy: flag and ask user which value to trust.
- Spike detection: Incerteza == 5 AND sole MAX driver → recommend Spike instead of scope split.
- Split pattern: auto-detected from catalog (workflow step, business rule, happy/unhappy path, CRUD, data variation).
- Gate 1 after ANALYZE: show split plan, wait for approval before drafting.
- Coverage check in DRAFT: every original AC must map to exactly one sub-story.
- HANDOFF menu: keep drafts / create in Azure / discard.
- Two new skill-specific references: `split-patterns.md`, `scoring-guide.md`.

**Validation:** Design reviewed and approved by user across three sections.

---

## Implementation Checkpoint - 2026-06-25T17:00

**Scope:** Implementation plan — `split-story` skill.

**Changes:**

- Wrote `docs/superpowers/plans/2026-06-25-split-story.md` (777 lines, 3 tasks).
- Committed: `17bbe13 docs: add split-story implementation plan`.

**Plan structure:**

- Task 1: `split-patterns.md` — 5-pattern catalog with detection signals, counter-signals, auto-selection decision tree.
- Task 2: `scoring-guide.md` — 6-driver table, ceiling logic, spike detection, discrepancy-handling protocol.
- Task 3: `SKILL.md` — 5-phase conductor (INGEST/SCORE/ANALYZE/DRAFT/HANDOFF), Gate 1, coverage check, 3-option HANDOFF menu, guardrails.

**Self-review findings fixed:**

- Added `acceptance_criteria: string[]` to the INGEST artifact record (was in spec, missing from first draft).
- Fixed MD060/MD032/MD040 lint warnings in plan document.

**Validation:** Plan self-review passed. Committed cleanly.

---

## Implementation Checkpoint - 2026-06-25T18:00

**Scope:** Subagent-driven implementation of all 3 split-story tasks.

**Changes:**

- `56bb9a9` feat(split-story): add split-patterns reference catalog
- `3947a05` feat(split-story): add scoring-guide reference
- `fe795fe` feat(split-story): add SKILL.md conductor (5 phases, 2 gates)
- `1ad96db` fix(split-story): tighten read-back assertion — check parent link and absence of stray Related links

**Files delivered:**

- `agile-workflow/skills/split-story/references/split-patterns.md` — 5 patterns, counter-signals, auto-selection decision tree
- `agile-workflow/skills/split-story/references/scoring-guide.md` — 6-driver table, ceiling, spike stub, discrepancy prompt
- `agile-workflow/skills/split-story/SKILL.md` — 5-phase conductor, Gate 1, 3-option HANDOFF, 5 guardrails

**Final review findings fixed:**

- Important: SKILL.md PHASE 5 read-back assertion tightened to assert both `System.Parent` and absence of stray `System.LinkTypes.Related` links, matching `azure-mechanics.md` mandate.
- Minor (deferred): spike stub heading style (bold vs. bare emoji+label) — no operational impact.
- Minor (deferred): vacuous AC coverage pass for raw/filesystem input with no AC section — unspecified by spec.

**Validation:** All 3 tasks passed per-task review (spec ✅, quality Approved). Final whole-branch review passed after fix. 4 commits clean.
