---
description: <One-line description of what this prompt does. State that it researches a feature and produces a pipeline-ready state file with specs, ready for `/pipeline-build`.>
model: <Model selector — typically a reasoning-capable model such as "opus" or "inherit".>
---

# Pipeline Plan

<Opening framing paragraph (1–2 sentences). State that this prompt is the planning pipeline orchestrator: it coordinates a researcher and a planner, then generates a pipeline state JSON file ready for `/pipeline-build`. Point the reader to the `Variables`, `Instructions`, `Process`, and `Rules` sections below.>

## Variables

<List each variable this prompt accepts, mapped to its positional argument. Typical: a single slot that accepts either plain text or a path to a markdown/text file.>

feature_input: $ARGUMENTS <(plain text description OR path to a .md/.txt file)>

## Instructions

<Bulleted list of top-level directives. Cover: the sequential two-subagent coordination (researcher first, then planner), the no-writing rule (this prompt does not write research or specs itself), the state-file generation responsibility, and the contract role of the state file between planning and execution.>

- <Directive — coordinate 2 subagents sequentially: researcher first, then planner.>
- <Directive — do NOT write research docs or specs yourself; subagents handle that.>
- <Directive — after both subagents finish, YOU generate the pipeline state JSON.>
- <Directive — the state file is the contract between planning and execution.>

## Process

### Step 1: <Resolve Input>

<Numbered list describing how the input is resolved into a usable feature description and a `<feature-name>` slug.>

1. <Action — if `$ARGUMENTS` is a file path (ends in `.md`/`.txt`), read the file to extract the feature details.>
2. <Action — if `$ARGUMENTS` is plain text, use it directly as the feature description.>
3. <Action — if empty, ask the user to provide the feature description.>
4. <Action — determine a `<feature-name>` slug in kebab-case.>

### Step 2: <Launch Researcher>

<Describe the researcher launch. Name the agent and path concretely; everything around them is meta-described.>

Spawn the **pipeline-researcher** agent (`.claude/agents/pipeline/pipeline-researcher.md`) with:
- <Input to pass — the full feature description.>
- <Input to pass — the feature-name slug (used for the output filename: `research/YYYY-MM-DD-<feature-name>.md`).>

<Short paragraph summarizing what the researcher does — reads key project files (entry doc, ai-implementation-docs), decomposes research, spawns codebase-locator / codebase-analyzer / codebase-pattern-finder in parallel, synthesizes findings, and returns the path to the research document.>

<Directive — wait for completion. Read the research document to verify it is substantive (has findings and file references, not just placeholders).>

### Step 3: <Launch Planner>

<Describe the planner launch. Provide a fenced block with the structured context the planner receives — the context template below is the required shape; every angle-bracket slot is replaced with concrete content at call time.>

Spawn the **pipeline-planner** agent (`.claude/agents/pipeline/pipeline-planner.md`) with the following context:

```
## Context
<Short paragraph establishing the planner's role: it has a research document analyzing the codebase for the feature; its job is to read the research, validate findings, decompose the work into specs, and write them.>

## Feature
<feature description>

## Research Document
<path to research document from Step 2>

## Output Directory
specs/<feature-name>/

## Instructions

1. **<Step title — e.g., read the research document thoroughly>** — <short description: understand what exists, the patterns, integration points, and risks.>

2. **<Step title — e.g., validate assumptions>** — <short description: spawn codebase-locator / codebase-analyzer / codebase-pattern-finder as needed to verify key assumptions from the research. Check referenced files, patterns, and integration points. Go deeper on anything flagged.>

3. **<Step title — e.g., decide decomposition>** — <short description: based on validated research, determine how many specs are needed; single spec for small features, otherwise break into small, independently buildable and testable changes; order specs so each depends only on prior ones; Spec 1 has zero dependencies on new code from other specs.>

4. **<Step title — e.g., write all specs>** — for each work item, create a spec file at:
   `specs/<feature-name>/task-<feature-name>-<order+1>-<descriptive-name>.md`

   <Short paragraph listing the required Plan Format sections the spec must include (metadata, overview, current state analysis, desired end state, out-of-scope, implementation approach, relevant files with file:line, user stories, phased implementation with changes required / code blocks / success criteria, testing strategy, acceptance criteria, validation commands, references, notes). Close with the placeholder-replacement rule and the no-open-questions rule.>

5. **<Step title — e.g., report>** — return:
   - <Item — the list of spec files created, in build order>
   - <Item — a one-line description of each spec>
   - <Item — any decisions made about decomposition and why>
```

<Directive — wait for completion. Verify the planner's output: all spec files exist in `specs/<feature-name>/`, no `<placeholder>` values remain, `file:line` references are present. If incomplete, send the planner back with specific feedback (max 1 retry).>

### Step 4: <Generate State File>

<Describe the state-file generation after both subagents finish and specs are verified. List the steps for enumerating specs, extracting ID/title, hashing file contents, assigning build-order, and writing the state file.>

1. <Action — list all `.md` files in `specs/<feature-name>/`.>
2. <Action — for each spec file: extract ID from filename, extract title from the first `#` heading, compute sha256 (first 8 chars) of file contents, assign `order` based on the planner's build order.>
3. <Action — write the state file to `specs/<feature-name>/pipeline-state.json` using the v2.0 schema below.>

<Preamble — the v2.0 schema below is consumed by `sprint_runner.py`. Field names, nesting, and phase keys are load-bearing and MUST stay concrete.>

```json
{
  "version": "2.0",
  "created_at": "<ISO timestamp>",
  "updated_at": "<ISO timestamp>",
  "project": {
    "root": "<absolute path to git project root>",
    "name": "<project directory name>"
  },
  "pipeline": {
    "status": "pending",
    "started_at": null,
    "completed_at": null,
    "current_item_index": null,
    "current_phase": null,
    "total_items": "<number of items>",
    "completed_items": 0,
    "failed_items": 0,
    "error": null
  },
  "source": {
    "type": "pipeline-plan",
    "input": "<original feature_input>",
    "research_path": "<absolute path to research document>",
    "specs_dir": "<absolute path to specs/<feature-name>/>"
  },
  "items": [
    {
      "id": "<task_id>",
      "title": "<spec title>",
      "status": "pending",
      "order": 0,
      "spec": {
        "path": "<absolute path to spec .md file>",
        "hash": "<first 8 chars sha256>"
      },
      "branch": null,
      "phases": {
        "build": { "status": "pending", "started_at": null, "completed_at": null, "output": null, "duration_seconds": null, "attempt": 0, "error": null },
        "test": { "status": "pending", "started_at": null, "completed_at": null, "output": null, "duration_seconds": null, "attempt": 0, "error": null, "all_passed": null },
        "review": { "status": "pending", "started_at": null, "completed_at": null, "output": null, "duration_seconds": null, "attempt": 0, "error": null, "verdict": null },
        "document": { "status": "pending", "started_at": null, "completed_at": null, "output": null, "duration_seconds": null, "attempt": 0, "error": null },
        "commit": { "status": "pending", "started_at": null, "completed_at": null, "sha": null, "message": null, "error": null }
      },
      "healing": {
        "test_fix_cycles": 0,
        "test_fix_max": 3,
        "review_fix_cycles": 0,
        "review_fix_max": 2,
        "patches": []
      },
      "started_at": null,
      "completed_at": null,
      "error": null
    }
  ]
}
```

### Step 5: <Report>

<Preamble sentence. Return a summary matching the structured shape below, and include the driver-contract marker lines described immediately after it. The sprint driver (`tools/sprint_runner.py`) greps the response for `SPEC_PATH:` and `E2E_PATH:` lines — each must appear on its own line, prefixed by the marker keyword, one marker line per spec file created. Omit this block and the driver cannot advance to the build stage.>

```markdown
## Pipeline Plan Complete

### Feature
<feature description>

### Research
<path to research document>

### Specs Created
| # | ID | Title | Spec Path |
|---|-----|-------|-----------|
| 1 | ... | ...   | ...       |

### State File
<path to pipeline-state.json>

### Next Step
Run `/pipeline-build <path to pipeline-state.json>` to execute the build pipeline.
```

Then, on their own lines, emit the driver-contract markers:

```
SPEC_PATH: <absolute path to the spec file created for item 1>
SPEC_PATH: <absolute path to the spec file created for item 2>
E2E_PATH: <absolute path to the e2e test file created under .claude/commands/e2e/>
```

Emit one `SPEC_PATH:` line per spec file created. Emit one `E2E_PATH:` line per e2e test file created. If no e2e file applies, omit the `E2E_PATH:` line.

## Rules

<Bulleted list of hard rules reinforcing the orchestrator role. Cover: coordinator-only role, no research/specs authoring, subagent-output verification, absolute-path requirement, JSON validity, no implementation, and no branch creation (that's `/pipeline-build`'s job).>

- <Rule — coordinator only: launch 2 subagents sequentially, then generate the state file.>
- <Rule — do NOT write research docs; the researcher handles that.>
- <Rule — do NOT write specs; the planner handles that.>
- <Rule — DO verify subagent outputs are complete before proceeding.>
- <Rule — all paths in the state file must be absolute.>
- <Rule — the state file must be valid JSON parseable by `JSON.parse()`.>
- <Rule — do NOT implement any code; only coordinate, verify, and generate state.>
- <Rule — do NOT create branches or worktrees; that is `/pipeline-build`'s job.>
