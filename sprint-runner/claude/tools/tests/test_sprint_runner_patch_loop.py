"""
Test suite for SprintExecutor._run_patch_then_implement helper.

This module exercises the PLAN->IMPLEMENT->COMMIT flow and validates:
- Plan file creation detection
- Step execution telemetry
- Plan-only commit guard
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import tools.sprint_runner as sr  # noqa: E402


class TestRunPatchThenImplement:
    """Test cases for _run_patch_then_implement helper method."""

    def _make_executor(self, tmp_path: Path, monkeypatch) -> sr.SprintExecutor:
        """Create a minimal SprintExecutor test harness."""
        # Bypass __init__ to avoid full initialization
        executor = sr.SprintExecutor.__new__(sr.SprintExecutor)

        # Set minimal attributes that the helper reads
        executor.sprint = Mock()
        executor.sprint.id = "13"
        executor.log_dir = tmp_path / "logs"
        executor.log_dir.mkdir(parents=True, exist_ok=True)
        executor.execute_model = "test-model"
        executor.s = {"step_executions": {}}

        # Mock ClaudeRunner
        executor.claude = Mock()

        # Monkeypatch module-level paths
        patch_dir = tmp_path / "patch"
        patch_dir.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr(sr, "PATCH_SPECS_DIR", patch_dir)
        monkeypatch.setattr(sr, "REPO_ROOT", tmp_path)

        return executor

    def test_happy_path(self, tmp_path: Path, monkeypatch):
        """Test successful PLAN->IMPLEMENT->COMMIT flow with non-plan files."""
        executor = self._make_executor(tmp_path, monkeypatch)

        # Mock ClaudeResult for successful calls
        plan_cr = Mock(spec=sr.ClaudeResult)
        plan_cr.succeeded = True
        plan_cr.error = None

        implement_cr = Mock(spec=sr.ClaudeResult)
        implement_cr.succeeded = True
        implement_cr.error = None

        commit_cr = Mock(spec=sr.ClaudeResult)
        commit_cr.succeeded = True
        commit_cr.error = None

        call_count = 0

        def claude_run_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # PLAN call - write the plan file
                plan_path = sr.PATCH_SPECS_DIR / "patch-sprint-13-e2e-1.md"
                plan_path.write_text("# Patch Plan\n\nImplementation steps...\n")
                return plan_cr
            elif call_count == 2:
                # IMPLEMENT call
                return implement_cr
            else:
                # COMMIT call
                return commit_cr

        executor.claude.run = Mock(side_effect=claude_run_side_effect)

        # Mock working_tree_clean to return False after implement (so commit runs)
        monkeypatch.setattr(sr, "working_tree_clean", lambda ignore=None: False)

        # Mock run_cmd for git diff to return non-plan files
        def mock_run_cmd(*args, **kwargs):
            if "diff" in args and "--name-only" in args:
                return SimpleNamespace(
                    stdout="backend/foo.py\nspecs/patch/patch-sprint-13-e2e-1.md\n",
                    returncode=0,
                    stderr="",
                )
            return SimpleNamespace(stdout="", returncode=0, stderr="")

        monkeypatch.setattr(sr, "run_cmd", mock_run_cmd)

        # Call the helper
        result = executor._run_patch_then_implement(
            kind="e2e",
            cycle=1,
            plan_prompt="PLAN_PROMPT_TEXT",
            commit_class="e2e patch cycle 1",
            rec_name="e2e_patch",
        )

        # Assertions
        assert executor.claude.run.call_count == 3, "Should make 3 Claude calls"
        assert executor.s["step_executions"]["e2e_patch"] == 1
        assert executor.s["step_executions"]["commit"] == 1

        # Check first call (PLAN)
        plan_call = executor.claude.run.call_args_list[0]
        assert plan_call[1]["step_name"] == "e2e-patch-1-plan"
        assert plan_call[1]["max_turns"] == sr.DEFAULT_MAX_TURNS
        assert plan_call[1]["model"] == "test-model"

        # Check second call (IMPLEMENT)
        impl_call = executor.claude.run.call_args_list[1]
        assert impl_call[1]["step_name"] == "e2e-patch-1-impl"
        assert impl_call[1]["max_turns"] == sr.BUILD_MAX_TURNS
        assert impl_call[1]["model"] == "test-model"

        # Check third call (COMMIT)
        commit_call = executor.claude.run.call_args_list[2]
        assert commit_call[1]["step_name"] == "e2e-patch-1-commit"
        assert commit_call[1]["max_turns"] == sr.DEFAULT_MAX_TURNS

        # Return value should be the implement call result
        assert result is implement_cr

    def test_plan_missing(self, tmp_path: Path, monkeypatch):
        """Test that StepFailed is raised when plan file is not created."""
        executor = self._make_executor(tmp_path, monkeypatch)

        # Mock ClaudeResult for plan call that doesn't write the file
        plan_cr = Mock(spec=sr.ClaudeResult)
        plan_cr.succeeded = True
        plan_cr.error = None

        executor.claude.run = Mock(return_value=plan_cr)

        # Call the helper and expect StepFailed
        with pytest.raises(sr.StepFailed) as exc_info:
            executor._run_patch_then_implement(
                kind="e2e",
                cycle=1,
                plan_prompt="PLAN_PROMPT_TEXT",
                commit_class="e2e patch cycle 1",
                rec_name="e2e_patch",
            )

        # Check exception message
        assert "patch plan was not produced" in str(exc_info.value)
        assert exc_info.value.step == "e2e_patch"

        # Assert only plan call was made
        assert executor.claude.run.call_count == 1

        # Assert no telemetry was recorded
        assert "e2e_patch" not in executor.s["step_executions"]
        assert "commit" not in executor.s["step_executions"]

    def test_plan_only_commit(self, tmp_path: Path, monkeypatch):
        """Test that StepFailed is raised when commit only touches plan files."""
        executor = self._make_executor(tmp_path, monkeypatch)

        # Mock ClaudeResult for all three calls
        plan_cr = Mock(spec=sr.ClaudeResult)
        plan_cr.succeeded = True
        plan_cr.error = None

        implement_cr = Mock(spec=sr.ClaudeResult)
        implement_cr.succeeded = True
        implement_cr.error = None

        commit_cr = Mock(spec=sr.ClaudeResult)
        commit_cr.succeeded = True
        commit_cr.error = None

        call_count = 0

        def claude_run_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # PLAN call - write the plan file
                plan_path = sr.PATCH_SPECS_DIR / "patch-sprint-13-e2e-1.md"
                plan_path.write_text("# Patch Plan\n")
                return plan_cr
            elif call_count == 2:
                # IMPLEMENT call
                return implement_cr
            else:
                # COMMIT call
                return commit_cr

        executor.claude.run = Mock(side_effect=claude_run_side_effect)

        # Mock working_tree_clean to return False (working tree is dirty)
        monkeypatch.setattr(sr, "working_tree_clean", lambda ignore=None: False)

        # Mock run_cmd for git diff to return ONLY plan file
        def mock_run_cmd(*args, **kwargs):
            if "diff" in args and "--name-only" in args:
                return SimpleNamespace(
                    stdout="specs/patch/patch-sprint-13-e2e-1.md\n",
                    returncode=0,
                    stderr="",
                )
            return SimpleNamespace(stdout="", returncode=0, stderr="")

        monkeypatch.setattr(sr, "run_cmd", mock_run_cmd)

        # Call the helper and expect StepFailed
        with pytest.raises(sr.StepFailed) as exc_info:
            executor._run_patch_then_implement(
                kind="e2e",
                cycle=1,
                plan_prompt="PLAN_PROMPT_TEXT",
                commit_class="e2e patch cycle 1",
                rec_name="e2e_patch",
            )

        # Check exception message contains "plan-only commit"
        assert "plan-only commit" in str(exc_info.value)
        assert exc_info.value.step == "e2e_patch"

        # Assert all three calls were made
        assert executor.claude.run.call_count == 3

        # Assert telemetry was recorded before the guard
        assert executor.s["step_executions"]["e2e_patch"] == 1
        assert executor.s["step_executions"]["commit"] == 1
