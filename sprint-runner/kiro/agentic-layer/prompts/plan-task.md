---
description: <One-line description of what this prompt does and when to invoke it. Frame it as a planning prompt: emphasize that it produces an implementation plan (not an implementation) and mention the key inputs it expects.>
---

# Task Planning

<Opening instruction (1–2 sentences). State what the prompt is asking the agent to do: create a plan to resolve a `Task`, using the specified markdown `Plan Format`, the `Instructions`, the `Process`, and the `Relevant Files`. Keep the backtick-wrapped section names intact so the agent can cross-reference them.>

## Variables

<List the input variables this prompt expects, one per line, in the form `variable_name: $N` where `$N` is the positional argument slot. Typical planning prompts take 1–3 variables (e.g., an issue identifier, a JSON payload describing the task, an optional run identifier). Use the shape below.>

<variable_name_1>: $1
<variable_name_2>: $2

## Instructions

<Bulleted list of hard rules the agent must follow while producing the plan. Mix "IMPORTANT:" imperatives with practical guidance. Expected content:
- A reminder that the agent is writing a plan, NOT executing the task.
- The filesystem location and naming convention for the output plan file, including any `{placeholder}` tokens that should be interpolated.
- A directive to use the `Plan Format` and to replace every `<placeholder>` with a concrete value.
- A "THINK HARD" / reasoning nudge.
- Skepticism and assumption-verification guidance.
- A rule forbidding open questions in the final plan.
- Phase-ordering constraints (each phase depends only on earlier phases; Phase 1 has no new-code dependencies).
- A rule to research existing patterns and conventions before planning.
- A rule to use specific `file:line` references throughout.
- A directive to protect the main context window by delegating search to subagents.
- Any project-specific rules (package managers, script runners, style constraints).
- Fallback behavior when inputs are empty or missing.
Aim for 10–15 bullets. Preserve bolded imperatives and "IMPORTANT:" markers.>

- IMPORTANT: <Scope-anchoring rule clarifying that the output is a plan, not an implementation.>
- <Output file location and naming convention, including interpolation tokens.>
- <Directive to follow the `Plan Format` and fill every `<placeholder>`.>
- <Reasoning and skepticism guidance.>
- <Phase-ordering and dependency constraints.>
- <Research, convention-following, and `file:line` citation rules.>
- <Context-window protection and subagent delegation rule.>
- <Project-specific tooling or style rules.>
- <Fallback behavior for empty or missing inputs.>

## Process

<Short lead-in sentence describing that the agent works through the following phases in order. Then provide three `###` phases covering: (1) context gathering, (2) research and discovery, (3) plan development and review. Preserve the three-phase structure exactly.>

### Phase 1: Context Gathering & Analysis

<Numbered list (3–4 items) describing how the agent resolves inputs and ingests the most important files directly into the main context before delegating. Each numbered item should have a bolded title and 2–4 sub-bullets of concrete actions. Typical content: resolving the input arguments, reading all mentioned files fully, reading contextual/overview docs, and an explicit "do NOT spawn subagents before reading key files yourself" guard.>

1. **<Input resolution step>**:
   - <Sub-action describing how to parse or interpret each input variable.>
   - <Sub-action describing fallback when inputs are missing.>
   - <Sub-action for the abort case.>

2. **<Direct file-reading step>**:
   - <Category of file to read, e.g., task description files.>
   - <Category of file to read, e.g., related implementation files.>
   - <Category of file to read, e.g., project-level overview docs.>
   - <Guard against premature subagent spawning.>

3. **<Contextual documentation step>**:
   - <Where to look for additional documentation pointers.>
   - <How to incorporate those pointers into the plan's Relevant Files section.>

### Phase 2: Research & Discovery

<Numbered list (2–4 items) describing how the agent delegates parallel research to subagents and then re-consolidates findings. Typical content: spawning parallel subagents with specific research goals, waiting for all subagents to complete before proceeding, and reading the files surfaced by research back into the main context.>

1. **<Parallel research step>**:
   - <Research goal, e.g., locate all files related to the task.>
   - <Research goal, e.g., document current patterns with `file:line` references.>
   - <Research goal, e.g., find similar implementations to model after.>
   - <Research goal, e.g., find prior plans or decisions about this area.>

2. **<Synchronization step>**

3. **<Main-context ingestion step>**

### Phase 3: Plan Development & Review

<Numbered list (4–5 items) describing how the agent assembles the plan, resolves ambiguities, writes the file, and validates it. Typical content: developing the plan sequentially on top of research findings, filling every placeholder, making best-judgment calls on ambiguities and documenting rationale in Notes, writing the file at the naming convention from Instructions, and a final verification pass (all placeholders replaced, all `file:line` refs accurate, no open questions, validation commands are executable).>

1. **<Plan drafting step>**

2. **<Placeholder-filling step>**

3. **<Ambiguity-resolution step>**

4. **<File-creation step>**

5. **<Verification step>**:
   - <Check that every `<placeholder>` is replaced with real content.>
   - <Check that every `file:line` reference is accurate.>
   - <Check that no open questions remain.>
   - <Check that validation commands are specific and executable.>

## Relevant Files

<Short lead-in sentence telling the agent which files to focus on. Then a bulleted list of 3–6 paths or glob patterns that are load-bearing for this prompt (project overview, build/run scripts, workflow scripts, any implementation-docs pointer file). Close with a one-sentence instruction to ignore files not relevant to the task.>

- `<path/to/overview-file>` - <Why this file matters.>
- `<path/to/scripts/**>` - <Why this directory matters.>
- `<path/to/workflow/**>` - <Why this directory matters.>
- <Instruction to read a documentation-pointer file and include its references when conditions match.>

<Closing one-line instruction to skip files that are not relevant to the task.>

## Task

<Short instruction telling the agent how to derive the task description from the input variables. Typically: extract the title and body from a JSON payload, or fall back to `$ARGUMENTS` if no structured input is provided. End with the literal `$ARGUMENTS` token so positional input is captured.>

$ARGUMENTS

## Plan Format

The markdown block below is a **starter template**, not a rigid contract. Teams adopting this prompt are expected to reshape it to match their planning conventions, tooling, and review culture. The default below is opinionated on purpose — copy it, then adapt.

**What must stay (invariants).** Downstream prompts (`implement.md`, `patch.md`, `review.md`) and the orchestrator read plans for a small set of anchors. If you rename or remove these, update the downstream prompts in the same change:

- A title heading for the plan
- One or more `## Phase N: <name>` sections, each with a `### Success Criteria:` checklist of runnable commands — the build/patch loop iterates by phase number
- A `## Validation Commands` section listing executable commands — this is what the review and patch phases re-run
- A `## Relevant Files` section — consumed by the builder and reviewer as the authoritative file manifest
- `file:line` citation discipline throughout

**What is safe to change.** Section naming (outside the invariants above), section ordering, the shape of testing strategy, acceptance criteria formatting, metadata fields, notes/references/migration-notes structure, code-block languages, and whether you use checkboxes or prose. If your team plans in user stories, swap `Overview` for a user-story block. If you document ADRs inline, add an `## ADR` section. Keep the invariants wired; everything else is yours.

**Before shipping template changes, update in lockstep:** `prompts/implement.md` (consumes phase Success Criteria), `prompts/patch.md` (targets specific phases by number), `prompts/review.md` (compares implementation against the plan shape).

### Default template

Use this as-is until you have a reason to change it. Replace every `<placeholder>` and `[bracketed slot]` with concrete content.

```markdown
# Task: [Task Name]

## Metadata
<One line per input variable, `key: `value`` form. At minimum: issue identifier, run identifier, raw issue payload.>

## Overview
[Brief description of what we're doing and why]

## Current State Analysis
[What exists now, what's missing, key constraints discovered]

### Key Discoveries:
- [Important finding with file:line reference]
- [Pattern to follow]
- [Constraint to work within]

## Desired End State
[What the codebase looks like after this task is complete, and how to verify it]

## What We're NOT Doing
[Explicitly list out-of-scope items to prevent scope creep]

## Implementation Approach
[High-level strategy and reasoning for the chosen approach]

## Relevant Files
Use these files to resolve the task:
<Bullets of existing files relevant to the task, each with a one-line reason.>

### New Files
<Bullets of new files to create, each with its purpose. Omit if none.>

---

## Phase 1: [Descriptive Name]

IMPORTANT: Execute every step in order, top to bottom.

### Overview
[What this phase accomplishes and why it comes first]

### Changes Required:
<Numbered change groups. Each group: `**File**`, `**Changes**`, fenced code block. 1–3 groups per phase.>

#### 1. [Component/File Group]
**File**: `path/to/file.ext`
**Changes**: [Summary of changes]

```[language]
// Specific code to add/modify
```

### Success Criteria:

- [ ] Tests pass: `[appropriate test command]`
- [ ] Type checking passes: `[typecheck command]`
- [ ] Build succeeds: `[build command]`

**Implementation Note**: After completing this phase, run all automated verification checks before proceeding.

---

## Phase 2: [Descriptive Name]
<Same shape as Phase 1. Add phase-specific checks to Success Criteria as needed.>

---

[Repeat the phase structure as many times as the task requires.]

---

## Testing Strategy

### Unit Tests:
- [What to test]
- [Key edge cases]

### Integration Tests:
- [End-to-end scenarios]

## Acceptance Criteria

- [ ] [Specific, measurable criterion]
- [ ] [Another criterion]
- [ ] All validation commands pass with zero errors

## Validation Commands
Execute every command to validate the task is complete with zero regressions. Every command must execute without errors. Don't validate with curl commands.

- `<validation command>` - <What this verifies>
- `<validation command>` - <What this verifies>

## References
- Similar implementation: `[file:line]`
- Related pattern: `[file:line]`

## Notes
[Any additional context, future considerations, or technical debt to be aware of]
```

## Report

<Closing instruction specifying exactly what the agent should return after the plan file has been written. Typical content: return exclusively the path to the created plan file, nothing else. Preserve the "IMPORTANT:" marker.>

- IMPORTANT: <Directive restricting the final output to a single file path.>
