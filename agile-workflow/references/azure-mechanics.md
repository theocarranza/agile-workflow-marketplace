# Azure DevOps Mechanics

The exact MCP calls and the traps that bite if you skip them. These are invariant — not seams.

## Read a work item (ingest)

Use `wit_get_work_item(id=<id>, expand=relations)` to load fields and relations in one call.

**URL → id:** Azure work-item URLs end with `/_workitems/edit/{id}` or `/_workitems/view/{id}`.
Extract the numeric `{id}` segment.

**Attachments:** With `expand=relations`, each `AttachedFile` relation includes `attributes.name`
and a `url` ending in the attachment GUID. Download via `wit_get_work_item_attachment` when the MCP
server supports it; otherwise REST:

```
GET https://dev.azure.com/{org}/{project}/_apis/wit/attachments/{attachmentId}?fileName={fileName}&download=true&api-version=7.1
```

Auth: MCP credentials, or `AZURE_DEVOPS_EXT_PAT` / `ADO_PAT` (Basic, empty username), or `az login`.

**Description references:** Parse `System.Description` for markdown links, bare URLs, filenames that
match attachment names, and vault/repo paths. Fetch those sources into supplementary context before
enrichment — see `enrich-work-item/references/azure-ingest.md` for the full bundle rules.

## Create a Story

Use `wit_create_work_item` (project = host's Azure project; repo context as needed):
- `workItemType: "User Story"` (or Bug/Tech Debt/Spike).
- **Description in Markdown format** — Markdown descriptions render fenced ASCII diagrams. Plain-text
  format mangles them.
- Set Story Points and tags at creation when supported.

## Link to parent — TWO GOTCHAS

### Gotcha 1 — always pass an explicit `type`
`wit_work_items_link` **defaults to `type: "related"`.** Omitting `type` silently creates a wrong
**Related** link instead of a parent link. ALWAYS pass `type: "parent"` explicitly.

### Gotcha 2 — a Story's parent is its FEATURE, not the Epic
Link the Story to the **Feature id**, never the Epic id. Skipping the Feature level breaks the
Epic→Feature→Story chain. If you have been handling the Epic id all session, do not reflexively reuse
it here — the parent is the Feature.

Fix sequence if a wrong link was made:
```
wit_work_item_unlink   id=<story> type=related      # remove the stray Related link
wit_work_item_unlink   id=<story> type=parent       # remove a wrong parent (e.g. → Epic)
wit_work_items_link    id=<story> linkToId=<feature> type=parent
```

## Rendering rules

- Work-item **description** bodies: **ASCII diagrams only.** Mermaid does NOT render in work-item
  descriptions (it renders only in the Wiki). Inline SVG is unsupported.
- Keep parentheses inside ASCII diagram boxes; outside diagrams, prefer one sentence per line.

## Verify (read-back, every time)
After creating + linking, read the item back and assert `System.Parent == <feature id>` and that the
sole hierarchy relation is Parent → the Feature. A failed assertion STOPS the run.
