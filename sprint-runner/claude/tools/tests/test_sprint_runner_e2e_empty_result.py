"""
Test suite for SprintExecutor.step_e2e empty result gate.

This module exercises Phase 1 of the fix for bogus e2e→patch triggers:
- Missing result file raises StepFailed
- Empty result file raises StepFailed
- Valid failing result invokes _e2e_patch (sanity check)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import tools.sprint_runner as sr  # noqa: E402


class TestStepE2eEmptyResultGate:
    """Test cases for step_e2e empty result JSON gate (Phase 1)."""

    def _make_executor(self, tmp_path: Path, monkeypatch) -> sr.SprintExecutor:
        """Create a minimal SprintExecutor test harness."""
        # Bypass __init__ to avoid full initialization
        executor = sr.SprintExecutor.__new__(sr.SprintExecutor)

        # Set minimal attributes that step_e2e reads
        executor.sprint = Mock()
        executor.sprint.id = "99"
        executor.sprint.branch = "sprint/99-test"

        executor.log_dir = tmp_path / "logs"
        executor.log_dir.mkdir(parents=True, exist_ok=True)

        executor.execute_model = "test-model"
        executor.dry_run = False
        executor.force_step = None

        # Initialize state dict with all required keys
        executor.s = {
            "e2e_test_path": "e2e/test_sprint_99.spec.ts",  # non-empty so step runs
            "errors": [],
            "steps": [],
            "step_executions": {},
            "specs": [],  # only used inside _e2e_patch
        }

        # Mock state object
        executor.state = SimpleNamespace(
            data={"run_id": "TEST-RUN-123"},
            save=Mock()
        )

        # Mock ClaudeRunner
        executor.claude = Mock()

        # Monkeypatch module-level REPO_ROOT so cr.log_path.relative_to(REPO_ROOT) works
        monkeypatch.setattr(sr, "REPO_ROOT", tmp_path)

        return executor

    def test_missing_result_file_raises_step_failed(self, tmp_path: Path, monkeypatch):
        """Test that missing result file triggers gate and raises StepFailed."""
        executor = self._make_executor(tmp_path, monkeypatch)

        # Mock ClaudeResult for successful agent run (but no result file written)
        cr = sr.ClaudeResult(
            exit_code=0,
            duration_seconds=1.5,
            last_assistant_text="completed e2e run",
            log_path=executor.log_dir / "e2e.jsonl",
            cost_usd=0.05,
            num_turns=42,
            error=None,
        )
        executor.claude.run = Mock(return_value=cr)

        # Spy on _e2e_patch to ensure it's NOT called
        executor._e2e_patch = Mock()

        # Do NOT create e2e-result-attempt-1.json (simulating agent that didn't write it)

        # Call step_e2e and expect StepFailed
        with pytest.raises(sr.StepFailed) as exc_info:
            executor.step_e2e()

        # Assert exception details
        assert exc_info.value.step == "e2e"
        assert "result JSON" in str(exc_info.value)

        # Assert error was recorded in state
        assert len(executor.s["errors"]) == 1
        assert executor.s["errors"][0]["step"] == "e2e"
        assert executor.s["errors"][0]["error"] == "agent did not write result JSON"

        # Assert _e2e_patch was NOT called (gate fired before patch logic)
        assert executor._e2e_patch.call_count == 0

    def test_empty_result_file_raises_step_failed(self, tmp_path: Path, monkeypatch):
        """Test that empty result file (missing 'passed'/'failed_steps') triggers gate."""
        executor = self._make_executor(tmp_path, monkeypatch)

        # Mock ClaudeResult
        cr = sr.ClaudeResult(
            exit_code=0,
            duration_seconds=2.0,
            last_assistant_text="wrote empty result",
            log_path=executor.log_dir / "e2e.jsonl",
            cost_usd=0.03,
            num_turns=15,
            error=None,
        )
        executor.claude.run = Mock(return_value=cr)

        # Spy on _e2e_patch
        executor._e2e_patch = Mock()

        # Create e2e-result-attempt-1.json with empty JSON object
        result_path = executor.log_dir / "e2e-result-attempt-1.json"
        result_path.write_text("{}")

        # Call step_e2e and expect StepFailed
        with pytest.raises(sr.StepFailed) as exc_info:
            executor.step_e2e()

        # Assert exception details
        assert exc_info.value.step == "e2e"
        assert "result JSON" in str(exc_info.value)

        # Assert error was recorded
        assert len(executor.s["errors"]) == 1
        assert executor.s["errors"][0]["step"] == "e2e"
        assert executor.s["errors"][0]["error"] == "agent did not write result JSON"

        # Assert _e2e_patch was NOT called
        assert executor._e2e_patch.call_count == 0

    def test_failing_result_invokes_e2e_patch(self, tmp_path: Path, monkeypatch):
        """Test that valid failing result bypasses gate and invokes _e2e_patch (sanity check)."""
        executor = self._make_executor(tmp_path, monkeypatch)

        # Mock ClaudeResult
        cr = sr.ClaudeResult(
            exit_code=0,
            duration_seconds=3.0,
            last_assistant_text="test failed",
            log_path=executor.log_dir / "e2e.jsonl",
            cost_usd=0.08,
            num_turns=25,
            error=None,
        )
        executor.claude.run = Mock(return_value=cr)

        # Create e2e-result-attempt-1.json with valid failing result
        result_path = executor.log_dir / "e2e-result-attempt-1.json"
        failing_result = {
            "passed": False,
            "failed_steps": [
                {
                    "step": "login",
                    "error": "button not found",
                    "screenshot": None,
                }
            ],
            "screenshots": [],
            "summary": "login step failed",
        }
        result_path.write_text(json.dumps(failing_result))

        # Spy on _e2e_patch and make it raise StepFailed to exit cleanly
        def mock_e2e_patch(cycle, result):
            raise sr.StepFailed("e2e_patch", "stop here for test")

        executor._e2e_patch = Mock(side_effect=mock_e2e_patch)

        # Call step_e2e and expect it to call _e2e_patch, then raise StepFailed from there
        with pytest.raises(sr.StepFailed):
            executor.step_e2e()

        # Assert _e2e_patch WAS called (gate did not fire)
        assert executor._e2e_patch.call_count == 1
        executor._e2e_patch.assert_called_once_with(1, failing_result)

        # Assert NO gate error in errors list
        gate_errors = [e for e in executor.s["errors"] if e.get("error") == "agent did not write result JSON"]
        assert len(gate_errors) == 0, "Gate should not have fired for valid failing result"
