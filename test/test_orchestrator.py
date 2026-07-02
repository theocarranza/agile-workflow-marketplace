import unittest
from dataclasses import replace
from pathlib import Path

from orchestrator_core.artifact_validator import outcome_from_results, validate_artifact
from orchestrator_core.ingest import ingest_vault_file
from orchestrator_core.reflection import ReflectionState, advance_reflection, evaluate_reflection


FIXTURE = Path(__file__).resolve().parent.parent / (
    "AI_Codex_AgileWorkflowMarketplace/Tickets/Ready/6869-login-form-validation.md"
)


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
