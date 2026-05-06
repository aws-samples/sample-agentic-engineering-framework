---
description: <One-line description of what this prompt produces and when to invoke it. Frame it as retrospective documentation generation from a git diff and (optionally) an originating spec.>
---

# Document Feature

<Opening framing paragraph (1–2 sentences). State that this prompt generates concise markdown documentation for an implemented feature by analyzing code changes and the originating specification, and that output lives under `ai_docs/`. Point the reader to the `Variables`, `Instructions`, `Process`, and `Documentation Format` sections below.>

## Variables

<List each variable this prompt accepts, mapped to positional arguments (`$1`, `$2`, ...). Include a short description of each, and flag optional slots explicitly.>

task_id: $1
spec_path: $2 <if provided, otherwise leave it blank>
documentation_screenshots_dir: $3 <if provided, otherwise leave it blank>

## Instructions

<Bulleted list of hard rules the documenter must follow. Preserve "IMPORTANT:" prefixes on rules that are easy to violate. Cover: retrospective-not-planning framing, output directory constraint (`ai_docs/` and nowhere else), screenshot directory constraint (`ai_docs/assets/`), filename convention, the `Documentation Format` contract, the placeholder-replacement rule, reasoning quality, skepticism (verify against code, not just the spec), audience (future devs + AI agents), `file:line` citation discipline, how to fan out for large diffs via parallel subagents, and the "why over what" framing. 10–12 bullets.>

- IMPORTANT: <Retrospective framing — this is documentation for work already done, not a forward plan.>
- IMPORTANT: <Output directory constraint — write the new documentation file inside `ai_docs/` and nowhere else.>
- <Screenshot directory constraint — `ai_docs/assets/`.>
- <Filename format rule — e.g., `feature-{task_id}-{descriptive-name}.md` with a short kebab-case name.>
- <Pointer to the `Documentation Format` below as the required shape.>
- IMPORTANT: <Placeholder-replacement rule — every `<placeholder>` must be replaced; omit optional sections rather than leaving them empty.>
- <Reasoning directive — think hard about what future readers need.>
- <Skepticism directive — verify what was built by reading code, not just the spec.>
- <Audience directive — future developers and AI agents researching the codebase.>
- <Citation directive — include specific `file:line` references in technical sections.>
- <Scaling directive — for large diffs, spawn parallel subagents by area (backend, frontend, infra) and synthesize.>
- <Framing directive — prioritize "why" (architecture decisions) over "what" (code summaries).>

## Process

<Short lead-in sentence describing the three-phase process. Then three `###` subsections, each with 2–4 numbered steps containing bolded titles and sub-bullets.>

### Phase 1: <Name of the context-gathering phase>

<Numbered list of steps to gather context before analyzing code. Typical steps: read the originating spec (if provided), consult the ai-implementation-docs index, and examine any provided screenshot directory.>

1. **<Step title — e.g., read the specification>** (if `spec_path` is provided):
   - <Sub-action — read the spec to understand original requirements>
   - <Sub-action — note success criteria>

2. **<Step title — e.g., read contextual docs>**:
   - <Sub-action — read the ai-implementation-docs index at `.claude/commands/ai-implementation-docs.md`>
   - <Sub-action — if the feature area matches an entry, read those docs for architectural context>

3. **<Step title — e.g., examine screenshots>** (if `documentation_screenshots_dir` is provided):
   - <Sub-action — list and examine screenshots in the provided directory>
   - <Sub-action — use visual context to describe UI changes>

### Phase 2: <Name of the code-analysis phase>

<Numbered list of steps to understand what was actually built. Typical steps: scope the changes via git diff, read the implementation (directly for small diffs, via parallel subagents for large ones), and identify architecture decisions.>

1. **<Step title — e.g., analyze the scope of changes>**:
   - <Sub-action — get a stat summary of files changed against the base branch>
   - <Sub-action — list the changed files>

2. **<Step title — e.g., understand the implementation>**:
   - <Sub-action — for small diffs, read the changes directly>
   - <Sub-action — for large diffs, spawn parallel subagents by area (backend/API, frontend/UI, infrastructure/config)>
   - <Sub-action — for each changed file, extract what it does, why it changed, and how it connects>

3. **<Step title — e.g., identify architecture decisions>**:
   - <Sub-action — compare spec to implementation and note divergences>
   - <Sub-action — look for patterns in data flow, component structure, error handling>
   - <Sub-action — identify non-obvious choices and the reasoning behind them>

### Phase 3: <Name of the writing-and-finalization phase>

<Numbered list of steps to produce the documentation artifact, update the ai-implementation-docs registry, and verify completeness.>

1. **<Step title — e.g., copy screenshots>** (if `documentation_screenshots_dir` is provided):
   - <Sub-action — create `ai_docs/assets/` if it doesn't exist>
   - <Sub-action — copy all screenshots preserving original filenames>

2. **<Step title — e.g., write the documentation>** using the `Documentation Format` below:
   - <Sub-action — fill all required sections with concrete content>
   - <Sub-action — omit optional sections entirely when not applicable (no empty placeholders)>
   - <Sub-action — use `file:line` references in technical sections>
   - <Sub-action — frame overview around the problem being solved, not just the changes>

3. **<Step title — e.g., update conditional documentation>**:
   - <Sub-action — read `.claude/commands/ai-implementation-docs.md`>
   - <Sub-action — add an entry for the new doc file using the `Conditional Docs Entry Format` below>
   - <Sub-action — make the entry actionable — when should a future dev or agent read this doc>

4. **<Step title — e.g., verify completeness>**:
   - <Check — all `<placeholder>` tags replaced>
   - <Check — all `file:line` references accurate>
   - <Check — screenshots referenced via correct relative paths under `assets/`>
   - <Check — optional sections filled or removed entirely>

## Documentation Format

<Preamble sentence stating this is the required shape for the generated doc. Mention that it addresses both human developers and AI agents, and that optional sections must be filled with concrete content or removed entirely — never left empty.>

```md
# <Feature Title>

**Task ID:** <task_id>
**Date:** <current date>
**Spec file:** <spec_path or "N/A">

## Overview

<2–3 sentence summary. Frame around the problem being solved, not just the changes. If a spec was provided, note whether the implementation matches it or diverged (and why).>

## Screenshots

<OPTIONAL section — keep only if `documentation_screenshots_dir` was provided and screenshots were copied; otherwise remove entirely.>

![<Description of what the screenshot shows>](assets/<screenshot-filename.png>)

## What Was Built

<Bulleted list grouped by functional area (not by file), 2–6 bullets, each with a bolded area name and a short "what + why" description.>

- **<Functional area>**: <what it does and why>
- **<Functional area>**: <what it does and why>

## Architecture Decisions

<OPTIONAL section — keep only for features with notable design choices; remove for simple changes. Document the non-obvious choices and why this approach over alternatives, each with a `file:line` reference.>

- **<Decision>**: <what was chosen and why, with file:line reference>
- **<Decision>**: <what was chosen and why>

## Technical Implementation

### Key Files

<List the most important files a developer should read to understand the feature, each with a `file:line` entry point and a one-line role description.>

- `<file_path:line>`: <role this file plays in the feature>
- `<file_path:line>`: <role this file plays in the feature>

### How It Works

<Narrative walk-through of the technical flow — how components interact, what happens when a user triggers the feature — written as prose a new developer can follow, with inline `file:line` references.>

### Dependencies Added

<OPTIONAL section — keep only if new packages or libraries were added; remove otherwise.>

- `<package_name>`: <what it's used for>

## How to Use

<Numbered, step-by-step instructions from the user's perspective.>

1. <Step 1>
2. <Step 2>

## Configuration

<OPTIONAL section — keep only if configuration options, environment variables, or settings exist; remove otherwise.>

- `<VARIABLE_NAME>`: <what it controls, default value>

## Testing

<Brief description of how to test the feature — commands to run and what to verify.>

## Notes

<OPTIONAL section — keep for additional context, known limitations, future considerations, or technical debt; remove if nothing notable.>
```

## Conditional Docs Entry Format

<Short preamble: after creating the documentation, add this entry to `.claude/commands/ai-implementation-docs.md` in the `## Entries` section.>

```md
- ai_docs/<your_documentation_file>.md
  - Context:
    - When working with `<feature area>`
    - When implementing `<related functionality>`
    - When troubleshooting `<specific issues>`
```

## Report

- IMPORTANT: <State the exact return contract — typically, return only the path to the documentation file created and nothing else.>
