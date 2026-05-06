"""
GitHub Webhook Trigger for AEF Pipeline.

FastAPI server that receives GitHub issue events and launches
PipelineRunner as a detached subprocess. Responds immediately
to meet GitHub's 10-second timeout.

Endpoints:
    POST /gh-webhook  -- Receive GitHub webhook events
    GET  /health      -- Health check

Usage:
    from triggers.webhook import start_webhook
    start_webhook(port=8001)
"""

from __future__ import annotations

import hashlib
import hmac
import os
import subprocess
import sys
from typing import Optional

from fastapi import FastAPI, Request, HTTPException

from engine.utils import setup_logger, get_safe_subprocess_env

# Configuration
BOT_IDENTIFIER = "[aef-pipeline]"
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")

_logger = setup_logger("webhook", "trigger_webhook")

# FastAPI app
app = FastAPI(
    title="AEF Webhook Trigger",
    description="GitHub webhook endpoint for AEF pipeline",
)


def _validate_webhook_signature(payload_body: bytes, signature: Optional[str]) -> bool:
    """Validate GitHub webhook signature using HMAC-SHA256.

    If GITHUB_WEBHOOK_SECRET is not set, validation is skipped
    (development mode). In production, the secret should always be set.

    Args:
        payload_body: Raw request body bytes.
        signature: X-Hub-Signature-256 header value.

    Returns:
        True if signature is valid or validation is skipped.
    """
    if not GITHUB_WEBHOOK_SECRET:
        _logger.warning("GITHUB_WEBHOOK_SECRET not set -- skipping signature validation")
        return True

    if not signature:
        _logger.warning("No signature header in webhook request")
        return False

    expected = "sha256=" + hmac.new(
        GITHUB_WEBHOOK_SECRET.encode("utf-8"),
        payload_body,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature)


def _extract_pipeline_config(text: str) -> dict:
    """Extract pipeline configuration from issue/comment text.

    Looks for patterns like:
        pipeline: sdlc
        pipeline_id: my-run-123
        model_set: opus

    Args:
        text: Issue body or comment body.

    Returns:
        Dict with extracted config keys. Empty dict if nothing found.
    """
    config = {}
    text_lower = text.lower()

    # Extract pipeline type
    for keyword in ["pipeline:", "workflow:"]:
        if keyword in text_lower:
            idx = text_lower.index(keyword) + len(keyword)
            value = text[idx:].strip().split()[0] if idx < len(text) else ""
            if value:
                config["pipeline_type"] = value.strip().lower()
                break

    # Extract pipeline_id
    if "pipeline_id:" in text_lower:
        idx = text_lower.index("pipeline_id:") + len("pipeline_id:")
        value = text[idx:].strip().split()[0] if idx < len(text) else ""
        if value:
            config["pipeline_id"] = value.strip()

    # Extract model_set
    if "model_set:" in text_lower:
        idx = text_lower.index("model_set:") + len("model_set:")
        value = text[idx:].strip().split()[0] if idx < len(text) else ""
        if value:
            config["model_set"] = value.strip()

    return config


def _launch_pipeline_detached(
    issue_number: int,
    config_path: str = "adw/agentic-layer/pipeline.yaml",
    pipeline_id: Optional[str] = None,
) -> dict:
    """Launch PipelineRunner as a detached subprocess.

    Uses Popen with start_new_session=True so the process outlives
    the webhook response. This is critical for meeting GitHub's
    10-second response timeout.

    Args:
        issue_number: GitHub issue number.
        config_path: Path to pipeline.yaml.
        pipeline_id: Optional pipeline run ID.

    Returns:
        Dict with launch status information.
    """
    cmd = [
        sys.executable,
        "adw/run.py",
        str(issue_number),
        "--config", config_path,
    ]
    if pipeline_id:
        cmd.extend(["--pipeline-id", pipeline_id])

    _logger.info(f"Launching detached pipeline: {' '.join(cmd)}")

    try:
        process = subprocess.Popen(
            cmd,
            cwd=os.getcwd(),
            env=get_safe_subprocess_env(),
            start_new_session=True,  # Detach from webhook process
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        _logger.info(f"Pipeline launched: PID={process.pid}, issue=#{issue_number}")
        return {
            "pid": process.pid,
            "issue_number": issue_number,
            "pipeline_id": pipeline_id,
        }

    except Exception as e:
        _logger.error(f"Failed to launch pipeline: {e}")
        raise


@app.post("/gh-webhook")
async def github_webhook(request: Request):
    """Handle GitHub webhook events.

    Processes:
    - issues.opened: New issue created
    - issue_comment.created: New comment on an issue

    Triggers a pipeline when:
    1. Event is a qualifying type
    2. Content contains trigger keyword or pipeline config
    3. Content is NOT from the bot (loop prevention)

    Returns immediately with 200 and launches work in background.
    """
    try:
        # Validate webhook signature
        body = await request.body()
        signature = request.headers.get("X-Hub-Signature-256")
        if not _validate_webhook_signature(body, signature):
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Parse event
        event_type = request.headers.get("X-GitHub-Event", "")
        payload = await request.json()
        action = payload.get("action", "")
        issue = payload.get("issue", {})
        issue_number = issue.get("number")

        _logger.info(
            f"Webhook received: event={event_type}, action={action}, "
            f"issue=#{issue_number}"
        )

        # Determine content to inspect
        content_to_check = ""
        trigger_reason = ""

        if event_type == "issues" and action == "opened" and issue_number:
            content_to_check = issue.get("body", "")
            trigger_reason = "New issue opened"

        elif event_type == "issue_comment" and action == "created" and issue_number:
            comment = payload.get("comment", {})
            content_to_check = comment.get("body", "")
            trigger_reason = "New comment"

        else:
            return {
                "status": "ignored",
                "reason": f"Not a qualifying event: {event_type}.{action}",
            }

        # Bot loop prevention
        if BOT_IDENTIFIER in content_to_check:
            _logger.info("Ignoring bot content to prevent loop")
            return {"status": "ignored", "reason": "Bot loop prevention"}

        # Check for trigger keyword
        if "aef" not in content_to_check.lower():
            return {
                "status": "ignored",
                "reason": "No trigger keyword found",
            }

        # Extract pipeline configuration from content
        pipeline_config = _extract_pipeline_config(content_to_check)
        pipeline_id = pipeline_config.get("pipeline_id")

        # Determine config path based on pipeline type
        pipeline_type = pipeline_config.get("pipeline_type", "sdlc")
        config_path = f"adw/agentic-layer/pipeline-{pipeline_type}.yaml"
        if not os.path.exists(config_path):
            config_path = "adw/agentic-layer/pipeline.yaml"

        # Launch pipeline in background
        launch_info = _launch_pipeline_detached(
            issue_number=issue_number,
            config_path=config_path,
            pipeline_id=pipeline_id,
        )

        return {
            "status": "accepted",
            "issue": issue_number,
            "pipeline_id": launch_info.get("pipeline_id"),
            "pipeline_type": pipeline_type,
            "reason": trigger_reason,
            "pid": launch_info.get("pid"),
        }

    except HTTPException:
        raise
    except Exception as e:
        _logger.error(f"Error processing webhook: {e}")
        # Always return 200 to GitHub to prevent retries
        return {"status": "error", "message": "Internal error processing webhook"}


@app.get("/health")
async def health():
    """Health check endpoint.

    Returns basic service status. Does not run external health checks
    to keep the response fast.
    """
    return {
        "status": "healthy",
        "service": "aef-webhook-trigger",
        "python": sys.version,
    }


def start_webhook(
    port: int = 8001,
    host: str = "0.0.0.0",
) -> None:
    """Start the webhook server.

    Args:
        port: Port to listen on (default: 8001).
        host: Host to bind to (default: 0.0.0.0).
    """
    import uvicorn

    _logger.info(f"Starting AEF webhook trigger on {host}:{port}")
    _logger.info(f"Webhook endpoint: POST /gh-webhook")
    _logger.info(f"Health check: GET /health")
    _logger.info(
        f"Signature validation: {'enabled' if GITHUB_WEBHOOK_SECRET else 'disabled'}"
    )

    uvicorn.run(app, host=host, port=port)
