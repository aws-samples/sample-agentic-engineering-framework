# sprint-runner — Installer-First, Sprint-Batched AEF Pipeline

A Kiro-CLI-driven SDLC pipeline that scaffolds itself into any existing git repository. An installer copies a `.kiro/` runtime and a stdlib-only Python orchestrator into your target project, then processes a sprint backlog end-to-end — research, plan, build, test, e2e, review, document, commit, publish — with crash-resumable state and self-healing patch loops on every gate.

Unlike `automated-kiro`, which bundles a target app and a declarative `workflow.yaml` engine, this sample is shaped around installing into an external repo you already own, and batching multiple sprint briefs per run rather than one GitHub issue.

## Structure

```
sprint-runner/
├── README.md                           # this file
├── .gitignore
└── agentic-layer/                      # ← the portable drop-in pipeline
    └── tools/
        ├── README.md                   # full installer + runner reference
        ├── install.py                  # scaffolds .kiro/ and tools/ into a target project
        ├── sprint_runner.py            # imperative orchestrator (9 stages per sprint)
        ├── pipeline_dashboard.py       # real-time run dashboard over state.json
        ├── kpi_report.py               # KPI extraction from state.json
        ├── smoke_subagent.py           # probe Kiro headless subagent delegation
        └── pipeline.yaml.template      # config template (installer fills stack section)
    ├── prompts/                        # 11 master phase prompts (installer adapts to target stack)
    └── agents/                         # 5 subagent prompts (builder, tester, codebase-*)
```

No target app ships inside this sample — the installer is designed to operate on a git repository you already have. See "Quick Start" below for a scratch-repo recipe.

## Prerequisites

- Python 3.11+ (stdlib only — no `pip install` needed)
- `kiro-cli` on `PATH` (or set `KIRO_CLI_PATH`)
- An existing git repository to install into
- Optional: `npx` (for Playwright MCP, used by the test/e2e/review browser role)

## Quick Start

```bash
# 1. Install the pipeline into your target project
python sprint-runner/agentic-layer/tools/install.py <target-project>

# 2. Move into the target and verify sprint discovery
cd <target-project>
python tools/sprint_runner.py --list-sprints

# 3. Run a sprint (sprints are markdown briefs under mvp-prd/sprint-planning/)
python tools/sprint_runner.py --sprint 03
```

Add `--no-detect` to `install.py` to skip the Kiro-driven stack detection pass (useful for offline dry runs — the installer will leave `TODO:` sentinels in `pipeline.yaml`). Add `--force` to overwrite an existing `.kiro/`.

## Pipeline Stages

| Stage | Description | Self-healing |
|---|---|---|
| branch | Create sprint branch from the default base | — |
| research | Analyze the codebase and prior decisions for sprint context | — |
| plan | Generate the implementation spec (+ E2E test plan) | — |
| build | Execute the spec via the `builder` subagent | — |
| test | Run validation tests; patch on failure | `test_patch_max` cycles (default 4) |
| e2e | Run Playwright E2E suite; patch on failure | `e2e_patch_max` cycles (default 3) |
| review | Review implementation against the spec; patch on findings | `review_patch_max` cycles (default 4) |
| document | Generate feature documentation from code + spec | — |
| commit | Commit changes on the sprint branch | — |
| publish | Merge to base and push | — |

Patch loops regenerate a focused patch spec (`specs/patch/patch-sprint-<id>-{test,e2e,review}-<n>.md`), hand it back to the `builder`, and re-run the failed gate until the cap is exhausted, at which point the run escalates.

## How It Works

1. `install.py` copies `prompts/`, `agents/`, and `tools/` into the target project's `.kiro/` and `tools/` directories, synthesizes three role agents (`pipeline-plan`, `pipeline-execute`, `pipeline-execute-browser`), and writes a `pipeline.yaml` with stack-specific lint/test/build commands discovered via a Kiro-driven detect pass.
2. `sprint_runner.py` reads `pipeline.yaml`, discovers sprint briefs in `mvp-prd/sprint-planning/`, and orchestrates each sprint through the 9 stages by invoking `kiro-cli chat --no-interactive` with the appropriate role agent and prompt.
3. State persists atomically in `.developer/sprint-runs/<run_id>/<sprint_id>/state.json` with a `RUNNING.lock` heartbeat. A crashed run is resumable via `--resume <run_id>` or rewindable via `--resume-from <run_id>:<sprint>:<step>`.
4. Each stage's structured output (JSON results for test/e2e/review) triggers gate evaluation. A failed gate runs the patch loop; an exhausted loop writes an escalation artifact (`MERGE_CONFLICT.md`, patch specs, per-step logs) into the run directory.

See `agentic-layer/tools/README.md` for the full CLI reference, `pipeline.yaml` key table, and troubleshooting recipes.

## Runtime Artifacts

All produced inside the target project (not inside this sample):

```
<target>/.developer/sprint-runs/<run_id>/<sprint_id>/
├── state.json                       # atomic per-sprint state
├── RUNNING.lock                     # heartbeat file (5s interval)
├── <step>.log                       # stdout/stderr per stage
├── <step>.prompt.txt                # the exact prompt sent to Kiro
├── test-result-attempt-*.json       # structured gate outputs
├── e2e-result-*.json
├── review-result-*.json
├── merge-outcome.json               # publish-stage merge result
└── MERGE_CONFLICT.md                # escalation artifact if healing exhausts
```

`specs/`, `research/`, and `ai_docs/` directories get created at the target root as stages produce implementation plans, research notes, and feature docs respectively.

## When to pick this over `automated-kiro`

Pick `sprint-runner` when:

- You have an **existing codebase** you want to install the pipeline into, rather than starting from a bundled demo.
- You deliver work in **sprint batches** rather than one GitHub issue at a time.
- You want **stdlib-only Python** with no `uv`/pydantic/pyyaml dependency footprint.
- You need **crash-resumable runs** — long sprints that can be paused, interrupted, or rewound to a specific step.
- Your trigger surface is **CLI-only** (no GitHub webhooks, no API server, no cron).

Pick `automated-kiro` instead when you want declarative workflow YAML, per-phase pydantic-typed gates, GitHub issue classification, or HTTP/webhook/cron triggers.

## Customizing

The `agentic-layer/` directory is the artifact you fork:

- `tools/pipeline.yaml.template` — path keys, patch-cycle caps, per-stage timeouts, transient retry policy, agent role mapping. The installer copies this to the target as `tools/pipeline.yaml` and fills in stack commands.
- `prompts/*.md` — phase prompts. The installer adapts them to the detected stack during install.
- `agents/*.md` — the 5 subagents (`builder`, `tester`, `codebase-locator`, `codebase-analyzer`, `codebase-pattern-finder`). Frontmatter `tools:` fields are converted to Kiro tool names at install time.
- Target `.kiro/steering/` — the installer ships a minimal `pipeline.md` + `mcp-servers.md`. Add project-specific steering files to the target after install.

### Customizing prompts

The most team-specific surface in the `prompts/` directory is the `## Plan Format` section inside `plan-task.md`, `plan-feature.md`, and `plan-bug.md`. Every team formats implementation plans differently — user stories vs. outcome-first, checklists vs. prose, ADRs inline vs. separate, EARS vs. free-form. The default templates are opinionated starters, not contracts.

Each `plan-*.md` file labels its Plan Format block with two lists: **invariants** (anchors the rest of the pipeline depends on — phase headings with Success Criteria, the Validation Commands section, Relevant Files, and — for `plan-feature.md` — the phase-owned vs runner-owned command split that `sprint_runner.py` depends on) and **safe to change** (section naming beyond the invariants, testing-strategy shape, metadata fields, acceptance criteria formatting). Start by reading those lists before editing.

When you reshape a Plan Format, update its downstream consumers in the same change:

- `prompts/implement.md` — reads the `### Success Criteria:` list per phase when driving the builder.
- `prompts/patch.md` — addresses phases by number when generating patch specs for the test/e2e/review healing loops.
- `prompts/review.md` — compares the implementation back against the plan's shape.
- `tools/sprint_runner.py` `step_plan()` — appends a RUNNER NOTE that depends on the phase-owned / runner-owned buckets and the `SPEC_PATH` / `E2E_PATH` output markers. If you rename those, fix them here too.

Recommended iteration loop: pick one sample sprint brief, run it end-to-end (`python tools/sprint_runner.py --sprint <id>`), read the produced spec under `specs/sprint-<id>-*/`, adjust the template, and re-run. The agent's output is your fastest signal for whether the template is pulling its weight.
