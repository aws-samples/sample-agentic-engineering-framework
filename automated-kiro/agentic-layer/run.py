#!/usr/bin/env -S uv run --project .
# /// script
# dependencies = ["python-dotenv", "pyyaml", "pydantic>=2.0", "fastapi>=0.100", "uvicorn>=0.20", "schedule>=1.2"]
# ///

"""
AEF Pipeline Runner (Kiro-only)

Usage:
  uv run run.py <issue-number>
  uv run run.py --local --spec "Add a /users endpoint"
  uv run run.py --local --spec specs/my-feature.md --issue-type bug

Arguments:
  issue-number        GitHub issue number to process (not needed with --local)

Options:
  --local             Run without GitHub (accepts --spec instead of issue number)
  --spec TEXT         Feature description or path to .md file (required with --local)
  --issue-type TYPE   Issue type: feature, bug, chore, patch (default: feature)
  --pipeline-id ID    Explicit workflow run ID (generated if omitted)
  --config PATH       Path to workflow.yaml (default: examples/kiro/workflow.yaml)
  --skip-phase NAME   Phase name to skip (can be repeated)
  --working-dir PATH  Working directory / worktree path (default: current directory)
  --api               Start ADW API server
  --api-port PORT     Port for API server (default: 8002)
"""

import argparse
import os
import sys

from dotenv import load_dotenv


def main():
    """Parse arguments and run the pipeline."""
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="AEF Pipeline Runner (Kiro)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "issue_number",
        nargs="?",
        type=int,
        help="GitHub issue number to process",
    )
    parser.add_argument("--pipeline-id", type=str, default=None, help="Pipeline run ID")
    # Resolve config path relative to this script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))

    parser.add_argument(
        "--config",
        type=str,
        default=os.path.join(script_dir, "examples", "kiro", "workflow.yaml"),
        help="Path to workflow.yaml",
    )
    parser.add_argument(
        "--skip-phase",
        action="append",
        default=[],
        dest="skip_phases",
        help="Phase to skip (repeatable)",
    )
    parser.add_argument(
        "--working-dir",
        type=str,
        default=None,
        help="Working directory / worktree path",
    )
    parser.add_argument(
        "--api",
        action="store_true",
        help="Start ADW API server (direct workflow execution)",
    )
    parser.add_argument(
        "--api-port",
        type=int,
        default=8002,
        help="Port for API server (default: 8002)",
    )

    # Local mode flags
    parser.add_argument(
        "--local",
        action="store_true",
        help="Run without GitHub -- accepts --spec instead of issue number",
    )
    parser.add_argument(
        "--spec",
        type=str,
        default=None,
        help="Feature description text or path to .md file (required with --local)",
    )
    parser.add_argument(
        "--issue-type",
        type=str,
        default="feature",
        choices=["feature", "bug", "chore", "patch"],
        help="Issue type for local mode (default: feature)",
    )

    args = parser.parse_args()

    if args.api:
        from triggers.api import start_api
        start_api(port=args.api_port)
        return

    # --- Local mode ---
    if args.local:
        if not args.spec:
            parser.error("--spec is required when using --local")

        from engine.utils import make_pipeline_id
        from engine.runner import PipelineRunner

        pipeline_id = args.pipeline_id or make_pipeline_id()
        working_dir = args.working_dir or os.getcwd()

        # Resolve spec: if it's a file path, read it; otherwise use as-is
        if os.path.isfile(args.spec):
            with open(args.spec, "r") as f:
                spec_description = f.read()
        else:
            spec_description = args.spec

        # Write synthetic spec file
        spec_dir = os.path.join(working_dir, "specs")
        os.makedirs(spec_dir, exist_ok=True)
        spec_path = os.path.join(spec_dir, f"local-{pipeline_id}.md")
        with open(spec_path, "w") as f:
            f.write(f"# Local Spec: {pipeline_id}\n\n")
            f.write(f"## Type\n{args.issue_type}\n\n")
            f.write(f"## Description\n{spec_description}\n")

        # Auto-skip classify (no issue to classify) and deploy (no remote)
        skip_phases = set(args.skip_phases) | {"classify", "deploy"}

        if not os.path.exists(args.config):
            print(f"ERROR: Config file not found: {args.config}", file=sys.stderr)
            sys.exit(1)

        runner = PipelineRunner(
            config_path=args.config,
            issue_number=0,
            pipeline_id=pipeline_id,
            working_dir=working_dir,
            skip_phases=list(skip_phases),
            local_mode=True,
            spec_description=spec_description,
        )
        # Set issue_type to "local" so plan template resolves to plan-local.md
        # (plan-{issue_class}.md -> plan-local.md, which uses ${spec_description})
        runner.manifest.update(issue_type="local")

        print(f"Pipeline {pipeline_id} starting in local mode...")
        print(f"Spec: {spec_path}")
        print(f"Type: {args.issue_type}")
        print(f"Skipping: {', '.join(sorted(skip_phases))}")
        print()

        success = runner.run()
        sys.exit(0 if success else 1)

    # --- Normal (GitHub) mode ---
    if args.issue_number is None:
        parser.error("issue_number is required (or use --local --spec)")

    if not os.path.exists(args.config):
        print(f"ERROR: Config file not found: {args.config}", file=sys.stderr)
        sys.exit(1)

    from engine.runner import PipelineRunner

    runner = PipelineRunner(
        config_path=args.config,
        issue_number=args.issue_number,
        pipeline_id=args.pipeline_id,
        working_dir=args.working_dir,
        skip_phases=args.skip_phases,
    )

    success = runner.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
