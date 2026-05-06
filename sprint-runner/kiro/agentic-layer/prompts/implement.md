---
description: <One-line description of what this prompt does. State that it executes a pre-written plan (e.g., a spec file) by delegating work to a builder subagent, and that it is invoked by the main agent with the plan as input.>
---

# <Top-level title — typically an imperative like "Implement the spec">
<One-sentence framing directive telling the model to follow `Instructions`, implement the `Plan`, then produce a `Report`. Keep the section names as backticked anchors so downstream headers match.>

## Instructions

<Bulleted list of 2–4 high-level directives the model must follow before touching any phase. Typical entries: read the plan in full, think about how phases connect, implement phases in order. Phrase each as a terse imperative.>

- <Imperative about reading and understanding the plan>
- <Imperative about execution order>

## MANDATORY - subagent-per-phase delegation

<Short paragraph (1–2 sentences) stating that this rule is non-negotiable and explaining the reason (main-agent context preservation). Use strong wording like "mandatory" and "ALL phases".>

<Numbered list (3 steps) describing the per-phase delegation loop. Each step is a short imperative covering: (1) spawning the builder subagent and what to pass it, (2) waiting and validating success criteria, (3) moving to the next phase with a fresh context window. Under step 1, include a nested bullet list naming the exact inputs passed to the subagent — typically the phase's change list verbatim, its success criteria, and anchor `file:line` references.>

1. <Spawn-subagent step with nested bullets for inputs>
- <Input slot — e.g., the phase's change list verbatim>
- <Input slot — e.g., the phase's success criteria>
- <Input slot — e.g., anchor `file:line` references>

2. <Wait-and-validate step>

3. <Advance-to-next-phase step>

<Bolded negative directive (e.g., **DO NOT**) forbidding the main agent from calling file-editing tools directly. Follow it with a 2–3 sentence explanation of why: the main session's role is coordination and reporting, each subagent owns its own context window, and staying out of file-editing tools is how the main session stays small.>

<Single-sentence escape hatch acknowledging that trivial edits (e.g., a one-line rename) may be done inline, but err on the side of delegating.>


## Plan

<Slot where the caller injects the plan content. Typically a single template variable like `$ARGUMENTS` on its own line.>

## REPORT
<Bulleted list (2–3 bullets) describing what the final report must contain. Typical entries: a concise bullet-point summary of work done, and a command-based summary of files and lines changed (e.g., `git diff --stat`). Phrase each as an imperative.>

- <Reporting directive — e.g., summarize work done as concise bullets>
- <Reporting directive — e.g., report files and total lines changed via a specific command>
