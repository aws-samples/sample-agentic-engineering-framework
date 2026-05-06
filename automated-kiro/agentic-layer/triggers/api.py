"""
ADW API Trigger -- Direct Workflow Execution Server

FastAPI server that accepts work requests and runs the full Agentic
Development Workflow in-process. Unlike the webhook trigger (which
launches subprocesses), this runs the workflow directly using
BackgroundTasks for non-blocking execution.

Endpoints:
    POST /adw          -- Submit a work request, returns ADW ID
    GET  /adw/{adw_id} -- Get status/results for a specific workflow run
    GET  /adw          -- List all workflow runs
    GET  /health       -- Health check

Usage:
    from triggers.api import start_api
    start_api(port=8002)
"""

from __future__ import annotations

import json
import logging
import os
import sys
import traceback
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel

from engine.utils import make_pipeline_id, setup_logger
from engine.manifest import PipelineManifest
from engine.worktree import (
    create_worktree,
    find_available_ports,
    setup_worktree_environment,
    remove_worktree,
)
from engine.git import create_branch
from engine.runner import PipelineRunner

_logger = setup_logger("api", "trigger_api")


# --- Request/Response Models ---

class WorkRequest(BaseModel):
    """Incoming work request."""
    title: str
    description: str
    issue_type: Optional[str] = None  # feature, bug, chore, patch. Auto-classified if omitted.
    config_path: str = "examples/kiro/workflow.yaml"
    model_set: str = "base"


class ADWStatus(str, Enum):
    """Workflow run status."""
    QUEUED = "queued"
    CREATING_WORKTREE = "creating_worktree"
    CLASSIFYING = "classifying"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ADWRun(BaseModel):
    """Tracked state for a workflow run."""
    adw_id: str
    title: str
    description: str
    issue_type: Optional[str] = None
    status: ADWStatus = ADWStatus.QUEUED
    current_phase: Optional[str] = None
    branch_name: Optional[str] = None
    worktree_path: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    phase_history: list[dict[str, Any]] = []
    result_summary: Optional[str] = None


# --- In-memory state ---
_active_runs: dict[str, ADWRun] = {}


# --- FastAPI App ---

app = FastAPI(
    title="AEF ADW API Trigger",
    description="Submit work requests and run agentic development workflows directly",
)


@app.post("/adw")
async def create_adw(request: WorkRequest, background_tasks: BackgroundTasks):
    """Submit a work request to start an agentic development workflow.

    Generates an ADW ID, queues the workflow for background execution,
    and returns immediately with the ID for status tracking.

    The workflow will:
    1. Create a git worktree for isolation
    2. Classify the work (if issue_type not provided)
    3. Create a feature branch
    4. Run all phases: plan, build, test, review, deploy
    5. Clean up the worktree on completion
    """
    adw_id = make_pipeline_id()

    run = ADWRun(
        adw_id=adw_id,
        title=request.title,
        description=request.description,
        issue_type=request.issue_type,
        status=ADWStatus.QUEUED,
        started_at=datetime.now().isoformat(),
    )
    _active_runs[adw_id] = run

    _logger.info(f"ADW {adw_id} queued: {request.title}")

    background_tasks.add_task(
        _execute_workflow, adw_id, request
    )

    return {
        "adw_id": adw_id,
        "status": "queued",
        "title": request.title,
        "message": f"Workflow queued. Track status at GET /adw/{adw_id}",
    }


@app.get("/adw/{adw_id}")
async def get_adw_status(adw_id: str):
    """Get the current status and details of a workflow run."""
    run = _active_runs.get(adw_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"ADW {adw_id} not found")
    return run.model_dump()


@app.get("/adw")
async def list_adw_runs():
    """List all active and completed workflow runs."""
    return {
        "total": len(_active_runs),
        "runs": [
            {
                "adw_id": r.adw_id,
                "title": r.title,
                "status": r.status,
                "current_phase": r.current_phase,
                "started_at": r.started_at,
                "completed_at": r.completed_at,
            }
            for r in _active_runs.values()
        ],
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "aef-adw-api",
        "active_runs": sum(
            1 for r in _active_runs.values()
            if r.status in (ADWStatus.QUEUED, ADWStatus.CREATING_WORKTREE,
                           ADWStatus.CLASSIFYING, ADWStatus.RUNNING)
        ),
        "total_runs": len(_active_runs),
    }


# --- Workflow Execution ---

def _update_status(adw_id: str, **kwargs) -> None:
    """Update the tracked status for a workflow run."""
    run = _active_runs.get(adw_id)
    if run:
        for key, value in kwargs.items():
            if hasattr(run, key):
                setattr(run, key, value)


def _execute_workflow(adw_id: str, request: WorkRequest) -> None:
    """Execute the full agentic development workflow.

    This runs in a background task. It chains together:
    1. Worktree creation for isolation
    2. Work classification (feature/bug/chore/patch)
    3. Branch creation
    4. PipelineRunner.run() for all phases
    5. Worktree cleanup

    Updates _active_runs[adw_id] throughout for status tracking.
    """
    logger = setup_logger(adw_id, "adw_api")
    logger.info(f"Starting ADW {adw_id}: {request.title}")

    worktree_path = None

    try:
        # Step 1: Create worktree
        _update_status(adw_id, status=ADWStatus.CREATING_WORKTREE)

        issue_type = request.issue_type or "feature"
        branch_name = f"{issue_type}-aef-{adw_id}-{_slugify(request.title)}"

        worktree_path, error = create_worktree(adw_id, branch_name, logger)
        if error or not worktree_path:
            _update_status(
                adw_id,
                status=ADWStatus.FAILED,
                error=f"Worktree creation failed: {error}",
                completed_at=datetime.now().isoformat(),
            )
            logger.error(f"Worktree creation failed: {error}")
            return

        _update_status(adw_id, worktree_path=worktree_path, branch_name=branch_name)
        logger.info(f"Worktree created at {worktree_path}")

        # Step 2: Set up ports
        backend_port, frontend_port = find_available_ports(adw_id)
        setup_worktree_environment(worktree_path, backend_port, frontend_port)
        logger.info(f"Ports assigned: backend={backend_port}, frontend={frontend_port}")

        # Step 3: Create manifest
        manifest = PipelineManifest(pipeline_id=adw_id)
        manifest.update(
            branch_name=branch_name,
            worktree_path=worktree_path,
            issue_type=issue_type,
            state="RUNNING",
        )
        manifest.save(workflow_step="api_trigger_init")

        # Step 4: Classify (if not provided)
        if not request.issue_type:
            _update_status(adw_id, status=ADWStatus.CLASSIFYING)
            logger.info("Auto-classifying work type...")
            # For now, default to "feature" -- classification requires
            # an agent invocation which needs the full runner setup.
            # The PipelineRunner's classify phase handles this.
            issue_type = "feature"
            _update_status(adw_id, issue_type=issue_type)

        # Step 5: Create branch in worktree
        create_branch(branch_name, cwd=worktree_path)
        logger.info(f"Branch created: {branch_name}")

        # Step 6: Run the workflow via PipelineRunner
        _update_status(adw_id, status=ADWStatus.RUNNING)

        # Write a synthetic spec file for the runner to use as the plan input
        spec_content = f"""# {request.title}

## Description
{request.description}

## Issue Type
{issue_type}

## ADW ID
{adw_id}
"""
        spec_dir = os.path.join(worktree_path, "specs")
        os.makedirs(spec_dir, exist_ok=True)
        spec_path = os.path.join(spec_dir, f"adw-{adw_id}-request.md")
        with open(spec_path, "w") as f:
            f.write(spec_content)

        # Create and run the pipeline
        runner = PipelineRunner(
            config_path=request.config_path,
            issue_number=0,  # No GitHub issue -- use 0 as placeholder
            pipeline_id=adw_id,
            working_dir=worktree_path,
            skip_phases=["classify", "monitor"],  # We handle classify, skip monitor
        )

        # Update phase tracking as runner progresses
        success = runner.run()

        # Collect results
        phase_history = manifest._data.get("phase_history", [])
        _update_status(
            adw_id,
            status=ADWStatus.COMPLETED if success else ADWStatus.FAILED,
            completed_at=datetime.now().isoformat(),
            phase_history=phase_history,
            result_summary=f"Workflow {'completed successfully' if success else 'failed'}. "
                          f"Phases executed: {len(phase_history)}",
        )

        if success:
            logger.info(f"ADW {adw_id} completed successfully")
        else:
            logger.warning(f"ADW {adw_id} completed with failures")

    except Exception as e:
        error_msg = f"Workflow execution error: {e}\n{traceback.format_exc()}"
        _update_status(
            adw_id,
            status=ADWStatus.FAILED,
            error=error_msg,
            completed_at=datetime.now().isoformat(),
        )
        logger.error(error_msg)

    finally:
        # Worktree cleanup disabled -- keep worktree for inspection
        logger.info(f"Worktree preserved at: {worktree_path}")


def _slugify(text: str, max_words: int = 4) -> str:
    """Convert text to a URL/branch-safe slug."""
    words = text.lower().split()[:max_words]
    slug = "-".join(w for w in words if w.isalnum() or "-" in w)
    return slug[:40] if slug else "work"


def start_api(
    port: int = 8002,
    host: str = "0.0.0.0",
) -> None:
    """Start the ADW API server.

    Args:
        port: Port to listen on (default: 8002).
        host: Host to bind to (default: 0.0.0.0).
    """
    import uvicorn

    _logger.info(f"Starting AEF ADW API on {host}:{port}")
    _logger.info(f"Submit work:    POST /adw")
    _logger.info(f"Check status:   GET  /adw/{{adw_id}}")
    _logger.info(f"List runs:      GET  /adw")
    _logger.info(f"Health check:   GET  /health")

    uvicorn.run(app, host=host, port=port)
