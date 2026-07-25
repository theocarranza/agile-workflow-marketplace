---
date: 2026-07-25
type: ticket
work_item_type: User Story
parent_feature_vault: Features/generate-breakdown-work-items.md
language: en
story_points: 3
tags: [ticket, user-story, breakdown-work-items]
---

# Intake and Selection UX for the Breakdown Skill

## 🎯 What

Ask the user for the Work Item ID, URL, or File System / Ledger reference that identifies the source User Story (or Feature/Epic for a fan-out run).
Ask the user for the output destination: file system location, Azure Task board, or both.
Ask the user for the output language, defaulting to English when none is informed.
Render every known invariant option (such as output destinations) as a selectable list, with single or multiple selection depending on context.
Render every known variant option (such as the list of Task work items per User Story) as a multi-select list that includes an `all` choice.
Always include `other (inform or describe)` as the last option on any selectable list.
Tag the first option with `Recommended` whenever the choice requires judgment.

## 💡 Why

Every later step of the breakdown workflow — Implementation Plan generation, Task decomposition, and fan-out across a Feature or Epic — depends on knowing which Story to work on, where to write the output, and in which language. Collecting these choices up front keeps the rest of the flow deterministic and avoids re-prompting mid-run.

## 📋 Expected Behavior

```
User input
   |
   v
[ID / URL / ledger ref] --> resolve source Work Item
   |
   v
[destination?] --> (file system | Azure Task board | both | other)
   |
   v
[language?] --> (en [default] | pt-BR | other)
   |
   v
Confirmed selections passed to downstream Stories
```

## ✅ Acceptance Criteria

- [ ] Given no Work Item ID, URL, or reference is provided, the user is prompted for one before continuing
- [ ] Given no destination is informed, the user sees a selectable list including file system, Azure Task board, both, and `other (inform or describe)`
- [ ] Given no language is informed, the language defaults to `en`
- [ ] Every invariant/variant option list ends with `other (inform or describe)`
- [ ] An `all` choice is offered whenever a variant option supports multiple selection
- [ ] The first option carries a `Recommended` tag whenever the choice requires judgment

## 🔧 Technical Notes

- Area: `agile-workflow` plugin, breakdown skill's intake layer — selection only, no Ledger or Azure writes in this Story.
- Consumed by the Implementation Plan Generation and Task Decomposition Stories.

## 📊 Complexity

**3 points** — Largest driver: Scope=3, Uncertainty=2, Integrations=1, Data=1, QA=2, Rollout=1 → 3 points

| Driver | Score |
|--------|-------|
| Scope | 3 |
| Uncertainty | 2 |
| Integrations | 1 |
| Data | 1 |
| QA | 2 |
| Rollout | 1 |

## 📄 Original Description

> ### Arguments and inputs
> 1. Ask the user for the Work Item ID, URL or File System / Ledger reference
> 2. Ask the user for the output destination, must be one of file system location, Azure Task board, or both
> 3. If no destination language is informed (one of en or pt-BR), assume the default en
>
> ### UI / UX
> 1. The known invariant options (such as output destinations) must be shown as selectable options with single or multiple selections as per context
> 2. The known variants (such as the Task work items list per User Story) must be shown as selectable options with single or multiple selections as per context with an option of `all` to include all multiple selection items
> 3. The option `other (inform or describe)` must always be the last option on the list and must always be included
> 4. A tag `Recommended` must always be added to a option when the context requires judgment, and such item must be the first on the list
