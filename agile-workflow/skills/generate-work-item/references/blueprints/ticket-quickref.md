# Ticket Quick Reference

Section layouts and frontmatter for tickets written to **`<vault>/Tickets/Ready/`**. These are
extracts from the enricher prompts — **read the full enricher before PHASE 4**.

| Work item type | Enricher | Spec blueprint |
| --- | --- | --- |
| Epic | `enrichers/epic-enricher.prompt.md` | `blueprints/spec-epic.md` |
| Feature | `enrichers/feature-enricher.prompt.md` | `blueprints/spec-feature.md` |
| User Story / Bug / Task | `enrichers/work-item-enricher.prompt.md` | `blueprints/spec-work-item.md` |

## Shared rules

- State each fact once. No repetition across sections.
- No `status:` in ticket frontmatter — lifecycle lives in folder + Azure.
- Filename until Azure assigns an id: `<parent-id>-<kebab-slug>` or `task-<kebab-slug>`.
- **Português BR** for body prose unless `idea` is explicitly another language.
- Body becomes the Azure description verbatim (Markdown).
- Link spec: `[[Specs/<spec-basename>]]`

---

## Epic

**Enricher:** `epic-enricher.prompt.md` — max **400 words** (excl. Descrição Original).

### Frontmatter

```yaml
---
date: <YYYY-MM-DD>
type: ticket
work_item_type: Epic
tags: [ticket, epic]
---
```

### Body (enricher §4)

```markdown
# <Title>

## 🎯 Visão Estratégica
## 📊 Problema de Negócio
## 🎯 Objetivos Estratégicos
## 📈 Métricas de Sucesso (KPIs/OKRs)
## 📦 Escopo Estratégico
### Incluído / ### Excluído (Fora do Escopo)
## 🔧 Áreas/Projetos Envolvidos
## 🔗 Dependências e Riscos Estratégicos
## 📄 Descrição Original
```

---

## Feature

**Enricher:** `feature-enricher.prompt.md` — max **300 words** (excl. Descrição Original).

### Frontmatter

```yaml
---
date: <YYYY-MM-DD>
type: ticket
work_item_type: Feature
parent_epic: <epic-id>
tags: [ticket, feature]
---
```

### Body (enricher §4)

```markdown
# <Title>

## 🎯 Objetivo
## 📦 Escopo
### Incluído / ### Excluído (Fora do Escopo)
## ✅ Critérios de Sucesso
## 🔧 Áreas/Módulos Envolvidos
## 📄 Descrição Original
```

---

## User Story / Bug

**Enricher:** `work-item-enricher.prompt.md` — max **200 words** (excl. Descrição Original,
Comportamento esperado, Anexos).

### Frontmatter

```yaml
---
date: <YYYY-MM-DD>
type: ticket
work_item_type: User Story   # or Bug
parent_feature: <feature-id>
story_points: <n>
tags: [ticket, user-story]   # or [ticket, bug]
---
```

### Body (enricher §6)

```markdown
# <Title>

## 🎯 O quê
## 💡 Por quê
## 📋 Comportamento esperado   <!-- optional -->
## ✅ Critérios de Aceite
## 🔧 Notas Técnicas
## 🔄 Como Reproduzir            <!-- bugs only -->
## 📊 Complexidade
## 📎 Anexos / Referências      <!-- optional -->
## 📄 Descrição Original
```

---

## Task

Lean subset of work-item enricher. Omit 📊 when trivial; omit 🔄 unless bug-fix task.

### Frontmatter

```yaml
---
date: <YYYY-MM-DD>
type: ticket
work_item_type: Task
parent_story: <story-id>
tags: [ticket, task]
---
```

### Body

Keep 🎯, 💡, ✅, 🔧, 📄.
