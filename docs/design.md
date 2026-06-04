# Design — `decompose-backlog` skill (`agile-workflow` plugin)

> Status: approved design, pre-implementation.
> Date: 2026-06-03.
> Origin: distilled from the live session that decomposed Azure DevOps Feature 6868
> ("Infraestrutura testes e2e Maestro", Epic 6858) into User Stories and created the
> first one (#6870) in Azure DevOps.

## Purpose

A **self-contained, standalone** Claude Code skill that drives the full arc of turning a
parent work item into correctly-parented child Stories in Azure DevOps, with a content
audit at the end. It is the executable orchestration that the team's existing planning
docs and enricher prompts describe but never operationalized into a repeatable procedure.

It carries its **own** copy of the decomposition rules (hierarchy, Definition of Ready,
story-point heuristic, ticket structure) and the Azure DevOps / vault mechanics, so it runs
without depending on any particular repository's `docs/` being present or readable.

**Portability note.** Concrete conventions named below — the draft directory (`Tickets/Ready/`),
the filename regex, the section labels in the local language, and the session-record/ledger
protocol — are the *defaults observed in the originating monorepo*. They are the skill's out-of-box
behavior, but the skill treats them as configurable seams, not hard requirements, so it can adapt to
a host repo that organizes drafts or records differently. The Azure DevOps mechanics and the
parent/coverage assertions are invariant.

## Scope

**In:** parent work item (Epic or Feature) in → right-sized child Stories, drafted, enriched,
created in Azure DevOps, correctly parented, and audited for requirement coverage out.

**Out:** authoring the Epic/Feature itself; implementing the Stories; sprint planning;
estimation ceremony. The skill starts at "a parent work item exists" and ends at "child
Stories exist, are parented, and every parent requirement has a home."

## Classification

A **process skill** — rigid on the operational steps (the Azure linking sequence and the
verification/audit assertions are non-negotiable), flexible on judgment (how many Stories to
split into, how to word each).

## Phases

The skill is a thin **conductor** over seven ordered phases. Each phase has a clear input and
a clear artifact out. Two hard approval gates protect the vault and Azure from unapproved
writes. Phases are resumable — a dead session can re-enter at VERIFY/AUDIT against the ids.

```
1. INGEST      Read the parent work item (Epic/Feature) from Azure via MCP.
               Extract: original text verbatim, acceptance criteria, parent chain.
               Read any linked spike/wiki. → "source of truth" notes.

2. DECOMPOSE   Split into candidate Stories under the sizing rule
               (1 Story = 1 sprint = 1 PR; story-point ceiling → split).
               Each Story traces to a verbatim slice of the parent text.
               → ordered list of Story stubs (title + 1-line scope + deps).
               ── GATE 1: present the split, wait for approval before drafting.

3. DRAFT       Write each Story to the vault Tickets/Ready/ as a draft that PASSES the
               hooks (frontmatter: type present, status forbidden; naming regex).
               Structure: O quê / Por quê / Comportamento / Critérios /
               Notas Técnicas / Complexidade / Descrição Original.
               → vault draft files.

4. ENRICH      Apply the work-item-enricher contract: tighten wording, ASCII diagrams,
               story-point justification, de-dup (each fact stated once).
               → enriched draft = exact Azure body.
               ── GATE 2: show the final body, wait for thumbs-up before any Azure write.

5. CREATE      Per approved Story: wit_create_work_item (Markdown description so diagrams
               render), then link parent with EXPLICIT type=parent to the FEATURE id.
               → Azure work items.

6. VERIFY      Structural. Read each created item back; assert System.Parent == Feature id;
               chain Epic→Feature→Story holds; reconcile vault frontmatter with the
               Azure-assigned id. → verified hierarchy + updated drafts.

7. AUDIT       Content + coverage. Retrieve each created item FRESH from Azure (not the
               local draft) and check:
                 a) FIDELITY  — Azure body matches the approved enriched draft
                    (no truncation, diagrams rendered, no MCP mangling).
                 b) COVERAGE  — every requirement / acceptance criterion in the PARENT
                    maps to ≥1 child Story; flag orphan requirements (dropped) and
                    Story scope with no parent anchor (scope creep).
                 c) DoR       — each Story meets Definition of Ready.
               → coverage report: requirement-by-requirement, pass/gap.
```

## Embedded guardrails (preflight / postflight)

The traps this skill exists to prevent — encoded as checkable assertions, not prose advice.

### Azure linking (preflight before CREATE, asserted in VERIFY)
- **Always pass explicit `type`** on the link call. Default is `related`; omitting it silently
  creates the wrong link.
- **A Story's parent is its FEATURE, never the Epic.** Assert `System.Parent == featureId`.
  Decomposing an Epic → the intermediate Features must exist first; Stories never attach
  directly to an Epic.
- **Description format = Markdown** so ASCII diagrams render. Work-item *bodies* use ASCII
  diagrams (Mermaid renders only in the Wiki, not in work-item descriptions).

### Vault hooks (preflight before DRAFT)
- Frontmatter: `type:` required; `status:` forbidden in `Tickets/`.
- Filename regex: `^(\d+|tech-debt|bug|task|spike)-[a-z0-9-]+`, lowercase. Use the parent
  Feature id as prefix until Azure assigns the real id, then rename.

### Content hygiene (applied in DRAFT/ENRICH)
- No machine-specific paths or local-only / spike folder references; the project root is the
  canonical root.
- Each fact stated once, in its natural section.
- Locale-correct technical vocabulary; no calques from English.
- No decision-making/meta in the ticket body — unresolved choices become `@TODO` annotations,
  not prose.

## Inputs / outputs

**Inputs**
- Required: a **parent work item id** (Epic or Feature).
- Optional: target sprint/iteration; story-point ceiling override (defaults to team standard).
- Implicit context: Azure project + repo; vault `Tickets/Ready/` location.

**Parent-type branch**
- Parent is a **Feature** → decompose straight into Stories.
- Parent is an **Epic** → stop and ask: decompose into Features first, or target an existing
  child Feature. No silent Epic-parented Stories.

**Outputs**
1. Vault drafts in `Tickets/Ready/` (hook-valid, enriched, reconciled to Azure ids).
2. Created Azure Stories, parented to the Feature.
3. A coverage report (Phase 7): parent-requirement → Story map, pass/gap.
4. A session-record checkpoint, per the host repo's ledger protocol (if present).

**Failure handling**
- Every Azure-mutating phase (CREATE) is preceded by an approval gate and followed by a
  read-back assertion. A failed assertion stops the skill and reports — no best-effort
  guessing, no proceeding past a structural or coverage gap.

## Packaging

Standalone marketplace repo, **not** committed to any consuming monorepo, maintained
separately. Layout mirrors the sibling `spike-workflow-marketplace`:

```
agile-workflow-marketplace/
├── .claude-plugin/marketplace.json      ← lists the plugin
├── README.md
├── .gitignore
├── docs/design.md                       ← this document
└── agile-workflow/
    ├── .claude-plugin/plugin.json
    └── skills/decompose-backlog/
        ├── SKILL.md                      ← the conductor (7 phases, gates, guardrails)
        └── references/                   ← self-contained rules, split out to keep SKILL.md lean
            ├── decomposition-rules.md    ← hierarchy, DoR, sizing, story-point heuristic
            ├── ticket-structure.md       ← vault draft format + hook constraints
            ├── azure-mechanics.md        ← create/link MCP calls, linking gotchas, rendering
            └── audit-checklist.md        ← fidelity / coverage / DoR checks
```

Installable via `/plugin marketplace add`. The `agile-workflow` plugin name leaves room for
sibling skills later (refinement, sprint planning, standalone backlog audit).

## Non-goals / YAGNI

- No automated story-point *calculation* — the heuristic guides a human/agent judgment, not a
  formula that emits a number unattended.
- No CI integration, no bulk/batch decomposition of many Features at once (one parent per run).
- No template engine — drafts are written directly, following the embedded structure.
