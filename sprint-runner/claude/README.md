# Sprint runner — Claude Code implementation

This example shows the **sprint runner** pattern using
[Claude Code](https://claude.com/claude-code). It is the Claude-native twin of
the Kiro implementation at [`../kiro/`](../kiro/).

Unlike the [human-in-loop example](../../human-in-loop/claude/), this one is
driven by a Python orchestrator that shells out to the `claude` CLI in headless
mode and runs an entire sprint (research → plan → build → test → e2e → review →
document → PR) without human intervention, with patch loops on failure.

## Layout

```
.claude/
    agents/             — 8 subagents (general-purpose + execution roles)
    commands/           — 14 slash commands invoked via `claude -p "/cmd …"`
    commands/e2e/       — 1 generic E2E template (copy + adapt per sprint)
    hooks/format.cjs    — PostToolUse formatter (ruff / prettier / biome)
tools/
    install.py                 — scaffold .claude/ + tools/ into a target repo (with stack adapt pass)
    sprint_runner.py           — the orchestrator
    pipeline_status_server.py  — flowchart dashboard over the current run
    tests/                     — pytest coverage for the trickier orchestration loops
```

### Why `.claude/` is hidden

`sprint_runner.py` runs `claude -p "/research-codebase …"` as a subprocess
with `cwd` set to the target repo. Claude Code only resolves project-scoped
slash commands from `.claude/commands/` relative to `cwd`. Renaming that
folder would break command resolution — so the hidden path is mechanically
required, not a style choice.

## Files at a glance

### Slash commands ([`.claude/commands/`](./.claude/commands/))

**Orchestrator entry point**
- [`pipeline-plan.md`](./.claude/commands/pipeline-plan.md) — Research a feature and produce a pipeline-ready state file with specs

**Planning / research**
- [`research-codebase.md`](./.claude/commands/research-codebase.md), [`research.md`](./.claude/commands/research.md)
- [`plan-feature.md`](./.claude/commands/plan-feature.md), [`plan-bug.md`](./.claude/commands/plan-bug.md), [`plan-task.md`](./.claude/commands/plan-task.md)

**Implementation**
- [`implement.md`](./.claude/commands/implement.md)
- [`patch.md`](./.claude/commands/patch.md) — Focused minimal patch plan for a specific review/test issue

**Validation**
- [`test.md`](./.claude/commands/test.md), [`validate.md`](./.claude/commands/validate.md), [`review.md`](./.claude/commands/review.md)

**Git / docs**
- [`commit.md`](./.claude/commands/commit.md), [`document.md`](./.claude/commands/document.md)

**Registry**
- [`implementation-docs.md`](./.claude/commands/implementation-docs.md) — Registry of implementation docs

**E2E validation** — single generic template at [`.claude/commands/e2e/test_example.md`](./.claude/commands/e2e/test_example.md). Copy and adapt per sprint.

### Subagents ([`.claude/agents/`](./.claude/agents/))

- `builder`, `codebase-locator`, `codebase-analyzer`, `codebase-pattern-finder`
- `planner`, `reviewer`, `tester`, `committer`

### Tools ([`tools/`](./tools/))

- [`install.py`](./tools/install.py) — stdlib-only installer. Copies `.claude/`
  and the two tool scripts into a target repo, creates the convention dirs,
  and runs a `claude -p` headless adapt pass that rewrites `<placeholder>`
  tokens inside the installed prompts based on the target's detected stack.
  Flags: `--force`, `--no-detect`, `--dry-run`.
- [`sprint_runner.py`](./tools/sprint_runner.py) — the orchestrator. Runs one
  or more sprints end-to-end, each through the 9-step pipeline, with:
  - per-step patch loops (up to 8 cycles for test/e2e/review)
  - transient-error retries with exponential backoff
  - atomic JSON state at `.developer/sprint-runs/<run_id>/state.json`
  - a `RUNNING.lock` heartbeat file for dashboards
  - `--resume`, `--resume-from RUN_ID:SPRINT:STEP`, `--force-step`, `--dry-run`
  - model split: Opus for planning, Sonnet for execution; `--opus-only` override
- [`pipeline_status_server.py`](./tools/pipeline_status_server.py) — stdlib
  `ThreadingHTTPServer` that reads the run state and renders a live flowchart
  dashboard with per-cycle expansion, screenshots, and log tails. Runs on
  port 8765 by default.
- [`tests/`](./tools/tests/) — pytest coverage for the trickier loops
  (empty e2e result handling, patch-cycle control flow).

## Setup

1. Install Claude Code: `npm i -g @anthropic-ai/claude-code`
2. Scaffold the pipeline into your target repo:
   ```bash
   python sprint-runner/claude/tools/install.py <target-repo>
   ```
   This copies `.claude/` and `tools/{sprint_runner,pipeline_status_server}.py`
   into the target, creates the convention dirs (`sprints/`, `specs/`,
   `research/`, `ai_docs/`), then runs a headless `claude -p` pass that
   detects the target's stack and rewrites the `<placeholder>` tokens inside
   the installed prompts. Flags: `--force` (overwrite existing `.claude/`),
   `--no-detect` (skip the adapt pass), `--dry-run`.
3. From inside the target: `python tools/sprint_runner.py --list-sprints`
4. Drop a sprint brief under `./sprints/` then run
   `python tools/sprint_runner.py --sprint 01`
5. (Optional) In another terminal: `python tools/pipeline_status_server.py`
   then open `http://localhost:8765/`.

### Manual install

If you'd rather not run the installer, copy `.claude/` and the two scripts in
`tools/` into the target repo yourself, then resolve any `<placeholder>`
tokens in `.claude/commands/*.md` by hand (or let the agent resolve them at
runtime — the prompts tolerate unresolved placeholders).

## Running a sprint

```bash
python tools/sprint_runner.py --sprint 03          # one sprint
python tools/sprint_runner.py --sprint 03-08       # range
python tools/sprint_runner.py --sprint 03,07,11    # explicit list
python tools/sprint_runner.py --resume 20260427-221809
python tools/sprint_runner.py --resume-from 20260427-221809:06:plan
python tools/sprint_runner.py --sprint 03 --dry-run    # snapshot prompts, no LLM calls
```

State and logs land in `.developer/sprint-runs/<run_id>/`.

## Adapting to your project

The prompts under `.claude/commands/` and `.claude/agents/` use generic
placeholder tokens (`<test command>`, `<package path>`, etc.) — they should
work in any repo as-is. The orchestrator in `tools/sprint_runner.py` has a
small number of things you'll want to review:

| Location | What it is | What to do |
|---|---|---|
| `SPRINT_DIR` in `tools/sprint_runner.py` | Directory scanned for sprint markdown files | Point it at wherever your sprint/epic docs live |
| `.claude/commands/e2e/test_example.md` | Template for sprint-level E2E files | Copy per sprint, fill in the placeholders |
| `.claude/commands/implementation-docs.md` | Registry of generated feature docs | Grows organically as `/document` runs |

The subagent definitions in `.claude/agents/` are generic and don't need
adaptation.

## What's NOT in this sample

- `.claude/output-styles/`, `.claude/scripts/` — cosmetic dev-env polish
  (statusline colors, terse-mode response style). Not load-bearing.
- Project-specific env-prep scripts (local-service lifecycle, volume
  repair, seed scripts). The pattern supports them via the E2E template's
  env-prep steps guidance — each project provides its own.
- `.claude/skills/` — unrelated domain skill.
