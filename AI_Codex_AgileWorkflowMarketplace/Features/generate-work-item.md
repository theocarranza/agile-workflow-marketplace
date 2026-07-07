---
type: feature
skill: generate-work-item
plugin: agile-workflow
---

# Generate Work Item

**Inputs:** 
- title string
- description string
- type: one of epic | feature | user-story
- parent: one of string | url
- attachment: one of url | path

## Description

Generates a work item for the inputs received. When the artifact is ready, present to the user the options for persisting the output:
1. Azure Devops Workspace
2. Codex Workflow AI Ledger if the project implements the Codex Workflow pattern

## Outputs

Bullet point list of requirements or short descriptive sentences
Numbered list of acceptance criteria
ANSII diagrams (if applicable)
References (urls, or internal links)

## Implementation notes

1. Include the spec file with the blueprint for the output
2. include one canonical example file, use dummy/fake contents
3. the inputs must be obtained via available user interface, providing choices for constant values such as work item type, or a text input. The inputs must be requested one at the time, and each step must include a brief description of the purpose of the input, and if it is required or optional 
4. if the user does not inform any output destinations, simply output on the chat window, formatted as markdown, ready to be copied