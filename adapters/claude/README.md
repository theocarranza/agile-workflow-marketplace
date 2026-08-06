# claude adapter

Builds a local marketplace under `dist/claude-marketplace/` for **agile-backlog-toolkit**.

```bash
python3 adapters/claude/build_plugin.py
bash adapters/claude/install.sh
```

Curl install:

```bash
curl -fsSL https://raw.githubusercontent.com/theocarranza/agile-workflow-marketplace/main/adapters/claude/install.sh \
  | bash -s -- --repo theocarranza/agile-workflow-marketplace --ref main
```

Host-only notes live in `skill-overlay.md` (minimal) and this README — not in portable `SKILL.md` frontmatter.
