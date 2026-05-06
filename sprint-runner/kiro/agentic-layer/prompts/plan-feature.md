---
description: <One-line description of what this prompt produces and when to invoke it. Frame it as a planning prompt that turns a feature request into a phased implementation plan via research and iteration.>
model: <Model selector — typically a reasoning-capable model such as "opus" or "inherit".>
---

# Feature Planning

<Opening directive (1–2 sentences). State the goal: create a new plan for the `Feature` using the exact specified markdown `Plan Format`. Reference the `Instructions`, `Process`, `Relevant Files`, and `Plan Format` sections below by name so the model knows which anchors to follow.>

## Variables

<Declare the positional arguments the prompt accepts. One line per variable in `name: $N` form. Typical slots include an identifier for the inbound work item and a JSON payload describing it.>

<variable_name_1>: $1
<variable_name_2>: $2

## Instructions

<Bulleted list of hard rules the planner must follow. Lead with the scope boundary ("we're writing the plan, not implementing the feature"), then cover: where the plan file lives and how it's named, how `<placeholder>` tokens are treated inside the `Plan Format`, reasoning expectations (think hard, be skeptical, no open questions), phase ordering rules, research expectations before planning, style constraints (follow existing patterns, avoid reinvention, specific `file:line` refs), context-window hygiene (delegate heavy searching to subagents), dependency/tooling conventions, and any UI-specific carve-outs (e.g., E2E test file creation belongs in a phase but the full browser suite is NOT a phase gate). Close with an input-resolution rule describing what to do when arguments are empty. Use "IMPORTANT:" prefixes on the non-negotiable items. Aim for 10–16 bullets.>

- IMPORTANT: <Scope boundary — we're writing a plan, not implementing the feature.>
- <Where to create the plan file and the exact filename convention, including how to derive any descriptive slug.>
- <How to use the `Plan Format` section below.>
- IMPORTANT: <Rule about replacing every `<placeholder>` in the `Plan Format` with concrete, detailed content.>
- <Reasoning directive — think hard about requirements, design, and approach.>
- <Skepticism directive — verify assumptions against real code, don't accept claims at face value.>
- <No-open-questions rule — resolve ambiguities before writing.>
- <Phase-ordering rule — each phase depends only on previous phases; Phase 1 has zero dependencies on new code.>
- <Research-first rule — investigate existing patterns, architecture, and conventions before planning.>
- <Consistency rule — follow existing patterns; don't reinvent the wheel.>
- <Quality rule — design for extensibility and maintainability.>
- <Citation rule — use specific `file:line` references throughout the plan.>
- <Context-window rule — delegate heavy searching to subagents.>
- <Dependency/tooling convention for adding new libraries and where to document them.>
- <Any simplicity constraints (e.g., avoid specific language features) that apply to the generated plan.>
- IMPORTANT: <UI / E2E carve-out — describe what to include in a phase when the feature has UI, what belongs in the plan's Relevant Files section for E2E context, and the hard rule that the full browser suite is NOT a per-phase Success Criterion because the runner owns that stage.>
- <Input-resolution fallback — what to do when `$ARGUMENTS` is empty and the JSON payload is missing.>

## Process

<Short lead-in sentence describing the four-phase process the planner follows. Then four `###` subsections, one per phase, each with a numbered list of 2–4 steps. Keep bolded step titles and the tone of concrete imperatives.>

### Phase 1: Context Gathering & Initial Analysis

<Numbered list (3–4 items) covering: resolving the input arguments into a concrete feature description, reading all explicitly-referenced files fully in the main context (include the project entry doc such as `README.md`), consulting any contextual documentation index, and optionally fanning out to parallel research subagents. For each step, bold a short imperative title followed by sub-bullets describing what to do.>

1. **<Step title — e.g., resolve input>**:
   - <Sub-step describing one branch of input handling>
   - <Sub-step describing another branch>
   - <Sub-step describing the abort/fallback case>

2. **<Step title — e.g., read mentioned files fully>**:
   - <Category of file to read>
   - <Category of file to read>
   - <Project entry document to start with>
   - <Anti-pattern to avoid (e.g., don't spawn subagents before reading key files yourself)>

3. **<Step title — e.g., read contextual docs>**:
   - <Which index or manifest to consult>
   - <What to do with its findings>

4. **<Step title — e.g., spawn parallel research agents>**:
   - <What each parallel agent investigates>
   - <What each parallel agent investigates>
   - <Why parallelism matters here>

### Phase 2: Research & Discovery

<Numbered list (3 items) covering: dispatching parallel subagents for deeper research (files and directories, implementation details with `file:line`, similar features, prior research/plans), waiting for ALL of them to finish, and pulling the files they surface back into the main context.>

1. **<Step title — e.g., spawn parallel subagents for research>**:
   - <Research goal>
   - <Research goal>
   - <Research goal>
   - <Research goal>

2. **<Step title — e.g., wait for all subagents to complete>**

3. **<Step title — e.g., read all identified files into main context>**

### Phase 3: Plan Development

<Numbered list (3 items) covering: developing the plan sequentially on top of research findings, ensuring every `<placeholder>` is filled with concrete actionable content, and resolving any remaining ambiguities via codebase research with the rationale captured in the Notes section.>

1. **<Step title>** <short description>

2. **<Step title>** <short description>

3. **<Step title>** <short description>

### Phase 4: Review & Finalize

<Numbered list (2 items) covering: creating the plan file at the agreed path with the agreed naming convention, and verifying the plan is complete against a small checklist (all placeholders replaced, all `file:line` refs accurate, no open questions, validation commands specific and executable).>

1. **<Step title — e.g., create the plan file>** <short description>

2. **<Step title — e.g., verify the plan is complete>**:
   - <Verification check>
   - <Verification check>
   - <Verification check>
   - <Verification check>

## Relevant Files

<Short lead-in sentence telling the planner which files to focus on. Then a bulleted list of project-wide anchors (project entry doc, scripts/automation directories, workflow directories, any documentation index to cross-reference). Close with a one-line reminder to ignore files that aren't relevant to the feature. 3–5 bullets.>

Focus on the following files:
- `<path/to/entry-doc>` - <Purpose>
- `<path/to/scripts-dir/**>` - <Purpose>
- `<path/to/workflow-dir/**>` - <Purpose>
- <Instruction to read the documentation index and pull in anything that matches the task>

<Closing one-liner telling the planner to ignore files not relevant to the feature.>

## Feature

<Describe where the feature details come from. Typically: extract from the JSON payload variable (parse it and use title/body fields). Then include a line that expands the positional arguments so free-form feature descriptions also flow through.>

$ARGUMENTS

## Plan Format

The markdown block below is a **starter template**, not a rigid contract. Teams adopting this prompt are expected to reshape it to match their planning conventions, tooling, and review culture. The default below is opinionated on purpose — copy it, then adapt.

**What must stay (invariants).** Downstream prompts (`implement.md`, `patch.md`, `review.md`) and `tools/sprint_runner.py` read plans for a small set of anchors. If you rename or remove these, update the downstream consumers in the same change:

- A title heading for the plan
- One or more `## Phase N: <name>` sections, each with a `### Success Criteria:` checklist of runnable commands — the build/patch loop iterates by phase number
- A `## Validation Commands` section with an explicit **phase-owned vs runner-owned** split — `sprint_runner.py` appends a RUNNER NOTE that depends on this bucketing to know which commands are gating a phase vs. which it executes itself in the E2E stage with its own patch-and-retry loop
- A `## Relevant Files` section — consumed by the builder and reviewer as the authoritative file manifest
- When a feature has UI: an `### E2E Test Files` subsection — the runner expects exactly one sprint-level E2E test file created alongside the spec(s)
- `file:line` citation discipline throughout

**What is safe to change.** Section naming (outside the invariants above), section ordering, User Stories shape (EARS vs. free-form), acceptance criteria formatting, metadata fields, performance/migration/notes sections, code-block languages, and whether you use checkboxes or prose. If your team plans by outcome rather than stories, drop `User Stories`. If you track ADRs inline, add an `## ADR` section. Keep the invariants wired; everything else is yours.

**Before shipping template changes, update in lockstep:** `prompts/implement.md` (consumes phase Success Criteria), `prompts/patch.md` (targets specific phases by number), `prompts/review.md` (compares implementation against the plan shape), and `tools/sprint_runner.py` `step_plan()` (appends the RUNNER NOTE — if you rename the command buckets or the `SPEC_PATH`/`E2E_PATH` output contract, fix it here).

### Default template

Use this as-is until you have a reason to change it. Replace every `<angle-bracket slot>` with concrete content.

```markdown
# [Feature/Task Name] Implementation Plan

## Metadata
<One line per positional variable, `key: `value`` form.>
<variable_name_1>: `{<variable_name_1>}`
<variable_name_2>: `{<variable_name_2>}`

## Overview
<Short paragraph: what we're implementing and why.>

## Current State Analysis
<Short paragraph: what exists, what's missing, key constraints from research.>

### Key Discoveries:
<3–5 findings, each with a `file:line` reference or a named pattern/constraint.>
- <Finding with `file:line`>
- <Pattern to follow>
- <Constraint to work within>

## Desired End State
<Short paragraph: end state after the plan is complete and how to verify.>

## What We're NOT Doing
<3–6 out-of-scope items to prevent scope creep.>

## Implementation Approach
<Short paragraph: high-level strategy and reasoning for the chosen approach.>

## Relevant Files
Use these files to implement the feature:
<Bullets of existing files, each `path/to/file.ext` + one-line reason.>

### New Files
<Bullets of files to create, each `path/to/new-file.ext` + purpose. Omit if none.>

## User Stories
Use these user stories to implement the feature:

### User Stories
<2–5 stories in EARS-style persona format: "As a [role], I want [action], so that [benefit]".>


---

## Phase 1: [Descriptive Name]

IMPORTANT: Execute every step in order, top to bottom.

### Overview
<Short paragraph: what this phase accomplishes and why it must come first (zero dependencies on new code).>

### Changes Required:
<Numbered change groups. Each group: bolded title, `**File**`, `**Changes**`, and a fenced language block. 1–4 groups per phase.>

#### 1. [Component/File Group]
**File**: `path/to/file.ext`
**Changes**: <Summary>

```[language]
<Specific code to add or modify — enough context to be unambiguous>
```

### Success Criteria:
<Phase-owned, runnable checks. Typical: tests, typecheck, lint, build.>

- [ ] Tests pass: `<test command>`
- [ ] Type checking passes: `<typecheck command>`
- [ ] Linting passes: `<lint command>`
- [ ] Build succeeds: `<build command>`

**Implementation Note**: <Reminder to run all automated verification before proceeding.>

---

## Phase 2: [Descriptive Name]
<Same shape as Phase 1. Assume Phase 1 is complete. Add phase-specific checks to Success Criteria as needed.>

---

[Repeat the phase structure as many times as the feature requires. Each phase depends only on earlier phases.]

---

## Testing Strategy

### Unit Tests:
<What to unit test and key edge cases.>
- <What to test>
- <Key edge case>

### Integration Tests:
<End-to-end scenarios that exercise multiple components.>
- <Scenario>

### E2E Test Files
<When to create E2E test files and where they live. The plan creates the file only (doesn't run the browser suite); keep steps minimal and specific; screenshots encouraged when useful.>

## Performance Considerations
<Short paragraph on performance implications or optimizations.>

## Migration Notes
<Short paragraph on handling existing data or systems. Omit if not applicable.>

## Acceptance Criteria
<Specific, measurable done criteria. Include the catch-all on validation commands.>

- [ ] <Specific, measurable criterion>
- [ ] <Another criterion>
- [ ] All validation commands pass with zero errors

## Validation Commands
Execute every command to validate the feature works with zero regressions. Every command must execute without errors.

**Command ownership** — <One sentence introducing the two buckets.>

- **Phase-owned (<fast, per-phase gates>):** <Command types safe as per-phase Success Criteria.>
- **Runner-owned (<sprint-level, NOT phase gates>):** <Runner re-executes these in a dedicated stage with its own patch-and-retry loop; do NOT list as per-phase Success Criteria.>

<If an E2E test file was created: include one runner-owned line that reads the E2E driver doc, then reads and executes the new E2E test file, marked as runner-owned for the sprint-level E2E stage.>

<Bulleted commands, each tagged phase-owned or runner-owned.>
- `<test command>` - <Purpose> (phase-owned)
- `<typecheck command>` - <Purpose> (phase-owned)
- `<build command>` - <Purpose> (phase-owned)
- `<lint command>` - <Purpose> (phase-owned)
- `<e2e command>` - Runner-owned; do NOT gate a phase on this

## References
<References to similar implementations or prior work, each a short label + `file:line`.>
- Similar implementation: `<file:line>`

## Notes
<Short paragraph: additional context, future considerations, tech debt, or rationale for judgment calls.>
```

## Report

- IMPORTANT: <Directive describing the exact and only output the prompt should return — typically the path to the plan file created and nothing else.>
