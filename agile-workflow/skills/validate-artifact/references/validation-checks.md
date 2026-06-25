# Validation Check Catalog

Full set of checks run by the `validate-artifact` skill, organized by category and artifact type.
Each check emits: `{ name, result: PASS|FAIL|WARN|SKIP, detail }`.

## a) STRUCTURAL

### Vault draft only

| Check | Condition | Result |
|---|---|---|
| `frontmatter-type-present` | `type:` key exists in frontmatter | FAIL if absent |
| `frontmatter-status-absent` | `status:` key NOT present in frontmatter | FAIL if present |
| `filename-regex` | Filename matches `^(\d+|tech-debt|bug|task|spike)-[a-z0-9-]+` | FAIL if no match |

### All sources — body sections

**User Story** — all 7 sections must be present. Emit one `body-section-missing: <name>` FAIL per absent section.

Required sections (detect by emoji + label heading):
- `🎯 O quê`
- `💡 Por quê`
- `📋 Comportamento esperado`
- `✅ Critérios de Aceite`
- `🔧 Notas Técnicas`
- `📊 Complexidade`
- `📄 Descrição Original`

**Feature / Epic** — title non-empty AND description non-empty. FAIL if either absent.

## b) HIERARCHY

Requires Azure MCP (`wit_get_work_item`). If `azure_id` is null and source is vault, emit
`WARN hierarchy-skipped-no-azure-id` and skip the entire category.

Failures are logged and validation continues to the next check.

| Artifact | Assertion | Check name | Result |
|---|---|---|---|
| User Story | `System.Parent` exists and its `WorkItemType == "Feature"` | `hierarchy-story-parent-is-feature` | FAIL if parent is Epic or missing |
| Feature | `System.Parent` exists and its `WorkItemType == "Epic"` | `hierarchy-feature-parent-is-epic` | FAIL if missing or wrong type |
| Epic | No child items with `WorkItemType == "User Story"` | `hierarchy-epic-no-direct-stories` | FAIL if any direct Story children found |

## c) CONTENT

### User Story only

| Check | Condition | Result |
|---|---|---|
| `content-complexidade-breakdown` | `📊 Complexidade` section contains per-driver scores — keywords: Escopo, Incerteza, Integrações, Dados, QA, Rollout | FAIL if absent |
| `content-story-points-set` | Story points field > 0 (frontmatter `story_points` or Azure `Microsoft.VSTS.Scheduling.StoryPoints`) | FAIL if unset or 0 |
| `content-descricao-original-present` | `📄 Descrição Original` section is non-empty | FAIL if empty |

### All artifact types

| Check | Condition | Result |
|---|---|---|
| `content-no-machine-paths` | Body does not contain absolute filesystem paths — pattern: `/home/`, `/Users/`, `C:\`, `D:\` | WARN if found |
| `content-no-meta-prose` | Body does not contain placeholder prose (`TBD`, `to be defined`, `a definir`) outside `@TODO` annotation context | WARN if found |

## d) DoR (Definition of Ready)

Applied to all artifact types unless noted.

| Check | Condition | Result |
|---|---|---|
| `dor-title-clear` | Title non-empty and word count > 5 | FAIL if not met |
| `dor-description-present` | Body / description field non-empty | FAIL if not met |
| `dor-story-points-set` *(User Story only)* | Story points > 0 | FAIL if not met |
| `dor-linked-to-feature` *(User Story only)* | Reuses result of `hierarchy-story-parent-is-feature` — no extra MCP call | FAIL if that check failed or was skipped |
