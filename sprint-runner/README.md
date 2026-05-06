# Sprint runner

A pattern for agentic engineering where a driver orchestrates the full
build cycle end-to-end without human intervention. One input (a sprint or
backlog item) goes in; research, plan, build, test, e2e, review, document,
and PR come out. Failures at any step trigger a patch loop — the driver
feeds the error back into the model, asks for a fix, and retries — until
the step passes or a retry budget is exhausted.

This pattern fits situations where the work is well-scoped, the test signal
is trustworthy, and throughput matters more than per-step review. It is the
opposite end of the spectrum from [`../human-in-loop/`](../human-in-loop/):
instead of stopping at every gate, the driver runs unattended and only
surfaces the final result (plus logs). If what you want is tight human
oversight, use that pattern instead.

The primary artifact across implementations is a **driver** (a Python
orchestrator) plus a library of step-specific prompts and subagents that the
driver invokes. The driver owns retry logic, patch loops, resume-from-last-step
behavior, and a lock/heartbeat so a dashboard can render the live pipeline
state.

## Implementations

| Tech | Path | Status |
|---|---|---|
| Kiro | [`./kiro/`](./kiro/) | complete |
| Claude Code | [`./claude/`](./claude/) | complete |

Both implementations express the same pattern with their respective native
primitives. The Kiro version uses Kiro agents and prompts invoked by
`sprint_runner.py`. The Claude version shells out to the `claude` CLI in
headless mode (`claude -p "/cmd …"`) and resolves slash commands from a
project-local `.claude/commands/`.
