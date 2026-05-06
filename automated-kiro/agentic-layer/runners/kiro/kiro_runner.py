"""Kiro CLI runner.

Wraps `kiro-cli chat --no-interactive` as a blocking subprocess.
Handles command construction, tool trust flags, timeout, and
stdout/stderr capture.

Dependencies: stdlib only + pydantic. ZERO imports from adw.engine.
"""

from __future__ import annotations

import logging
import os
import subprocess
import time
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

KIRO_PATH = os.getenv("KIRO_CLI_PATH", "kiro-cli")


@dataclass
class KiroRunnerConfig:
    """Configuration for a single Kiro CLI invocation.

    Attributes:
        prompt: The prompt text to send to Kiro.
        cwd: Working directory for the subprocess.
        trust_tools: List of specific tools to trust (e.g., ["read", "write", "shell"]).
                     Ignored if trust_all is True.
        trust_all: If True, use --trust-all-tools instead of --trust-tools.
        verbose: If True, add --verbose flag.
        timeout: Subprocess timeout in seconds. Default 1800 (30 minutes).
    """
    prompt: str
    cwd: str
    trust_tools: list[str] = field(default_factory=lambda: ["read", "write", "shell"])
    trust_all: bool = True
    verbose: bool = False
    timeout: int = 1800


@dataclass
class KiroRunResult:
    """Result of a Kiro CLI invocation.

    Attributes:
        result_text: Captured stdout from kiro-cli.
        is_error: True if the invocation failed (non-zero exit or timeout).
        exit_code: Process exit code. -1 for timeout, -2 for other exceptions.
        duration_ms: Wall-clock execution time in milliseconds.
    """
    result_text: str
    is_error: bool
    exit_code: int
    duration_ms: int


def build_kiro_command(config: KiroRunnerConfig) -> list[str]:
    """Build the kiro-cli command line from config.

    Pure function with no side effects. Constructs the argument list
    for subprocess.run().

    The command structure is:
        kiro-cli chat --no-interactive <prompt> [--trust-all-tools | --trust-tools t1,t2] [--verbose]

    Args:
        config: Runner configuration.

    Returns:
        List of command-line arguments suitable for subprocess.run().
    """
    cmd = [KIRO_PATH, "chat", "--no-interactive", config.prompt]

    # Trust flags
    if config.trust_all:
        cmd.append("--trust-all-tools")
    elif config.trust_tools:
        cmd.extend(["--trust-tools", ",".join(config.trust_tools)])

    # Verbose
    if config.verbose:
        cmd.append("--verbose")

    return cmd


def run_kiro(config: KiroRunnerConfig) -> KiroRunResult:
    """Execute kiro-cli as a blocking subprocess.

    Runs the command built by build_kiro_command(), captures stdout and
    stderr, handles timeout, and returns a KiroRunResult.

    Unlike other runners that may use JSONL streaming, Kiro produces plain text on
    stdout. We capture the entire output as a single string.

    Args:
        config: Runner configuration.

    Returns:
        KiroRunResult with captured output, error status, exit code, and duration.
    """
    cmd = build_kiro_command(config)

    logger.info(
        "Running kiro-cli: cwd=%s, trust_all=%s, timeout=%d",
        config.cwd, config.trust_all, config.timeout,
    )
    logger.debug("Full command: %s", cmd)

    start_ms = _now_ms()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=config.cwd,
            timeout=config.timeout,
        )

        duration_ms = _now_ms() - start_ms
        stdout = result.stdout.strip() if result.stdout else ""
        stderr = result.stderr.strip() if result.stderr else ""

        if result.returncode != 0:
            logger.error(
                "kiro-cli failed (exit %d): %s", result.returncode, stderr[:500]
            )
            # Combine stdout and stderr for error context
            error_text = stdout
            if stderr:
                error_text = f"{stdout}\n\nSTDERR:\n{stderr}" if stdout else stderr

            return KiroRunResult(
                result_text=error_text,
                is_error=True,
                exit_code=result.returncode,
                duration_ms=duration_ms,
            )

        logger.info(
            "kiro-cli completed successfully in %dms (%d chars output)",
            duration_ms, len(stdout),
        )

        return KiroRunResult(
            result_text=stdout,
            is_error=False,
            exit_code=0,
            duration_ms=duration_ms,
        )

    except subprocess.TimeoutExpired:
        duration_ms = _now_ms() - start_ms
        logger.error("kiro-cli timed out after %dms", duration_ms)
        return KiroRunResult(
            result_text=f"kiro-cli timed out after {config.timeout}s",
            is_error=True,
            exit_code=-1,
            duration_ms=duration_ms,
        )

    except FileNotFoundError:
        duration_ms = _now_ms() - start_ms
        msg = f"kiro-cli not found at '{KIRO_PATH}'. Install it or set KIRO_CLI_PATH."
        logger.error(msg)
        return KiroRunResult(
            result_text=msg,
            is_error=True,
            exit_code=-2,
            duration_ms=duration_ms,
        )

    except Exception as e:
        duration_ms = _now_ms() - start_ms
        msg = f"Unexpected error running kiro-cli: {e}"
        logger.error(msg)
        return KiroRunResult(
            result_text=msg,
            is_error=True,
            exit_code=-2,
            duration_ms=duration_ms,
        )


def _now_ms() -> int:
    """Return current time in milliseconds."""
    return int(time.time() * 1000)
