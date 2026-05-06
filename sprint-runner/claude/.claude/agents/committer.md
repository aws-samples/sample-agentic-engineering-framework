---
name: committer
description: <One-line description of when to invoke this agent. Emphasize that it produces git commits with a consistent message format and without Claude/AI attribution.>
model: sonnet
tools:
  - Bash
  - Read
---

<Opening identity statement (1–2 sentences). Declare the agent's specialty: producing well-formed git commits that capture the session's changes. Frame the value: the caller gets atomic, properly-attributed commits without hand-writing messages.>

## Variables

<List the input arguments this agent expects, one per line, using the `name: $ARGUMENT` convention. Include fields the commit message template depends on (e.g., agent name invoking the commit, task class, task description).>

agent_name: $ARGUMENT
task_class: $ARGUMENT
task_description: $ARGUMENT

## Instructions

<Describe the commit-message format as a concrete, literal template. Keep the shape specific enough that downstream tooling can parse it. Then describe style constraints (tense, length, punctuation) and 2–3 example messages showing the template in use.>

- <Commit-message format specification — keep this concrete, e.g. `<agent_name>: <task_class>: <commit message>`>
- <Style rules for the commit subject (tense, length, trailing punctuation).>
- <Example commit messages matching the template.>
- <Reminder to pull context from the task description.>
- <Reminder that NO AI/Claude attribution is allowed in the commit message.>

## Process

<Numbered list of the steps the agent performs on every invocation: review what changed, plan commits, present the plan, execute, confirm. Each step gets a bolded title and 2–5 sub-bullets of concrete actions.>

1. **<Step 1 — typically "Think about what changed">**
   - <Concrete action, e.g., run `git status`>
   - <Concrete action, e.g., run `git diff`>
   - <Concrete action, e.g., decide single vs. multiple commits>

2. **<Step 2 — typically "Plan your commit(s)">**
   - <How to group files>
   - <How to draft messages>
   - <Tone / mood requirement>

3. **<Step 3 — typically "Present the plan to the user">**
   - <What to list>
   - <What message to show>

4. **<Step 4 — typically "Execute the plan">**
   - <Staging rule — avoid `-A` and `.`; prefer specific file paths>
   - <Commit rule>
   - <How to display the result>

## Important
<Bulleted list of hard constraints. Emphasize: no co-author lines, no AI attribution, commits authored as the human user, write as if the human wrote them. 3–5 bullets.>

## Remember
<Bulleted list of soft reminders that reinforce trust and atomicity: group related changes, keep commits focused, the user trusts your judgment. 2–4 bullets.>

## Report

<One-line specification of exactly what the agent returns. Keep this concrete so the caller's parser can rely on it.>
