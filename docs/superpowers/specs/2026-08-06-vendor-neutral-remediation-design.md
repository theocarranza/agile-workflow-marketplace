# Vendor-Neutral Remediation Design

## Goal

Finish the v0.11.0 vendor-neutral refactor without changing skill identifiers or the GitHub repository name.

## Architecture

The package directory becomes `agile-backlog-toolkit`. Shared work-item shapes live only in
`common/templates`; skills retain only workflow-specific references. Host adapters contain only
their manifests, while the installer builds separate physical host bundles from a common resource
set. The provider seam continues to use neutral `provider`, `provider_id`, and `parent_id` fields.

## Installer behavior

The installer creates independent Claude, Codex, and Cursor trees with copied common resources,
skills, references, orchestrator code, and the appropriate manifest. It wires Azure MCP only for
Azure modes and Linear MCP only for Linear modes. A detected managed installation requires an
interactive replacement decision; non-interactive installation aborts before mutation. If a fresh
replacement fails, only the partially created managed state is removed.

## Validation

Tests enforce the canonical-source rule, the provider/host duplication rule, all provider and host
installation combinations, clean replacement semantics, and Linear Epic → Feature → User Story →
Task parent chains and labels. The requested Python 3.12 pytest command is the final verification.
