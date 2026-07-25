import unittest
from dataclasses import replace
from pathlib import Path

from orchestrator_core.artifact_validator import outcome_from_results, validate_artifact
from orchestrator_core.ingest import ingest_from_text, ingest_vault_file
from orchestrator_core.reflection import ReflectionState, advance_reflection, evaluate_reflection


FIXTURE = Path(__file__).resolve().parent.parent / (
    "AI_Codex_AgileWorkflowMarketplace/Tickets/Ready/6869-login-form-validation.md"
)


EN_STORY_BODY = """\
# Validate login form fields and show inline errors

## 🎯 What

Validate login fields with inline error messages.

## 💡 Why

Users get no feedback when submitting invalid forms.

## 📋 Expected Behavior

- Show an error when leaving an empty field

## ✅ Acceptance Criteria

- [ ] Show a message when the email field is empty
- [ ] Show a message when the password field is empty

## 🔧 Technical Notes

- Authentication module

## 📊 Complexity

**2 points** — Largest driver: Scope=2, Uncertainty=1, Integrations=1, Data=1, QA=2, Rollout=1 → 2 points

## 📄 Original Description

Fictional story for login validation.
"""


class TestArtifactValidator(unittest.TestCase):
    def test_good_story_passes(self) -> None:
        record = ingest_vault_file(FIXTURE)
        results = validate_artifact(record)
        self.assertEqual(outcome_from_results(results), "PASS")

    def test_missing_type_fails(self) -> None:
        record = ingest_vault_file(FIXTURE)
        bad = replace(record, frontmatter={})
        results = validate_artifact(bad)
        self.assertEqual(outcome_from_results(results), "FAIL")
        names = [r.name for r in results if r.result == "FAIL"]
        self.assertIn("frontmatter-type-present", names)

    def test_pt_br_story_defaults_when_language_key_absent(self) -> None:
        record = ingest_vault_file(FIXTURE)
        self.assertNotIn("language", record.frontmatter)
        results = validate_artifact(record)
        self.assertEqual(outcome_from_results(results), "PASS")

    def test_en_story_fails_without_language_frontmatter(self) -> None:
        record = ingest_from_text(
            "---\ntype: ticket\nwork_item_type: User Story\nstory_points: 2\n---\n\n" + EN_STORY_BODY,
            filename="0000-en-story",
        )
        results = validate_artifact(record)
        self.assertEqual(outcome_from_results(results), "FAIL")
        names = [r.name for r in results if r.result == "FAIL"]
        self.assertTrue(any(name.startswith("body-section-missing: 🎯") for name in names))

    def test_en_story_passes_with_language_en_frontmatter(self) -> None:
        record = ingest_from_text(
            "---\ntype: ticket\nwork_item_type: User Story\nstory_points: 2\nlanguage: en\n---\n\n"
            + EN_STORY_BODY,
            filename="0000-en-story",
        )
        results = validate_artifact(record)
        self.assertEqual(outcome_from_results(results), "PASS")

    def test_pt_br_story_fails_when_declared_language_is_en(self) -> None:
        record = ingest_vault_file(FIXTURE)
        mislabeled = replace(record, frontmatter={**record.frontmatter, "language": "en"})
        results = validate_artifact(mislabeled)
        self.assertEqual(outcome_from_results(results), "FAIL")


class TestReflection(unittest.TestCase):
    def test_circuit_breaker_on_max_attempts(self) -> None:
        state = ReflectionState()
        for _ in range(3):
            state = advance_reflection(state, ["missing section"], max_attempts=3)
        self.assertTrue(state.blocked)

    def test_identical_critiques_trip_breaker(self) -> None:
        state = advance_reflection(ReflectionState(), ["same"], max_attempts=3)
        state = advance_reflection(state, ["same"], max_attempts=3)
        self.assertTrue(state.blocked)

    def test_clean_pass_completed_mode(self) -> None:
        decision = evaluate_reflection([], has_draft=True)
        self.assertEqual(decision.mode, "completed")


if __name__ == "__main__":
    unittest.main()
