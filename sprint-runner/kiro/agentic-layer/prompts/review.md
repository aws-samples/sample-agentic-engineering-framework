---
description: <One-line description of the review prompt. State that it verifies implemented work against a specification and returns structured findings.>
---

# Review

<Opening paragraph (2–3 sentences). Describe what this prompt does: compare implementation against a specification, validate behavior where relevant (including UI if applicable), capture evidence, and emit a structured report. Frame the scope: review, not rebuild.>

## Variables

<List each input variable the prompt accepts, one per line, in `name: <description of value>` form. Include positional args (`$1`, `$2`, ...), defaults for optional inputs, and any derived paths the prompt will compute. Typical entries: the spec file path, an agent identifier, and a directory for review artifacts. 3–5 variables.>

spec_file: <What the first positional argument should point to>
agent_name: <Fallback rule when the second positional argument is omitted>
review_image_dir: <Template for the absolute path where review artifacts will be written>

## Instructions

<Bulleted list of the non-negotiable rules for the reviewer. Bold or prefix with "IMPORTANT:" any rule the model tends to violate (reviewing vs. testing, reviewing vs. implementing, trusting diffs blindly, leaking prose around a JSON response). Include a reasoning nudge ("THINK HARD", "ultrathink") for the judgment-heavy steps. 5–7 bullets.>

- IMPORTANT: <Scope boundary 1 — e.g., what the reviewer is doing vs. what they are NOT doing>
- IMPORTANT: <Scope boundary 2 — e.g., document issues, don't fix them>
- <Reasoning directive — when to slow down and think deeply>
- <Skepticism directive — how to verify claims rather than trust summaries>
- <Context-protection directive — when to delegate to subagents>
- <Output-purity directive — what the final response must and must not contain>

### Issue Severity Guidelines

<Lead-in sentence stating that every issue must be classified by impact. Follow with a severity table: three rows is typical, columns are `Severity` and `Meaning`. Fill each row with a `<code-style severity name>` and a one-line rule describing when it applies (blocking vs. non-blocking, user-impact vs. internal concern). End with a one-line reminder that non-critical issues should not be reported at all.>

| Severity    | Meaning                                                                                       |
|-------------|-----------------------------------------------------------------------------------------------|
| `<severity-name>`   | <When this severity applies — include whether it blocks release>                      |
| `<severity-name>` | <When this severity applies>                                                                |
| `<severity-name>` | <When this severity applies>                                                                |

<One-line reminder that focuses the reviewer on user-visible, feature-critical issues.>

## Setup

<Describe any preparation the reviewer must perform before starting the review (starting the app, loading fixtures, reading a setup command file). Include IMPORTANT callouts for setup steps that must actually be executed rather than skimmed. Note any environment specifics the reviewer should detect (ports, worktree conventions, URL templates).>

- <Setup step — e.g., read and execute a preparation command file>
- <Environment detail — e.g., how ports or URLs are resolved>
- <Environment detail — e.g., default values when environment files are absent>

## Process

<Short lead-in (1 sentence) stating that the review proceeds in phases. The phases below are fixed — do not add or remove them.>

### Phase 1: Context Gathering

<Numbered list of 2–4 steps for loading all relevant context into the main window before any reviewing happens. Each step has a bolded title and 2–4 sub-bullets describing concrete actions. Typical steps: read the spec fully, inspect the branch/diff scope, read conditional docs that apply to the feature area.>

1. **<Step title — e.g., read the spec>**:
   - <Concrete action involving the spec file>
   - <Fallback behavior when an input is missing>
   - <What to extract from the spec — the review checklist>

2. **<Step title — e.g., understand the diff>**:
   - <Git command to confirm branch>
   - <Git command to measure scope>
   - <Git command to list changed files>

3. **<Step title — e.g., read conditional docs>**:
   - <Where conditional docs live>
   - <Rule for when to read them>

### Phase 2: Code Review

<Lead-in sentence stating the review goal as a question (e.g., "is what was built what was requested?"). Then a numbered list with 3 items: small-diff handling, large-diff handling with parallel subagents, and a review checklist. Use bolded titles for each numbered item.>

1. **<Small-diff handling label>** (<threshold>):
   - <How to read changes directly>
   - <How to map each change back to a spec requirement>

2. **<Large-diff handling label>** (<threshold>):
   - <Directive to spawn parallel subagents, with 2–4 suggested review slices, each a bolded label followed by what it covers:>
     - **<Slice 1 label>**: <What this subagent reviews>
     - **<Slice 2 label>**: <What this subagent reviews>
     - **<Slice 3 label>**: <What this subagent reviews>
   - <Synchronization rule — wait for all subagents before proceeding>
   - <What each subagent must return, with `file:line` citation requirement>

3. **<Review checklist label>** — <for each spec requirement, verify:>
   - **<Dimension 1>**: <One-line check>
   - **<Dimension 2>**: <One-line check>
   - **<Dimension 3>**: <One-line check>
   - **<Dimension 4>**: <One-line check>

### Phase 3: Visual Review

<Opening IMPORTANT callout stating the conditions under which this phase runs and when to skip it entirely. Then a numbered list of 3 steps for navigating the app, validating against the spec, and capturing screenshots. Each step has a bolded title and 2–4 sub-bullets.>

IMPORTANT: <Rule for when this phase applies vs. when to skip>.

1. **<Step title — e.g., find navigation guides>**:
   - <Where to look for navigation references>
   - <How to use them — as guides, not as tests>

2. **<Step title — e.g., navigate and validate>**:
   - <How to open the app>
   - <What paths to walk>
   - <What comparison to make>

3. **<Step title — e.g., capture screenshots>**:
   - <Target count of screenshots and what they should cover>
   - <Naming convention>
   - <Rule for handling visual issues discovered during capture>
   - <Where screenshots are stored and the path format>

### Phase 4: Synthesis & Report

<Numbered list of 4–6 steps for turning findings into the final structured output. Each step is one line. Typical steps: compile findings, classify issues, write the summary in a specific voice, determine the success flag with explicit rules, emit the JSON with no surrounding prose.>

1. **<Step — e.g., compile findings>** — <Where findings come from>
2. **<Step — e.g., classify issues>** — <Using the severity guidelines>
3. **<Step — e.g., write the summary>** — <Length and voice>
4. **<Step — e.g., determine success>**:
   - <Rule that makes success true>
   - <Rule that makes success false>
5. **<Step — e.g., emit the JSON>** — <Purity rule>

## Report

<Bulleted list of output-contract rules. Bold or IMPORTANT-tag the rules most often violated (output must be JSON only, success flag semantics, screenshot inclusion even on success, absolute paths). Close with a rationale bullet explaining why this contract matters to downstream automation.>

- IMPORTANT: <Output-purity rule — JSON only, matching the structure below>
- <Success-flag rule for the passing case>
- <Success-flag rule for the failing case>
- <What the issues array may contain>
- <Rule for screenshots — always included, absolute paths>
- <Rationale — how downstream agents consume this output>

### Output Structure

<Lead-in sentence stating that the JSON must match the schema below exactly. A good template has: a top-level boolean flag, a short human-readable summary string, an array of issue objects (each with id, screenshot reference, description, resolution, severity), and a separate array of showcase screenshot paths. Describe field semantics inline as string values.>

```json
{
    "<success-flag-key>": "<type — semantics of true vs. false>",
    "<summary-key>": "<type — length, voice, what it describes>",
    "<issues-array-key>": [
        {
            "<issue-id-key>": "<type — how the id is derived>",
            "<issue-screenshot-key>": "<type — absolute path format>",
            "<issue-description-key>": "<type — what to describe>",
            "<issue-resolution-key>": "<type — what guidance to provide>",
            "<issue-severity-key>": "<type — enumerated severity values>"
        }
    ],
    "<screenshots-array-key>": [
        "<type — absolute path to a screenshot showcasing functionality>"
    ]
}
```
