---
description: <One-line description of what this prompt does. State that it implements a plan from a spec file by delegating each phase to a dedicated subagent.>
---

# Implement the spec

<Opening framing paragraph (1–2 sentences). State that the prompt follows the `Instructions` to implement the `Plan`, then produces a `Report`. Point the reader to the delegation section describing the one-subagent-per-phase rule.>

## Instructions

<Bulleted list of top-level directives. Keep it short: read the plan fully, think about how phases connect, implement each phase sequentially from top to bottom.>

- <Directive — e.g., read the plan fully and think about how the phases connect.>
- <Directive — e.g., implement each phase sequentially, top to bottom.>

## <Name of the mandatory subagent-per-phase delegation section>

<Preamble paragraph. State that this rule is non-negotiable: ALL phases must be delegated to a subagent so both the main session and each subagent keep their context budgets intact.>

<Numbered list describing how each phase is delegated:>

1. <Step — for each numbered Phase in the plan, spawn exactly one `builder` subagent via the Agent/Task tool and pass it:>
   - <what to pass — the Phase's Changes Required block verbatim>
   - <what to pass — the Phase's Success Criteria>
   - <what to pass — anchor `file:line` references the Phase names>

2. <Step — wait for the subagent to finish, read its summary, validate the Phase's Success Criteria against the working tree.>

3. <Step — only then move on to the next Phase (new subagent, fresh window).>

<Paragraph stating the DO-NOT rule: never call file-editing tools (`Edit`, `Write`, multi-file `Read`) in the main context — if you catch yourself about to edit a file, stop and spawn a subagent. The main session's job is coordination and reporting; each subagent gets its own context window, so the main session stays small by staying out of file-editing tools.>

<Optional escape-hatch sentence allowing trivial one-line edits inline when a subagent would refuse the change as too small, with a reminder to err toward delegation.>

## Plan

$ARGUMENTS

## REPORT

<Bulleted list describing the final report contract.>

- <Directive — summarize the work in concise bullet points.>
- <Directive — report the files and total lines changed using a `git diff --stat` summary.>
