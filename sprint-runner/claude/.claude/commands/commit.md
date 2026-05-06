---
description: <One-line description of what this prompt does. State that it creates a git commit accounting for every change in the working tree.>
---

# /commit

<Opening framing paragraph (1–2 sentences). State that the goal is to create a git commit capturing the entire current working-tree change set — accounting for every modified and untracked file — rather than guessing which files are "relevant" to a task description. Point the reader to the `Variables`, `Process`, `Important`, and `Report` sections below.>

## Variables

<List each variable this prompt accepts. Each slot names the variable, the positional argument it maps to (`$ARGUMENT`/`$1`/`$2`/...), and whether it is required or advisory. Include a hint slot the invoker can pass for commit-message shaping, with a clear note that the hint must NOT filter which files are staged — the diff is the source of truth.>

agent_name: $ARGUMENT
task_class: $ARGUMENT
task_description: $ARGUMENT — <OPTIONAL hint for the commit message only. Do NOT use this to filter which files to stage. The diff is the source of truth.>

## Process

<Short lead-in sentence stating the steps are ordered and the enumeration step must not be skipped. Then a numbered sequence of `###` subsections, each a discrete phase with concrete actions.>

### 1. <Observation step title>

<Describe the observation commands that list every changed path and the corresponding diff content. Emphasize that the porcelain output defines the universe of files that must be accounted for in the next step — no silent omissions.>

- <Command to enumerate changed paths>
- <Command to summarize the diff scope>
- <Command to read the actual changes, not just filenames>

### 2. <Enumerate and classify step title>

<Describe the rule that EVERY path from the observation step must appear in exactly one of two lists — include or exclude — using a specific textual format. Include an example of the line format the invoker must emit.>

```
include: <path>  — <why it belongs in this commit>
exclude: <path>  — <concrete reason it is unrelated>
```

<Bulleted list of VALID exclusion reasons (specific and concrete — e.g., scratch/debug output, a stale unrelated modification from a prior task, an accidental secret file).>

- <Valid exclusion reason>
- <Valid exclusion reason>
- <Valid exclusion reason>

<Bulleted list of INVALID exclusion reasons (e.g., "not mentioned in the task description", "not named in the spec", "the commit message only talks about X", "I'm not sure what this file is — if you're not sure, include it").>

- <Invalid exclusion reason>
- <Invalid exclusion reason>
- <Invalid exclusion reason>
- <Invalid exclusion reason>

<Closing paragraph emphasizing that omission is NOT the same as exclusion — every path from step 1 must appear in the list.>

### 3. <Staging step title>

<Describe staging only the `include:` files using explicit paths. Provide a template command.>

```
git add <path/to/file-a> <path/to/file-b> ...
```

- <Rule — e.g., NEVER use `git add -A`, `git add .`, or `git add -u`. Explicit paths only.>
- <Rule — e.g., it's fine to pass many paths on one line when the include list is large.>

### 4. <Compose the commit message step title>

<Describe the commit message format and subject line rules. Typical format: `<agent_name>: <task_class>: <subject line>`.>

Format: `<agent_name>: <task_class>: <subject line>`

<Bulleted list of subject line rules — tense/mood, length cap, no trailing period, description sourced from the actual staged diff (run `git diff --cached` and summarize), and conflict-resolution rule between task_description hints and the diff.>

- <Subject line rule — tense and mood>
- <Subject line rule — length cap and no trailing period>
- <Subject line rule — source of truth is the staged diff>
- <Subject line rule — hint/diff conflict resolution>

<Optional-body rule: when a body is allowed, and the format (blank line + bullet list, one bullet per concern).>

<Illustrative examples of well-formed commit messages. Examples are placeholder-only — adapt to your team's conventions.>

- `<agent>: <class>: <imperative subject>`
- `<agent>: <class>: <imperative subject>`
- `<agent>: <class>: <imperative subject>`

### 5. <Commit, push, confirm step title>

<Describe the final commit/push/confirm sequence with the commands the invoker should run.>

- <Command to create the commit>
- <Command to push>
- <Command to confirm the commit landed>

### 6. <Verification step title>

<Describe the post-commit verification: re-run the porcelain enumeration, confirm only explicitly-excluded files remain, and loop back to step 2 if anything else is unstaged.>

## Important:

<Bulleted list of hard, non-negotiable rules around attribution and authorship — no co-author lines, no automated attribution, commit messages authored as if the human user wrote them. 4–6 bullets.>

- <Attribution rule>
- <Attribution rule>
- <Attribution rule>
- <Attribution rule>

## Report

- IMPORTANT: <State the exact return contract — typically, return only the commit message that was used and nothing else.>
