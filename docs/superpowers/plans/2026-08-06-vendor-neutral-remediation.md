# Vendor-Neutral Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the vendor-neutral package rename, canonical source consolidation, installer assembly, and provider coverage.

**Architecture:** Rename the package directory in one atomic move, route shared markdown references to `common/templates`, and use installer functions to copy self-contained host bundles. Tests describe packaging boundaries, install combinations, replacement cleanup, and Linear’s four-level hierarchy.

**Tech Stack:** Python 3.12, pytest, Markdown skill packages.

## Global Constraints

- Display name is `Agile Backlog Toolkit`; identifier is `agile-backlog-toolkit`.
- Preserve skill folder names and the Epic → Feature → User Story → Task hierarchy.
- Reject legacy artifact schema clearly; use neutral string identity fields only.
- Do not rename the GitHub remote repository.

### Task 1: Canonical templates and package rename

**Files:** Rename `agile-workflow/` to `agile-backlog-toolkit/`; move shared contracts to
`agile-backlog-toolkit/common/templates/`; update skill references, root symlinks, docs, tests, and
installer source paths.

- [ ] Add a duplication regression test and run it red.
- [ ] Move package and canonical templates, retaining only skill-specific contracts.
- [ ] Run the duplication test green and commit.

### Task 2: Host assembly and installer replacement semantics

**Files:** Modify `scripts/install.py`; extend installer tests.

- [ ] Add matrix and clean-replacement tests, then observe expected failures.
- [ ] Assemble physical resource trees per Claude, Codex, and Cursor host; maintain Antigravity.
- [ ] Run installer tests green and commit.

### Task 3: Linear hierarchy coverage and full verification

**Files:** Modify provider tests and minimal Linear adapter code if required.

- [ ] Add a four-level create/read test and observe it fail.
- [ ] Correct only adapter behavior needed for the neutral hierarchy.
- [ ] Run the requested full suite, validate skills, commit, and push.
