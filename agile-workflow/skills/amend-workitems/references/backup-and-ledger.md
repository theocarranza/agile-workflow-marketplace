# Backup, Ledger, and revision rules

Before analysis, create a timestamped backup outside the mutation path. Use
`<vault>/_backups/amend-workitems/<UTC timestamp>/` for a Ledger-backed run, or
`.agentic/backups/amend-workitems/<UTC timestamp>/` for an Azure-only run. Prefer a Ledger
snapshot when the source is Azure-backed: save raw work-item JSON, revisions, relations,
attachments, and all descendant bodies. Also copy the local tree and related
`Implementation_Plans/` notes when available. If only a filesystem/Ledger source exists, copy
the complete source tree and record SHA-256 checksums. Never treat a directory listing as a backup.

When a local AI Codex Ledger is present:

1. resolve the vault from project config or `AI_Codex*/`;
2. use the Obsidian CLI `search` command for ids, titles, and keywords when the binary is usable;
3. fall back to `rg` if Obsidian is unavailable and record that limitation;
4. include matching `Implementation_Plans/` notes in the snapshot and scan.

Record source revisions at scan time and compare them again immediately before approval. A changed
revision invalidates the affected proposal; refresh that node, re-run contextual search, and show a
new preview. A failed backup, incomplete descendant enumeration, or Azure/Ledger disagreement is a
hard stop. Keep the backup after success so the user can recover manually.
