"""
Quality Gate Evaluator

Loads gate YAML files and evaluates phase outputs against gate criteria.
Implements the three-layer gate taxonomy: classification, healing, disposition.

The evaluator answers HOW to check. The gate YAML answers WHAT to check.
The pipeline runner answers WHAT TO DO with the result.
"""

from __future__ import annotations

import os
import yaml
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional


class GateAction(Enum):
    """What the gate recommends after evaluation."""
    CONTINUE = "continue"       # Gate passed, proceed to next phase
    RETRY = "retry"             # Gate failed, re-run the same phase
    PATCH = "patch"             # Gate failed, run patcher then re-run phase
    ESCALATE = "escalate"       # Gate failed, healing exhausted, need human
    ABORT = "abort"             # Gate failed, disposition says stop pipeline


class PhaseDisposition(Enum):
    """How a phase failure affects pipeline flow.

    This is NOT in the gate YAML -- it comes from pipeline.yaml's
    phase configuration. The same gate can be REQUIRED at L4 and
    OPTIONAL at L3. Disposition is about pipeline flow control,
    not gate evaluation.
    """
    REQUIRED = "required"       # Failure stops the pipeline
    OPTIONAL = "optional"       # Failure logs a warning, pipeline continues
    CHECKPOINT = "checkpoint"   # Failure pauses for human approval


@dataclass
class GateResult:
    """Structured result from gate evaluation.

    The runner reads this to decide: continue, heal, escalate, or abort.
    """
    passed: bool
    action: GateAction
    message: str
    blocker_count: int = 0
    issues: list[dict[str, Any]] = field(default_factory=list)


# Type alias for criteria evaluation functions.
# Each function takes (phase_output: dict, threshold: Any) -> (passed, message)
CriteriaFn = Callable[[dict[str, Any], Any], tuple[bool, str]]


def _check_all_tests_pass(phase_output: dict[str, Any], threshold: Any) -> tuple[bool, str]:
    """Check that all items in test results have passed: true.

    Expects phase_output to contain a 'test_results' key with a list of
    dicts, each having a 'passed' boolean field.
    """
    results = phase_output.get("test_results", [])
    if not results:
        return False, "No test results found in phase output"

    failed = [r for r in results if not r.get("passed", False)]
    if failed:
        names = [r.get("test_name", "unknown") for r in failed[:5]]
        suffix = f" (and {len(failed) - 5} more)" if len(failed) > 5 else ""
        return False, f"{len(failed)} test(s) failed: {', '.join(names)}{suffix}"

    return True, f"All {len(results)} tests passed"


def _check_no_blockers(phase_output: dict[str, Any], threshold: Any) -> tuple[bool, str]:
    """Check that review issues have zero items with severity 'blocker'.

    Expects phase_output to contain a 'review_issues' key with a list of
    dicts, each having an 'issue_severity' field.
    """
    issues = phase_output.get("review_issues", [])
    blockers = [i for i in issues if i.get("issue_severity") == "blocker"]

    if blockers:
        descs = [i.get("issue_description", "unknown")[:60] for i in blockers[:3]]
        suffix = f" (and {len(blockers) - 3} more)" if len(blockers) > 3 else ""
        return False, f"{len(blockers)} blocker(s): {'; '.join(descs)}{suffix}"

    return True, f"No blockers found ({len(issues)} total issues)"


def _check_manifest_complete(phase_output: dict[str, Any], threshold: Any) -> tuple[bool, str]:
    """Check that all required manifest fields are populated.

    Expects phase_output to contain a 'manifest' key with a dict.
    The threshold is a list of required field names.
    """
    manifest = phase_output.get("manifest", {})
    required_fields = threshold if isinstance(threshold, list) else []

    missing = [f for f in required_fields if not manifest.get(f)]
    if missing:
        return False, f"Missing manifest fields: {', '.join(missing)}"

    return True, "All required manifest fields populated"


def _check_coverage_minimum(phase_output: dict[str, Any], threshold: Any) -> tuple[bool, str]:
    """Check that code coverage meets a numeric minimum.

    Expects phase_output to contain a 'coverage' key with a numeric value.
    The threshold is the minimum percentage (e.g., 80).
    """
    coverage = phase_output.get("coverage")
    if coverage is None:
        return False, "No coverage data found in phase output"

    min_coverage = float(threshold) if threshold else 0
    if coverage < min_coverage:
        return False, f"Coverage {coverage}% below minimum {min_coverage}%"

    return True, f"Coverage {coverage}% meets minimum {min_coverage}%"


# Built-in criteria registry. Maps criteria name (from gate YAML) to
# evaluation function. Extend by adding entries to this dict.
CRITERIA_REGISTRY: dict[str, CriteriaFn] = {
    "all_tests_pass": _check_all_tests_pass,
    "no_blockers": _check_no_blockers,
    "manifest_complete": _check_manifest_complete,
    "coverage_minimum": _check_coverage_minimum,
}


class GateEvaluator:
    """Loads gate YAML definitions and evaluates phase outputs against them.

    Gate YAML files define WHAT to check (criteria) and HOW to heal (retry config).
    The evaluator implements the evaluation logic for each criteria type.
    Disposition (does failure stop the pipeline) is NOT in the gate YAML --
    it comes from pipeline.yaml and is passed in by the runner.

    Usage:
        evaluator = GateEvaluator(gates_dir="adw/agentic-layer/gates")
        result = evaluator.evaluate("test-pass", phase_output)
        if not result.passed:
            healing = evaluator.get_healing_config("test-pass")
            # runner decides what to do based on healing config and disposition
    """

    def __init__(self, gates_dir: str) -> None:
        """Load all YAML gate files from the given directory.

        Args:
            gates_dir: Path to directory containing gate YAML files.
                       Each .yaml file is loaded and indexed by its
                       'gate' field (the gate name).
        """
        self._gates: dict[str, dict[str, Any]] = {}
        self._criteria_registry: dict[str, CriteriaFn] = dict(CRITERIA_REGISTRY)

        if not os.path.isdir(gates_dir):
            raise FileNotFoundError(f"Gates directory not found: {gates_dir}")

        for filename in os.listdir(gates_dir):
            if not filename.endswith((".yaml", ".yml")):
                continue
            filepath = os.path.join(gates_dir, filename)
            with open(filepath, "r") as f:
                gate_def = yaml.safe_load(f)
            if gate_def and "gate" in gate_def:
                self._gates[gate_def["gate"]] = gate_def

    @property
    def gate_names(self) -> list[str]:
        """Return list of loaded gate names."""
        return list(self._gates.keys())

    def register_criteria(self, name: str, fn: CriteriaFn) -> None:
        """Register a custom criteria evaluation function.

        Args:
            name: Criteria name as it appears in gate YAML.
            fn: Function with signature (phase_output, threshold) -> (bool, str).
        """
        self._criteria_registry[name] = fn

    def evaluate(self, gate_name: str, phase_output: dict[str, Any]) -> GateResult:
        """Evaluate structured phase output against a gate's criteria.

        Runs each criteria defined in the gate's YAML against the phase
        output. If ANY criteria fails, the gate fails. The action is
        determined by the gate's on_fail setting.

        Args:
            gate_name: Name of the gate (matches 'gate' field in YAML).
            phase_output: Structured dict from phase execution
                          (e.g., parsed JSON test results).

        Returns:
            GateResult with passed status, recommended action, and details.

        Raises:
            KeyError: If gate_name is not found in loaded gates.
        """
        if gate_name not in self._gates:
            raise KeyError(f"Gate not found: {gate_name}. Available: {self.gate_names}")

        gate_def = self._gates[gate_name]
        criteria = gate_def.get("criteria", {})
        all_passed = True
        messages = []
        issues = []

        for criteria_name, threshold in criteria.items():
            fn = self._criteria_registry.get(criteria_name)
            if fn is None:
                messages.append(f"Unknown criteria: {criteria_name} (skipped)")
                continue

            passed, msg = fn(phase_output, threshold)
            messages.append(msg)

            if not passed:
                all_passed = False
                issues.append({
                    "criteria": criteria_name,
                    "message": msg,
                    "threshold": threshold,
                })

        if all_passed:
            return GateResult(
                passed=True,
                action=GateAction.CONTINUE,
                message="; ".join(messages),
            )

        # Gate failed -- determine action from gate config
        on_fail = gate_def.get("on_fail", "escalate")
        action_map = {
            "retry": GateAction.RETRY,
            "patch": GateAction.PATCH,
            "escalate": GateAction.ESCALATE,
            "log": GateAction.CONTINUE,  # log-only: continue despite failure
        }
        action = action_map.get(on_fail, GateAction.ESCALATE)

        # Count blockers from classified issues
        classified = self.classify_issues(phase_output, gate_name)
        blocker_count = len(classified.get("blocker", []))

        return GateResult(
            passed=False,
            action=action,
            message="; ".join(messages),
            blocker_count=blocker_count,
            issues=issues,
        )

    def get_disposition(
        self, gate_name: str, autonomy_level: str
    ) -> PhaseDisposition:
        """Return the disposition for a gate at a given autonomy level.

        Disposition is looked up from pipeline.yaml's phase config, but
        for convenience, gate YAML files can include a disposition_overrides
        map keyed by autonomy level. If no override exists, defaults to
        REQUIRED.

        Args:
            gate_name: Name of the gate.
            autonomy_level: One of "assisted", "supervised", "autonomous", "ase".

        Returns:
            PhaseDisposition enum value.
        """
        if gate_name not in self._gates:
            return PhaseDisposition.REQUIRED

        gate_def = self._gates[gate_name]
        overrides = gate_def.get("disposition_overrides", {})
        disposition_str = overrides.get(autonomy_level, "required")

        disposition_map = {
            "required": PhaseDisposition.REQUIRED,
            "optional": PhaseDisposition.OPTIONAL,
            "checkpoint": PhaseDisposition.CHECKPOINT,
        }
        return disposition_map.get(disposition_str, PhaseDisposition.REQUIRED)

    def get_healing_config(self, gate_name: str) -> dict[str, Any]:
        """Return the healing/retry configuration for a gate.

        Healing config is IN the gate YAML because it describes the gate's
        remediation behavior, not the pipeline's flow control.

        Args:
            gate_name: Name of the gate.

        Returns:
            Dict with keys: max_retries (int), stop_on_no_progress (bool),
            strategy (str: "retry" or "patch"). Defaults provided for
            missing fields.
        """
        if gate_name not in self._gates:
            return {
                "max_retries": 0,
                "stop_on_no_progress": True,
                "strategy": "retry",
            }

        gate_def = self._gates[gate_name]
        return {
            "max_retries": gate_def.get("max_retries", 3),
            "stop_on_no_progress": gate_def.get("stop_on_no_progress", True),
            "strategy": gate_def.get("on_fail", "retry"),
        }

    def classify_issues(
        self, phase_output: dict[str, Any], gate_name: str
    ) -> dict[str, list[dict[str, Any]]]:
        """Classify issues from phase output by severity using gate criteria.

        This is the classification layer of the gate taxonomy. It reads
        the phase output's issue list and groups them by severity.

        Args:
            phase_output: Structured dict from phase execution.
            gate_name: Name of the gate (used to determine which
                       output fields to inspect).

        Returns:
            Dict mapping severity level to list of issues.
            E.g., {"blocker": [...], "tech_debt": [...], "skippable": [...]}
        """
        classified: dict[str, list[dict[str, Any]]] = {
            "blocker": [],
            "tech_debt": [],
            "skippable": [],
        }

        # Check review issues
        review_issues = phase_output.get("review_issues", [])
        for issue in review_issues:
            severity = issue.get("issue_severity", "skippable")
            if severity in classified:
                classified[severity].append(issue)
            else:
                classified["skippable"].append(issue)

        # Check test results -- failed tests are blockers
        test_results = phase_output.get("test_results", [])
        for result in test_results:
            if not result.get("passed", True):
                classified["blocker"].append({
                    "type": "test_failure",
                    "test_name": result.get("test_name", "unknown"),
                    "message": result.get("error_message", "Test failed"),
                })

        return classified
