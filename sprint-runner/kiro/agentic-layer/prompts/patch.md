---
description: <One-line description of what this prompt produces and when to invoke it. State that it creates a focused patch plan, name the primary input (e.g., a review change request), and emphasize the "minimal, targeted changes" quality bar.>
---

# <Prompt Title — typically "Patch Plan" or the name of the artifact being produced>

<Opening instruction (1–2 sentences) stating the goal. Frame: "Create a **<artifact type>** to <specific objective> based on the `<primary_input>`. Follow the `Instructions` and `Process` to produce <what kind of output>." Bold the artifact type. Keep the stylistic emphasis on scope minimalism if the original has it.>

## Variables

<List every positional argument the prompt accepts, one per line, in the shape `variable_name: $N` or `variable_name: $N if provided, otherwise <fallback>`. For optional arguments, annotate with `(optional)` and describe the expected shape (e.g., a path, a comma-separated list, a default agent name). 3–5 variables is typical.>

<variable_1>: $1
<variable_2>: $2 if provided, otherwise <fallback behavior>
<variable_3>: $3 if provided, otherwise use '<default value>'
<variable_4>: $4 (optional) - <description of shape and purpose>

## Instructions

<Bulleted list of top-level rules the agent must follow while producing the artifact. Lead with "IMPORTANT:" bullets for the non-negotiable framing rules (e.g., that this is a PLAN not an implementation, that scope must stay minimal). Mix in directives about: how to use the primary input, how to fill placeholders in the `Plan Format`, a "THINK HARD" or reasoning-model nudge, a skepticism reminder, a citation-discipline reminder (e.g., `file:line` references), and how to derive any validation steps. 6–10 bullets.>

- IMPORTANT: <Non-negotiable framing rule — e.g., what the artifact is and is NOT.>
- IMPORTANT: <Non-negotiable scope rule — e.g., keep changes minimal, only address the stated input.>
- <Directive tying the work back to `<primary_input>`.>
- <Directive about filling every `<placeholder>` in the `Plan Format` with specific implementation details.>
- <Reasoning-model nudge — e.g., "Use your reasoning model: THINK HARD about ...".>
- <Skepticism directive — e.g., "Be skeptical — verify assumptions with actual code.">
- <Citation-discipline directive — e.g., use specific `file:line` references throughout.>
- <Directive about how to derive validation steps, including the fallback behavior if a source is not provided.>

## Process

<Introduce the step-by-step procedure the agent follows on every invocation. Organize into numbered phases with `###` sub-headers. Typically 2 phases, ordered from context-gathering to plan-authoring. Preserve the phase names from the original if they exist.>

### Phase 1: <Name of the context-gathering phase>

<Numbered list of 4–6 steps the agent performs before drafting the artifact. Each step has a bolded imperative lead ("**Read**", "**Examine**", "**Run**", "**Spawn**") followed by a short description. Cover: reading any provided source spec, examining supplementary inputs (screenshots, logs), running diagnostic commands, reading contextual docs, and optionally spawning parallel subagents for targeted discovery.>

1. **<Imperative>** <what to do and why, referencing the relevant variable or file>.

2. **<Imperative>** <what to do and why>.

3. **<Imperative>** <what to do and why>.

4. **<Imperative>**:
   - <Sub-step — e.g., read a specific doc to check for task-matching conditions>.
   - <Sub-step — e.g., follow the referenced documentation if conditions match>.

5. **<Imperative>** if needed to:
   - <Targeted discovery task with `file:line` reference goal>
   - <Targeted discovery task>

### Phase 2: <Name of the plan-authoring phase>

<Numbered list of 3–5 steps the agent performs to produce the artifact. Cover: drafting the plan with the right focus, ensuring every placeholder is filled, writing the file to the conventional location, and verifying the result against a checklist.>

1. **<Imperative>** — <how to draft and what quality bar to hold>.

2. **<Imperative>** <what to verify about placeholder completeness>.

3. **<Imperative>** <where to write the file, including the naming convention>.

4. **<Imperative>** the plan is complete:
   - <Checklist item — e.g., all `<placeholder>` tags replaced>
   - <Checklist item — e.g., all `file:line` references are accurate>
   - <Checklist item — e.g., validation commands are specific and executable>
   - <Checklist item — e.g., scope is minimal with no extras>

## Relevant Files

<Short lead-in sentence telling the agent which files matter for this prompt. Then a bulleted list of file globs or specific paths with a one-line description each. Close with a one-line instruction to ignore unrelated files. 3–5 bullets.>

Focus on the following files:
- `<path or glob>` - <One-line purpose>
- `<path or glob>` - <One-line purpose>
- `<path or glob>` - <One-line purpose>
- Read `<path/to/contextual-doc>` to check if your task requires additional documentation

Ignore files not relevant to the <artifact type>.

## Plan Format

<Describe the exact shape of the artifact. Provide a fenced code block containing a fully-worked template with `<angle-bracket>` slots. The outer fence should use the language tag of the artifact being produced (e.g., `markdown`). Preserve every section the original template had: a title line, a Metadata block with run_id and primary input, an Overview, a Current State with Key Discoveries, an explicit "What We're NOT Doing" scope fence, a Files to Modify list, numbered Implementation Steps each with a **File** and an inner fenced code snippet, a Success Criteria checklist, a Validation section, a Patch Scope summary, and a References list. Callers pattern-match on this template, so the shape must stay stable.>

```markdown
# <Artifact Type>: [<Concise Title Slot>]

## Metadata
run_id: `{run_id}`
<primary_input_name>: `{<primary_input_name>}`

## Overview
**<Source Reference Label>:** [<variable value or "N/A">]
**Issue:** [<Brief description of the issue based on `<primary_input>`>]
**Fix Approach:** [<Brief description of the solution approach and reasoning>]

## Current State

[<What's happening now vs what should happen, with file:line references to the exact locations>]

### Key Discoveries:
- [<Finding with file:line reference>]
- [<Constraint or pattern to respect>]

## What We're NOT Doing

[<Explicitly list out-of-scope items — only the stated input, nothing else>]

## Files to Modify

Use these files to implement the <artifact type>:

<list only the files that need changes with file:line references — be specific and minimal>

## Implementation Steps

IMPORTANT: Execute every step in order, top to bottom.

### Step 1: [<Specific action>]
**File**: `<path/to/file.ext>`
- [<Implementation detail with line references>]
- [<Implementation detail>]

```[language]
<Specific code to add/modify>
```

### Step 2: [<Specific action>]
**File**: `<path/to/file.ext>`
- [<Implementation detail with line references>]
- [<Implementation detail>]

```[language]
<Specific code to add/modify>
```

[<Continue as needed — keep it to 2-5 steps>]

## Success Criteria

- [ ] <Primary objective met — e.g., review issue resolved>
- [ ] <Regression guard — e.g., no regressions introduced>
- [ ] <Validation guard — e.g., all validation commands pass with zero errors>

## Validation

Execute every command to validate the <artifact type> is complete with zero regressions.

<List 1-5 specific commands or checks to verify the work is correct>

## Patch Scope
**Lines of code to change:** [<estimate>]
**Risk level:** [<low|medium|high>]
**Testing required:** [<brief description>]

## References

- <Primary reference label>: `[<file:line>]`
- <Secondary reference label>: `[<file:line>]`
```

## Report

- IMPORTANT: <Single-line directive describing what the agent should return at the end. Typical shape: "Return exclusively the path to the <artifact> file created and nothing else." Keep the exclusivity wording if the original has it.>
