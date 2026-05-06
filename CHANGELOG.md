# Changelog

All notable changes to this project are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-05-06

Initial public release.

### Added
- Top-level README introducing the Agentic Engineering Framework (AEF) model, the four autonomy levels, and a pattern × tech matrix across the samples.
- `agent-samples/` — six tech-agnostic primitive agent configs and prompt templates (plan, build, test, review, document, deploy).
- `human-in-loop/` pattern — markdown-gated, human-driven workflow in two variants:
  - `human-in-loop/kiro/` with a sample Vite landing page and three gate checklists.
  - `human-in-loop/claude/` with matching slash-command prompts and subagent definitions.
- `automated-kiro/` — declarative `workflow.yaml` engine, Kiro CLI runner, CLI/API/webhook/cron triggers, and a bundled FastAPI demo target.
- `sprint-runner/` pattern — imperative Python orchestrator with 9-stage pipeline, crash-resumable `state.json`, self-healing patch loops, and per-sprint batch delivery:
  - `sprint-runner/kiro/` with an installer that scaffolds `.kiro/` into an external git repo.
  - `sprint-runner/claude/` with `.claude/commands/` and `.claude/agents/` plus a `claude`-shelling orchestrator and live status server.
- Documentation: per-pattern READMEs, per-tech READMEs, and AEF concept-to-sample mapping table.
