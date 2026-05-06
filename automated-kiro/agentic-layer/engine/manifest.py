"""Pipeline manifest -- state management for pipeline runs.

The manifest tracks pipeline state, phase history, artifacts, retry counts,
and gate results. It is the single source of truth for a pipeline run.

File location: agent_runs_log/{pipeline_id}/manifest.json
"""

import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

from .types import PipelineManifestData
from .utils import get_project_root


class PipelineManifest:
    """Pipeline state container with persistence.

    The manifest wraps a PipelineManifestData model and provides
    mutation methods, persistence, and query methods for the pipeline runner.
    """

    MANIFEST_FILENAME = "manifest.json"

    def __init__(self, pipeline_id: str, issue_number: Optional[str] = None):
        """Create a new manifest for a pipeline run.

        Args:
            pipeline_id: 8-character UUID identifying this pipeline run.
            issue_number: Optional GitHub issue number that triggered this run.

        Raises:
            ValueError: If pipeline_id is empty or None.
        """
        if not pipeline_id:
            raise ValueError("pipeline_id is required for PipelineManifest")

        self._data: Dict[str, Any] = PipelineManifestData(
            pipeline_id=pipeline_id,
            issue_number=issue_number,
        ).model_dump()
        self.logger = logging.getLogger(__name__)

    # --- Mutation ---

    def update(self, **kwargs) -> None:
        """Update manifest fields with validation.

        Only allows updating fields defined in PipelineManifestData.
        Silently ignores unknown fields.
        """
        valid_fields = set(PipelineManifestData.model_fields.keys())
        for key, value in kwargs.items():
            if key in valid_fields:
                self._data[key] = value

    def record_phase(
        self,
        phase: str,
        status: str,
        iteration: int = 1,
        artifacts: Optional[Dict[str, str]] = None,
        gate_result: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a phase execution in the history.

        Appends to phase_history. If the same phase+iteration already
        exists, updates the existing entry instead of appending.
        Also merges artifacts into the top-level artifacts dict.

        Args:
            phase: Phase name (e.g., "plan", "build", "test").
            status: Phase status ("complete", "failed", "skipped").
            iteration: 1-based iteration number (>1 means retry).
            artifacts: artifact_name -> file_path pairs produced.
            gate_result: Optional gate evaluation result.
        """
        entry = {
            "phase": phase,
            "status": status,
            "iteration": iteration,
            "artifacts": artifacts or {},
            "gate_result": gate_result,
        }

        # Check if we should update an existing entry
        history = self._data.get("phase_history", [])
        updated = False
        for i, existing in enumerate(history):
            if existing["phase"] == phase and existing["iteration"] == iteration:
                history[i] = entry
                updated = True
                break

        if not updated:
            history.append(entry)

        self._data["phase_history"] = history

        # Merge artifacts into top-level artifacts dict
        if artifacts:
            top_artifacts = self._data.get("artifacts", {})
            top_artifacts.update(artifacts)
            self._data["artifacts"] = top_artifacts

        # Update total_retries: count all entries with iteration > 1
        total_retries = sum(1 for h in history if h["iteration"] > 1)
        self._data["total_retries"] = total_retries

    # --- Query ---

    def get_current_phase(self) -> Optional[str]:
        """Return the name of the most recently recorded phase."""
        history = self._data.get("phase_history", [])
        if not history:
            return None
        return history[-1]["phase"]

    def get_artifact(self, artifact_name: str) -> Optional[str]:
        """Return the file path for a named artifact."""
        return self._data.get("artifacts", {}).get(artifact_name)

    def get_retry_count(self, phase: str) -> int:
        """Return how many times a phase has been attempted.

        Returns 0 if phase never ran. First attempt = 1.
        """
        history = self._data.get("phase_history", [])
        return len([h for h in history if h["phase"] == phase])

    def is_phase_complete(self, phase: str) -> bool:
        """Check if a phase has completed successfully."""
        history = self._data.get("phase_history", [])
        return any(
            h["phase"] == phase and h["status"] == "complete"
            for h in history
        )

    def get_phase_history(self, phase: str) -> List[Dict[str, Any]]:
        """Return all history entries for a specific phase, ordered by iteration."""
        history = self._data.get("phase_history", [])
        return sorted(
            [h for h in history if h["phase"] == phase],
            key=lambda h: h["iteration"],
        )

    def get_working_directory(self) -> str:
        """Return the working directory for this pipeline.

        Returns worktree_path if set, otherwise the project root.
        """
        worktree = self._data.get("worktree_path")
        if worktree:
            return worktree
        return str(get_project_root())

    # --- Persistence ---

    def get_manifest_path(self) -> str:
        """Return the full path to the manifest JSON file.

        Location: {project_root}/agent_runs_log/{pipeline_id}/manifest.json
        """
        project_root = get_project_root()
        return str(
            project_root / "agent_runs_log" / self._data["pipeline_id"] / self.MANIFEST_FILENAME
        )

    def save(self, workflow_step: Optional[str] = None) -> None:
        """Save manifest to disk with Pydantic validation.

        Validates data against PipelineManifestData before writing.
        Creates parent directories if needed.

        Args:
            workflow_step: Optional label for log messages.
        """
        # Validate with Pydantic
        validated = PipelineManifestData(**self._data)

        manifest_path = self.get_manifest_path()
        os.makedirs(os.path.dirname(manifest_path), exist_ok=True)

        with open(manifest_path, "w") as f:
            json.dump(validated.model_dump(), f, indent=2)

        self.logger.info(f"Saved manifest to {manifest_path}")
        if workflow_step:
            self.logger.info(f"Manifest updated by: {workflow_step}")

    @classmethod
    def load(
        cls, pipeline_id: str, logger: Optional[logging.Logger] = None
    ) -> Optional["PipelineManifest"]:
        """Load a manifest from disk.

        Args:
            pipeline_id: The pipeline ID to load.
            logger: Optional logger for messages.

        Returns:
            PipelineManifest instance, or None if not found or invalid.
        """
        project_root = get_project_root()
        manifest_path = str(
            project_root / "agent_runs_log" / pipeline_id / cls.MANIFEST_FILENAME
        )

        if not os.path.exists(manifest_path):
            return None

        try:
            with open(manifest_path, "r") as f:
                data = json.load(f)

            # Validate
            validated = PipelineManifestData(**data)

            # Construct instance
            manifest = cls(validated.pipeline_id)
            manifest._data = validated.model_dump()

            if logger:
                logger.info(f"Loaded manifest from {manifest_path}")
                logger.debug(f"State: {json.dumps(manifest._data, indent=2)}")

            return manifest
        except Exception as e:
            if logger:
                logger.error(f"Failed to load manifest from {manifest_path}: {e}")
            return None

    # --- Inter-process Transfer ---

    @classmethod
    def from_stdin(cls) -> Optional["PipelineManifest"]:
        """Read manifest from stdin if available (piped input).

        Returns None if stdin is a tty or input is empty/invalid.
        """
        if sys.stdin.isatty():
            return None
        try:
            input_data = sys.stdin.read()
            if not input_data.strip():
                return None
            data = json.loads(input_data)
            pipeline_id = data.get("pipeline_id")
            if not pipeline_id:
                return None
            manifest = cls(pipeline_id)
            manifest._data = data
            return manifest
        except (json.JSONDecodeError, EOFError):
            return None

    def to_stdout(self) -> None:
        """Write manifest to stdout as JSON for piping."""
        print(json.dumps(self._data, indent=2))

    # --- Convenience Properties ---

    @property
    def pipeline_id(self) -> str:
        return self._data["pipeline_id"]

    @property
    def state(self) -> str:
        return self._data.get("state", "INITIALIZED")

    @property
    def escalated(self) -> bool:
        return self._data.get("escalated", False)

    @property
    def total_retries(self) -> int:
        return self._data.get("total_retries", 0)

    @property
    def issue_number(self) -> Optional[str]:
        return self._data.get("issue_number")

    @property
    def branch_name(self) -> Optional[str]:
        return self._data.get("branch_name")

    @property
    def model_set(self) -> str:
        return self._data.get("model_set", "base")

    @property
    def issue_type(self) -> Optional[str]:
        return self._data.get("issue_type")
