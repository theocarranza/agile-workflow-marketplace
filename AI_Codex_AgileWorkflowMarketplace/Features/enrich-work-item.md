---
type: feature
skill: enrich-work-item
plugin: agile-workflow
---

# Enrich Work Item

**Inputs:** 
- source: one of url | path | text
- type: one of epic | feature | user-story
- parent: one of string | url
- attachment: one of url | path

## Description

Apply the enricher pattern for the informed work-item type. When the artifact is ready, present to the user the options for persisting the output:
1. Azure Devops Workspace
2. Codex Workflow AI Ledger if the project implements the Codex Workflow pattern

When `source` is an **Azure DevOps URL or work-item id**, ingest per `references/azure-ingest.md`: fetch the work item (`wit_get_work_item` with relations), download attachments (`wit_get_work_item_attachment` or REST), parse the description for linked documents/URLs/paths, and fold fetched content into enrichment context before applying the enricher. **Descrição Original** remains the work-item description verbatim.

## Outputs
Document with the exact format given by the corresponding type

## Implementation notes

1. Include the spec file with the blueprint for the output
2. include one canonical example file, use dummy/fake contents
3. the inputs must be obtained via available user interface, providing choices for constant values such as work item type, or a text input. The inputs must be requested one at the time, and each step must include a brief description of the purpose of the input, and if it is required or optional 
4. if the user does not inform any output destinations, simply output on the chat window, formatted as markdown, ready to be copied