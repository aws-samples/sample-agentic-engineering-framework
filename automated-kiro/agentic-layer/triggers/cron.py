"""
Cron-based trigger that polls GitHub for qualifying issues.

Polls every N seconds (default: 20) to detect:
1. New issues without comments
2. Issues where the latest comment contains a trigger keyword

When a qualifying issue is found, launches PipelineRunner as a subprocess
to ensure clean state per run.

Usage:
    from triggers.cron import start_cron
    start_cron(interval=20, config_path="adw/agentic-layer/pipeline.yaml")
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from typing import Optional

import schedule

from engine.github import (
    fetch_open_issues,
    fetch_issue,
    get_repo_url,
    extract_repo_path,
)
from engine.utils import setup_logger, get_safe_subprocess_env

# Trigger keyword -- issues/comments containing this trigger the pipeline
TRIGGER_KEYWORD = "aef"

# Bot identifier to prevent processing our own comments
BOT_IDENTIFIER = "[aef-pipeline]"

# Module-level state
_processed_issues: set[int] = set()
_issue_last_comment: dict[int, Optional[str]] = {}
_shutdown_requested = False
_logger = setup_logger("cron", "trigger_cron")


def _signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global _shutdown_requested
    _logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    _shutdown_requested = True


def _should_process_issue(repo_path: str, issue_number: int) -> bool:
    """Determine if an issue should be processed based on comments.

    An issue qualifies if:
    1. It has no comments (new issue), OR
    2. Its latest comment contains the trigger keyword and hasn't been processed

    Args:
        repo_path: GitHub repository path (owner/repo).
        issue_number: Issue number to check.

    Returns:
        True if the issue should be processed.
    """
    issue = fetch_issue(issue_number, repo_path=repo_path)
    comments = issue.comments

    # New issue with no comments
    if not comments:
        _logger.info(f"Issue #{issue_number} has no comments -- qualifying")
        return True

    latest_comment = comments[-1]
    comment_body = latest_comment.body.lower()
    comment_id = latest_comment.id

    # Skip if we already processed this comment
    if _issue_last_comment.get(issue_number) == comment_id:
        return False

    # Skip bot comments to prevent loops
    if BOT_IDENTIFIER.lower() in comment_body:
        return False

    # Check for trigger keyword
    if TRIGGER_KEYWORD in comment_body:
        _logger.info(
            f"Issue #{issue_number} -- latest comment contains '{TRIGGER_KEYWORD}'"
        )
        _issue_last_comment[issue_number] = comment_id
        return True

    return False


def _launch_pipeline(
    issue_number: int,
    config_path: str,
) -> bool:
    """Launch PipelineRunner as a subprocess for an issue.

    Runs `uv run adw/run.py <issue_number> --config <config_path>`
    as a subprocess. Each pipeline run gets its own process for
    clean state isolation.

    Args:
        issue_number: GitHub issue number.
        config_path: Path to pipeline.yaml.

    Returns:
        True if subprocess launched successfully.
    """
    try:
        # Build the command
        cmd = [
            sys.executable,
            "adw/run.py",
            str(issue_number),
            "--config", config_path,
        ]

        _logger.info(f"Launching pipeline for issue #{issue_number}: {' '.join(cmd)}")

        # Run as subprocess (blocking -- cron handles one at a time)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=get_safe_subprocess_env(),
        )

        if result.returncode == 0:
            _logger.info(f"Pipeline completed successfully for issue #{issue_number}")
            return True
        else:
            _logger.error(
                f"Pipeline failed for issue #{issue_number}: {result.stderr[:500]}"
            )
            return False

    except Exception as e:
        _logger.error(f"Exception launching pipeline for issue #{issue_number}: {e}")
        return False


def _check_and_process_issues(
    repo_path: str,
    config_path: str,
) -> None:
    """Main check cycle: fetch issues, filter, and process qualifying ones.

    Args:
        repo_path: GitHub repository path (owner/repo).
        config_path: Path to pipeline.yaml.
    """
    if _shutdown_requested:
        _logger.info("Shutdown requested, skipping check cycle")
        return

    start_time = time.time()
    _logger.info("Starting issue check cycle")

    try:
        issues = fetch_open_issues(repo_path)
        if not issues:
            _logger.info("No open issues found")
            return

        qualifying = []
        for issue in issues:
            issue_number = issue.number
            if not issue_number:
                continue
            if issue_number in _processed_issues:
                continue
            if _should_process_issue(repo_path, issue_number):
                qualifying.append(issue_number)

        if qualifying:
            _logger.info(f"Found {len(qualifying)} qualifying issues: {qualifying}")
            for issue_number in qualifying:
                if _shutdown_requested:
                    _logger.info("Shutdown requested, stopping issue processing")
                    break
                if _launch_pipeline(issue_number, config_path):
                    _processed_issues.add(issue_number)
                else:
                    _logger.warning(
                        f"Failed to process issue #{issue_number}, will retry next cycle"
                    )
        else:
            _logger.info("No qualifying issues found")

        cycle_time = time.time() - start_time
        _logger.info(
            f"Check cycle completed in {cycle_time:.2f}s. "
            f"Total processed this session: {len(_processed_issues)}"
        )

    except Exception as e:
        _logger.error(f"Error during check cycle: {e}")
        import traceback
        traceback.print_exc()


def start_cron(
    interval: int = 20,
    config_path: str = "adw/agentic-layer/pipeline.yaml",
) -> None:
    """Start the cron polling loop.

    Polls GitHub every `interval` seconds for qualifying issues.
    Blocks the calling thread. Exits gracefully on SIGINT/SIGTERM.

    Args:
        interval: Polling interval in seconds (default: 20).
        config_path: Path to pipeline.yaml.
    """
    global _shutdown_requested
    _shutdown_requested = False

    try:
        repo_url = get_repo_url()
        repo_path = extract_repo_path(repo_url)
    except (ValueError, RuntimeError) as e:
        _logger.error(f"Cannot determine repository: {e}")
        sys.exit(1)

    _logger.info(f"Starting AEF cron trigger")
    _logger.info(f"Repository: {repo_path}")
    _logger.info(f"Polling interval: {interval}s")
    _logger.info(f"Trigger keyword: '{TRIGGER_KEYWORD}'")
    _logger.info(f"Pipeline config: {config_path}")

    # Register signal handlers
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    # Schedule the check function
    schedule.every(interval).seconds.do(
        _check_and_process_issues, repo_path, config_path
    )

    # Run initial check immediately
    _check_and_process_issues(repo_path, config_path)

    # Main loop
    _logger.info("Entering main scheduling loop")
    while not _shutdown_requested:
        schedule.run_pending()
        time.sleep(1)

    _logger.info("Cron trigger shutdown complete")
