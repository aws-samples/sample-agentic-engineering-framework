# Kiro — Automated ADW

Automated Agentic Development Workflow (ADW) using the Kiro CLI as the subprocess runner. Kiro runs in headless mode (`kiro-cli chat --no-interactive`), with agent personas prepended to prompts and pre-research subagents for the plan phase.

## Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.11+ |
| uv | latest |
| Kiro CLI (`kiro-cli`) | latest |

## Configuration

### workflow.yaml

The `workflow.yaml` file defines the 8-phase SDLC workflow:

- **runner: kiro** — tells the engine to use the Kiro CLI executor.
- **agents_dir** — path to persona files (`kiro-layer/agents/`). The engine loads the persona markdown and prepends it to the phase prompt before invocation.
- **pre_research** — configures subagent invocations that run before the plan phase. Three sequential subagents gather codebase context:
  1. `codebase-locator` — finds relevant files and entry points.
  2. `codebase-analyzer` — analyzes architecture and patterns.
  3. `pattern-finder` — identifies conventions and style patterns.

## Running

From the project root:

```bash
uv run run.py <issue-number> --config examples/kiro/workflow.yaml
```

Optional flags:

```bash
--pipeline-id <id>        # Explicit run ID (auto-generated if omitted)
--skip-phase <name>       # Skip a phase (repeatable)
--working-dir <path>      # Override working directory
```

## Key files

```
examples/kiro/
  workflow.yaml                      # ADW configuration
  kiro-layer/
    prompts/                         # Prompt templates
      classify.md
      plan-feature.md / plan-bug.md / plan-chore.md / plan-patch.md
      build.md
      test.md / resolve-test.md
      review.md
      document.md
      deploy.md
      monitor.md
      branch-name.md
    agents/                          # Agent persona definitions
      builder.md
      tester.md
      codebase-locator.md
      codebase-analyzer.md
      pattern-finder.md
    gates/                           # Quality gate definitions
      test-pass.yaml
      review-severity.yaml
      deploy-readiness.yaml
    tools/
      permissions.yaml               # File-operation permissions per phase
```
