---
type: feature
source: |-
  https://learn.microsoft.com/en-us/azure/devops/boards/get-started/plan-track-work?view=azure-devops&tabs=agile-process
  https://learn.microsoft.com/en-us/azure/devops/boards/work-items/about-work-items?view=azure-devops&tabs=agile-process
tags:
  - azure
  - work-item
  - user-story
  - tracking
  - agile-workflow
created: 2026-07-25
skill: generate-breakdown-work-items
plugin: agile-workflow
status: active
---

# Generate Breakdown Work Items from Acceptance Criteria

## 🎯 Objective

Enable a team, starting from a User Story (or from a Feature/Epic with child Stories), to obtain atomic child Tasks aligned to acceptance criteria — with an implementation plan in the AI Codex Ledger — so delivery work is traceable, testable, and ready to execute on the board.

## 📦 Scope

### Included

- Per–User Story workflow: read Feature and Story, analyze acceptance criteria, generate an implementation plan in the ledger, decompose into atomic Tasks (atomic-commit concept), attach as children
- Default Staging and Review Tasks always included; final Breakdown Task assigned to the Story assignee and moved to Done
- Fan-out from Feature or Epic: run the workflow for each child User Story
- Output destination: filesystem/ledger, Azure Task board, or both; language en (default) or pt-BR
- Selection UX: invariant and variant options (incl. `all`), last option always `other (inform or describe)`, `Recommended` tag on the first option when judgment is required

### Excluded (Out of Scope)

- Inventing or rewriting the User Story acceptance criteria
- Estimating story points or complexity at the Feature level
- Implementing target-product code — only generate and persist work items / plan

## ✅ Success Criteria

- [ ] Given a User Story with acceptance criteria, the skill generates child Tasks that cover those criteria plus Staging, Review, and Breakdown
- [ ] The implementation plan is saved to the AI Codex Ledger before Tasks are created
- [ ] The Breakdown Task is Done and assigned to the same user as the User Story
- [ ] Destinations (ledger, Azure, both) and language (en | pt-BR) follow the user’s choice
- [ ] UI selections follow the invariant/variant, `all`, `other`, and `Recommended` rules

## 🔧 Areas/Modules Involved

- Plugin `agile-workflow` (new breakdown skill)
- Azure Boards (child Tasks under User Story)
- AI Codex Ledger (implementation plan and drafts)

## 📄 Original Description

Given a parent User Story, generate one or more Task for each entry on the acceptance criteria list. The objective is to have tasks (child work items) representing atomic units of work that, together, describe the process and steps to delivering what is required by the user story.

### User Story Workflow
Given a Work item of type User Story
1. Read the parent Feature body
2. Read the User Story body
3. Analyze the acceptance criteria list
4. Generate the Implementation Plan for the user Story and save it on the local AI Codex Ledger
5. Break the Implementation Plan in atomic tasks so that a task obeys the description of an atomic commit in concept (atomic, self contained unit of work that will add a single change to the project and can be tested with a unit test)
6. Add the tasks to the User Story as children work items
7. The default tasks Staging and Review must be always added
8. Add a last task named "Breakdown", assign it to the same user assigned to the User Story, and move the task to done

### Epic or Feature Workflow
Given a Work Item of Type Feature or Epic
1. Read the work item's children
2. For each User Story, execute `User Story Workflow`

### Arguments and inputs
1. Ask the user for the Work Item ID, URL or File System / Ledger reference
2. Ask the user for the output destination, must be one of file system location, Azure Task board, or both
3. If no destination language is informed (one of en or pt-BR), assume the default en

### UI / UX
1. The known invariant options (such as output destinations) must be shown as selectable options with single or multiple selections as per context
2. The known variants (such as the Task work items list per User Story) must be shown as selectable options with single or multiple selections as per context with an option of `all` to include all multiple selection items
3. The option `other (inform or describe)` must always be the last option on the list and must always be included
4. A tag `Recommended` must always be added to a option when the context requires judgment, and such item must be the first on the list
