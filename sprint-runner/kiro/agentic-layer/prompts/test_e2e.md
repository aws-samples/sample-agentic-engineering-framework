# E2E Test Runner

<Opening statement (1–2 sentences) declaring what this prompt does. State that the agent executes end-to-end tests through a specific browser-automation mechanism (e.g., Playwright MCP) and that failures must be surfaced explicitly with the exact step that broke. Keep the tone imperative.>

## Variables

<List each input variable the prompt consumes, one per line, in the form `variable_name: <description of how the value is resolved>`. Include any `$ARGUMENT` fallbacks, environment-file lookups, or default values. Typical slots are an agent name, the test file path, and the target application URL. Describe the resolution order for each slot, not concrete values.>

- `<variable_name>: $ARGUMENT if provided, otherwise <fallback description>`
- `<variable_name>: $ARGUMENT` — <what this input is used for>
- `<variable_name>: $ARGUMENT if provided, otherwise determine from <source>:`
  - <first fallback rule>
  - <second fallback rule>

## Instructions

<Bulleted list of imperative instructions the agent follows on every run. Mirror the original shape: resolve any missing variables first, then read the test file, then execute steps, then evaluate outcomes, then emit the output. Include "IMPORTANT:" prefixes for non-negotiable items (output format, step ordering, screenshot handling). Include a "Ultra think" or equivalent reasoning nudge before the execution step. Aim for 10–18 bullets, one imperative per bullet. Use `<angle-bracket>` slots for any names that refer to other sections (e.g., `<section that lists the test steps>`), file paths, URLs, or tool names the filler must supply.>

- <Instruction to resolve missing variables against their documented fallbacks>
- <Instruction to read the `<test file variable>`>
- <Instruction to digest the narrative/context section so the agent knows what is being validated>
- IMPORTANT: <Instruction to execute the ordered steps section using the designated automation tool>
- <Instruction to evaluate the success-criteria section and fail-fast with an explanation when any criterion is not met>
- <Instruction to evaluate any inline verification steps and fail-fast on those too>
- <Instruction about capturing screenshots at the points specified in the test file>
- IMPORTANT: <Instruction to return results using the shape defined in the Output Format section>
- <Instruction about browser launch mode (e.g., headed vs. headless) and why>
- <Instruction to use the resolved application URL consistently>
- <Instruction to allow time for async operations and element visibility>
- IMPORTANT: <Instruction about where each screenshot must be saved, using absolute paths, and how to name them>
- <Instruction to capture and report any unexpected errors>
- Ultra think about <what needs careful reasoning, e.g., the ordered test steps> and execute them in order
- <Instruction to mark the test failed immediately on any error and report which step failed, with a concrete example string such as `'(Step <N>) Failed to <action> on <target>'`>
- <Instruction to resolve the absolute codebase path (e.g., via `pwd`) so screenshot paths are correct>

## Setup

<Numbered list of environmental preconditions the agent must establish before driving the browser. Keep the original three-item shape: (1) required tools and a "do not improvise a fallback" rule, (2) dev-server pre-warm procedure with a port-check + background-start + polling loop, (3) optional supplementary command file to read. Use `<angle-bracket>` slots for tool names, ports, URLs, log paths, and timeouts. Preserve the STOP-and-report directive when required tooling is missing.>

1. **Required tools**: <Name the required browser-automation mechanism and state that the agent must use its tools directly. Call out the specific anti-pattern to avoid (e.g., writing a standalone script and shelling out). Explain briefly why the required path is preferred. Close with: if the required tools are missing, STOP and report an environmental error; do not fall back to improvising.>

2. **Pre-warm the dev server** before driving any browser:
   - <Rule for when nothing is listening on the target port: how to start the server in the background, where to write logs, which endpoint to poll, what response codes count as "up", and the maximum wait time>
   - <Rule for when something IS already listening on the target port: reuse it, do NOT restart>
   - <Rule for priming the first page compile (e.g., a warm-up GET on `/`) so the first navigation is fast>

3. <Optional-file instruction: read `<path to optional prep file>` if it exists; skip silently if absent rather than erroring.>

## Screenshot Directory

<Describe the canonical on-disk location where screenshots must be written. Provide the path as a single-line template using `<angle-bracket>` slots for the codebase root, run identifier, agent name, and a per-test subdirectory derived from the test file name. End with the `*.png` glob.>

<absolute path to codebase>/<fixed subpath>/<run_id>/<agent_name>/<img subdir>/<per-test directory>/*.png

<Short prose block (3–5 bullets or sentences) explaining the naming convention and why the directory structure is shaped this way. Cover: descriptive per-screenshot names, grouping by run ID, grouping by agent name with 1–2 example agent-name shapes in `<angle brackets>`, and grouping by a per-test subdirectory derived from the test file name with an example mapping in `<angle brackets>`.>

## Report

<Bulleted list of output-time rules. Cover: return only the structured output described below, capture unexpected errors, and confirm all screenshots landed in the Screenshot Directory. Use "IMPORTANT:" on the non-negotiable items.>

- <Directive to return only the structured output specified in the test file>
- <Directive to capture any unexpected errors>
- IMPORTANT: <Directive to ensure every screenshot is saved under the Screenshot Directory>

### Output Format

<Short lead-in describing what makes a good example here: a minimal JSON object with a stable set of keys (test name, pass/fail status, array of absolute screenshot paths, optional error field). Then provide the fenced JSON block below. Keep the ```json fence and the overall shape; replace concrete values with `<angle-bracket>` slots. Include 2–4 example screenshot-path entries so callers can see the numbered-prefix naming convention.>

```json
{
  "test_name": "<Test Name Here>",
  "status": "<passed|failed>",
  "screenshots": [
    "<absolute path to codebase>/<fixed subpath>/<run_id>/<agent_name>/<img subdir>/<test name>/01_<descriptive name>.png",
    "<absolute path to codebase>/<fixed subpath>/<run_id>/<agent_name>/<img subdir>/<test name>/02_<descriptive name>.png",
    "<absolute path to codebase>/<fixed subpath>/<run_id>/<agent_name>/<img subdir>/<test name>/03_<descriptive name>.png"
  ],
  "error": "<null when passed, otherwise a short failure description that names the failing step>"
}
```
