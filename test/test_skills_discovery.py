import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_ROOT = ROOT / "skills"
PLUGIN_SKILLS = ROOT / "agile-workflow" / "skills"
EXPECTED = (
    "decompose-backlog",
    "validate-artifact",
    "auto-fix-artifact",
    "split-story",
    "generate-work-item",
    "enrich-work-item",
    "generate-plain-language-documentation",
)


class TestSkillsDiscoveryLayout(unittest.TestCase):
    def test_root_skills_symlinks_resolve(self) -> None:
        self.assertTrue(SKILLS_ROOT.is_dir(), "root skills/ directory is required for registry discovery")
        for name in EXPECTED:
            link = SKILLS_ROOT / name
            self.assertTrue(link.is_symlink(), f"skills/{name} should symlink to plugin skill")
            target = link.resolve()
            self.assertEqual(target, (PLUGIN_SKILLS / name).resolve())
            self.assertTrue((target / "SKILL.md").is_file())

    def test_skills_sh_json_lists_all_skills(self) -> None:
        import json

        config = json.loads((ROOT / "skills.sh.json").read_text(encoding="utf-8"))
        listed = {
            skill
            for group in config["groupings"]
            for skill in group["skills"]
        }
        self.assertEqual(listed, set(EXPECTED))


if __name__ == "__main__":
    unittest.main()
