"""Agent persona loader for Kiro.

Reads agent persona markdown files with YAML frontmatter. Since Kiro
has no --system-prompt flag, agent personas are loaded from .md files
and prepended to the user prompt.

File format:
    ---
    name: agent-name
    description: What this agent does
    tools:
      - read
      - write
    model: default
    ---

    You are an agent that does X...

Dependencies: stdlib only + pydantic. ZERO imports from adw.engine.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Default agents directory relative to project root
DEFAULT_AGENTS_DIR = os.getenv("KIRO_AGENTS_DIR", "adw/agents")

# Separator used when prepending system_prompt to user prompt
PROMPT_SEPARATOR = "\n\n---\n\n"


@dataclass
class AgentDefinition:
    """Parsed agent persona definition.

    Loaded from a markdown file with YAML frontmatter.

    Attributes:
        name: Agent identifier (e.g., "research-agent").
        description: Human-readable description of the agent's purpose.
        tools: List of tool categories this agent needs (e.g., ["read", "shell"]).
               Maps to Kiro's --trust-tools flag values.
        model: Model hint. Kiro ignores this (no model selection), but it is
               preserved for documentation and potential future use.
        system_prompt: The persona text (markdown body after frontmatter).
    """
    name: str
    description: str = ""
    tools: list[str] = field(default_factory=list)
    model: str = "default"
    system_prompt: str = ""


def load_agent(
    agent_name: str,
    agents_dir: Optional[str] = None,
) -> AgentDefinition:
    """Load an agent persona definition from a markdown file.

    Searches for {agents_dir}/{agent_name}.md. If not found, tries
    replacing hyphens with underscores and vice versa as a fallback
    (e.g., "research-agent" -> "research_agent.md").

    Args:
        agent_name: Name of the agent (used as filename without .md extension).
        agents_dir: Directory containing agent .md files. Defaults to
                    KIRO_AGENTS_DIR env var or "adw/agents".

    Returns:
        AgentDefinition with parsed frontmatter and system_prompt.

    Raises:
        FileNotFoundError: If no matching agent file is found.
        ValueError: If the file cannot be parsed (missing frontmatter).
    """
    dir_path = Path(agents_dir) if agents_dir else Path(DEFAULT_AGENTS_DIR)

    # Try exact name first, then hyphen/underscore fallback
    candidates = [
        dir_path / f"{agent_name}.md",
        dir_path / f"{agent_name.replace('-', '_')}.md",
        dir_path / f"{agent_name.replace('_', '-')}.md",
    ]

    file_path = None
    for candidate in candidates:
        if candidate.is_file():
            file_path = candidate
            break

    if file_path is None:
        searched = [str(c) for c in candidates]
        raise FileNotFoundError(
            f"Agent '{agent_name}' not found. Searched: {searched}"
        )

    logger.info("Loading agent from: %s", file_path)
    content = file_path.read_text(encoding="utf-8")

    return _parse_agent_file(content, agent_name)


def _parse_agent_file(content: str, fallback_name: str) -> AgentDefinition:
    """Parse a markdown file with YAML frontmatter into an AgentDefinition.

    The file format is:
        ---
        name: value
        description: value
        tools:
          - tool1
          - tool2
        model: value
        ---

        Body text here (becomes system_prompt)

    Uses a simple line-by-line parser for the YAML frontmatter instead of
    importing PyYAML, keeping dependencies minimal. Supports:
    - Simple key: value pairs
    - List items (lines starting with "  - ")

    Args:
        content: Full file content.
        fallback_name: Name to use if not specified in frontmatter.

    Returns:
        AgentDefinition with parsed fields.

    Raises:
        ValueError: If frontmatter delimiters are missing or malformed.
    """
    lines = content.split("\n")

    # Find frontmatter boundaries
    delimiter_indices = []
    for i, line in enumerate(lines):
        if line.strip() == "---":
            delimiter_indices.append(i)
        if len(delimiter_indices) == 2:
            break

    if len(delimiter_indices) < 2:
        raise ValueError(
            "Agent file must contain YAML frontmatter between --- delimiters. "
            f"Found {len(delimiter_indices)} delimiter(s)."
        )

    start_idx = delimiter_indices[0] + 1
    end_idx = delimiter_indices[1]

    # Parse frontmatter (simple YAML subset)
    frontmatter = _parse_simple_yaml(lines[start_idx:end_idx])

    # Everything after the closing --- is the system_prompt
    body_lines = lines[end_idx + 1:]
    system_prompt = "\n".join(body_lines).strip()

    # Extract tools list
    tools = frontmatter.get("tools", [])
    if isinstance(tools, str):
        tools = [t.strip() for t in tools.split(",") if t.strip()]

    return AgentDefinition(
        name=frontmatter.get("name", fallback_name),
        description=frontmatter.get("description", ""),
        tools=tools,
        model=frontmatter.get("model", "default"),
        system_prompt=system_prompt,
    )


def _parse_simple_yaml(lines: list[str]) -> dict:
    """Parse a simple subset of YAML from frontmatter lines.

    Supports:
    - key: value (string values)
    - key: followed by indented list items (  - value)

    Does NOT support nested objects, multi-line strings, or complex YAML.
    This keeps the dependency footprint at zero (no PyYAML needed).

    Args:
        lines: Lines between the --- delimiters.

    Returns:
        Dict of parsed key-value pairs.
    """
    result: dict = {}
    current_key: Optional[str] = None
    current_list: Optional[list] = None

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Check for list item (indented "- value")
        if line.startswith("  - ") or line.startswith("\t- "):
            item = stripped.lstrip("- ").strip()
            if current_key and current_list is not None:
                current_list.append(item)
            continue

        # Check for key: value
        if ":" in stripped:
            # Finalize previous list if any
            if current_key and current_list is not None:
                result[current_key] = current_list

            colon_idx = stripped.index(":")
            key = stripped[:colon_idx].strip()
            value = stripped[colon_idx + 1:].strip()

            current_key = key

            if value:
                # Simple key: value
                result[key] = value
                current_list = None
            else:
                # key: with no value -- expect list items to follow
                current_list = []

    # Finalize last list if any
    if current_key and current_list is not None:
        result[current_key] = current_list

    return result


def build_combined_prompt(system_prompt: str, user_prompt: str) -> str:
    """Combine a system prompt and user prompt with the standard separator.

    Since Kiro has no --system-prompt flag, the agent persona is prepended
    to the user's prompt with a separator.

    Args:
        system_prompt: Agent persona text.
        user_prompt: The user's task prompt.

    Returns:
        Combined prompt string: "{system_prompt}\\n\\n---\\n\\n{user_prompt}"
    """
    if not system_prompt:
        return user_prompt
    if not user_prompt:
        return system_prompt
    return f"{system_prompt}{PROMPT_SEPARATOR}{user_prompt}"
