"""Subagent system for Kiro pre-research.

Since Kiro has no Agent tool at runtime, pre-research tasks must run
as separate sequential Kiro invocations before the main task. A subagent:

1. Loads an agent persona via agent_loader.load_agent()
2. Combines the persona's system_prompt with the task prompt
3. Invokes run_kiro() with the combined prompt
4. Returns a SubagentResult with the output

Subagents are designed to run sequentially -- each subagent's output
can feed into the next subagent's prompt or into the main task prompt.

Dependencies: adw.kiro.kiro_runner, adw.kiro.agent_loader. ZERO imports from adw.engine.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from .agent_loader import AgentDefinition, build_combined_prompt, load_agent
from .kiro_runner import KiroRunnerConfig, KiroRunResult, run_kiro

logger = logging.getLogger(__name__)


@dataclass
class SubagentResult:
    """Result of a subagent invocation.

    Attributes:
        agent_name: Name of the agent persona used.
        output: Captured text output from the Kiro invocation.
        is_error: True if the invocation failed.
        duration_ms: Wall-clock execution time in milliseconds.
    """
    agent_name: str
    output: str
    is_error: bool
    duration_ms: int


def run_kiro_subagent(
    agent_name: str,
    task_prompt: str,
    cwd: str,
    agents_dir: Optional[str] = None,
    trust_all: bool = True,
    timeout: int = 1800,
    verbose: bool = False,
) -> SubagentResult:
    """Load an agent persona and execute a task via Kiro.

    High-level entry point that:
    1. Loads the agent definition from a .md file
    2. Combines the agent's system_prompt with the task_prompt
    3. Configures trust flags from the agent's tools list (unless trust_all)
    4. Invokes run_kiro() with the combined prompt
    5. Returns a SubagentResult

    Args:
        agent_name: Name of the agent persona to load (filename without .md).
        task_prompt: The task-specific prompt text.
        cwd: Working directory for the Kiro subprocess.
        agents_dir: Directory containing agent .md files. Uses default if None.
        trust_all: If True, use --trust-all-tools. If False, derive trust_tools
                   from the agent definition's tools list.
        timeout: Subprocess timeout in seconds.
        verbose: Enable verbose Kiro output.

    Returns:
        SubagentResult with output, error status, and timing.

    Raises:
        FileNotFoundError: If the agent persona file is not found.
        ValueError: If the agent persona file is malformed.
    """
    logger.info(
        "Running subagent '%s' with task prompt (%d chars)",
        agent_name, len(task_prompt),
    )

    # Step 1: Load agent definition
    agent = load_agent(agent_name, agents_dir=agents_dir)
    logger.info(
        "Loaded agent '%s': description='%s', tools=%s",
        agent.name, agent.description, agent.tools,
    )

    # Step 2: Combine prompts
    combined_prompt = build_combined_prompt(agent.system_prompt, task_prompt)
    logger.debug(
        "Combined prompt length: %d chars (system=%d, task=%d)",
        len(combined_prompt), len(agent.system_prompt), len(task_prompt),
    )

    # Step 3: Configure runner
    config = KiroRunnerConfig(
        prompt=combined_prompt,
        cwd=cwd,
        trust_tools=agent.tools if not trust_all else ["read", "write", "shell"],
        trust_all=trust_all,
        verbose=verbose,
        timeout=timeout,
    )

    # Step 4: Execute
    kiro_result: KiroRunResult = run_kiro(config)

    # Step 5: Build subagent result
    subagent_result = SubagentResult(
        agent_name=agent.name,
        output=kiro_result.result_text,
        is_error=kiro_result.is_error,
        duration_ms=kiro_result.duration_ms,
    )

    if kiro_result.is_error:
        logger.warning(
            "Subagent '%s' failed (exit %d) in %dms",
            agent.name, kiro_result.exit_code, kiro_result.duration_ms,
        )
    else:
        logger.info(
            "Subagent '%s' completed in %dms (%d chars output)",
            agent.name, kiro_result.duration_ms, len(kiro_result.result_text),
        )

    return subagent_result


def run_subagent_chain(
    agents: list[tuple[str, str]],
    cwd: str,
    agents_dir: Optional[str] = None,
    trust_all: bool = True,
    timeout: int = 1800,
    verbose: bool = False,
    stop_on_error: bool = True,
) -> list[SubagentResult]:
    """Run multiple subagents sequentially, feeding each output to the next.

    Each entry in agents is (agent_name, task_prompt). The output of each
    subagent is appended to the next subagent's task_prompt as context.

    This is the pre-research pattern: run a series of research agents
    to gather context, then feed all their outputs into the main task.

    Args:
        agents: List of (agent_name, task_prompt) tuples to execute in order.
        cwd: Working directory for all Kiro subprocesses.
        agents_dir: Directory containing agent .md files. Uses default if None.
        trust_all: If True, use --trust-all-tools for all invocations.
        timeout: Per-invocation timeout in seconds.
        verbose: Enable verbose Kiro output.
        stop_on_error: If True, stop the chain on first error.

    Returns:
        List of SubagentResult, one per agent invoked (may be shorter than
        input list if stop_on_error is True and an error occurred).
    """
    results: list[SubagentResult] = []
    accumulated_context = ""

    for agent_name, task_prompt in agents:
        # Append previous outputs as context
        if accumulated_context:
            augmented_prompt = (
                f"{task_prompt}\n\n"
                f"## Previous Research Output\n\n"
                f"{accumulated_context}"
            )
        else:
            augmented_prompt = task_prompt

        result = run_kiro_subagent(
            agent_name=agent_name,
            task_prompt=augmented_prompt,
            cwd=cwd,
            agents_dir=agents_dir,
            trust_all=trust_all,
            timeout=timeout,
            verbose=verbose,
        )
        results.append(result)

        if result.is_error and stop_on_error:
            logger.warning(
                "Subagent chain stopped at '%s' due to error", agent_name,
            )
            break

        # Accumulate successful output for the next agent
        if not result.is_error:
            accumulated_context += f"\n### {agent_name}\n{result.output}\n"

    return results
