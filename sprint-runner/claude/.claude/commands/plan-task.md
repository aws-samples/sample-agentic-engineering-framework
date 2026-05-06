---
description: <One-line description of what this prompt does. State that it creates a plan for maintenance tasks (refactors, small-scale changes, non-feature-non-bug work) with parallel codebase research.>
---

# Task Planning

<Opening framing paragraph (1–2 sentences). State the goal: create a new plan to resolve the `Task` using the exact specified markdown `Plan Format`. Point the reader to the `Instructions`, `Process`, and `Relevant Files` sections. Make clear this prompt is planning the task, not performing it.>

## Variables

<List each variable this prompt accepts, mapped to its positional argument. Typical: an identifier and a payload (plain text or a path to a .md/.txt file).>

task_id: $1
task_input: $2 <(plain text description OR path to a local .md/.txt file)>

## Instructions

<Bulleted list of hard rules the planner must follow. Preserve "IMPORTANT:" prefixes on rules that are easy to violate. Cover: planning-vs-doing boundary, filename convention, the `Plan Format` contract, the placeholder-replacement rule, reasoning quality, skepticism, no-open-questions, phase ordering, research-first, pattern consistency, citation discipline, context-window hygiene, and input-resolution fallback. Aim for 10–14 bullets.>

- IMPORTANT: <Planning-vs-doing boundary — we're writing a plan; we are NOT resolving the task.>
- <Output location + filename convention — create the plan in `specs/` as `task-{task_id}-sdlc_planner-{descriptive-name}.md`, where `{descriptive-name}` is a short kebab-case name derived from the task.>
- <Directive — use the `Plan Format` below as the required shape.>
- IMPORTANT: <Replace every `<placeholder>` in the `Plan Format` with concrete content.>
- <Reasoning directive — think hard about the plan and the steps to accomplish the task.>
- <Skepticism directive — verify assumptions with actual code; don't just accept claims.>
- <No-open-questions rule — resolve all ambiguities before writing.>
- <Phase-ordering rule — each phase depends only on prior phases; Phase 1 has zero dependencies on new code.>
- <Research-first rule — investigate existing patterns, architecture, and conventions before planning.>
- <Consistency rule — follow existing patterns; don't reinvent the wheel.>
- <Citation rule — use specific `file:line` references throughout the plan.>
- <Context-window rule — delegate heavy searching to subagents.>
- <Input-resolution fallback — what to do when `$ARGUMENTS` is empty and `task_input` is missing (use available context to infer; abort with an error if nothing can be determined).>

## Process

<Short lead-in sentence describing the three-phase process. Then three `###` subsections with numbered steps (bolded titles + sub-bullets).>

### Phase 1: <Name of the context-gathering phase>

<Numbered list of steps the planner takes to orient.>

1. **<Step title — e.g., resolve input>**:
   - <Sub-action — if `task_input` is a file path (`.md`/`.txt`), read the file for task details>
   - <Sub-action — if `task_input` is plain text, use it directly>
   - <Sub-action — incorporate any additional context from `$ARGUMENTS`>
   - <Sub-action — if no task can be determined, abort with an error>

2. **<Step title — e.g., read all mentioned files FULLY>**:
   - <Category — task description / task input>
   - <Category — project entry doc>
   - <Category — `.claude/commands/ai-implementation-docs.md` for additional documentation hints>
   - <Anti-pattern reminder — do NOT spawn subagents before reading these key files yourself>

3. **<Step title — e.g., read contextual docs>**:
   - <Sub-action — check `.claude/commands/ai-implementation-docs.md` for docs matching this task area>
   - <Sub-action — include matched docs in the plan's `Relevant Files` section>

### Phase 2: <Name of the research-and-discovery phase>

<Numbered list covering: spawning parallel subagents for research, waiting for ALL to complete, and pulling the files they surface back into the main context.>

1. **<Step title — e.g., spawn parallel subagents for research>**:
   - **codebase-locator** — <Research goal — find files related to the task>
   - **codebase-analyzer** — <Research goal — understand the current implementation with `file:line` references>
   - **codebase-pattern-finder** — <Research goal — find similar work or patterns to model after>
   - <Optional project-specific locator — e.g., find prior plans or decisions about this area>

2. **<Step title — e.g., wait for ALL subagents to complete>**

3. **<Step title — e.g., read all identified files>** into main context

### Phase 3: <Name of the plan-development-and-review phase>

<Numbered list covering: developing the plan sequentially on research findings, filling all placeholders, resolving ambiguities, creating the plan file, and verifying completeness.>

1. **<Step title — e.g., develop the plan>** sequentially based on research findings

2. **<Step title — e.g., ensure all placeholders are filled>** with concrete content

3. **<Step title — e.g., resolve any ambiguities>** via codebase research — make a best-judgment decision and document rationale in Notes

4. **<Step title — e.g., create the plan file>** in `specs/` with the naming convention

5. **<Step title — e.g., verify the plan is complete>**:
   - <Completeness check — no `<placeholder>` tokens remain>
   - <Accuracy check — `file:line` references resolve>
   - <Clarity check — no open questions remain>
   - <Executability check — validation commands are specific and runnable>

## Relevant Files

<Short lead-in sentence telling the planner where to focus. Then a bulleted list of project-wide anchors (entry doc, backend/core source, frontend source, ai-implementation-docs index). Close with a one-line reminder to ignore files not relevant to the task.>

Focus on the following files:
- `<path/to/entry-doc>` - <Purpose — project overview and instructions>
- `<path/to/backend-or-core-source>` - <Purpose — core source code>
- `<path/to/frontend-source>` - <Purpose — frontend source, if applicable>
- <Directive — read `.claude/commands/ai-implementation-docs.md` to check if the task requires additional documentation>

<Closing one-liner telling the planner to ignore files not relevant to the task.>

## Task

<Describe where the task details come from. Typical: extract from the `task_input` variable (read file if path, use text directly otherwise). Then include a line that expands the positional arguments so free-form task descriptions also flow through.>

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
task_id: `{task_id}`
task_input: `{task_input}`

## Overview
<Brief description of what we're doing and why.>

## Current State Analysis
<What exists now, what's missing, key constraints discovered.>

### Key Discoveries:
- <Important finding with `file:line` reference>
- <Pattern to follow>
- <Constraint to work within>

## Desired End State
<What the codebase looks like after this task is complete, and how to verify it.>

## What We're NOT Doing
<Explicitly list out-of-scope items to prevent scope creep.>

## Implementation Approach
<High-level strategy and reasoning for the chosen approach.>

## Relevant Files
Use these files to resolve the task:
<Bullets of existing files relevant to the task, each with a one-line reason.>

### New Files
<Bullets of new files to create, each with its purpose. Omit if none.>

---

## Phase 1: [Descriptive Name]

IMPORTANT: Execute every step in order, top to bottom.

### Overview
<What this phase accomplishes and why it comes first.>

### Changes Required:
<Numbered change groups. Each group: `**File**`, `**Changes**`, fenced code block. 1–3 groups per phase.>

#### 1. [Component/File Group]
**File**: `path/to/file.ext`
**Changes**: <Summary of changes>

```[language]
<Specific code to add or modify>
```

### Success Criteria:

- [ ] Tests pass: `<test command>`
- [ ] Type checking passes: `<typecheck command>`
- [ ] Build succeeds: `<build command>`

**Implementation Note**: After completing this phase, run all automated verification checks before proceeding.

---

## Phase 2: [Descriptive Name]
<Same shape as Phase 1. Add phase-specific checks to Success Criteria as needed.>

---

[Repeat the phase structure as many times as the task requires.]

---

## Testing Strategy

### Unit Tests:
- <What to test>
- <Key edge cases>

### Integration Tests:
- <End-to-end scenarios>

## Acceptance Criteria

- [ ] <Specific, measurable criterion>
- [ ] <Another criterion>
- [ ] All validation commands pass with zero errors

## Validation Commands
Execute every command to validate the task is complete with zero regressions. Every command must execute without errors.

- `<test command>` - <What passing proves>
- `<typecheck command>` - <What passing proves>
- `<build command>` - <What passing proves>
- `<lint command>` - <What passing proves>

## References
- Similar implementation: `<file:line>`
- Related pattern: `<file:line>`

## Notes
<Any additional context, future considerations, or technical debt to be aware of.>
```

## Report

- IMPORTANT: <State the exact return contract — typically, return only the path to the plan file created and nothing else.>
