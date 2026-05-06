"""Worktree isolation and port management for concurrent pipeline execution.

Provides utilities for creating and managing git worktrees under trees/<pipeline_id>/
and allocating unique ports for each isolated instance. Supports up to 15 concurrent
pipeline runs with deterministic port assignment and collision fallback.
"""

import logging
import os
import shutil
import socket
import subprocess
from typing import Dict, Optional, Tuple


def _get_project_root() -> str:
    """Discover the project root using git.

    Returns:
        Absolute path to the git repository root.

    Raises:
        RuntimeError: If not inside a git repository.
    """
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Not inside a git repository: {result.stderr.strip()}")
    return result.stdout.strip()


def get_worktree_path(pipeline_id: str) -> str:
    """Get absolute path to a pipeline's worktree directory.

    Pure path computation -- does not check whether the directory exists.

    Args:
        pipeline_id: The pipeline ID (used as directory name under trees/).

    Returns:
        Absolute path to the worktree directory.
    """
    project_root = _get_project_root()
    return os.path.join(project_root, "trees", pipeline_id)


def get_ports_for_pipeline(pipeline_id: str) -> Tuple[int, int]:
    """Deterministically assign ports based on pipeline ID.

    Converts the first 8 alphanumeric characters of the pipeline ID to a
    base-36 integer, then maps to an index 0-14. Backend ports use range
    9100-9114, frontend ports use range 9200-9214.

    Args:
        pipeline_id: The pipeline ID.

    Returns:
        Tuple of (backend_port, frontend_port).
    """
    try:
        id_chars = "".join(c for c in pipeline_id[:8] if c.isalnum())
        if not id_chars:
            raise ValueError("No alphanumeric characters in pipeline_id")
        index = int(id_chars, 36) % 15
    except (ValueError, TypeError):
        index = hash(pipeline_id) % 15

    backend_port = 9100 + index
    frontend_port = 9200 + index
    return backend_port, frontend_port


def is_port_available(port: int) -> bool:
    """Check if a port is available for binding.

    Attempts to bind a socket to the port on localhost. If the bind
    succeeds, the port is available.

    Args:
        port: Port number to check.

    Returns:
        True if the port is available, False otherwise.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.bind(("localhost", port))
            return True
    except (socket.error, OSError):
        return False


def find_available_ports(pipeline_id: str, max_attempts: int = 15) -> Tuple[int, int]:
    """Find available ports starting from deterministic assignment.

    Starts with the deterministic port pair for this pipeline ID, then
    walks through the range looking for an available pair if the first
    choice is occupied.

    Args:
        pipeline_id: The pipeline ID.
        max_attempts: Maximum number of port pairs to try (default 15).

    Returns:
        Tuple of (backend_port, frontend_port).

    Raises:
        RuntimeError: If no available port pair is found within max_attempts.
    """
    base_backend, base_frontend = get_ports_for_pipeline(pipeline_id)
    base_index = base_backend - 9100

    for offset in range(max_attempts):
        index = (base_index + offset) % 15
        backend_port = 9100 + index
        frontend_port = 9200 + index

        if is_port_available(backend_port) and is_port_available(frontend_port):
            return backend_port, frontend_port

    raise RuntimeError(
        f"No available ports in range 9100-9114/9200-9214 after {max_attempts} attempts"
    )


def create_worktree(
    pipeline_id: str, branch_name: str, logger: logging.Logger
) -> Tuple[Optional[str], Optional[str]]:
    """Create a git worktree for isolated pipeline execution.

    Creates a worktree at trees/{pipeline_id}/ branching from origin/main.
    If the branch already exists, attaches the worktree to the existing branch.
    If the worktree directory already exists, returns the existing path.

    Args:
        pipeline_id: The pipeline ID (directory name under trees/).
        branch_name: The git branch name to create or attach.
        logger: Logger instance for progress and error reporting.

    Returns:
        Tuple of (worktree_path, error_message).
        worktree_path is the absolute path if successful, None if error.
        error_message is None if successful, a description string if error.
    """
    project_root = _get_project_root()

    # Create trees directory if needed
    trees_dir = os.path.join(project_root, "trees")
    os.makedirs(trees_dir, exist_ok=True)

    worktree_path = os.path.join(trees_dir, pipeline_id)

    # If worktree already exists, return it
    if os.path.exists(worktree_path):
        logger.warning(f"Worktree already exists at {worktree_path}")
        return worktree_path, None

    # Fetch latest from origin
    logger.info("Fetching latest changes from origin")
    fetch_result = subprocess.run(
        ["git", "fetch", "origin"],
        capture_output=True,
        text=True,
        cwd=project_root,
    )
    if fetch_result.returncode != 0:
        logger.warning(f"Failed to fetch from origin: {fetch_result.stderr}")

    # Create worktree with new branch from origin/main
    cmd = ["git", "worktree", "add", "-b", branch_name, worktree_path, "origin/main"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)

    if result.returncode != 0:
        # Branch may already exist -- try attaching without -b
        if "already exists" in result.stderr:
            cmd = ["git", "worktree", "add", worktree_path, branch_name]
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=project_root
            )

        if result.returncode != 0:
            error_msg = f"Failed to create worktree: {result.stderr.strip()}"
            logger.error(error_msg)
            return None, error_msg

    logger.info(f"Created worktree at {worktree_path} for branch {branch_name}")
    return worktree_path, None


def validate_worktree(
    pipeline_id: str, manifest: Dict
) -> Tuple[bool, Optional[str]]:
    """Validate worktree exists in manifest, filesystem, and git.

    Performs three-way validation to ensure consistency:
    1. Manifest has a worktree_path value
    2. The directory exists on the filesystem
    3. The path appears in git worktree list output

    Args:
        pipeline_id: The pipeline ID to validate.
        manifest: The pipeline manifest dict (must contain 'worktree_path' key).

    Returns:
        Tuple of (is_valid, error_message).
        is_valid is True if all three checks pass.
        error_message is None if valid, a description of the first failure if not.
    """
    # Check 1: manifest has worktree_path
    worktree_path = manifest.get("worktree_path")
    if not worktree_path:
        return False, "No worktree_path in manifest"

    # Check 2: directory exists
    if not os.path.exists(worktree_path):
        return False, f"Worktree directory not found: {worktree_path}"

    # Check 3: git knows about it
    result = subprocess.run(
        ["git", "worktree", "list"],
        capture_output=True,
        text=True,
    )
    if worktree_path not in result.stdout:
        return False, f"Worktree not registered with git: {worktree_path}"

    return True, None


def remove_worktree(
    pipeline_id: str, logger: logging.Logger
) -> Tuple[bool, Optional[str]]:
    """Remove a worktree and clean up.

    Attempts git worktree remove --force first. If that fails (e.g., git
    metadata is corrupted), falls back to shutil.rmtree for manual cleanup.

    Args:
        pipeline_id: The pipeline ID for the worktree to remove.
        logger: Logger instance for progress and error reporting.

    Returns:
        Tuple of (success, error_message).
        success is True if the worktree was removed (by either method).
        error_message is None if successful, a description string if both methods fail.
    """
    worktree_path = get_worktree_path(pipeline_id)

    # Try git remove first
    cmd = ["git", "worktree", "remove", worktree_path, "--force"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        # Fall back to manual removal
        if os.path.exists(worktree_path):
            try:
                shutil.rmtree(worktree_path)
                logger.warning(
                    f"Manually removed worktree directory: {worktree_path}"
                )
            except Exception as e:
                error_msg = (
                    f"Failed to remove worktree: {result.stderr.strip()}, "
                    f"manual cleanup also failed: {e}"
                )
                logger.error(error_msg)
                return False, error_msg
        # else: directory doesn't exist, consider it removed

    # Prune any stale worktree references
    subprocess.run(["git", "worktree", "prune"], capture_output=True, text=True)

    logger.info(f"Removed worktree at {worktree_path}")
    return True, None


def setup_worktree_environment(
    worktree_path: str, backend_port: int, frontend_port: int
) -> None:
    """Create .ports.env file in the worktree with port configuration.

    The .ports.env file is consumed by:
    - The install-worktree command (copies ports into .env files)
    - The prepare-app command (reads ports to start services)
    - The review command (reads ports to navigate to the application)

    This function ONLY creates .ports.env. It does NOT install dependencies,
    copy .env files, or configure MCP. Those are the install-worktree command's
    responsibility.

    Args:
        worktree_path: Absolute path to the worktree directory.
        backend_port: Backend port number (typically 9100-9114).
        frontend_port: Frontend port number (typically 9200-9214).
    """
    ports_env_path = os.path.join(worktree_path, ".ports.env")

    with open(ports_env_path, "w") as f:
        f.write(f"BACKEND_PORT={backend_port}\n")
        f.write(f"FRONTEND_PORT={frontend_port}\n")
        f.write(f"VITE_BACKEND_URL=http://localhost:{backend_port}\n")
