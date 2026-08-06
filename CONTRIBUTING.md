# Contributing

## Versioning

Keep these in lockstep when you cut a release:

1. Root `VERSION`
2. `.plugin/plugin.json` `version`
3. `.cursor-plugin/plugin.json` and marketplace `version`
4. `.claude-plugin/plugin.json` and marketplace `version`
5. `.agents/plugins/marketplace.json` plugin `version`
6. `adapters/*/plugin.template.json` `name` / `version`
7. `CHANGELOG.md` entry

`scripts/validate.sh` fails if they drift.

Do **not** add `.codex-plugin/` — Codex uses `.agents/plugins/marketplace.json`.

## Skill frontmatter

Portable Agent Skills frontmatter only:

- `name`
- `description`
- `license`

No host fields (`allowed-tools`, `metadata`, `compatibility`, model/UI keys) in `SKILL.md`.

## Do not hand-edit `dist/`

Marketplace trees and zips under `dist/` are generated. Run:

```bash
python3 adapters/cursor/build_plugin.py
# or
./scripts/build_all.sh
```

## Validation

```bash
./scripts/validate.sh
python3 -m unittest discover -s adapters/tests -v
PYTHONPATH=. python3 -m pytest test/ -q
./scripts/build_all.sh
```
