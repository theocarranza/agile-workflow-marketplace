# codex adapter

Builds a local marketplace under `dist/codex-marketplace/` for **agile-backlog-toolkit**.

```bash
python3 adapters/codex/build_plugin.py
bash adapters/codex/install.sh
```

Curl install:

```bash
curl -fsSL https://raw.githubusercontent.com/theocarranza/agile-workflow-marketplace/main/adapters/codex/install.sh \
  | bash -s -- --repo theocarranza/agile-workflow-marketplace --ref main
```

Host-only notes live in `skill-overlay.md` (minimal) and this README — not in portable `SKILL.md` frontmatter.
