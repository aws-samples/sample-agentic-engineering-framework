"""Data types for the AEF Pipeline Engine.

All Pydantic models for the system. This module has zero internal dependencies.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# --- Enums and Literals ---

PipelinePhase = Literal["classify", "plan", "build", "test", "review", "document", "deploy", "monitor"]
IssueType = Literal["feature", "bug", "chore", "patch", "local"]
ModelSet = Literal["base", "heavy"]
Severity = Literal["blocker", "tech_debt", "skippable"]
GateAction = Literal["retry", "patch", "escalate", "log"]
PhaseDisposition = Literal["required", "optional", "checkpoint"]


class RetryCode(str, Enum):
    """Codes indicating different types of errors that may be retryable."""
    AGENT_ERROR = "agent_error"
    TIMEOUT = "timeout"
    EXECUTION_ERROR = "execution_error"
    NONE = "none"


# --- GitHub Models ---


class GitHubUser(BaseModel):
    """A GitHub user account."""
    login: str
    id: Optional[str] = None
    name: Optional[str] = None
    is_bot: bool = Field(default=False)


class GitHubLabel(BaseModel):
    """A GitHub issue/PR label."""
    id: str
    name: str
    color: str
    description: Optional[str] = None


class GitHubComment(BaseModel):
    """A GitHub issue or PR comment."""
    model_config = ConfigDict(populate_by_name=True)

    id: str
    author: GitHubUser
    body: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")


class GitHubIssueListItem(BaseModel):
    """A GitHub issue in list form (fewer fields than full issue)."""
    model_config = ConfigDict(populate_by_name=True)

    number: int
    title: str
    body: str
    labels: List[GitHubLabel] = []
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class GitHubIssue(BaseModel):
    """A full GitHub issue with all fields."""
    model_config = ConfigDict(populate_by_name=True)

    number: int
    title: str
    body: str
    state: str
    author: GitHubUser
    assignees: List[GitHubUser] = []
    labels: List[GitHubLabel] = []
    comments: List[GitHubComment] = []
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    closed_at: Optional[datetime] = Field(None, alias="closedAt")
    url: str


# --- Agent Models ---


class AgentPromptRequest(BaseModel):
    """Request to send a prompt to an agent."""
    prompt: str
    pipeline_id: str
    agent_name: str = "ops"
    model: Literal["sonnet", "opus"] = "sonnet"
    allowed_tools: List[str] = []
    output_file: str
    working_dir: Optional[str] = None


class AgentPromptResponse(BaseModel):
    """Response from an agent prompt execution."""
    output: str
    success: bool
    session_id: Optional[str] = None
    retry_code: RetryCode = RetryCode.NONE


class AgentTemplateRequest(BaseModel):
    """Request to execute an agent template (slash command)."""
    agent_name: str
    slash_command: str
    args: List[str]
    pipeline_id: str
    model: Literal["sonnet", "opus"] = "sonnet"
    working_dir: Optional[str] = None
    template_path: Optional[str] = None
    template_vars: Dict[str, str] = {}


# --- Result Models ---


class TestResult(BaseModel):
    """Result of a single test execution."""
    test_name: str
    passed: bool
    execution_command: str
    test_purpose: str
    error: Optional[str] = None


class ReviewIssue(BaseModel):
    """A single issue found during code review."""
    review_issue_number: int
    issue_description: str
    issue_resolution: str
    issue_severity: Severity


class ReviewResult(BaseModel):
    """Aggregate result of a code review."""
    success: bool
    review_summary: str
    review_issues: List[ReviewIssue] = []


# --- Pipeline Manifest ---


class PipelineManifestData(BaseModel):
    """State of a pipeline run. Replaces ADWStateData."""
    pipeline_id: str
    issue_number: Optional[str] = None
    branch_name: Optional[str] = None
    plan_file: Optional[str] = None
    issue_type: Optional[IssueType] = None
    worktree_path: Optional[str] = None
    model_set: ModelSet = "base"
    state: str = "INITIALIZED"
    phase_history: List[dict] = []
    artifacts: dict = {}
    total_retries: int = 0
    escalated: bool = False


# --- Gate & Pipeline Configuration ---


class GateConfig(BaseModel):
    """Configuration for a quality gate."""
    name: str
    trigger: str
    severity: Severity = "blocker"
    criteria: dict = {}
    on_fail: GateAction = "retry"
    max_retries: int = 3
    stop_on_no_progress: bool = True


class PhaseConfig(BaseModel):
    """Configuration for a pipeline phase."""
    name: PipelinePhase
    required: bool = True
    disposition: PhaseDisposition = "required"
    template: str = ""
    retry: int = 3
    gate: Optional[GateConfig] = None
    tools: List[str] = []


class EscalationConfig(BaseModel):
    """Configuration for escalation when loops exhaust."""
    target: str = "human"
    timeout_hours: int = 24
    include: List[str] = []


class LoopConfig(BaseModel):
    """Configuration for a retry/patch loop."""
    max: int = 3
    trigger: str = ""
    on_exhaust: str = "escalate"
    cost_ceiling: Optional[float] = None


class PipelineConfig(BaseModel):
    """Top-level pipeline configuration loaded from pipeline.yaml."""
    version: int = 1
    runner: str = "kiro"
    phases: List[PhaseConfig] = []
    gates: dict = {}
    loops: Dict[str, LoopConfig] = {}
    tools: dict = {}
    escalation: EscalationConfig = EscalationConfig()
    routing: dict = {}
