"""GitHub API integration via the gh CLI.

All GitHub operations go through the gh CLI tool to avoid
direct API token management. Functions are stateless -- they
accept explicit parameters and return typed results.

Dependencies: engine.types, engine.utils
"""

import json
import logging
import os
import subprocess
from typing import List, Optional

from .types import GitHubIssue, GitHubIssueListItem, GitHubComment
from .utils import get_safe_subprocess_env

logger = logging.getLogger(__name__)

# Bot identifier prepended to all comments created by the pipeline.
# Used to distinguish pipeline comments from human comments and to
# find/update existing pipeline comments.
BOT_IDENTIFIER = "[AEF-PIPELINE]"


def get_repo_url(cwd: Optional[str] = None) -> str:
    """Get the GitHub repository URL from the current git repo.

    Args:
        cwd: Working directory. Defaults to current directory.

    Returns:
        Repository URL string (e.g., "https://github.com/owner/repo").

    Raises:
        RuntimeError: If not in a git repo or no remote configured.
    """
    result = subprocess.run(
        ["gh", "repo", "view", "--json", "url", "-q", ".url"],
        capture_output=True, text=True, cwd=cwd,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to get repo URL: {result.stderr}")
    return result.stdout.strip()


def extract_repo_path(url: str) -> str:
    """Extract owner/repo from a GitHub URL.

    Handles:
    - https://github.com/owner/repo
    - https://github.com/owner/repo.git
    - git@github.com:owner/repo.git

    Args:
        url: GitHub repository URL.

    Returns:
        "owner/repo" string.
    """
    # Strip trailing .git
    url = url.rstrip("/").removesuffix(".git")

    if "github.com/" in url:
        parts = url.split("github.com/")[-1]
        return parts
    elif "github.com:" in url:
        parts = url.split("github.com:")[-1]
        return parts

    raise ValueError(f"Cannot extract repo path from URL: {url}")


def fetch_issue(number: int, repo_path: Optional[str] = None, cwd: Optional[str] = None) -> GitHubIssue:
    """Fetch a GitHub issue with full details including comments.

    Args:
        number: Issue number.
        repo_path: "owner/repo" string. If None, inferred from current repo.
        cwd: Working directory for git context.

    Returns:
        GitHubIssue model.

    Raises:
        RuntimeError: If the gh command fails.
    """
    cmd = [
        "gh", "issue", "view", str(number),
        "--json", "number,title,body,state,author,assignees,labels,comments,createdAt,updatedAt,closedAt,url",
    ]
    if repo_path:
        cmd.extend(["--repo", repo_path])

    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=cwd,
        env=get_safe_subprocess_env(),
    )

    if result.returncode != 0:
        raise RuntimeError(f"Failed to fetch issue #{number}: {result.stderr}")

    data = json.loads(result.stdout)
    return GitHubIssue.model_validate(data)


def make_issue_comment(
    number: int,
    body: str,
    repo_path: Optional[str] = None,
    cwd: Optional[str] = None,
) -> None:
    """Create a comment on a GitHub issue.

    Automatically prepends BOT_IDENTIFIER to the comment body so
    pipeline comments can be identified and filtered.

    Args:
        number: Issue number.
        body: Comment body (markdown).
        repo_path: "owner/repo" string.
        cwd: Working directory.
    """
    full_body = f"{BOT_IDENTIFIER}\n\n{body}"

    cmd = ["gh", "issue", "comment", str(number), "--body", full_body]
    if repo_path:
        cmd.extend(["--repo", repo_path])

    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=cwd,
        env=get_safe_subprocess_env(),
    )

    if result.returncode != 0:
        logger.error(f"Failed to comment on issue #{number}: {result.stderr}")
    else:
        logger.info(f"Commented on issue #{number}")


def fetch_open_issues(
    repo_path: Optional[str] = None,
    cwd: Optional[str] = None,
    limit: int = 100,
) -> List[GitHubIssueListItem]:
    """Fetch open issues from a GitHub repository.

    Args:
        repo_path: "owner/repo" string.
        cwd: Working directory.
        limit: Maximum number of issues to fetch.

    Returns:
        List of GitHubIssueListItem models.
    """
    cmd = [
        "gh", "issue", "list",
        "--state", "open",
        "--limit", str(limit),
        "--json", "number,title,body,labels,createdAt,updatedAt",
    ]
    if repo_path:
        cmd.extend(["--repo", repo_path])

    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=cwd,
        env=get_safe_subprocess_env(),
    )

    if result.returncode != 0:
        logger.error(f"Failed to fetch issues: {result.stderr}")
        return []

    data = json.loads(result.stdout)
    return [GitHubIssueListItem.model_validate(item) for item in data]


def mark_issue_in_progress(
    number: int,
    repo_path: Optional[str] = None,
    cwd: Optional[str] = None,
) -> None:
    """Mark an issue as in-progress by adding a label.

    Adds the "in-progress" label. Creates the label if it does not exist.

    Args:
        number: Issue number.
        repo_path: "owner/repo" string.
        cwd: Working directory.
    """
    cmd = ["gh", "issue", "edit", str(number), "--add-label", "in-progress"]
    if repo_path:
        cmd.extend(["--repo", repo_path])

    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=cwd,
        env=get_safe_subprocess_env(),
    )

    if result.returncode != 0:
        # Label might not exist -- try to create it first
        create_cmd = ["gh", "label", "create", "in-progress", "--color", "FFA500", "--force"]
        if repo_path:
            create_cmd.extend(["--repo", repo_path])
        subprocess.run(create_cmd, capture_output=True, text=True, cwd=cwd)

        # Retry adding the label
        subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)

    logger.info(f"Marked issue #{number} as in-progress")
