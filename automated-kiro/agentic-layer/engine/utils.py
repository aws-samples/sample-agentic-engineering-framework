"""Utility functions for the AEF Pipeline Engine.

ID generation, logging, JSON parsing, environment validation, subprocess safety.
"""

import json
import logging
import os
import re
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

T = TypeVar("T")


def get_project_root() -> Path:
    """Return the project root directory.

    Checks PROJECT_ROOT env var first, then walks up from this file
    to the project root (3 levels: engine/ -> agentic-layer/ -> project root).
    """
    env_root = os.getenv("PROJECT_ROOT")
    if env_root:
        return Path(env_root)
    # This file is at agentic-layer/engine/utils.py
    # project root is 3 levels up: engine/ -> agentic-layer/ -> project root
    return Path(__file__).parent.parent.parent


def make_pipeline_id() -> str:
    """Generate an 8-character UUID for pipeline tracking."""
    return str(uuid.uuid4())[:8]


def setup_logger(
    pipeline_id: str, phase_name: str = "pipeline"
) -> logging.Logger:
    """Set up a dual-output logger (file + console).

    File handler: DEBUG level, writes to agent_runs_log/{pipeline_id}/{phase_name}/execution.log
    Console handler: INFO level, writes to stdout.

    Args:
        pipeline_id: The pipeline run ID.
        phase_name: The current phase or component name.

    Returns:
        Configured Logger instance.
    """
    project_root = get_project_root()
    log_dir = project_root / "agent_runs_log" / pipeline_id / phase_name
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "execution.log"

    logger = logging.getLogger(f"aef_{pipeline_id}_{phase_name}")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    # File handler -- DEBUG
    fh = logging.FileHandler(log_file, mode="a")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    # Console handler -- INFO
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(message)s"))

    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.info(f"AEF Logger initialized -- pipeline: {pipeline_id}, phase: {phase_name}")
    logger.debug(f"Log file: {log_file}")
    return logger


def parse_json(text: str, target_type: Type[T] = None) -> Union[T, Any]:
    """Parse JSON that may be wrapped in markdown code blocks.

    Handles:
    - Raw JSON
    - JSON wrapped in ```json ... ```
    - JSON wrapped in ``` ... ```
    - JSON with extra whitespace or surrounding text

    Args:
        text: String containing JSON, possibly wrapped in markdown.
        target_type: Optional Pydantic model or List[Model] to validate into.

    Returns:
        Parsed JSON object, optionally validated as target_type.

    Raises:
        ValueError: If JSON cannot be parsed from the text.
    """
    # Try to extract from markdown code blocks
    code_block_pattern = r"```(?:json)?\s*\n(.*?)\n```"
    match = re.search(code_block_pattern, text, re.DOTALL)

    if match:
        json_str = match.group(1).strip()
    else:
        json_str = text.strip()

    # If not starting with [ or {, try to find JSON boundaries
    if not (json_str.startswith("[") or json_str.startswith("{")):
        array_start = json_str.find("[")
        array_end = json_str.rfind("]")
        obj_start = json_str.find("{")
        obj_end = json_str.rfind("}")

        if array_start != -1 and (obj_start == -1 or array_start < obj_start):
            if array_end != -1:
                json_str = json_str[array_start : array_end + 1]
        elif obj_start != -1:
            if obj_end != -1:
                json_str = json_str[obj_start : obj_end + 1]

    try:
        result = json.loads(json_str)

        if target_type and hasattr(target_type, "__origin__"):
            if target_type.__origin__ == list:
                item_type = target_type.__args__[0]
                if hasattr(item_type, "model_validate"):
                    result = [item_type.model_validate(item) for item in result]
        elif target_type:
            if hasattr(target_type, "model_validate"):
                result = target_type.model_validate(result)

        return result
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}. Text was: {json_str[:200]}...")


def check_env_vars(
    required: Optional[List[str]] = None,
    logger: Optional[logging.Logger] = None,
) -> None:
    """Check that required environment variables are set.

    Args:
        required: List of var names. Defaults to ["KIRO_CLI_PATH"] (optional check).
        logger: Optional logger for error reporting.

    Raises:
        SystemExit: If any required vars are missing.
    """
    if required is None:
        required = []

    missing = [var for var in required if not os.getenv(var)]
    if missing:
        msg = "Missing required environment variables:"
        if logger:
            logger.error(msg)
            for var in missing:
                logger.error(f"  - {var}")
        else:
            print(msg, file=sys.stderr)
            for var in missing:
                print(f"  - {var}", file=sys.stderr)
        sys.exit(1)


def get_safe_subprocess_env() -> Dict[str, str]:
    """Return filtered environment variables safe for subprocess execution.

    Includes only variables needed for agent execution, filtering out
    potentially sensitive or unnecessary variables.

    Returns:
        Dictionary of safe environment variables (None values filtered out).
    """
    safe_vars = {
        "KIRO_CLI_PATH": os.getenv("KIRO_CLI_PATH"),
        "GITHUB_PAT": os.getenv("GITHUB_PAT"),
        "HOME": os.getenv("HOME"),
        "USER": os.getenv("USER"),
        "PATH": os.getenv("PATH"),
        "SHELL": os.getenv("SHELL"),
        "TERM": os.getenv("TERM"),
        "LANG": os.getenv("LANG"),
        "PYTHONPATH": os.getenv("PYTHONPATH"),
        "PYTHONUNBUFFERED": "1",
        "PWD": os.getcwd(),
    }
    # Mirror GITHUB_PAT as GH_TOKEN for gh CLI
    github_pat = os.getenv("GITHUB_PAT")
    if github_pat:
        safe_vars["GH_TOKEN"] = github_pat

    return {k: v for k, v in safe_vars.items() if v is not None}
