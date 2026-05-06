"""Git operations for pipeline execution.

Branch management, commits, PR creation, and merge operations.
All functions take an optional cwd parameter for worktree support.

Dependencies: engine.utils
"""

import logging
import subprocess
from typing import Optional

from .utils import get_safe_subprocess_env

logger = logging.getLogger(__name__)


def _run_git(
    args: list,
    cwd: Optional[str] = None,
    check: bool = True,
) -> subprocess.CompletedProcess:
    """Run a git command with safe environment.

    Args:
        args: Git subcommand and arguments (e.g., ["branch", "--show-current"]).
        cwd: Working directory.
        check: If True, raise on non-zero exit.

    Returns:
        CompletedProcess result.

    Raises:
        subprocess.CalledProcessError: If check=True and command fails.
    """
    cmd = ["git"] + args
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=cwd,
        env=get_safe_subprocess_env(),
    )
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode, cmd, result.stdout, result.stderr,
        )
    return result


def get_current_branch(cwd: Optional[str] = None) -> str:
    """Get the current git branch name.

    Args:
        cwd: Working directory.

    Returns:
        Branch name string.
    """
    result = _run_git(["branch", "--show-current"], cwd=cwd)
    return result.stdout.strip()


def create_branch(name: str, cwd: Optional[str] = None) -> None:
    """Create and checkout a new branch.

    If the branch already exists, just checks it out.

    Args:
        name: Branch name.
        cwd: Working directory.
    """
    # Try to create new branch
    result = _run_git(["checkout", "-b", name], cwd=cwd, check=False)
    if result.returncode != 0:
        # Branch might already exist -- try checking it out
        _run_git(["checkout", name], cwd=cwd)
    logger.info(f"On branch: {name}")


def push_branch(name: str, cwd: Optional[str] = None) -> None:
    """Push a branch to the remote.

    Uses --set-upstream on first push, --force-with-lease for safety.

    Args:
        name: Branch name.
        cwd: Working directory.
    """
    _run_git(["push", "--set-upstream", "origin", name, "--force-with-lease"], cwd=cwd)
    logger.info(f"Pushed branch: {name}")


def commit_changes(message: str, cwd: Optional[str] = None) -> bool:
    """Stage all changes and commit.

    Runs git add -A followed by git commit.
    Returns False if there is nothing to commit.

    Args:
        message: Commit message.
        cwd: Working directory.

    Returns:
        True if a commit was created, False if nothing to commit.
    """
    _run_git(["add", "-A"], cwd=cwd)

    # Check if there are staged changes
    result = _run_git(["diff", "--cached", "--quiet"], cwd=cwd, check=False)
    if result.returncode == 0:
        # No changes staged
        logger.info("Nothing to commit")
        return False

    _run_git(["commit", "-m", message], cwd=cwd)
    logger.info(f"Committed: {message[:80]}")
    return True


def check_pr_exists(
    branch: str,
    repo_path: Optional[str] = None,
    cwd: Optional[str] = None,
) -> Optional[str]:
    """Check if a PR already exists for a branch.

    Args:
        branch: Branch name.
        repo_path: "owner/repo" string.
        cwd: Working directory.

    Returns:
        PR URL if exists, None otherwise.
    """
    cmd = ["gh", "pr", "view", branch, "--json", "url", "-q", ".url"]
    if repo_path:
        cmd.extend(["--repo", repo_path])

    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=cwd,
        env=get_safe_subprocess_env(),
    )

    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    return None


def create_pr(
    title: str,
    body: str,
    branch: str,
    repo_path: Optional[str] = None,
    cwd: Optional[str] = None,
    base: str = "main",
) -> str:
    """Create a pull request.

    Args:
        title: PR title.
        body: PR body (markdown).
        branch: Head branch name.
        repo_path: "owner/repo" string.
        cwd: Working directory.
        base: Base branch (default "main").

    Returns:
        PR URL string.

    Raises:
        RuntimeError: If PR creation fails.
    """
    cmd = [
        "gh", "pr", "create",
        "--title", title,
        "--body", body,
        "--head", branch,
        "--base", base,
    ]
    if repo_path:
        cmd.extend(["--repo", repo_path])

    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=cwd,
        env=get_safe_subprocess_env(),
    )

    if result.returncode != 0:
        raise RuntimeError(f"Failed to create PR: {result.stderr}")

    pr_url = result.stdout.strip()
    logger.info(f"Created PR: {pr_url}")
    return pr_url


def approve_pr(
    number: int,
    repo_path: Optional[str] = None,
    cwd: Optional[str] = None,
) -> None:
    """Approve a pull request.

    Args:
        number: PR number.
        repo_path: "owner/repo" string.
        cwd: Working directory.
    """
    cmd = ["gh", "pr", "review", str(number), "--approve"]
    if repo_path:
        cmd.extend(["--repo", repo_path])

    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=cwd,
        env=get_safe_subprocess_env(),
    )

    if result.returncode != 0:
        logger.error(f"Failed to approve PR #{number}: {result.stderr}")
    else:
        logger.info(f"Approved PR #{number}")


def merge_pr(
    number: int,
    method: str = "squash",
    repo_path: Optional[str] = None,
    cwd: Optional[str] = None,
) -> None:
    """Merge a pull request.

    Args:
        number: PR number.
        method: Merge method ("merge", "squash", "rebase"). Default "squash".
        repo_path: "owner/repo" string.
        cwd: Working directory.
    """
    cmd = ["gh", "pr", "merge", str(number), f"--{method}", "--delete-branch"]
    if repo_path:
        cmd.extend(["--repo", repo_path])

    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=cwd,
        env=get_safe_subprocess_env(),
    )

    if result.returncode != 0:
        raise RuntimeError(f"Failed to merge PR #{number}: {result.stderr}")
    logger.info(f"Merged PR #{number} via {method}")


def finalize_git_operations(
    pipeline_id: str,
    branch_name: str,
    issue_number: Optional[str] = None,
    repo_path: Optional[str] = None,
    cwd: Optional[str] = None,
    logger_instance: Optional[logging.Logger] = None,
) -> Optional[str]:
    """Push branch, create or update PR.

    This is the high-level function called by the pipeline runner
    at the deploy phase. It:
    1. Pushes the branch to origin
    2. Checks if a PR already exists
    3. Creates a PR if none exists
    4. Returns the PR URL

    Args:
        pipeline_id: Pipeline run ID (for PR body).
        branch_name: Branch to push.
        issue_number: Optional issue number to reference in PR.
        repo_path: "owner/repo" string.
        cwd: Working directory.
        logger_instance: Optional logger.

    Returns:
        PR URL string, or None if push/PR creation failed.
    """
    log = logger_instance or logger

    try:
        # Push branch
        push_branch(branch_name, cwd=cwd)

        # Check for existing PR
        existing_pr = check_pr_exists(branch_name, repo_path=repo_path, cwd=cwd)
        if existing_pr:
            log.info(f"PR already exists: {existing_pr}")
            return existing_pr

        # Build PR title and body
        title = f"[AEF-{pipeline_id}] "
        if issue_number:
            title += f"Resolve #{issue_number}"
        else:
            title += f"Pipeline {pipeline_id}"

        body_parts = [
            f"## Pipeline Run: `{pipeline_id}`",
            "",
        ]
        if issue_number:
            body_parts.append(f"Resolves #{issue_number}")
            body_parts.append("")
        body_parts.extend([
            "---",
            f"*Created by AEF Pipeline `{pipeline_id}`*",
        ])
        body = "\n".join(body_parts)

        pr_url = create_pr(
            title=title,
            body=body,
            branch=branch_name,
            repo_path=repo_path,
            cwd=cwd,
        )
        return pr_url

    except Exception as e:
        log.error(f"Git finalization failed: {e}")
        return None
