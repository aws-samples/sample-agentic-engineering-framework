---
description: <One-line description of the documentation-generation command. State that it produces feature documentation by reconciling code changes against a specification, and name the output directory (e.g., `docs/`).>
---

# <Command Title — imperative verb phrase, e.g., "Document Feature">

<Opening paragraph (2–3 sentences) describing what this command does. Name the artifact produced (markdown documentation), the inputs it reconciles (git diff against a base branch, a specification, optional screenshots), and the output directory. Keep the voice direct — this paragraph is the hover-description for the command.>

## Variables

<List the variables the command accepts from the invocation, one per line, in the form `name: $N if provided, otherwise <fallback behavior>`. Typical slots: the spec file path and an optional assets/screenshots directory. Keep each entry on a single line.>

<variable_name_1>: $1 if provided, otherwise <fallback behavior>
<variable_name_2>: $2 if provided, otherwise <fallback behavior>

## Instructions

<Bulleted list of top-level imperatives that frame the entire task. Mix `IMPORTANT:` directives with orientation statements. Cover: framing (the work is already done — this is post-hoc documentation), the output path convention, a pointer to the `Documentation Format` section, the rule about replacing every `<placeholder>`, a reasoning nudge (e.g., "THINK HARD about what future readers need"), a skepticism directive (verify what was built by reading code, not just the spec), audience guidance (who the docs are for), a precision directive about `file:line` references, a performance directive about delegating heavy work to subagents, and a "why not what" focus directive. Aim for 8–10 bullets, each one imperative sentence. Bold or `IMPORTANT:`-prefix the load-bearing ones.>

- IMPORTANT: <Framing directive about the documentation being retrospective, not forward-looking.>
- <Directive about the output file path convention, including the filename pattern.>
- <Directive pointing to the `Documentation Format` section below.>
- IMPORTANT: <Directive about replacing every `<placeholder>` and omitting optional sections rather than leaving them empty.>
- <Reasoning/thinking directive.>
- <Skepticism directive — verify against code, not just the spec.>
- <Audience directive — name the two (or more) reader personas.>
- <Precision directive about `file:line` references.>
- <Context-window directive — when to delegate to subagents.>
- <"Why over what" focus directive.>

## Process

<Short lead-in sentence (optional) introducing the phased approach. The process is broken into three phases, each with a `###` sub-header and a numbered list of steps. Each numbered step has a bolded title and 2–4 sub-bullets describing concrete actions.>

### Phase 1: <Name of the context-gathering phase>

<Numbered list of 2–4 steps. Typical coverage: read the spec (if provided), read any existing contextual documentation that could be relevant or duplicated, examine auxiliary inputs like screenshots. Each step has a bolded title and sub-bullets of concrete actions.>

1. **<Step title — e.g., "Read the specification">** (if `<variable_name>` is provided):
   - <Concrete action>
   - <Concrete action>
   - <Concrete action>

2. **<Step title — e.g., "Read contextual docs">**:
   - <Concrete action>
   - <Concrete action>

3. **<Step title — e.g., "Examine screenshots">** (if `<variable_name>` is provided):
   - <Concrete action>
   - <Concrete action>

### Phase 2: <Name of the code-analysis phase>

<Numbered list of 2–4 steps covering: determining the scope of changes via git, reading the changed code (with a branching rule for small vs. large diffs), and identifying architecture decisions by comparing spec-vs-implementation. The large-diff branch should enumerate parallel subagent groupings.>

1. **<Step title — e.g., "Analyze the scope of changes">**:
   - <Concrete git command and what it reveals>
   - <Concrete git command and what it reveals>

2. **<Step title — e.g., "Understand the implementation">**:
   - <Rule for small diffs — a threshold and the action>
   - <Rule for large diffs — the threshold and the subagent-delegation action, followed by 2–4 indented bullets naming the parallel groups (e.g., Backend/API, Frontend/UI, Infrastructure/Config)>
   - <Per-file directive — what to extract from each changed file>

3. **<Step title — e.g., "Identify architecture decisions">**:
   - <Concrete action comparing spec to implementation>
   - <Concrete action noting deviations>
   - <Concrete action identifying patterns>

### Phase 3: <Name of the writing-and-finalization phase>

<Numbered list of 3–4 steps covering: handling any asset copying (screenshots), writing the documentation using the format section, updating any conditional/index documentation, and a final completeness-verification checklist.>

1. **<Step title — e.g., "Copy screenshots">** (if `<variable_name>` is provided):
   - <Concrete action — directory creation>
   - <Concrete action — file copy rule>
   - <Concrete action — reference path convention>

2. **<Step title — e.g., "Write the documentation">** using the `Documentation Format` below:
   - <Concrete directive about filling required sections>
   - <Concrete directive about omitting optional sections>
   - <Concrete directive about `file:line` references>
   - <Concrete directive about the overview's framing>

3. **<Step title — e.g., "Update conditional documentation">**:
   - <Concrete action — read the index file>
   - <Concrete action — add a new entry in the format specified below>
   - <Concrete action — describe what makes a useful entry>

4. **<Step title — e.g., "Verify completeness">**:
   - <Checklist item>
   - <Checklist item>
   - <Checklist item>
   - <Checklist item>

## Documentation Format

<Short lead-in (optional) describing what makes a good filled-in document: concrete content replacing every `<placeholder>`, optional sections either filled or removed entirely, `file:line` references in technical sections, and a narrative voice that addresses both audiences named in Instructions. The fenced block below is the template the command will produce.>

```md
# <Feature Title>

**Date:** <current date>
**Spec file:** <spec_path or "N/A">

## Overview

<2–3 sentence summary slot. Describe what belongs here: frame around the problem being solved, not just the changes; if a spec was provided, note whether the implementation matches it.>

## Screenshots

<OPTIONAL section marker — describe the condition under which this section is kept (assets directory provided and screenshots copied) vs. removed entirely.>

![<Description of what the screenshot shows>](assets/<screenshot-filename.png>)

## What Was Built

<List slot. Describe the shape: bulleted list grouped by functional area rather than by file, 2–6 bullets, each with a bolded area name and a short "what + why" description.>

- **<Functional area>**: <what it does and why>
- **<Functional area>**: <what it does and why>

## Architecture Decisions

<OPTIONAL section marker — describe when this section is kept (features with notable design choices) vs. removed (simple changes). Frame its value: most useful section for future developers.>

<Paragraph slot explaining what decisions and reasoning to capture here.>

- **<Decision>**: <what was chosen and why, with file:line reference>
- **<Decision>**: <what was chosen and why>

## Technical Implementation

### Key Files

<List slot. Describe the shape: the most important files a developer should read to understand the feature, each with a `file:line` entry point and a one-line role description.>

- `<file_path:line>`: <role this file plays in the feature>
- `<file_path:line>`: <role this file plays in the feature>

### How It Works

<Narrative slot. Describe what belongs here: a walk-through of the technical flow — how components interact, what happens when a user triggers the feature — written as prose a new developer can follow, with `file:line` references inline.>

### Dependencies Added

<OPTIONAL section marker — kept only if new packages/libraries were added, removed otherwise.>

- `<package_name>`: <what it's used for>

## How to Use

<Step-by-step slot from the user's perspective. Describe the shape: a numbered list of concrete usage steps.>

1. <Step 1>
2. <Step 2>

## Configuration

<OPTIONAL section marker — kept only if configuration options, environment variables, or settings exist.>

- `<VARIABLE_NAME>`: <what it controls, default value>

## Testing

<Short slot describing how to test the feature — commands to run and what to verify.>

## Notes

<OPTIONAL section marker — kept for additional context, known limitations, future considerations, or technical debt; removed if nothing notable.>
```

## Conditional Docs Entry Format

<Short lead-in describing the purpose of this section: after creating the documentation, the command must register it in an index file so future sessions know when to load it. The fenced block below is the entry template.>

```md
- docs/<your_documentation_file>.md
  - Context:
    - When working with <feature area>
    - When implementing <related functionality>
    - When troubleshooting <specific issues>
```

## Report

<Directive slot describing exactly what the command returns at the end of its run. Keep this tight — typically a single `IMPORTANT:` bullet naming the one thing to output (and nothing else).>

- IMPORTANT: <What to return — e.g., the path to the documentation file created, and nothing else.>
