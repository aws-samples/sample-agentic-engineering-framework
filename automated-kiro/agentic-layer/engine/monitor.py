"""
Monitor Phase - KPI Tracking

Collects pipeline metrics from the PipelineManifest and appends
structured KPI data to a markdown file. This is the observation
layer -- it measures pipeline performance without modifying code
or configuration.

The Monitor-to-Plan feedback arc is HUMAN-MEDIATED by default.
This module generates reports. It does NOT auto-create issues.
This is a deliberate safety decision: automated feedback loops
risk infinite self-generating work.

Per Harmony: "Monitor is the only phase where failure does not
affect the pipeline outcome."
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any, Optional

from engine.manifest import PipelineManifest


# Default KPI output file
DEFAULT_KPI_PATH = "ai_docs/agentic_kpis.md"


def track_kpis(
    manifest: PipelineManifest,
    logger: logging.Logger,
    kpi_path: str = DEFAULT_KPI_PATH,
) -> bool:
    """Collect and record pipeline KPIs from the manifest.

    Triple-nested try/except to ensure KPI tracking NEVER fails the
    pipeline. A KPI tracking failure must never abort a successful
    pipeline run.

    Per Harmony Monitor phase: "Best-effort recording is critical.
    If the Monitor phase cannot access a particular metric, it should
    skip that metric and note it as N/A rather than failing."

    Args:
        manifest: Completed pipeline manifest with phase history and artifacts.
        logger: Logger instance.
        kpi_path: Path to KPI markdown file (default: ai_docs/agentic_kpis.md).

    Returns:
        True if KPIs were successfully recorded, False otherwise.
    """
    try:
        # Layer 1: Collect metrics
        try:
            metrics = _collect_metrics(manifest, logger)
        except Exception as e:
            logger.warning(f"Error collecting metrics: {e}")
            metrics = _fallback_metrics(manifest)

        # Layer 2: Format and write KPIs
        try:
            report = _format_kpi_report(metrics, manifest, logger)
            _append_kpi_report(report, kpi_path, logger)
            logger.info(f"KPI report appended to {kpi_path}")
            return True
        except Exception as e:
            logger.warning(f"Error writing KPI report: {e}")
            # Try minimal write
            try:
                _append_minimal_record(manifest, kpi_path, logger)
                return True
            except Exception as e2:
                logger.error(f"Even minimal KPI recording failed: {e2}")
                return False

    except Exception as e:
        # Layer 3: Outer catch-all. If we get here, something very unexpected happened.
        logger.error(f"Unexpected error in KPI tracking: {e}")
        return False


def _collect_metrics(
    manifest: PipelineManifest,
    logger: logging.Logger,
) -> dict[str, Any]:
    """Collect all available metrics from the manifest.

    Args:
        manifest: Pipeline manifest with execution data.
        logger: Logger instance.

    Returns:
        Dict of metric name -> value. Missing metrics are "N/A".
    """
    metrics: dict[str, Any] = {}

    # Basic info
    metrics["pipeline_id"] = manifest.pipeline_id
    metrics["issue_number"] = manifest.issue_number
    metrics["status"] = manifest.state
    metrics["escalated"] = manifest.escalated
    metrics["timestamp"] = datetime.now().isoformat()

    # Phase history -- get all entries from internal data
    phase_history = manifest._data.get("phase_history", [])
    metrics["phase_count"] = len(phase_history)
    metrics["phases"] = phase_history

    # Calculate total retries
    total_retries = sum(
        max(0, entry.get("iteration", 1) - 1)
        for entry in phase_history
    )
    metrics["total_retries"] = total_retries

    # Phase durations
    total_duration = sum(
        entry.get("duration", 0) for entry in phase_history
    )
    metrics["total_duration_seconds"] = round(total_duration, 2)
    metrics["total_duration_human"] = _format_duration(total_duration)

    # Per-phase breakdown
    phase_breakdown = []
    for entry in phase_history:
        phase_breakdown.append({
            "phase": entry.get("phase", "unknown"),
            "status": entry.get("status", "unknown"),
            "iterations": entry.get("iteration", 1),
            "duration": round(entry.get("duration", 0), 2),
        })
    metrics["phase_breakdown"] = phase_breakdown

    # Artifact stats
    artifacts = manifest._data.get("artifacts", {})
    plan_artifact = artifacts.get("plan", "")
    metrics["plan_size_chars"] = len(plan_artifact) if plan_artifact else "N/A"

    # Count test and review iterations specifically
    test_iterations = 0
    review_iterations = 0
    for entry in phase_history:
        if entry.get("phase") == "test":
            test_iterations = max(test_iterations, entry.get("iteration", 1))
        elif entry.get("phase") == "review":
            review_iterations = max(review_iterations, entry.get("iteration", 1))
    metrics["test_iterations"] = test_iterations
    metrics["review_iterations"] = review_iterations

    # Success streak -- read from existing KPI file
    metrics["success_streak"] = _calculate_success_streak(
        manifest.state, kpi_path=DEFAULT_KPI_PATH, logger=logger,
    )

    return metrics


def _fallback_metrics(manifest: PipelineManifest) -> dict[str, Any]:
    """Minimal metrics when full collection fails."""
    return {
        "pipeline_id": getattr(manifest, "pipeline_id", "unknown"),
        "status": getattr(manifest, "state", "unknown"),
        "timestamp": datetime.now().isoformat(),
        "error": "Full metric collection failed",
    }


def _format_duration(seconds: float) -> str:
    """Format seconds into human-readable duration."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    return f"{minutes}m {remaining_seconds}s"


def _calculate_success_streak(
    current_status: str,
    kpi_path: str,
    logger: logging.Logger,
) -> int:
    """Calculate the current success streak from KPI history.

    Reads the existing KPI file and counts consecutive "complete"
    statuses from the most recent entry backward.

    Args:
        current_status: Status of the current pipeline run.
        kpi_path: Path to KPI file.
        logger: Logger instance.

    Returns:
        Current streak count (including this run if successful).
    """
    streak = 0

    try:
        if not os.path.exists(kpi_path):
            return 1 if current_status == "complete" else 0

        with open(kpi_path, "r") as f:
            content = f.read()

        # Count consecutive "Status | complete" lines from the end
        # This is a simple heuristic -- reads the markdown table rows
        lines = content.split("\n")
        for line in reversed(lines):
            if "| complete |" in line.lower():
                streak += 1
            elif "| failed |" in line.lower() or "| escalated |" in line.lower():
                break

    except Exception as e:
        logger.warning(f"Error calculating success streak: {e}")

    if current_status == "complete":
        streak += 1

    return streak


def _format_kpi_report(
    metrics: dict[str, Any],
    manifest: PipelineManifest,
    logger: logging.Logger,
) -> str:
    """Format metrics into a KPI report section.

    Follows the Harmony Monitor phase KPI Report Template format.

    Args:
        metrics: Collected metrics dict.
        manifest: Pipeline manifest.
        logger: Logger instance.

    Returns:
        Formatted markdown string.
    """
    sections = []

    # Header
    pipeline_id = metrics.get("pipeline_id", "unknown")
    sections.append(f"## KPI Report -- {pipeline_id}")
    sections.append("")
    sections.append(f"*Generated: {metrics.get('timestamp', 'N/A')}*")
    sections.append("")

    # Summary table
    sections.append("### Summary")
    sections.append("| Metric | Value |")
    sections.append("|--------|-------|")
    sections.append(f"| Status | {metrics.get('status', 'N/A')} |")
    sections.append(f"| Issue | #{metrics.get('issue_number', 'N/A')} |")
    sections.append(f"| Duration | {metrics.get('total_duration_human', 'N/A')} |")
    sections.append(f"| Total Retries | {metrics.get('total_retries', 'N/A')} |")
    sections.append(f"| Test Iterations | {metrics.get('test_iterations', 'N/A')} |")
    sections.append(f"| Review Iterations | {metrics.get('review_iterations', 'N/A')} |")
    sections.append(f"| Plan Size | {metrics.get('plan_size_chars', 'N/A')} chars |")
    sections.append(f"| Success Streak | {metrics.get('success_streak', 'N/A')} |")
    sections.append(f"| Escalated | {metrics.get('escalated', False)} |")
    sections.append("")

    # Per-phase breakdown
    phase_breakdown = metrics.get("phase_breakdown", [])
    if phase_breakdown:
        sections.append("### Per-Phase Breakdown")
        sections.append("| Phase | Status | Iterations | Duration |")
        sections.append("|-------|--------|------------|----------|")
        for phase in phase_breakdown:
            sections.append(
                f"| {phase['phase']} | {phase['status']} | "
                f"{phase['iterations']} | {_format_duration(phase['duration'])} |"
            )
        sections.append("")

    # Feedback items (human-mediated)
    feedback_items = []
    if metrics.get("total_retries", 0) >= 3:
        feedback_items.append(
            f"- High retry count ({metrics['total_retries']}). "
            f"Consider reviewing test stability or plan quality."
        )
    if metrics.get("status") == "failed":
        feedback_items.append(
            f"- Pipeline failed. Review escalation context in issue #{metrics.get('issue_number')}."
        )
    if metrics.get("escalated"):
        feedback_items.append(
            f"- Pipeline escalated to human. Check if gate thresholds need adjustment."
        )

    if feedback_items:
        sections.append("### Feedback (Human Review Recommended)")
        sections.extend(feedback_items)
    else:
        sections.append("### Feedback")
        sections.append("- None (clean run)")

    sections.append("")
    sections.append("---")
    sections.append("")

    return "\n".join(sections)


def _append_kpi_report(
    report: str,
    kpi_path: str,
    logger: logging.Logger,
) -> None:
    """Append KPI report to the KPI markdown file.

    Creates the file with a header if it doesn't exist.

    Args:
        report: Formatted KPI report string.
        kpi_path: Path to KPI file.
        logger: Logger instance.
    """
    # Ensure directory exists
    kpi_dir = os.path.dirname(kpi_path)
    if kpi_dir:
        os.makedirs(kpi_dir, exist_ok=True)

    # Create header if file doesn't exist
    if not os.path.exists(kpi_path):
        header = (
            "# Agentic KPIs\n\n"
            "Pipeline performance metrics tracked by the AEF Monitor phase.\n"
            "This file is human-mediated: metrics are recorded automatically,\n"
            "but action items require human review and decision.\n\n"
            "---\n\n"
        )
        with open(kpi_path, "w") as f:
            f.write(header)

    with open(kpi_path, "a") as f:
        f.write(report)


def _append_minimal_record(
    manifest: PipelineManifest,
    kpi_path: str,
    logger: logging.Logger,
) -> None:
    """Append a minimal one-line record when full reporting fails.

    This is the last-resort recording mechanism. Even if metric
    collection and formatting fail, we still want to record that
    a pipeline ran.
    """
    kpi_dir = os.path.dirname(kpi_path)
    if kpi_dir:
        os.makedirs(kpi_dir, exist_ok=True)
    line = (
        f"| {getattr(manifest, 'pipeline_id', '?')} "
        f"| {getattr(manifest, 'state', '?')} "
        f"| {datetime.now().isoformat()} "
        f"| (metrics unavailable) |\n"
    )
    with open(kpi_path, "a") as f:
        f.write(line)
