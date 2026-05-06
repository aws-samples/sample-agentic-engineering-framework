"""Kiro agent wrapper for the pipeline engine.

Bridges engine types (AgentTemplateRequest, AgentPromptResponse) with
the standalone Kiro runner (KiroRunnerConfig, KiroRunResult).
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path

from engine.types import (
    AgentPromptResponse,
    AgentTemplateRequest,
    ModelSet,
    RetryCode,
)
from engine.utils import get_project_root

from .kiro_runner import KiroRunnerConfig, run_kiro

logger = logging.getLogger(__name__)


_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _strip_ansi(text: str) -> str:
    """Strip ANSI escape codes from text."""
    return _ANSI_RE.sub("", text)


def _map_exit_code_to_retry_code(exit_code: int, is_error: bool) -> RetryCode:
    """Map Kiro exit code to engine RetryCode."""
    if not is_error:
        return RetryCode.NONE
    if exit_code == -1:
        return RetryCode.TIMEOUT
    return RetryCode.EXECUTION_ERROR


def _read_template(template_path: str) -> str:
    """Read a prompt template file from disk.

    Args:
        template_path: Absolute path to the template .md file.

    Returns:
        Template contents as a string.

    Raises:
        FileNotFoundError: If the template file does not exist.
    """
    path = Path(template_path)
    if not path.is_file():
        raise FileNotFoundError(f"Prompt template not found: {template_path}")
    return path.read_text(encoding="utf-8")


def _substitute_vars(template: str, template_vars: dict) -> str:
    """Substitute ${variable} placeholders in a template.

    Args:
        template: Template text with ${variable} placeholders.
        template_vars: Dict of variable names to values.

    Returns:
        Template with placeholders replaced.
    """
    result = template
    for key, value in template_vars.items():
        result = result.replace(f"${{{key}}}", str(value))
    return result


def save_prompt(pipeline_id: str, agent_name: str, prompt: str) -> None:
    """Save prompt to disk for audit trail."""
    # Extract command name from slash command, or use agent_name
    match = re.match(r"^(/\w+)", prompt)
    command_name = match.group(1)[1:] if match else agent_name
    project_root = get_project_root()
    prompt_dir = project_root / "agent_runs_log" / pipeline_id / agent_name / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    (prompt_dir / f"{command_name}.txt").write_text(prompt)


def execute_template(
    request: AgentTemplateRequest,
    model_set: ModelSet = "base",
) -> AgentPromptResponse:
    """Execute a Kiro CLI template for a pipeline phase.

    If request.template_path is set, reads the template file from disk,
    substitutes ${variable} placeholders with request.template_vars,
    and sends the full text to kiro-cli.

    If no template_path, falls back to sending the slash command string
    (for backwards compatibility).

    Args:
        request: Template request with agent_name, slash_command, args, pipeline_id.
        model_set: Ignored by Kiro (Kiro selects model internally).

    Returns:
        AgentPromptResponse from execution.
    """
    # Build prompt: read template file or fall back to slash command
    if request.template_path:
        logger.info(f"Reading template: {request.template_path}")
        try:
            prompt = _read_template(request.template_path)
            if request.template_vars:
                prompt = _substitute_vars(prompt, request.template_vars)
        except FileNotFoundError as e:
            logger.error(f"Template not found: {e}")
            return AgentPromptResponse(
                output=str(e),
                success=False,
                session_id=None,
                retry_code=RetryCode.EXECUTION_ERROR,
            )
    else:
        prompt = f"{request.slash_command} {' '.join(request.args)}"

    # Save for audit
    save_prompt(request.pipeline_id, request.agent_name, prompt)

    # Build Kiro config
    cwd = request.working_dir or os.getcwd()
    config = KiroRunnerConfig(
        prompt=prompt,
        cwd=cwd,
        trust_all=True,
    )

    # Execute
    logger.info(f"Invoking kiro-cli for {request.agent_name} ({len(prompt)} chars)")
    kiro_result = run_kiro(config)

    # Translate result
    return AgentPromptResponse(
        output=_strip_ansi(kiro_result.result_text),
        success=not kiro_result.is_error,
        session_id=None,
        retry_code=_map_exit_code_to_retry_code(
            kiro_result.exit_code, kiro_result.is_error
        ),
    )
