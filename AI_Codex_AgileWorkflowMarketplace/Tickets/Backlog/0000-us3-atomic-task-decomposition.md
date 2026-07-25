---
date: 2026-07-25
type: ticket
work_item_type: User Story
parent_feature_vault: Features/generate-breakdown-work-items.md
language: en
story_points: 5
tags: [ticket, user-story, breakdown-work-items]
---

# Atomic Task Decomposition and Work Item Attachment

## 🎯 What

Break the saved Implementation Plan into atomic Tasks, each scoped to a single atomic commit — one self-contained, testable unit of work.
Always add a default Staging Task and a default Review Task.
Add a final Task named "Breakdown", assign it to the same user assigned to the User Story, and move it to Done.
Attach every generated Task to the User Story as a child work item.
Write the Tasks to the destination(s) chosen during intake — file system/ledger, Azure Task board, or both.

## 💡 Why

Atomic, testable Tasks are what make the Implementation Plan executable and trackable on the board; the Staging/Review/Breakdown convention keeps every Story's Task list consistent and signals completion the same way across the team.

## 📋 Expected Behavior

```
Implementation Plan
        |
        v
 split into atomic Tasks (1 task = 1 atomic commit)
        |
        +--> Task: Staging (always)
        +--> Task: Review (always)
        +--> Task: Breakdown (assignee = Story assignee, status = Done)
        |
        v
 attach all Tasks as children of the User Story
        |
        v
 write to destination(s): ledger | Azure Task board | both
```

## ✅ Acceptance Criteria

- [ ] Every Task derived from the Plan is scoped to a single atomic, testable unit of work
- [ ] A Staging Task and a Review Task are present on every run, regardless of Plan content
- [ ] A "Breakdown" Task is added last, assigned to the User Story's assignee, and set to Done
- [ ] All generated Tasks are attached as children of the User Story
- [ ] Tasks are written to the destination(s) selected during intake (file system, Azure Task board, or both)

## 🔧 Technical Notes

- Area: Azure Boards (child Task creation, assignment, status transition), AI Codex Ledger (file write).
- Depends on the Implementation Plan saved by the Plan Generation Story and the destination choice from the Intake Story.

## 📊 Complexity

**5 points** — Largest driver: Scope=3, Uncertainty=3, Integrations=5, Data=3, QA=3, Rollout=2 → 5 points

| Driver | Score |
|--------|-------|
| Scope | 3 |
| Uncertainty | 3 |
| Integrations | 5 |
| Data | 3 |
| QA | 3 |
| Rollout | 2 |

## 📄 Original Description

> ### User Story Workflow (continued)
> 5. Break the Implementation Plan in atomic tasks so that a task obeys the description of an atomic commit in concept (atomic, self contained unit of work that will add a single change to the project and can be tested with a unit test)
> 6. Add the tasks to the User Story as children work items
> 7. The default tasks Staging and Review must be always added
> 8. Add a last task named "Breakdown", assign it to the same user assigned to the User Story, and move the task to done
>
> ### Scope
> Output destination: filesystem/ledger, Azure Task board, or both; language en (default) or pt-BR
