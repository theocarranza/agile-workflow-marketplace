# cursor adapter

Builds a local marketplace under `dist/cursor-marketplace/` for **agile-backlog-toolkit**.

```bash
python3 adapters/cursor/build_plugin.py
bash adapters/cursor/install.sh
```

Curl install:

```bash
curl -fsSL https://raw.githubusercontent.com/theocarranza/agile-workflow-marketplace/main/adapters/cursor/install.sh \
  | bash -s -- --repo theocarranza/agile-workflow-marketplace --ref main
```

Host-only notes live in `skill-overlay.md` (minimal) and this README — not in portable `SKILL.md` frontmatter.
