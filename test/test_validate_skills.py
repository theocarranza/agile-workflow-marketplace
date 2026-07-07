import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "validate-skills.sh"


class TestValidateSkills(unittest.TestCase):
    def test_all_skills_pass_skills_ref(self) -> None:
        result = subprocess.run(
            [str(SCRIPT)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=result.stdout + result.stderr,
        )
        self.assertIn("validating generate-work-item", result.stdout)
        self.assertIn("validating enrich-work-item", result.stdout)


if __name__ == "__main__":
    unittest.main()
