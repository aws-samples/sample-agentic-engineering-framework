# Human-in-the-loop

A pattern for agentic engineering where the model never runs the full cycle on
its own. Work is broken into discrete steps — plan, implement, test, review,
commit — and between each step the human inspects what the model produced and
decides whether to advance, correct, or roll back. The agent is a force
multiplier, not an autonomous operator.

This pattern fits situations where the cost of an unreviewed mistake is high,
the work is novel enough that the model can't be fully trusted, or the human
wants to stay in the loop for learning or alignment reasons. It trades
throughput for control. If what you want is an unattended pipeline, see
[`../sprint-runner/`](../sprint-runner/) instead.

The primary artifact across implementations is a **prompt library**: a set of
short, focused markdown prompts (one per step) plus subagent definitions. Each
prompt is written to stop at a review boundary and hand control back to the
human. No orchestrator auto-advances between them. To run the pattern you
invoke prompts one at a time, review the output, and invoke the next.

## Implementations

| Tech | Path | Status |
|---|---|---|
| Kiro | [`./kiro/`](./kiro/) | complete |
| Claude Code | [`./claude/`](./claude/) | complete |

Both implementations express the same pattern with their respective native
primitives (Kiro agents + gates; Claude Code slash commands + subagents). Read
either one to learn the flow; the prompt intents map across cleanly.
