"""
Agentic Development Workflow Runner

The single orchestrator that executes workflow phases in order,
evaluates quality gates, runs self-healing loops, and handles escalation.

Different autonomy levels are different workflow.yaml configurations,
not different scripts.
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any, Optional

from engine.config import load_config
from engine.manifest import PipelineManifest
from engine.github import make_issue_comment
from engine.git import commit_changes, push_branch
from engine.gate import GateEvaluator, GateResult, GateAction, PhaseDisposition
from engine.utils import setup_logger, parse_json, make_pipeline_id
from engine.types import AgentTemplateRequest


def _resolve_runner(runner_name: str):
    """Resolve the execute_template function for the given runner name.

    Args:
        runner_name: Runner identifier from workflow.yaml ("kiro").

    Returns:
        The execute_template callable for the selected runner.

    Raises:
        ValueError: If runner_name is not recognized.
    """
    if runner_name == "kiro":
        from runners.kiro.agent import execute_template
        return execute_template
    raise ValueError(
        f"Unknown runner: '{runner_name}'. Supported: 'kiro'"
    )


@dataclass
class PhaseResult:
    """Result of a single phase execution."""
    phase_name: str
    success: bool
    output: Any = None
    parsed_output: dict[str, Any] = field(default_factory=dict)
    gate_result: Optional[GateResult] = None
    duration_seconds: float = 0.0
    iterations: int = 1
    error: Optional[str] = None


class PipelineRunner:
    """Executes a pipeline defined by pipeline.yaml.

    One runner handles one issue. The runner:
    1. Loads pipeline.yaml for phase order, gate bindings, and autonomy config
    2. Creates or loads a PipelineManifest for state tracking
    3. Executes phases sequentially
    4. Evaluates gates after each phase
    5. Runs healing loops when gates fail
    6. Escalates when healing exhausts

    Usage:
        runner = PipelineRunner(
            config_path="adw/agentic-layer/pipeline.yaml",
            issue_number=42,
        )
        runner.run()
    """

    def __init__(
        self,
        config_path: str,
        issue_number: int,
        pipeline_id: Optional[str] = None,
        working_dir: Optional[str] = None,
        skip_phases: Optional[list[str]] = None,
        local_mode: bool = False,
        spec_description: str = "",
    ) -> None:
        """Initialize the runner.

        Args:
            config_path: Path to pipeline.yaml.
            issue_number: GitHub issue number being processed (0 for local mode).
            pipeline_id: Optional ID for this pipeline run. Generated if not provided.
            working_dir: Optional working directory (worktree path). Defaults to cwd.
            skip_phases: Optional list of phase names to skip.
            local_mode: If True, skip all GitHub API calls.
            spec_description: Feature description text (used in local mode).
        """
        self.config = load_config(config_path)
        self._config_path = config_path
        self.issue_number = issue_number
        self.pipeline_id = pipeline_id or make_pipeline_id()
        self.working_dir = working_dir or os.getcwd()
        self.skip_phases = set(skip_phases or [])
        self.local_mode = local_mode
        self.spec_description = spec_description
        self.logger = setup_logger(self.pipeline_id, "runner")

        # Create manifest for this pipeline run
        self.manifest = PipelineManifest(
            pipeline_id=self.pipeline_id,
            issue_number=str(issue_number),
        )

        # Initialize gate evaluator -- use gates from config or a default path
        gates_config = self.config.gates or {}
        gates_dir = gates_config.get("dir", None)
        if not gates_dir:
            # Try to find gates directory relative to config
            config_parent = os.path.dirname(os.path.abspath(config_path))
            candidate = os.path.join(config_parent, "gates")
            if os.path.isdir(candidate):
                gates_dir = candidate
            else:
                # Use a fallback that we create if needed
                gates_dir = os.path.join(config_parent, "gates")
                os.makedirs(gates_dir, exist_ok=True)

        self.gate_evaluator = GateEvaluator(gates_dir)

        # Resolve runner backend
        self._execute_template = _resolve_runner(self.config.runner)

        # Pipeline config shortcuts
        self.phases = self.config.phases
        self.autonomy_level = "supervised"  # Default; could be extended via config

        self.logger.info(
            f"PipelineRunner initialized: pipeline_id={self.pipeline_id}, "
            f"issue=#{issue_number}, runner={self.config.runner}, "
            f"autonomy={self.autonomy_level}, "
            f"phases={[p.name for p in self.phases]}"
        )

    def run_phase(self, phase_config: Any) -> PhaseResult:
        """Execute a single phase of the pipeline.

        Steps:
        1. Resolve prompt template / slash command from config
        2. Execute the phase via agent.execute_template()
        3. Parse structured output (JSON for test/review, text for others)
        4. Evaluate gate if one is bound to this phase
        5. Record phase result in manifest

        Note: Healing loop is NOT called here. The caller (run()) handles
        healing because it needs access to the full pipeline context.

        Args:
            phase_config: PhaseConfig from pipeline config, or a dict with
                         keys: name, template, gate (optional), output_format.

        Returns:
            PhaseResult with execution details.
        """
        # Support both PhaseConfig objects and dicts
        if isinstance(phase_config, dict):
            phase_name = phase_config["name"]
            template = phase_config.get("template", "")
            gate_config = phase_config.get("gate")
            output_format = phase_config.get("output_format", "text")
            artifact_key = phase_config.get("artifact_key", phase_name)
        else:
            phase_name = phase_config.name
            template = phase_config.template
            gate_config = phase_config.gate
            output_format = "json" if phase_name in ("test", "review") else "text"
            artifact_key = phase_name

        start_time = time.time()
        self.logger.info(f"=== Starting phase: {phase_name} ===")

        # Update manifest state
        self.manifest.update(state=f"RUNNING_{phase_name.upper()}")

        # Resolve template / slash command
        # For Kiro: template is a file path like "kiro-layer/prompts/build.md" -> pass as template_path
        slash_command = f"/{phase_name}"
        template_path = None
        if template and not template.startswith("/"):
            # Resolve {issue_class} placeholder in template filename
            issue_class = self.manifest.issue_type or "feature"
            template = template.replace("{issue_class}", issue_class)
            # File path -- resolve relative to config directory
            config_dir = os.path.dirname(os.path.abspath(self._config_path))
            template_path = os.path.join(config_dir, template)
        elif template and template.startswith("/"):
            slash_command = template

        # Build template variables from manifest artifacts
        template_vars = self._build_template_vars(phase_name)

        # Build template request
        request = AgentTemplateRequest(
            agent_name=phase_name,
            slash_command=slash_command,
            args=[f"--pipeline-id={self.pipeline_id}", f"--issue={self.issue_number}"],
            pipeline_id=self.pipeline_id,
            working_dir=self.working_dir,
            template_path=template_path,
            template_vars=template_vars,
        )

        # Execute agent with template
        try:
            agent_response = self._execute_template(
                request=request,
                model_set=self.manifest.model_set,
            )
        except Exception as e:
            self.logger.error(f"Phase {phase_name} agent execution failed: {e}")
            duration = time.time() - start_time
            self.manifest.record_phase(
                phase=phase_name,
                status="failed",
                iteration=1,
            )
            return PhaseResult(
                phase_name=phase_name,
                success=False,
                error=str(e),
                duration_seconds=duration,
            )

        if not agent_response.success:
            self.logger.error(f"Phase {phase_name} failed: {agent_response.output}")
            duration = time.time() - start_time
            self.manifest.record_phase(
                phase=phase_name,
                status="failed",
                iteration=1,
            )
            return PhaseResult(
                phase_name=phase_name,
                success=False,
                output=agent_response.output,
                error=f"Agent returned failure: {agent_response.output[:200]}",
                duration_seconds=duration,
            )

        # Parse structured output if applicable
        parsed_output = {}
        if output_format == "json":
            try:
                parsed_output = parse_json(agent_response.output)
            except Exception as e:
                self.logger.warning(
                    f"Failed to parse {phase_name} output as JSON: {e}"
                )
                parsed_output = {"raw_output": agent_response.output}

        # Store artifact in manifest
        artifacts = {artifact_key: agent_response.output}

        # Evaluate gate if one is bound to this phase
        gate_result = None
        gate_name = None
        if isinstance(gate_config, dict):
            gate_name = gate_config.get("name") or gate_config.get("gate")
        elif gate_config is not None and hasattr(gate_config, "name"):
            gate_name = gate_config.name

        if gate_name:
            self.logger.info(f"Evaluating gate: {gate_name}")
            try:
                gate_result = self.gate_evaluator.evaluate(gate_name, parsed_output)
                self.logger.info(
                    f"Gate {gate_name}: passed={gate_result.passed}, "
                    f"action={gate_result.action.value}"
                )
            except KeyError:
                self.logger.warning(f"Gate {gate_name} not found, skipping evaluation")

        duration = time.time() - start_time
        success = gate_result.passed if gate_result else True

        result = PhaseResult(
            phase_name=phase_name,
            success=success,
            output=agent_response.output,
            parsed_output=parsed_output,
            gate_result=gate_result,
            duration_seconds=duration,
        )

        # Record in manifest
        gate_result_dict = None
        if gate_result:
            gate_result_dict = {
                "passed": gate_result.passed,
                "action": gate_result.action.value,
                "message": gate_result.message,
                "blocker_count": gate_result.blocker_count,
            }

        self.manifest.record_phase(
            phase=phase_name,
            status="complete" if success else "failed",
            iteration=1,
            artifacts=artifacts,
            gate_result=gate_result_dict,
        )

        return result

    def _build_template_vars(self, phase_name: str) -> dict[str, str]:
        """Build template variables from manifest artifacts.

        Each phase's prompt template can reference previous phase outputs.
        Artifact chaining map (from Harmony architecture):
          Plan produces $plan_artifact -> consumed by Build
          Build produces $build_artifact -> consumed by Test
          Test produces $test_results -> consumed by Review
          Review produces $review_artifact -> consumed by Document, Deploy
        """
        artifacts = self.manifest._data.get("artifacts", {})
        return {
            "plan_artifact": artifacts.get("plan", ""),
            "build_artifact": artifacts.get("build", ""),
            "test_results": artifacts.get("test", ""),
            "review_artifact": artifacts.get("review", ""),
            "doc_artifact": artifacts.get("document", ""),
            "deploy_artifact": artifacts.get("deploy", ""),
            "issue_number": str(self.issue_number),
            "pipeline_id": self.pipeline_id,
            "working_dir": self.working_dir,
            "spec_description": self.spec_description,
        }

    # --- Healing Loop ---

    def run_healing_loop(
        self,
        phase_config: Any,
        initial_gate_result: GateResult,
    ) -> PhaseResult:
        """Run the self-healing loop for a failing phase.

        Two strategies:
        - retry: Re-run the same phase (equivalent to tac-7's test retry loop)
        - patch: Run a patcher agent, then re-run the phase (equivalent to
                 tac-7's review-patch loop)

        The loop terminates when:
        1. Gate passes (happy path)
        2. Max retries exhausted
        3. No progress detected (stop_on_no_progress: same failure count)

        Args:
            phase_config: The failing phase's config (PhaseConfig or dict).
            initial_gate_result: The GateResult from the initial evaluation.

        Returns:
            PhaseResult from the final attempt (may still be failing).
        """
        # Extract gate name
        if isinstance(phase_config, dict):
            phase_name = phase_config["name"]
            gate_config = phase_config.get("gate")
        else:
            phase_name = phase_config.name
            gate_config = phase_config.gate

        gate_name = ""
        if isinstance(gate_config, dict):
            gate_name = gate_config.get("name") or gate_config.get("gate", "")
        elif gate_config is not None and hasattr(gate_config, "name"):
            gate_name = gate_config.name

        healing_config = self.gate_evaluator.get_healing_config(gate_name)

        max_retries = healing_config["max_retries"]
        stop_on_no_progress = healing_config["stop_on_no_progress"]
        strategy = healing_config["strategy"]

        self.logger.info(
            f"Starting healing loop for {phase_name}: strategy={strategy}, "
            f"max_retries={max_retries}, stop_on_no_progress={stop_on_no_progress}"
        )

        prev_blocker_count = initial_gate_result.blocker_count
        last_result = PhaseResult(
            phase_name=phase_name,
            success=False,
            gate_result=initial_gate_result,
        )

        for attempt in range(1, max_retries + 1):
            self.logger.info(f"Healing attempt {attempt}/{max_retries} for {phase_name}")

            # Step 1: Remediation action based on strategy
            if strategy == "patch":
                self._run_patcher(phase_name, initial_gate_result)

            # Step 2: Re-run the failing phase
            retry_result = self.run_phase(phase_config)
            retry_result.iterations = attempt + 1  # +1 for the initial run

            # Step 3: Check gate result
            if retry_result.gate_result and retry_result.gate_result.passed:
                self.logger.info(f"Healing succeeded on attempt {attempt}")
                retry_result.success = True
                self.manifest.record_phase(
                    phase=phase_name,
                    status="healed",
                    iteration=attempt + 1,
                )
                return retry_result

            # Step 4: Check for progress
            current_blocker_count = (
                retry_result.gate_result.blocker_count
                if retry_result.gate_result
                else prev_blocker_count
            )

            if stop_on_no_progress and current_blocker_count >= prev_blocker_count:
                self.logger.warning(
                    f"No progress detected: {current_blocker_count} blockers "
                    f"(was {prev_blocker_count}). Stopping healing loop."
                )
                break

            prev_blocker_count = current_blocker_count
            last_result = retry_result

        # Healing exhausted
        self.logger.warning(
            f"Healing exhausted for {phase_name} after {max_retries} attempts"
        )
        self.manifest.update(state=f"HEALING_EXHAUSTED_{phase_name.upper()}")

        return last_result

    def _run_patcher(self, phase_name: str, gate_result: GateResult) -> None:
        """Run the patcher agent to fix issues before re-running a phase.

        This is the equivalent of tac-7's resolve_failed_tests() and
        resolve_blocker_issues(). The patcher receives the gate result's
        issues and attempts to fix them.

        Args:
            phase_name: Name of the failing phase.
            gate_result: The gate result containing issues to fix.
        """
        self.logger.info(f"Running patcher for {phase_name}")

        # Build patcher context from gate result issues
        patcher_context = {
            "phase": phase_name,
            "issues": gate_result.issues,
            "blocker_count": gate_result.blocker_count,
            "message": gate_result.message,
        }

        # Build a patch request
        request = AgentTemplateRequest(
            agent_name=f"{phase_name}_patcher",
            slash_command="/patch",
            args=[json.dumps(patcher_context)],
            pipeline_id=self.pipeline_id,
            working_dir=self.working_dir,
        )

        try:
            patcher_response = self._execute_template(
                request=request,
                model_set=self.manifest.model_set,
            )

            if patcher_response.success:
                self.logger.info(f"Patcher completed for {phase_name}")
                # Commit patcher changes
                commit_changes(
                    message=f"fix({phase_name}): healing patch for {self.pipeline_id}",
                    cwd=self.working_dir,
                )
            else:
                self.logger.warning(f"Patcher failed for {phase_name}: {patcher_response.output}")

        except Exception as e:
            self.logger.error(f"Patcher exception for {phase_name}: {e}")

    # --- Full Pipeline Orchestration ---

    def run(self) -> bool:
        """Execute the full pipeline.

        Iterates over phases defined in pipeline.yaml. For each phase:
        1. Skip if in skip_phases set
        2. Run the phase
        3. If gate fails: run healing loop
        4. If healing fails: check disposition
           - REQUIRED: escalate and abort
           - OPTIONAL: warn and continue
           - CHECKPOINT: escalate and pause (for human input)
        5. Commit changes if phase produced code modifications

        Returns:
            True if pipeline completed successfully, False if aborted.
        """
        self.logger.info(
            f"=== Pipeline starting: {self.pipeline_id} ==="
        )
        self.manifest.update(state="RUNNING")
        pipeline_success = True

        for phase_config in self.phases:
            phase_name = phase_config.name

            # Check skip list
            if phase_name in self.skip_phases:
                self.logger.info(f"Skipping phase: {phase_name} (in skip list)")
                self.manifest.record_phase(phase=phase_name, status="skipped")
                continue

            # Check if phase is required (enabled)
            if not phase_config.required:
                self.logger.info(f"Skipping phase: {phase_name} (not required in config)")
                self.manifest.record_phase(phase=phase_name, status="disabled")
                continue

            # Execute the phase
            result = self.run_phase(phase_config)

            # If phase failed and has a gate, try healing
            if not result.success and result.gate_result:
                gate_result = result.gate_result

                if gate_result.action in (GateAction.RETRY, GateAction.PATCH):
                    # Run healing loop
                    result = self.run_healing_loop(phase_config, gate_result)

                if not result.success:
                    # Healing failed or was not attempted -- check disposition
                    gate_name = ""
                    if phase_config.gate and hasattr(phase_config.gate, "name"):
                        gate_name = phase_config.gate.name

                    disposition = self.gate_evaluator.get_disposition(
                        gate_name, self.autonomy_level
                    )

                    if disposition == PhaseDisposition.REQUIRED:
                        self.logger.error(
                            f"Phase {phase_name} FAILED with REQUIRED disposition. "
                            f"Aborting pipeline."
                        )
                        self.handle_escalation(phase_name, result.gate_result)
                        pipeline_success = False
                        break

                    elif disposition == PhaseDisposition.OPTIONAL:
                        self.logger.warning(
                            f"Phase {phase_name} failed with OPTIONAL disposition. "
                            f"Continuing pipeline."
                        )
                        if not self.local_mode:
                            make_issue_comment(
                                self.issue_number,
                                f"[{self.pipeline_id}] WARNING: {phase_name} phase failed "
                                f"but is optional. Continuing.\n\n"
                                f"Details: {result.gate_result.message if result.gate_result else 'N/A'}",
                            )

                    elif disposition == PhaseDisposition.CHECKPOINT:
                        self.logger.info(
                            f"Phase {phase_name} failed at CHECKPOINT. "
                            f"Escalating for human review."
                        )
                        self.handle_escalation(phase_name, result.gate_result)
                        # For checkpoint, we mark as needing review but don't abort
                        self.manifest.update(state="AWAITING_REVIEW")
                        pipeline_success = False
                        break

            elif not result.success:
                # Phase failed without a gate (agent error)
                self.logger.error(f"Phase {phase_name} failed without gate: {result.error}")
                self.handle_escalation(phase_name, None)
                pipeline_success = False
                break

            # Phase succeeded -- commit if phase tools include write
            if result.success and "write" in phase_config.tools:
                try:
                    committed = commit_changes(
                        message=f"{phase_name}({self.pipeline_id}): {phase_name} phase complete",
                        cwd=self.working_dir,
                    )
                    if committed:
                        self.logger.info(f"Committed changes from {phase_name}")
                    else:
                        self.logger.info(f"No changes to commit from {phase_name}")
                except Exception as e:
                    self.logger.warning(f"Commit failed for {phase_name}: {e}")

        # Pipeline complete
        final_state = "COMPLETE" if pipeline_success else "FAILED"
        self.manifest.update(state=final_state)
        self.manifest.save()

        self.logger.info(
            f"=== Pipeline {final_state}: {self.pipeline_id} ==="
        )

        # Run Monitor phase -- KPI tracking (non-fatal)
        try:
            from engine.monitor import track_kpis
            track_kpis(self.manifest, self.logger)
        except Exception as e:
            self.logger.warning(f"KPI tracking failed (non-fatal): {e}")

        return pipeline_success

    def handle_escalation(
        self,
        phase_name: str,
        gate_result: Optional[GateResult],
    ) -> None:
        """Handle escalation when a phase fails beyond recovery.

        Collects forensic context from the manifest and posts a detailed
        comment to the GitHub issue. This gives the human everything
        they need to understand what happened without starting from scratch.

        Per Harmony architecture: "Escalation is a feature, not a failure."

        Args:
            phase_name: Name of the phase that failed.
            gate_result: The final gate result (may be None for agent errors).
        """
        self.logger.info(f"Escalating phase {phase_name} to human")
        self.manifest.update(escalated=True)

        # Collect forensic context
        artifacts = self.manifest._data.get("artifacts", {})
        phase_history = self.manifest._data.get("phase_history", [])

        # Build escalation comment
        sections = [
            f"## Pipeline Escalation: {phase_name}",
            f"**Pipeline ID**: {self.pipeline_id}",
            f"**Issue**: #{self.issue_number}",
            f"**Failed Phase**: {phase_name}",
            "",
        ]

        if gate_result:
            sections.extend([
                "### Gate Result",
                f"- **Passed**: {gate_result.passed}",
                f"- **Action**: {gate_result.action.value}",
                f"- **Blockers**: {gate_result.blocker_count}",
                f"- **Message**: {gate_result.message}",
                "",
            ])

            if gate_result.issues:
                sections.append("### Issues")
                for issue in gate_result.issues[:10]:  # Cap at 10 issues
                    sections.append(f"- **{issue.get('criteria', 'unknown')}**: {issue.get('message', '')}")
                sections.append("")

        # Include phase history
        if phase_history:
            sections.append("### Phase History")
            for entry in phase_history:
                status_icon = {
                    "complete": "OK",
                    "failed": "FAIL",
                    "healed": "HEALED",
                    "skipped": "SKIP",
                }.get(entry.get("status", ""), "?")
                sections.append(
                    f"- [{status_icon}] {entry.get('phase', '?')} "
                    f"(iterations: {entry.get('iteration', 1)})"
                )
            sections.append("")

        # Include key artifacts (truncated)
        for key in ["plan", "test", "review"]:
            if key in artifacts:
                content = str(artifacts[key])[:500]
                sections.extend([
                    f"### Artifact: {key}",
                    f"```\n{content}\n```",
                    "",
                ])

        sections.extend([
            "### Your Options",
            "- **Give guidance**: Point the agent in the right direction and resume",
            "- **Override gate**: Accept the current output and continue",
            "- **Update layer**: Modify a prompt or gate config, then re-run",
            "- **Abort**: Stop the pipeline (all artifacts are preserved)",
        ])

        comment = "\n".join(sections)

        if self.local_mode:
            # Write escalation to local file instead of GitHub
            from engine.utils import get_project_root
            esc_dir = get_project_root() / "agent_runs_log" / self.pipeline_id
            esc_dir.mkdir(parents=True, exist_ok=True)
            esc_path = esc_dir / "escalation.md"
            esc_path.write_text(comment, encoding="utf-8")
            self.logger.info(f"Escalation written to {esc_path}")
        else:
            try:
                make_issue_comment(self.issue_number, comment)
                self.logger.info("Escalation comment posted to issue")
            except Exception as e:
                self.logger.error(f"Failed to post escalation comment: {e}")
