# automated-kiro — Full Automated AEF Pipeline

An 8-phase SDLC pipeline using the Kiro CLI as the runner. The pipeline classifies issues, plans implementations, builds code, runs tests, reviews against specs, generates documentation, deploys via PR, and tracks KPIs — all autonomously with self-healing loops.

## Structure

```
automated-kiro/
├── main.py                          # Sample app entry point
├── src/app.py                       # Sample FastAPI app (demo target)
├── tests/test_app.py                # Sample test
├── pyproject.toml                   # App dependencies
├── agent_runs_log/                  # Pipeline execution logs (gitignored)
├── specs/                           # Generated implementation plans (gitignored)
├── ai_docs/                         # Generated documentation & KPIs (gitignored)
└── agentic-layer/                   # ← The portable drop-in pipeline
    ├── run.py                       # Pipeline CLI entry point
    ├── pyproject.toml               # Engine dependencies
    ├── engine/                      # Core pipeline orchestrator
    │   ├── runner.py                #   Phase execution + healing loops
    │   ├── config.py                #   workflow.yaml loader
    │   ├── types.py                 #   Pydantic models
    │   ├── gate.py                  #   Quality gate evaluator
    │   ├── manifest.py              #   Pipeline state tracking
    │   ├── git.py                   #   Git operations
    │   ├── github.py                #   GitHub issue/PR integration
    │   ├── worktree.py              #   Git worktree isolation
    │   ├── monitor.py               #   KPI tracking
    │   └── utils.py                 #   Logging, JSON parsing, env
    ├── runners/kiro/                # Kiro CLI runner
    │   ├── kiro_runner.py           #   Subprocess wrapper
    │   ├── agent.py                 #   Engine bridge (template → kiro-cli)
    │   ├── agent_loader.py          #   Persona .md file loader
    │   └── subagent.py              #   Pre-research subagent chain
    ├── triggers/                    # Pipeline trigger mechanisms
    │   ├── api.py                   #   FastAPI trigger server
    │   ├── webhook.py               #   GitHub webhook trigger
    │   └── cron.py                  #   Polling trigger
    └── examples/kiro/
        ├── workflow.yaml            # 8-phase pipeline config
        └── kiro-layer/
            ├── prompts/             # Phase prompt templates
            ├── agents/              # Agent persona definitions
            ├── gates/               # Quality gate YAML definitions
            └── tools/               # Tool permission matrix
```

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- `kiro-cli` on PATH (or set `KIRO_CLI_PATH` env var)

## Running the Pipeline

```bash
cd agentic-layer

# Install dependencies
uv sync

# Run pipeline for a GitHub issue
uv run run.py <issue-number>

# Run in local mode (no GitHub)
uv run run.py --local --spec "Add a /users endpoint" --issue-type feature

# With options
uv run run.py 42 --pipeline-id my-run --skip-phase document

# Start API trigger server
uv run run.py --api --api-port 8002
```

## Pipeline Phases

| Phase | Description | Gate |
|---|---|---|
| classify | Determine issue type (feature/bug/chore/patch) | — |
| plan | Create implementation plan with pre-research | — |
| build | Execute the plan | — |
| test | Run validation tests | test-pass (all tests must pass) |
| review | Review against specification | review-severity (no blockers) |
| document | Generate documentation | — |
| deploy | Commit + create PR | deploy-readiness |
| monitor | Track pipeline KPIs | — (optional) |

## How It Works

1. `run.py` loads `examples/kiro/workflow.yaml`
2. The engine resolves the `kiro` runner → `runners/kiro/agent.py`
3. For each phase, the engine reads the prompt template from `kiro-layer/prompts/`
4. `agent.py` substitutes template variables and invokes `kiro-cli chat --no-interactive`
5. Quality gates evaluate structured output after test/review/deploy phases
6. Self-healing loops retry or patch when gates fail
7. Escalation posts to GitHub when healing exhausts

## Customizing

Copy the `agentic-layer/` directory into your own project and modify:

- `examples/kiro/workflow.yaml` — Add/remove phases, change gate bindings
- `kiro-layer/prompts/*.md` — Customize prompt templates for each phase
- `kiro-layer/agents/*.md` — Create new agent personas
- `kiro-layer/gates/*.yaml` — Define custom quality gates
- `kiro-layer/tools/permissions.yaml` — Adjust tool permissions per phase
