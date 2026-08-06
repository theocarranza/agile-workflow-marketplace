"""Regression guards for the vendor-neutral package layout."""

from __future__ import annotations

import hashlib
import unittest
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT
TEMPLATES = PACKAGE / "common" / "templates"
CANONICAL = (
    "canonical-epic.md",
    "canonical-feature.md",
    "canonical-user-story.md",
    "canonical-task.md",
    "output-formats.md",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TestCanonicalTemplateLayout(unittest.TestCase):
    def test_shared_templates_have_one_canonical_home(self) -> None:
        self.assertEqual({path.name for path in TEMPLATES.iterdir()}, set(CANONICAL))

    def test_skill_provider_and_host_folders_do_not_copy_shared_templates(self) -> None:
        canonical_digests = {digest(TEMPLATES / name) for name in CANONICAL}
        folders = (
            PACKAGE / "skills",
            PACKAGE / "orchestrator_core" / "providers",
            PACKAGE / ".claude-plugin",
            PACKAGE / ".cursor-plugin",
            PACKAGE / ".plugin",
        )
        copied = tuple(
            path
            for folder in folders
            for path in folder.rglob("*.md")
            if digest(path) in canonical_digests
        )
        self.assertEqual(copied, ())

    def test_common_has_no_byte_identical_file_pairs(self) -> None:
        files = tuple((PACKAGE / "common").rglob("*.md"))
        duplicates = tuple(
            (left.relative_to(PACKAGE), right.relative_to(PACKAGE))
            for left, right in combinations(files, 2)
            if digest(left) == digest(right)
        )
        self.assertEqual(duplicates, ())


if __name__ == "__main__":
    unittest.main()
