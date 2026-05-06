---
description: <One-line description of what this prompt does. State that it researches the codebase for a specific task and produces a structured research report.>
---

# Codebase Research

<Opening framing paragraph (1–2 sentences). State the role: the prompt is a codebase researcher that explores the project thoroughly and produces a structured research report. Point the reader to the `Instructions`, `Output Format`, and `Rules` sections.>

## Task

$ARGUMENTS

## Instructions

<Numbered list of the exploration steps the researcher follows. Typical steps: explore the project structure, read relevant source/config/test/doc files, search for patterns and conventions, identify dependencies and integration points, and emit the output in the required format.>

1. <Step — explore the project structure using directory/tree tools.>
2. <Step — read relevant source files, configs, tests, and docs.>
3. <Step — search for patterns, conventions, and naming standards.>
4. <Step — identify dependencies, potential conflicts, and integration points.>
5. <Step — emit the research report in the `Output Format` below.>

## Output Format

<Preamble sentence stating the researcher's entire response must match the markdown skeleton below.>

```markdown
# Research Report: <task title>

## Project Overview
<Stack, frameworks, language. Entry points and main files.>
- <Detail>
- <Detail>

## Relevant Files
<For each relevant file, one bullet:>
- `<path/to/file>` — <what it does, why it matters for this task>

## Architecture & Patterns
<How the codebase is structured, conventions used (naming, error handling, logging), and patterns to follow when adding new code.>
- <Structural observation>
- <Convention>
- <Pattern to follow>

## Integration Points
<Where the new work connects to existing code; existing functions/classes to use or extend; import patterns.>
- <Integration point>
- <Function/class to reuse>
- <Import pattern>

## Dependencies
<External packages relevant to this task; internal module dependencies.>
- <External package>
- <Internal module>

## Risks & Gotchas
<Potential conflicts or breaking changes; edge cases to consider; known quirks or limitations.>
- <Risk>
- <Edge case>
- <Quirk>

## Suggested Approach
<Brief recommendation based on what was found; key decisions the planner should consider.>
- <Recommendation>
- <Key decision>
```

## Rules

<Bulleted list of hard rules the researcher must follow. Cover: thoroughness (the planner depends on this report), concrete `file:line` references, surfacing surprising or non-obvious findings, and explicit uncertainty when something is unclear.>

- <Rule — be thorough; the planner depends entirely on this report.>
- <Rule — reference specific files and line numbers.>
- <Rule — note things that are surprising or non-obvious.>
- <Rule — if something is unclear, say so explicitly.>
