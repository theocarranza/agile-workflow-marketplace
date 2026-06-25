# split-story Skill — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the `split-story` skill — a 5-phase conductor that takes a single User Story, scores it with the 6-driver MAX heuristic, determines if/how to split it, drafts sub-stories with coverage validation, and hands them off to the vault or Azure.

**Architecture:** Three markdown files are created under `agile-workflow/skills/split-story/`. Two skill-specific reference files (`split-patterns.md`, `scoring-guide.md`) provide structured lookup tables the SKILL.md conductor reads at runtime. The conductor itself (`SKILL.md`) is a self-contained prompt with all phase logic inline and pointers to shared + skill-specific references.

**Tech Stack:** Markdown conductor files; Azure DevOps MCP (`wit_get_work_item`, `wit_create_work_item`, `wit_work_items_link`); Obsidian vault at `AI_Codex_AgileWorkflowMarketplace/`.

## Global Constraints

- All three files are plain markdown — no code execution, no build step.
- Shared references live at `agile-workflow/references/` — never duplicated inside the skill.
- Skill-specific references live at `agile-workflow/skills/split-story/references/`.
- SKILL.md frontmatter must include `name:`, `description:`, and `allowed-tools:` keys.
- No `status:` key anywhere in vault draft frontmatter produced by the skill.
- Filename pattern for vault drafts: `^(\d+|tech-debt|bug|task|spike)-[a-z0-9-]+`, all lowercase.
- Azure links always use explicit `type: "parent"` in `wit_work_items_link`.
- After `wit_create_work_item`, always read back with `wit_get_work_item` and assert `System.Parent == feature_id` before reporting success.
- Default story-point ceiling: 5. Overridable per invocation.
- Spike detection rule: `Incerteza == 5` AND Incerteza is the sole MAX driver — recommend Spike, not scope split.
- Coverage check: every original AC must appear in exactly one sub-story's `📄 Descrição Original`.
- Body sections for sub-stories (in order): 🎯 O quê / 💡 Por quê / 📋 Comportamento esperado / ✅ Critérios de Aceite / 🔧 Notas Técnicas / 📊 Complexidade / 📄 Descrição Original.

---

## File Map

| File | Status | Responsibility |
| --- | --- | --- |
| `agile-workflow/skills/split-story/references/split-patterns.md` | Create | Catalog of 5 split patterns with detection signals and auto-selection decision tree |
| `agile-workflow/skills/split-story/references/scoring-guide.md` | Create | 6-driver scoring table, ceiling logic, spike detection rule, discrepancy-handling protocol |
| `agile-workflow/skills/split-story/SKILL.md` | Create | 5-phase conductor (INGEST → SCORE → ANALYZE → DRAFT → HANDOFF) with 2 gates and all guardrails |

---

### Task 1: Create `split-patterns.md`

**Files:**

- Create: `agile-workflow/skills/split-story/references/split-patterns.md`

**Interfaces:**

- Consumes: nothing from earlier tasks.
- Produces: a pattern catalog that `SKILL.md` (Task 3) references in PHASE 3 — ANALYZE. The SKILL.md directs the agent to "read `./references/split-patterns.md` for the pattern catalog and auto-selection decision tree."

- [ ] **Step 1: Create the directory and file**

```bash
mkdir -p agile-workflow/skills/split-story/references
```

Then create `agile-workflow/skills/split-story/references/split-patterns.md` with this exact content:

````markdown
# Split Pattern Catalog

Reference for the `split-story` skill ANALYZE phase. Each pattern includes: detection signals
(what to look for in the story body and ACs), a decision rule for auto-selection, and a
negative example so the agent knows when NOT to pick it.

## Pattern 1 — Workflow Step

**What it means:** The story describes a sequential process with multiple distinct steps. Each
step can be delivered independently and yields value on its own.

**Detection signals:**
- Body or ACs contain sequential connectives: "first", "then", "after", "next", "finally",
  "when X is done, Y"
- Numbered list of actions in expected behavior or ACs
- The story title contains "flow", "process", or "wizard"
- Body references multiple screens or pages in a navigation sequence

**Split rule:** One sub-story per sequential step. Sub-story N can be built and tested before
step N+1 exists.

**Coverage rule:** Each step maps to one AC cluster. No step is left without a sub-story.

**Counter-signal (don't pick this pattern if):** Steps are not independently deployable — e.g.,
step 2 is only testable if step 1 is in prod. Use Happy/Unhappy Path instead if the relationship
is success vs. error.

**Example:**
Original: "As a user, I can register, verify my email, and set my profile."
Split: (1) Register — account creation, (2) Email verification, (3) Profile setup.

---

## Pattern 2 — Business Rule

**What it means:** The story applies different logic depending on a condition. Each distinct
rule/branch can be built and tested independently.

**Detection signals:**
- ACs contain "if / when / unless / except when" branching
- ACs list multiple independent conditions each with different outcomes
- Body mentions user roles, plan tiers, permission levels, or regional rules
- Multiple `[ ]` AC checkboxes each govern a different scenario

**Split rule:** One sub-story per distinct rule branch. Sub-story titles include the condition:
"…when user is admin", "…for Pro-tier accounts".

**Coverage rule:** Every condition in the original ACs appears in exactly one sub-story.

**Counter-signal:** If branches share so much code that delivering one without the other is
meaningless (e.g., toggle on/off), use Happy/Unhappy Path instead.

**Example:**
Original: "Price shown in cart changes based on whether user has a coupon, is logged in, or
qualifies for bulk discount."
Split: (1) Logged-out base price, (2) Coupon application, (3) Bulk discount rule.

---

## Pattern 3 — Happy / Unhappy Path

**What it means:** The story describes both a success flow and one or more error/edge cases.
The error flows are independent enough to be validated separately.

**Detection signals:**
- ACs include both positive outcomes and error/validation scenarios
- Body uses phrases like "if invalid", "on failure", "error message", "fallback", "retry"
- ACs mix `should succeed when` and `should show error when` items
- The story handles a form or API call with both valid and invalid inputs

**Split rule:** Sub-story 1 = happy path only. Sub-story 2+ = error / edge cases grouped by
similarity. Sub-story 2 can reference Sub-story 1's success state as a prerequisite for negative
testing.

**Coverage rule:** Every AC item maps to happy or unhappy; none is orphaned.

**Counter-signal:** If the error handling is a single validation (one input, one error message),
it is not big enough to warrant a separate sub-story. Absorb into the happy-path story.

**Example:**
Original: "User submits payment form; card is charged; if card is declined, show error."
Split: (1) Successful payment flow, (2) Declined card and retry handling.

---

## Pattern 4 — CRUD Operation

**What it means:** The story covers multiple create / read / update / delete operations on the
same entity. Each operation is independently shippable.

**Detection signals:**
- ACs contain "create", "list", "view", "edit", "update", "delete", "archive" for the same noun
- Body or title references a management screen or admin panel
- Story points are high because the entity has multiple lifecycle operations

**Split rule:** One sub-story per CRUD verb. Sequence: Create → Read/List → Update → Delete
(so each sub-story can be validated end-to-end on the prior one's output). Read and List may
be combined if trivially similar.

**Coverage rule:** Every operation mentioned in original ACs appears in exactly one sub-story.

**Counter-signal:** If the story only has two operations (e.g., create + delete with no
list/edit), verify each sub-story still exceeds the ceiling before splitting — a two-operation
story may already be right-sized.

**Example:**
Original: "Admin can create, view, edit, and delete user accounts."
Split: (1) Create account, (2) View/list accounts, (3) Edit account, (4) Delete account.

---

## Pattern 5 — Data Variation

**What it means:** The story handles the same operation for multiple distinct data types, entity
subtypes, or input formats. Each variation has different validation, rendering, or processing
logic.

**Detection signals:**
- ACs list the same verb applied to multiple nouns: "upload PDF", "upload image", "upload CSV"
- Body mentions multiple entity subtypes: "internal user", "external contractor", "guest"
- Story handles different API payload schemas or response shapes
- Complexity is driven by the Dados driver (modeling or migration across variants)

**Split rule:** One sub-story per data variant. All sub-stories share the same operation; they
differ in the data contract and validation rules.

**Coverage rule:** Every data type / variant mentioned in original ACs appears in exactly one
sub-story.

**Counter-signal:** If the variants differ only in a label or color (purely presentational),
they are not separate sub-stories — they are configuration. Do not split.

**Example:**
Original: "System accepts file uploads: PDF documents, PNG/JPEG images, and CSV data exports."
Split: (1) PDF upload and validation, (2) Image upload and validation, (3) CSV upload and
parsing.

---

## Auto-Selection Decision Tree

Evaluate signals in this order. Use the first pattern whose primary signal is present. If two
patterns tie, prefer the one with more distinct AC items mapping to it.

```text
1. Body/ACs describe a sequential process with independently deliverable steps?
   → Workflow Step

2. ACs contain distinct condition branches (if/when/unless) each with different outcomes?
   → Business Rule

3. ACs mix success scenarios and error/edge-case scenarios?
   → Happy / Unhappy Path

4. Story covers multiple CRUD verbs on the same entity?
   → CRUD Operation

5. Story handles the same operation across multiple data types or entity variants?
   → Data Variation
```

If no pattern clearly fits, surface this to the user before drafting and ask them to identify
the natural split axis.
````

- [ ] **Step 2: Verify required content is present**

Run these checks — all must pass:

```bash
grep -c "Pattern 1 — Workflow Step" agile-workflow/skills/split-story/references/split-patterns.md
# Expected: 1

grep -c "Pattern 5 — Data Variation" agile-workflow/skills/split-story/references/split-patterns.md
# Expected: 1

grep -c "Auto-Selection Decision Tree" agile-workflow/skills/split-story/references/split-patterns.md
# Expected: 1

grep -c "Counter-signal" agile-workflow/skills/split-story/references/split-patterns.md
# Expected: 5 (one per pattern)
```

All four commands must return their expected value. If any returns 0, the file content is missing — rewrite the file.

- [ ] **Step 3: Commit**

```bash
git add agile-workflow/skills/split-story/references/split-patterns.md
git commit -m "feat(split-story): add split-patterns reference catalog"
```

Expected: commit succeeds, no errors.

---

### Task 2: Create `scoring-guide.md`

**Files:**

- Create: `agile-workflow/skills/split-story/references/scoring-guide.md`

**Interfaces:**

- Consumes: nothing from earlier tasks.
- Produces: a scoring reference that `SKILL.md` (Task 3) reads in PHASE 2 — SCORE. The SKILL.md directs the agent to "read `./references/scoring-guide.md` for the complete driver table, ceiling value, spike rule, and discrepancy-handling protocol before scoring."

- [ ] **Step 1: Create `scoring-guide.md`**

Create `agile-workflow/skills/split-story/references/scoring-guide.md` with this exact content:

````markdown
# Scoring Guide

Reference for the `split-story` skill SCORE phase. Covers the 6-driver MAX heuristic,
story-point ceiling, spike detection, and discrepancy handling.

## 6-Driver MAX Heuristic

Score each driver independently on the 1/2/3/5 scale. The story's calculated points =
the **MAX** across all drivers (not the sum). This ensures one hard dimension cannot be
diluted by easy ones.

| Driver | 1 | 2 | 3 | 5 |
|---|---|---|---|---|
| **Escopo** | One tiny, isolated change | One area or module | Multiple artifacts or one complex area | Multiple areas or significant cross-cutting scope |
| **Incerteza** | Fully known — clear spec, no research needed | Mostly known — minor unknowns resolvable in breakdown | Some meaningful unknowns — may need spike or tech research | Significant unknowns — direction unclear; investigation required before implementation |
| **Integrações** | No integrations | One stable, well-documented integration | A couple of integrations to coordinate | Many integrations or one unstable / undocumented integration |
| **Dados** | No data concerns | Trivial data (simple fields, no migration) | Some data shaping (schema change, mapping) | Complex modeling or data migration |
| **QA** | Trivial — no meaningful test scenarios | Unit-level coverage only | One distinct user flow to test | Multi-screen E2E journey or complex state combinations |
| **Rollout** | No rollout concerns | Simple feature flag or config toggle | Coordinated rollout (multiple environments / teams) | Risky or irreversible rollout (data migration, external API, billing) |

### How to Score

1. For each driver, pick the score that best matches the story as written.
2. Record all six scores.
3. `calculated_points = MAX(Escopo, Incerteza, Integrações, Dados, QA, Rollout)`.
4. Note which driver(s) are at the MAX — this is the dominant driver(s).

### Recording Format

Use this format in the story's `📊 Complexidade` section:

```text
5 pts — driver: QA=5 (multi-screen E2E); Incerteza=3; Escopo=3; rest ≤2
```

Always state which driver set the MAX and the brief reason why.

---

## Story-Point Ceiling

**Default ceiling: 5 points.**

If `calculated_points ≤ ceiling`: the story is right-sized. No split needed (ANALYZE Branch A).

If `calculated_points > ceiling`: split is required.
`split_count = ⌈calculated_points / ceiling⌉`.

The ceiling is overridable per invocation via an optional argument. If the user passes a
ceiling override, use it instead of 5.

---

## Spike Detection Rule

**Condition:** `Incerteza == 5` AND Incerteza is the sole MAX driver (no other driver also
scored 5).

**Recommendation:** Do NOT split the story by scope. Scope-splitting does not reduce
uncertainty — it just produces multiple uncertain stories. Instead, recommend a Spike:
a time-boxed investigation story that produces a decision or proof-of-concept.

**Spike stub format (when user confirms):**

```markdown
**🎯 O quê**
Investigar [the unknown aspect] para determinar [what decision or output is needed].

**💡 Por quê**
A incerteza elevada nesta história impede uma estimativa confiável e aumenta o risco de
retrabalho.

**📋 Comportamento esperado**
Ao final do spike, a equipe tem: [specific deliverable — e.g., "a documented approach and
updated estimate for the original story"].

**✅ Critérios de Aceite**
- [ ] [Specific question 1 answered with documented evidence]
- [ ] [Specific question 2 answered with documented evidence]
- [ ] Original story re-estimated and ready for next sprint.

**🔧 Notas Técnicas**
Time-box: [team's default spike duration — e.g., 1 sprint or 2 days].

**📊 Complexidade**
3 pts — driver: Escopo=3 (spike output = decision doc + re-estimate); Incerteza=1
(investigation itself is bounded).

**📄 Descrição Original**
[Verbatim slice of the original story that triggered the spike recommendation.]
```

When drafting a Spike stub, fill each `[placeholder]` with content derived from the original
story's description and the specific unknown that caused `Incerteza=5`.

---

## Discrepancy Handling

A discrepancy occurs when the story has a declared story-point value (from frontmatter
`story_points` or Azure `Microsoft.VSTS.Scheduling.StoryPoints`) that differs from
`calculated_points`.

### Protocol

1. **Show both values** with the full driver breakdown for the calculated value.
2. **Do not auto-resolve.** Always ask the user which value to trust.
3. **Present exactly this prompt:**

```text
Story points discrepancy detected.

Declared:   <X> pts  (from <source: frontmatter | Azure>)
Calculated: <Y> pts  (MAX driver: <driver>=<score> — <reason>)

Driver breakdown:
  Escopo:      <score>
  Incerteza:   <score>
  Integrações: <score>
  Dados:       <score>
  QA:          <score>
  Rollout:     <score>

Which value should be used for the split decision?
  1. Declared (<X> pts)
  2. Calculated (<Y> pts)
```

4. Wait for user input. Proceed with `active_points = user's chosen value`.

### When declared and calculated agree

If `declared_points == calculated_points`: no prompt shown. Proceed with
`active_points = declared_points`.

### When story points are not declared

If no story points are declared in any source: skip the discrepancy check entirely. Proceed
with `active_points = calculated_points`.
````

- [ ] **Step 2: Verify required content is present**

```bash
grep -c "6-Driver MAX Heuristic" agile-workflow/skills/split-story/references/scoring-guide.md
# Expected: 1

grep -c "Spike Detection Rule" agile-workflow/skills/split-story/references/scoring-guide.md
# Expected: 1

grep -c "Discrepancy Handling" agile-workflow/skills/split-story/references/scoring-guide.md
# Expected: 1

grep -c "Default ceiling: 5 points" agile-workflow/skills/split-story/references/scoring-guide.md
# Expected: 1

grep -c "Incerteza is the sole MAX driver" agile-workflow/skills/split-story/references/scoring-guide.md
# Expected: 1
```

All five commands must return 1. If any returns 0, the content is missing — rewrite the file.

- [ ] **Step 3: Commit**

```bash
git add agile-workflow/skills/split-story/references/scoring-guide.md
git commit -m "feat(split-story): add scoring-guide reference"
```

Expected: commit succeeds, no errors.

---

### Task 3: Create `split-story/SKILL.md`

**Files:**

- Create: `agile-workflow/skills/split-story/SKILL.md`

**Interfaces:**

- Consumes: `./references/split-patterns.md` (Task 1) — read during PHASE 3.
- Consumes: `./references/scoring-guide.md` (Task 2) — read during PHASE 2.
- Consumes: `../../references/decomposition-rules.md` — shared, already exists.
- Consumes: `../../references/ticket-structure.md` — shared, already exists.
- Consumes: `../../references/azure-mechanics.md` — shared, already exists.
- Produces: the conductor that the agent plugin loads when the user invokes `split-story`.

- [ ] **Step 1: Verify shared references exist**

```bash
ls agile-workflow/references/decomposition-rules.md \
   agile-workflow/references/ticket-structure.md \
   agile-workflow/references/azure-mechanics.md
```

Expected: all three files listed with no "No such file" errors. If any is missing, stop — do not create SKILL.md until shared references are in place.

- [ ] **Step 2: Create `SKILL.md`**

Create `agile-workflow/skills/split-story/SKILL.md` with this exact content:

````markdown
---
name: split-story
description: >
  Lateral story-sizing skill. Takes a single User Story and determines if it should be split,
  how many sub-stories to create, and what split pattern to use — then drafts sub-stories and
  hands them off. Use when the user asks "split this story", "is this story too big?",
  "analyze this story for sizing", or provides a vault path / Azure ID / file path / raw text
  and wants a split recommendation. One story per invocation.
allowed-tools: >
  Read Write Edit Glob Grep Bash
  mcp__azure-devops__wit_get_work_item
  mcp__azure-devops__wit_create_work_item
  mcp__azure-devops__wit_work_items_link
---

# split-story

Lateral story-sizing skill. Load reference files as each phase needs them.

References (shared, in `../../references/`):
- `decomposition-rules.md` — 6-driver MAX heuristic, story-point ceiling, DoR, hierarchy rules.
- `ticket-structure.md` — body sections, frontmatter constraints, content hygiene.
- `azure-mechanics.md` — MCP calls, linking gotchas, rendering rules.

References (skill-specific, in `./references/`):
- `split-patterns.md` — split pattern catalog with detection signals and auto-selection rules.
- `scoring-guide.md` — 6-driver scoring table, ceiling logic, spike detection rule, discrepancy
  handling.

---

## PHASE 1 — INGEST

**Input:** one of — vault draft path, Azure work item ID, arbitrary file system path, or raw
text pasted inline.

Determine source from the argument:

**If vault draft path** (path under the vault, recognized by vault folder prefix or `.md`
extension inside the vault tree):
1. Read the markdown file. Parse frontmatter: extract `work_item_type`, `story_points`,
   `parent_feature`, `azure_id`. Parse body: identify sections by emoji + label headings.

**If Azure ID** (numeric argument):
1. Call `wit_get_work_item(id=<id>, expand=relations)`.
2. Extract: `System.Title`, `System.Description`,
   `Microsoft.VSTS.Scheduling.StoryPoints`, `System.Parent`.

**If file system path** (non-vault path to a `.md` or `.txt` file):
1. Read the file from disk. Parse as markdown. Extract any frontmatter if present; treat body
   as the full description.

**If raw text** (multi-line pasted content, no recognizable path or ID):
1. Use the pasted content directly as the body. No frontmatter to parse; treat the entire
   input as the story description.

Normalize into a unified artifact record:

```text
{
  title:                string | null   (frontmatter/title field, or first heading, or null)
  body:                 string          (full description / body text)
  story_points:         number | null   (null if not declared in any source)
  acceptance_criteria:  string[]        (each AC line from the ✅ Critérios de Aceite section;
                                         empty array if the section is absent)
  parent_feature:       string | number | null
  azure_id:             number | null
  source:               "vault" | "azure" | "filesystem" | "raw"
}
```

Extract `acceptance_criteria` by reading the `✅ Critérios de Aceite` section and splitting on
checkbox lines (`- [ ]` or `- [x]`). For Azure source, parse the same section from
`System.Description` markdown. For raw text or filesystem source, parse from the body if the
section heading is present; otherwise `acceptance_criteria = []`.

If artifact cannot be parsed (empty content, unreadable file, MCP error): STOP and report the
specific failure. Do not proceed.

---

## PHASE 2 — SCORE

Read `./references/scoring-guide.md` for the complete driver table, ceiling value, spike rule,
and discrepancy-handling protocol before scoring.

Apply the 6-driver MAX heuristic to the normalized artifact:

1. Score each driver (Escopo, Incerteza, Integrações, Dados, QA, Rollout) on the 1/2/3/5 scale.
2. `calculated_points = MAX(all driver scores)`.
3. Record which driver(s) are at the MAX — these are the dominant drivers.

**Discrepancy check** (run only if `story_points` is declared and non-null):
- If `declared == calculated`: proceed with `active_points = declared`.
- If `declared ≠ calculated`: follow the discrepancy-handling protocol in `scoring-guide.md`
  exactly — show both values with driver breakdown and wait for user choice.
  `active_points = user-chosen value`.

**If `story_points` not declared:** `active_points = calculated_points`. No prompt shown.

---

## PHASE 3 — ANALYZE

Read `./references/split-patterns.md` for the pattern catalog and auto-selection decision tree.

**Branch A — No split needed:**

If `active_points ≤ ceiling` (default 5, or override from invocation argument):

1. Print: `Story is right-sized at <active_points> pts (ceiling: <ceiling>).`
2. Print the driver breakdown (all six driver scores).
3. STOP. No vault files written. No further phases execute.

**Branch B — Spike recommended:**

If `Incerteza == 5` AND Incerteza is the sole MAX driver (no other driver also scored 5):

1. Present spike rationale: uncertainty dominates; scope-splitting does not reduce risk —
   investigation does.
2. Show the user the specific unknown that caused Incerteza=5 (derived from the story body).
3. Ask: "Recommend a Spike instead of a scope split. Shall I draft a Spike stub?"
4. Wait for user confirmation before proceeding to DRAFT.
   - Confirmed → proceed to DRAFT (Spike mode).
   - Declined → STOP.

**Branch C — Split:**

1. `split_count = ⌈active_points / ceiling⌉`.
2. Auto-select split pattern using the decision tree in `split-patterns.md`.
3. Show reasoning: one sentence per pattern considered; one winner with justification.
4. Derive `split_count` sub-story titles and one-line scopes.
5. Estimate point value per sub-story: re-apply driver scoring to the narrowed scope.
   Each sub-story should score ≤ ceiling after the split.
6. Map which ACs from the original story belong to each sub-story.

**── GATE 1: present split plan to user ──**

Show:
- Pattern chosen and why (one sentence)
- Number of sub-stories
- For each sub-story: proposed title + one-line scope + estimated points
- Which original ACs map to each sub-story

Wait for explicit approval (`yes` / `proceed` / `ok` or equivalent) before entering DRAFT.
If the user revises the plan (different pattern, different count, adjusted titles): incorporate
revisions and re-show the updated plan. Do not proceed until the plan is approved.

---

## PHASE 4 — DRAFT

Read `../../references/ticket-structure.md` and `../../references/decomposition-rules.md`
before writing any files.

**Spike mode** (Branch B confirmed):

1. Draft one vault file at:
   `AI_Codex_AgileWorkflowMarketplace/Tickets/Ready/<parent_feature_id>-spike-<slug>.md`
2. Fill all 7 body sections using the Spike stub format from `./references/scoring-guide.md`.
3. Fill each `[placeholder]` with content derived from the original story.

**Split mode** (Branch C approved):

For each approved sub-story:

1. Filename: `<parent_feature_id>-<n>-<kebab-slug>.md` — e.g., `6868-1-register-flow.md`.
2. Path: `AI_Codex_AgileWorkflowMarketplace/Tickets/Ready/<filename>`.
3. Frontmatter (hook-valid — no `status:`, no `azure_id:` yet):

```yaml
---
date: <YYYY-MM-DD>
type: ticket
work_item_type: User Story
parent_feature: <parent_feature_id>
story_points: <estimated-points>
---
```

4. Body: all 7 sections per `ticket-structure.md` (in order):
   - 🎯 O quê
   - 💡 Por quê
   - 📋 Comportamento esperado
   - ✅ Critérios de Aceite
   - 🔧 Notas Técnicas
   - 📊 Complexidade — driver breakdown for this sub-story's narrowed scope
   - 📄 Descrição Original — the exact verbatim slice of the original story's ACs that this
     sub-story covers. No paraphrasing.

**Coverage check** (run after all files are written, before HANDOFF):

1. List every AC item from the original story.
2. For each item, confirm it appears in exactly one sub-story's `📄 Descrição Original`.
3. If any AC item appears in zero sub-stories: STOP and report
   `ORPHAN AC: <item>` — dropped requirement.
4. If any AC item appears in two or more sub-stories: STOP and report
   `DUPLICATE COVERAGE: <item>` — ambiguous scope.
5. Any gap or duplicate must be resolved by revising the draft files before HANDOFF.
   Do not silently patch — surface the issue to the user.

---

## PHASE 5 — HANDOFF

Present a summary:
- List each sub-story: title + point estimate + vault file path.
- Coverage confirmation: "All <N> original ACs covered."

Show options:

```text
Sub-stories drafted. What would you like to do?

1. Keep as vault drafts — done; continue manually or via decompose-backlog.
2. Create in Azure and link to parent Feature — creates items and links hierarchy.
3. Discard drafts — delete vault files and stop.
```

Wait for user choice.

**Option 1 — Keep:**
Report vault file paths and stop. No further action.

**Option 2 — Azure:**
Read `../../references/azure-mechanics.md` before making any MCP calls.

For each sub-story draft (in order):

1. `wit_create_work_item` with `Markdown description` = full body from the draft.
2. Assert response contains `System.Id`. If absent: STOP and report failure with the item
   title and the raw error.
3. `wit_work_items_link` with explicit `type: "parent"` linking the new item to
   `parent_feature_id`.
4. Read back: `wit_get_work_item(id=<new_id>, expand=relations)`.
   Assert `System.Parent == parent_feature_id`.
   If assertion fails: STOP and report
   `LINK ASSERTION FAILED for <title>: expected parent <parent_feature_id>, got <actual>`.
5. Update vault draft frontmatter: set `azure_id: <new_id>`. Rename file to
   `<new_id>-<slug>.md`.

After all items: report each — title, Azure ID, parent link status.

**Option 3 — Discard:**
Delete each vault draft file written in PHASE 4. Report `Drafts discarded.` and stop.

---

## Guardrails

- **One story per run.** Process only the first argument if multiple are given.
- **No silent patching.** Coverage gaps and duplicates surface to the user — never auto-resolved.
- **No Azure writes without user consent.** Azure MCP calls execute only if the user selects
  HANDOFF option 2.
- **Gate before draft.** DRAFT phase does not execute until GATE 1 is explicitly approved.
- **Spike ≠ split.** When Incerteza is the sole dominant driver, recommend a Spike; do not
  force a scope split.
````

- [ ] **Step 3: Verify SKILL.md structure**

```bash
grep -c "^name: split-story" agile-workflow/skills/split-story/SKILL.md
# Expected: 1

grep -c "PHASE 1 — INGEST" agile-workflow/skills/split-story/SKILL.md
# Expected: 1

grep -c "PHASE 5 — HANDOFF" agile-workflow/skills/split-story/SKILL.md
# Expected: 1

grep -c "GATE 1" agile-workflow/skills/split-story/SKILL.md
# Expected: 1

grep -c "\.\./\.\./references/" agile-workflow/skills/split-story/SKILL.md
# Expected: 3  (decomposition-rules, ticket-structure, azure-mechanics)

grep -c "\./references/" agile-workflow/skills/split-story/SKILL.md
# Expected: 4  (split-patterns and scoring-guide each appear twice: reference list + phase read instruction)
```

All commands must return their expected value. If any returns 0, the file content is missing or a path is wrong — fix inline.

- [ ] **Step 4: Verify file layout**

```bash
find agile-workflow/skills/split-story -type f | sort
```

Expected output (exactly these three files):

```text
agile-workflow/skills/split-story/SKILL.md
agile-workflow/skills/split-story/references/scoring-guide.md
agile-workflow/skills/split-story/references/split-patterns.md
```

- [ ] **Step 5: Commit**

```bash
git add agile-workflow/skills/split-story/SKILL.md
git commit -m "feat(split-story): add SKILL.md conductor (5 phases, 2 gates)"
```

Expected: commit succeeds, no errors.
