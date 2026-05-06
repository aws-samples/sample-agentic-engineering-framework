---
description: <One-line description of what this prompt does. State that it reviews implemented work against a spec file with screenshots and emits a JSON report.>
---

# Review

<Opening framing paragraph (1–2 sentences). State that the prompt reviews work done against a specification file (`specs/*.md`) to ensure implemented features match requirements. It uses the spec to understand the requirements and the git diff (if available) to understand the changes. If the work has UI, it captures screenshots of critical paths. If there are issues, it reports them; if not, it reports success. Point the reader to the `Variables`, `Instructions`, `Process`, and `Report` sections.>

## Variables

<List each variable this prompt accepts, mapped to its positional argument. Include a derived path slot for the review image directory. Mark optional slots with a default or skip rule.>

task_id: $ARGUMENT
spec_file: $ARGUMENT
agent_name: $ARGUMENT <if provided, otherwise use a sensible default>
review_image_dir: `<absolute path to codebase>/agents/<task_id>/<agent_name>/review_img/`

## Instructions

<Bulleted list of hard rules the reviewer must follow. Preserve "IMPORTANT:" prefixes on rules that are easy to violate. Cover: the review-not-rebuild boundary, the report-but-don't-fix rule, the skeptical verification rule, the blocker-vs-cosmetic judgment call, when to fan out via parallel subagents for large diffs, and the output-purity rule (JSON only, no surrounding prose or markdown fences, ready for immediate `JSON.parse()`). 5–8 bullets.>

- IMPORTANT: <Review-not-rebuild boundary — document what you find; do NOT fix issues.>
- IMPORTANT: <Actionable reporting rule — report issues with actionable descriptions, but let a separate patch agent fix them.>
- <Reasoning directive — think hard about blocker vs. cosmetic.>
- <Skepticism directive — verify claims by reading the actual code changes, not just summaries.>
- <Scaling directive — when diff analysis exceeds ~200 lines, spawn parallel subagents to review separate areas and keep the main session small.>
- IMPORTANT: <Output-purity rule — the final response MUST be JSON only, matching the `Output Structure` schema, with NO surrounding prose or markdown fences. The output will be immediately parsed with `JSON.parse()`.>

### Issue Severity Guidelines

<Preamble sentence — every issue must be classified by impact. Think hard about user-facing vs. internal concerns. The severity labels below are load-bearing: downstream automation groups issues by these exact strings.>

| Severity     | Meaning                                                                                               |
|--------------|-------------------------------------------------------------------------------------------------------|
| `skippable`  | <Meaning — non-blocker for release, but still a problem worth documenting (e.g., minor UX inconsistency).> |
| `tech_debt`  | <Meaning — non-blocker for release, but creates technical debt that should be addressed in the future.>    |
| `blocker`    | <Meaning — blocks release; will harm the user experience or cause the feature to malfunction.>             |

<Closing paragraph — focus on user-visible, feature-critical issues; do not report issues that have no practical impact.>

## Setup

<IMPORTANT directive — if the work can be validated by UI validation, follow any project-specific setup file (e.g., a `prepare_app` command) to start local services and prepare test fixtures before reviewing UI-bearing work. Detect ports from environment files if available, or use documented defaults. The application URL will typically be `http://localhost:<PORT>`.>

## Process

<Short lead-in. The review proceeds in four phases.>

### Phase 1: <Name of the context-gathering phase>

<Numbered list of steps covering: reading the spec fully, understanding the diff (branch, stat, filenames), and reading conditional docs.>

1. **<Step title — e.g., read the spec>**:
   - <Sub-action — read the spec file in full to understand requirements>
   - <Sub-action — extract the review checklist: what was requested, what success looks like>
   - <Sub-action — if `spec_file` is missing, infer requirements from branch name or commit messages>

2. **<Step title — e.g., understand the diff>**:
   - <Sub-action — confirm the current branch>
   - <Sub-action — measure scope (files changed, lines added/removed) with `git diff <base branch> --stat`>
   - <Sub-action — list changed files with `git diff <base branch> --name-only`>

3. **<Step title — e.g., read conditional docs>**:
   - <Sub-action — read `.claude/commands/ai-implementation-docs.md` to discover supplementary documentation>
   - <Sub-action — if the feature area matches an entry, read those docs for architectural context>

### Phase 2: <Name of the code-review phase>

<Short lead-in — the goal: is what was built what was requested?>

1. **<Step title — e.g., for small diffs>** (< ~200 lines total):
   - <Sub-action — read changes directly using `git diff <base branch>`>
   - <Sub-action — map each change back to a spec requirement>

2. **<Step title — e.g., for large diffs>** (>= ~200 lines total):
   - <Sub-action — spawn parallel subagents to review different slices (backend/API, frontend/UI, infrastructure/config)>
   - <Sub-action — wait for all subagents to complete before proceeding>
   - <Sub-action — each subagent must return findings with `file:line` citations>

3. **<Step title — e.g., review checklist>** — for each spec requirement, verify:
   - <Check — Completeness: does the implementation cover all requirements?>
   - <Check — Correctness: does the implementation match the spec's described behavior?>
   - <Check — Integration: do the changes integrate cleanly with existing code?>
   - <Check — Quality: are the changes maintainable, readable, and following project conventions?>

### Phase 3: <Name of the visual-review phase>

<IMPORTANT — this phase applies ONLY if the feature has user-facing UI changes. If the work is backend-only or infrastructure-only, skip this phase entirely.>

1. **<Step title — e.g., find navigation guides>**:
   - <Sub-action — look for corresponding E2E test files in `.claude/commands/e2e/test_*.md` that mirror the feature name>
   - <Sub-action — use these files ONLY as navigation guides for screenshot locations, not as tests>

2. **<Step title — e.g., navigate and validate>**:
   - <Sub-action — open the application in a browser (using the URL from Setup)>
   - <Sub-action — walk the critical paths described in the spec>
   - <Sub-action — compare what you see against spec requirements>

3. **<Step title — e.g., capture screenshots>**:
   - <Sub-action — target 1–5 screenshots showcasing the new functionality>
   - <Naming convention — `01_<descriptive_name>.png`, `02_<descriptive_name>.png`, etc.>
   - <Sub-action — if you discover a visual issue, screenshot it and add it to `review_issues` with description, resolution, and severity>
   - <IMPORTANT directive — copy all screenshots to the provided `review_image_dir` using full absolute paths>

### Phase 4: <Name of the synthesis-and-report phase>

<Short lead-in — turn findings into the final structured output.>

1. **<Step title — e.g., compile findings>** — gather results from code review and visual review (if applicable)
2. **<Step title — e.g., classify issues>** — assign severity using the guidelines above
3. **<Step title — e.g., write the summary>** — 2–4 sentences in standup-meeting voice: what was built, whether it matches the spec
4. **<Step title — e.g., determine success>**:
   - <`success: true` if there are NO BLOCKING issues (can still have `skippable` or `tech_debt` issues)>
   - <`success: false` ONLY if there are BLOCKING issues>
5. **<Step title — e.g., emit the JSON>** — no markdown fences, no surrounding prose, just the JSON object

## Report

<Preamble — output contract rules for downstream automation. The invariants below are load-bearing: downstream automation parses these exact field names.>

- IMPORTANT: <Return results exclusively as a JSON object based on the `Output Structure` below. Do not include any additional text, explanations, or markdown formatting.>
- <Rule — `success` should be `true` if there are NO BLOCKING issues (implementation matches spec for critical functionality).>
- <Rule — `success` should be `false` ONLY if there are BLOCKING issues that prevent the work from being released.>
- <Rule — `review_issues` can contain issues of any severity (`skippable`, `tech_debt`, or `blocker`).>
- <Rule — `screenshots` should ALWAYS contain paths to screenshots showcasing the new functionality, regardless of success status. Use full absolute paths.>
- <Rationale — this allows subsequent agents to quickly identify and resolve blocking errors while documenting all issues.>

### Output Structure

<Preamble — the JSON must match the schema below exactly. The runner parses these exact field names: `success`, `review_summary`, `review_issues`, and `screenshots` are load-bearing. Every field inside `review_issues[]` is consumed by downstream automation.>

```json
{
    "success": "boolean - true if there are NO BLOCKING issues (can have skippable/tech_debt issues), false if there are BLOCKING issues",
    "review_summary": "string - 2-4 sentences describing what was built and whether it matches the spec. Written as if reporting during a standup meeting.",
    "review_issues": [
        {
            "review_issue_number": "number - the issue number based on the index of this issue",
            "screenshot_path": "string - /absolute/path/to/screenshot_that_shows_review_issue.png",
            "issue_description": "string - description of the issue",
            "issue_resolution": "string - description of the resolution",
            "issue_severity": "string - severity of the issue between 'skippable', 'tech_debt', 'blocker'"
        }
    ],
    "screenshots": [
        "string - /absolute/path/to/screenshot_showcasing_functionality.png",
        "string - /absolute/path/to/screenshot_showcasing_functionality.png"
    ]
}
```
