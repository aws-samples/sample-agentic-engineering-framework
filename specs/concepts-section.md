Good. I now have a thorough understanding of the entire codebase -- the design system (colors, fonts, components, animations), the framework philosophy, pipeline architecture, glossary terms, and open questions. Let me now produce the complete spec.

---

Here is the full detailed page spec for the Concepts section. Since I cannot create the file at `/Users/alejtr/Documents/obsidian/obsidian/agentic-layer-framework/website/specs/concepts-section.md`, I am delivering it in full below for you to save.

---

# Concepts Section -- Page Spec

> **Target directory:** `/website/specs/concepts-section.md`
> **Audience for this spec:** One frontend developer and one tech content writer.
> **Design system source of truth:** `/website/index.html` (Tailwind config, CSS custom styles, component patterns).

---

## Global Design Notes (apply to every page)

### Layout shell
Every concept page uses a shared layout:
- Fixed top nav (same as `index.html` -- void/80 backdrop-blur, same links, AEF logo).
- Page hero area: small section with `uppercase font-mono text-glow tracking-wider` label, large `text-4xl sm:text-5xl font-bold` heading, `text-secondary text-lg` subtitle.
- Content sections separated by `border-t border-subtle` with `py-24 sm:py-32` spacing.
- Ambient glow blobs (`ambient-glow` class) placed sparingly per page.
- Dot grid background on hero only.
- Footer identical to `index.html`.
- `reveal` class on all content blocks for scroll-triggered fade-in.
- Sidebar TOC on large screens (sticky, left column) listing all H2 headings on the page with active-state highlighting.

### Shared component patterns (from index.html)
- **Cards:** `rounded-xl bg-surface border border-subtle hover:border-glow-faint hover:bg-raised transition-all duration-250` with `p-6 lg:p-8`.
- **Code blocks:** `code-block` class (void bg, subtle border, 8px radius). Syntax colors: `.var` indigo, `.keyword` purple, `.string` emerald, `.comment` muted, `.type` cyan.
- **Permission badges:** `.perm-allowed` (green) and `.perm-denied` (red) with `px-2 py-0.5 text-[10px] font-mono rounded`.
- **Phase color dots:** `w-2.5 h-2.5 rounded-full bg-{phase} shadow-[0_0_8px_rgba(...)]`.
- **Label badges:** `px-2 py-0.5 text-[10px] font-mono rounded bg-{color}/10 text-{color} border border-{color}/20`.
- **Step connector:** `step-connector` class (2px wide, gradient from glow to subtle).

### Breadcrumb + concept nav
Each page has a horizontal breadcrumb (`Home > Concepts > Page Title`) and a bottom navigation strip linking prev/next concept page.

### Cross-link convention
In-page links to other concept pages use a styled inline link: `text-glow hover:text-glow-hover underline underline-offset-4 decoration-glow/30`.
Links to pipeline phases use the phase color.

---

## Page 1: `/concepts/agentic-layer`

### Title
**The Agentic Layer**

### Purpose
Explain the foundational idea that the agentic layer -- not the source code -- is the primary artifact teams build and maintain. This is the single most important concept in the framework and must click for every reader.

### Content Outline

#### H2: What Is the Agentic Layer?
- **Opening paragraph:** The agentic layer is the configuration surface that sits between your team and your codebase. It contains everything an AI agent needs to do engineering work autonomously: prompt templates that define behavior, tool configurations that grant capabilities, quality gates that enforce standards, and pipeline definitions that orchestrate phases.
- **Key distinction:** The agentic layer is not code that runs. It is configuration that governs how code gets written. Think of it as the engineering playbook that agents follow.
- **Bullet list -- what it contains:**
  - Prompt templates (one per phase, versioned like code)
  - Tool configurations (which capabilities each phase can access)
  - Quality gates (pass/fail criteria per phase)
  - Pipeline definitions (phase ordering, loop limits, escalation rules)
  - Custom commands and skills (reusable prompt+tool bundles)

#### H2: The Three-Layer Architecture
- Full explanation of the three-layer diagram already teased on the landing page. Each layer gets its own subsection:

##### H3: Layer 1 -- Agentic Layer (Humans Collaborate Here)
- This is where your team spends its time.
- Contains: prompt templates, tool configs, quality gates, pipeline YAML, custom commands/skills.
- Version-controlled alongside the codebase (or in a separate repo for multi-project orgs).
- Changes to this layer change how every future task is executed.
- Analogy: if the codebase is a factory floor, the agentic layer is the set of Standard Operating Procedures posted on the wall.

##### H3: Layer 2 -- Pipeline Engine (Framework Runs Here)
- The orchestration runtime that reads the agentic layer and executes phases.
- Manages: phase sequencing, artifact chaining between phases, feedback loop execution, state tracking, escalation.
- You do not modify this layer. You configure it via the agentic layer.
- Analogy: the factory conveyor belt. It moves work through stations according to the SOPs.

##### H3: Layer 3 -- Codebase (Agents Work Here)
- Your source code, tests, documentation, infrastructure files.
- Agents read, write, test, and ship changes here -- following the prompts and permissions defined in the agentic layer.
- This is output, not input. The quality of this layer is a function of the quality of the agentic layer.

#### H2: Why Teams Collaborate on the Layer
- **The old model:** developers write code, review each other's code, maintain tribal knowledge about patterns and standards.
- **The AEF model:** developers write prompt templates, review each other's templates, and codify standards into quality gates. The code is generated output.
- **What changes:**
  - Code reviews become layer reviews (did the template change improve output quality?).
  - Onboarding means learning the layer (reading prompts and gates, not memorizing a codebase).
  - Architecture discussions become prompt architecture discussions.
  - Pair programming becomes pair prompting.

#### H2: The Role Shift -- Developer to Pipeline Architect
- Developers still need engineering judgment. That judgment now goes into designing prompts, choosing tool permissions, and calibrating gates.
- The new skill set: prompt design, pipeline tuning, gate calibration, artifact chain design.
- This is not "no-code." This is meta-engineering -- engineering the system that engineers.

#### H2: "The Code Is Output, the Agentic Layer Is the Product"
- Practical implications:
  - Your agentic layer gets the same rigor as production code: version control, code review, testing, documentation.
  - When output quality degrades, you fix the layer, not the generated code.
  - When onboarding a new project, you port your agentic layer (or adapt it), not your code patterns.
  - The agentic layer is portable across codebases. The same Plan template can work for a Python backend and a React frontend.

### UI Components
1. **Three-layer interactive diagram** -- Vertical stack of three styled cards (same as landing page but larger and interactive). Clicking a layer expands it to show its contents with icons and descriptions.
2. **Code block** -- Show the `agentic-layer/` directory tree (reuse from landing page, same styling).
3. **Before/After comparison card** -- Two-column card: left side "Traditional Team" (bullet list), right side "AEF Team" (bullet list). Use `bg-surface` with a vertical divider in `border-subtle`.
4. **Callout box** -- Styled `bg-glow-faint border border-glow/20 rounded-xl p-6` with the quote: "The code is output. The agentic layer is the product."

### Diagrams Needed
1. **Three-Layer Stack Diagram (SVG, animated):** Three horizontal bands stacked vertically. Top band (glow border) labeled "Agentic Layer" with icons for Prompts, Tools, Gates, Config. Middle band (plan border) labeled "Pipeline Engine" with the 7-phase flow as a mini horizontal strip. Bottom band (build border) labeled "Codebase" with file icons. Arrows flow downward between layers. On hover, each layer highlights and shows a tooltip with a one-line description. Use the `nodeBreath` animation on each layer border.

2. **Role Shift Timeline (SVG or CSS):** Horizontal before/after. Left: stick figure labeled "Developer" with arrow pointing to code icon. Right: stick figure labeled "Pipeline Architect" with arrow pointing to agentic layer icon (gear/template). A dotted line separates old and new.

### Code/Prompt Examples

**Example: Minimal agentic layer for a new project**
```yaml
# pipeline.yaml — minimum viable agentic layer
phases:
  - plan:
      template: prompts/plan.md
      tools: [read, search]
  - build:
      template: prompts/build.md
      tools: [read, search, execute, write]
      gates:
        - tests_pass: true
  - review:
      template: prompts/review.md
      tools: [read, search]
      gates:
        - no_blockers: true

loops:
  test_retry: { max: 3 }
  review_patch: { max: 3 }

escalation:
  target: human
  include: [plan, build_report, test_results, review_issues]
```

### Cross-Links
- Links to: `/concepts/tool-permissions` (tool configurations), `/concepts/artifact-chaining` (pipeline definitions), `/concepts/prompt-engineering` (prompt templates), `/concepts/ase` (maturity levels for the layer).
- Links from pipeline phases: all 7 phase pages should link here.

### Content Writer Notes
- **Tone:** Authoritative but approachable. This is the "aha moment" page -- the reader should leave understanding why this framework exists.
- **Emphasis:** Hammer the inversion: you are not writing code, you are writing the instructions that write code. Repeat this in different ways.
- **Analogy:** Use the factory SOPs analogy consistently. The agentic layer is the playbook. The pipeline is the conveyor belt. The codebase is the product rolling off the line.
- **Avoid:** Do not make this sound like "no-code" or "low-code." This is for engineers who understand software deeply -- they are applying that understanding at a higher level of abstraction.

---

## Page 2: `/concepts/agent-patterns`

### Title
**Agent Orchestration Patterns**

### Purpose
Teach when to use a single agent versus multiple agents, and present the four orchestration models with enough detail that a reader can choose and implement the right one.

### Content Outline

#### H2: When One Agent Is Enough
- Simple, well-scoped tasks: classification, commit message generation, small patches (under ~200 lines), single-file changes.
- Rule of thumb: if the task fits in one context window with room to spare, one agent is fine.
- Advantages: simpler orchestration, lower cost, faster execution, easier debugging.

#### H2: When You Need Multiple Agents
- Signals that demand multi-agent:
  - Task requires more context than one window can hold.
  - Task crosses multiple domains (backend + frontend + infra).
  - Quality matters enough to justify cross-validation.
  - Research phase produces too much information for one agent to synthesize.
- Multi-agent adds overhead. Use it when the quality/capability gain justifies it.

#### H2: The Four Orchestration Models

##### H3: 1. Sequential Handoff
- **How it works:** Agent A produces output. Agent B takes that output and validates, refines, or extends it. Linear chain.
- **Diagram:** Two boxes (A and B) connected by an arrow. A's output label feeds into B's input.
- **When to use:** Builder produces code, tester validates it. Planner produces plan, validator checks it. Simple two-step quality assurance.
- **Pros:** Simple to implement, easy to debug, clear accountability.
- **Cons:** No parallelism, bottlenecked by slowest agent, single point of failure per step.
- **AEF phases that use this:** Plan (planner + validator), Build (builder + self-reviewer).

##### H3: 2. Parallel Fan-Out / Merge
- **How it works:** Multiple agents work on the same task simultaneously (or on sub-parts). A coordinator agent merges their outputs into one.
- **Diagram:** One "dispatch" box fans out to 3 parallel agent boxes, which all feed into a "merge" box.
- **When to use:** Research-heavy planning (3 agents research different aspects of the codebase). Review (security reviewer + performance reviewer + style reviewer in parallel).
- **Pros:** Faster for independent subtasks, diverse perspectives, scales well.
- **Cons:** Merge step is hard -- conflicts, redundancy. Coordinator needs strong instructions.
- **AEF phases that use this:** Review (parallel specialist reviewers), Plan (parallel research agents).

##### H3: 3. Hierarchical Delegation
- **How it works:** A lead agent decomposes the task and dispatches subtasks to worker agents. Workers report back. Lead synthesizes.
- **Diagram:** Tree structure. One "lead" box at top, arrows down to 3 "worker" boxes, arrows back up to lead.
- **When to use:** Large builds that can be decomposed (lead architect delegates backend, frontend, database subtasks). Complex reviews across multiple subsystems.
- **Pros:** Scales to complex tasks, protects lead agent's context window (workers hold subtask context, lead holds only summaries).
- **Cons:** Lead agent must decompose well. Communication overhead. Workers may produce inconsistent outputs.
- **AEF phases that use this:** Build (for large features), Review (main reviewer delegates to sub-reviewers).

##### H3: 4. Adversarial / Debate
- **How it works:** Two agents argue opposing positions or propose competing solutions. A judge agent evaluates and decides.
- **Diagram:** Two boxes (Advocate A, Advocate B) with arrows into a "Judge" box. Dashed lines between advocates labeled "counter-argument."
- **When to use:** Architecture decisions with multiple valid approaches. Risk assessment. When you want to surface edge cases and trade-offs.
- **Pros:** Surfaces hidden risks, reduces confirmation bias, produces more thorough analysis.
- **Cons:** Expensive (3+ agents), slower, judge must be well-calibrated.
- **AEF phases that use this:** Plan (for major architectural decisions), Review (for controversial trade-offs).

#### H2: Decision Tree
- Interactive flowchart:
  1. Is the task simple and single-domain? -> YES -> Single agent. DONE.
  2. Does the task need cross-validation? -> YES -> Sequential Handoff.
  3. Can subtasks run independently? -> YES -> Parallel Fan-Out.
  4. Is the task decomposable into parts requiring different expertise? -> YES -> Hierarchical Delegation.
  5. Are there competing valid approaches and the stakes are high? -> YES -> Adversarial Debate.

#### H2: Context Window Protection
- Why subagent delegation prevents context overflow.
- The main agent holds the high-level plan and summaries. Workers hold only their subtask context.
- Rule: if you are feeding more than 40% of the context window with prior artifacts, delegate to subagents.

#### H2: Phase-to-Pattern Mapping

| Phase | Recommended Pattern | Why |
|-------|-------------------|-----|
| Plan | Sequential Handoff or Adversarial | Planner + validator, or competing approaches for complex features |
| Build | Hierarchical Delegation | Lead architect + specialist builders for large diffs |
| Test | Single Agent or Sequential Handoff | Usually one agent runs tests; handoff to fixer if failures |
| Review | Parallel Fan-Out | Security, performance, style reviewers in parallel |
| Document | Single Agent | Usually simple enough for one agent |
| Deploy | Single Agent | Mechanical: commits, PR creation |
| Monitor | Single Agent | Metric collection and threshold checking |

### UI Components
1. **Four pattern cards** -- Each pattern gets a card with a header, mini SVG diagram, "When to use" bullets, and pros/cons pills (green for pros, amber for cons).
2. **Interactive decision tree** -- Flowchart built with SVG. Each decision node is clickable and highlights the path to the recommended pattern. Final node glows with the recommendation.
3. **Phase mapping table** -- Styled table with phase color dots, permission badges style.
4. **Context window meter** -- A visual bar showing context usage. A threshold line at 40% labeled "delegate beyond this point."

### Diagrams Needed
1. **Sequential Handoff (SVG):** Two rounded rects A -> B with an arrow and data label.
2. **Parallel Fan-Out (SVG):** One rect fans to 3 rects, all merge into one rect. Parallel arrows animated with `flowPulse`.
3. **Hierarchical Delegation (SVG):** Tree: one rect at top, three below, arrows down and back up.
4. **Adversarial Debate (SVG):** Two rects with bidirectional dashed arrows, both feeding into a Judge rect below.
5. **Decision Tree (SVG, interactive):** 5-node flowchart with yes/no branches. Click a node to expand its description.

### Code/Prompt Examples

**Example: Hierarchical delegation in a Build phase prompt**
```markdown
# Build Phase — Lead Architect

## Role
You are the Lead Software Engineer. You will decompose
the implementation plan into subtasks and delegate each
to a specialist builder agent.

## Subtask Delegation
For each subtask:
1. Create a focused brief (context, files, acceptance criteria)
2. Spawn a subagent with the brief
3. Collect the subagent's output
4. Validate consistency across all subtask outputs
5. Merge into a unified changeset

## Constraints
- Each subagent gets ONLY the files relevant to its subtask
- Never pass the full plan to a subagent — summarize
- If a subagent's output conflicts with another, YOU resolve it
```

### Cross-Links
- Links to: `/concepts/self-healing` (loops use sequential handoff), `/concepts/tool-permissions` (each agent in a pattern inherits phase permissions), `/concepts/agentic-layer` (patterns are configured in the layer).
- Links to pipeline phases: Plan, Build, Review.

### Content Writer Notes
- **Tone:** Practical and pattern-oriented. This is a reference page -- readers will return to it when deciding how to structure a new phase.
- **Emphasis:** The decision tree is the centerpiece. Make it visually prominent and easy to follow.
- **Analogy:** Sequential Handoff = assembly line. Parallel Fan-Out = multiple inspectors checking a car simultaneously. Hierarchical = a general directing lieutenants. Adversarial = a courtroom debate.
- **Avoid:** Do not imply multi-agent is always better. Single agent is the default; multi-agent is an upgrade when justified.

---

## Page 3: `/concepts/self-healing`

### Title
**Self-Healing Loops**

### Purpose
Explain why pipelines must be able to recover from failures autonomously, and detail the two loop types, their termination conditions, and escalation behavior.

### Content Outline

#### H2: Why Linear Pipelines Fail
- The naive approach: run Plan, run Build, run Test, run Review -- if anything fails, throw an error.
- Problem: AI agents produce imperfect output. Tests will fail. Reviews will find issues. This is expected, not exceptional.
- A pipeline that stops on first failure is useless in practice. You need cycles, not lines.

#### H2: The Test Retry Loop
- **Trigger:** One or more tests fail after the Build phase produces code.
- **Cycle:**
  1. Test phase runs all tests.
  2. If failures exist: package failure details (test name, expected vs actual, stack trace, relevant source file).
  3. Spawn a builder agent with the failure context + original plan.
  4. Builder agent patches the code.
  5. Re-run all tests.
  6. Repeat until all pass or max retries reached.
- **Default max retries:** 3.
- **What the builder agent receives:** The original plan artifact, the current code state, and the specific test failure details. This is artifact chaining in action.

#### H2: The Review-Patch Loop
- **Trigger:** Review phase finds blocker-severity issues.
- **Cycle:**
  1. Review phase analyzes code + test results.
  2. If blockers found: package issue details (file, line, severity, description, suggested fix).
  3. Inject patch context into a builder agent.
  4. Builder agent patches the code.
  5. Re-run tests (test loop may fire within this).
  6. Re-run review.
  7. Repeat until no blockers or max retries reached.
- **Default max retries:** 3.
- **Severity classification:** Blocker (triggers loop), Tech-debt (logged but does not block), Skippable (noted, no action).

#### H2: The Full Rebuild Loop
- **Trigger:** Review finds fundamental/architectural issues that patches cannot fix.
- **Action:** Pipeline returns to Build phase with the review feedback as additional context.
- **Default max retries:** 1 (this is expensive; if the approach is fundamentally wrong, a human should probably weigh in).

#### H2: Loop Termination Conditions
- **Happy path:** All gates pass. Loop exits, pipeline continues.
- **Max retries exhausted:** Loop exits, pipeline escalates.
- **No new information:** If the retry produces the same failure, the loop should detect this and exit early rather than wasting retries. (Advanced: diff the failure outputs between iterations.)

#### H2: Escalation -- When Loops Fail
- What the human receives:
  - The original plan artifact.
  - The build report (what was built, what changed).
  - All test results across iterations (showing the progression or lack thereof).
  - All review findings across iterations.
  - A summary of what the pipeline tried and why it gave up.
- The human gets a complete forensic picture, not "Error: tests failed."
- After human input, the pipeline resumes from the phase where it stopped (not from scratch, unless the human directs otherwise).

#### H2: Configuring Loops
- `pipeline.yaml` configuration:
  ```yaml
  loops:
    test_retry:
      max: 3
      trigger_on: [test_failure]
    review_patch:
      max: 3
      trigger_on: [blocker]
      ignore: [tech_debt, skippable]
    full_rebuild:
      max: 1
      trigger_on: [architectural_issue]
  escalation:
    target: human
    include: [plan, build_report, test_results, review_issues]
  ```

#### H2: Why 3 Retries Is the Default
- Empirical observation: most fixable issues resolve within 1-2 retries. If 3 retries haven't fixed it, the issue is likely a deeper misunderstanding (wrong approach, underspecified plan, missing context).
- Cost consideration: each retry invokes an agent. 3 retries triples the cost of a phase. Diminishing returns beyond 3.
- Configurable: teams can set 1 (fail fast) or 5 (for complex integration tests) depending on context.

#### H2: Anti-Patterns
- **Infinite loops:** Never remove the max retry limit. Always have a termination condition.
- **Retrying without new information:** If the builder agent patches the same code the same way twice, the loop should break. Inject the failure history into the retry prompt so the agent tries a different approach.
- **Retrying non-deterministic failures:** Flaky tests should be identified and quarantined, not retried endlessly. Add a "known flaky" list to the test gate config.

### UI Components
1. **Animated loop flowcharts** (two separate ones for Test Retry and Review-Patch) -- SVG with dashed-line arcs similar to the landing page pipeline loops. Use `loop-arc` animation class.
2. **Retry counter visualization** -- Three circles (iteration 1, 2, 3). On hover, each shows what happened in that iteration (pass/fail, what was fixed). If all three fail, a fourth "Escalate" box appears with a human icon.
3. **Config code block** -- `pipeline.yaml` example with syntax highlighting.
4. **Escalation report card** -- Mock-up of what a human sees when escalation fires: a card with tabs for Plan, Build Report, Test Results (iteration 1/2/3), Review Findings.

### Diagrams Needed
1. **Test Retry Loop Flowchart (SVG, animated):** Diamond "Tests pass?" -> YES: proceed to Review. NO: "Builder patches" box -> arrow back to "Run tests" -> diamond again. Counter shows iteration number. After 3, arrow to "Escalate" box. Use test phase color (#10B981).

2. **Review-Patch Loop Flowchart (SVG, animated):** Diamond "Review clean?" -> YES: proceed to Document. NO (blocker): "Builder patches" -> "Re-test" -> diamond "Tests pass?" -> YES: back to "Review" -> diamond "Review clean?" again. After 3 iterations, "Escalate." Use review phase color (#3B82F6) for the review path and test phase color for the test sub-loop.

3. **Escalation Report Mockup (HTML/CSS):** A styled card showing the full context the human receives. Tabs for each artifact type.

### Code/Prompt Examples

**Example: Retry prompt injected into builder agent on test failure**
```markdown
# Test Retry — Iteration ${retry_count} of ${max_retries}

## Context
You are fixing test failures from iteration ${retry_count - 1}.

## Original Plan
${plan_artifact}

## Current Test Failures
${test_results}

## Previous Fix Attempts
${previous_patches}

## Instructions
1. Analyze EACH failure — distinguish test bugs from code bugs.
2. Fix ONE failure at a time, starting with the simplest.
3. Do NOT modify passing tests.
4. If a failure was present in the previous iteration and
   your prior fix did not work, try a DIFFERENT approach.
```

### Cross-Links
- Links to: `/concepts/artifact-chaining` (how failure context flows between iterations), `/concepts/agent-patterns` (loops use sequential handoff), `/concepts/tool-permissions` (builder agents in loops get Build-phase permissions), `/concepts/ase` (higher autonomy levels depend on reliable loops).
- Links to pipeline phases: Test, Review, Build.

### Content Writer Notes
- **Tone:** Reassuring. The message is: failures are expected and handled. This is not fragile.
- **Emphasis:** The pipeline is designed to fail gracefully, not designed to never fail. The loops are the mechanism for graceful failure.
- **Analogy:** A compiler that shows you the error and suggests a fix, then applies the fix and recompiles. Except instead of a compiler, it is the entire engineering pipeline.
- **Avoid:** Do not make loops sound magical. They have limits. Be honest about when they fail and what happens next (escalation).

---

## Page 4: `/concepts/artifact-chaining`

### Title
**Artifact Chaining**

### Purpose
Explain how stateless agents maintain pipeline continuity through structured artifacts and template variable substitution -- the pipeline's memory system.

### Content Outline

#### H2: The Problem -- Agents Are Stateless
- Each agent invocation starts with a blank slate. There is no shared memory, no session state, no database the agent automatically consults.
- So how does the Build agent know what the Plan agent decided? How does the Review agent know what tests passed?
- This is the fundamental problem artifact chaining solves.

#### H2: The Solution -- Artifacts and Template Variables
- Each phase produces a structured output called an artifact.
- The next phase's prompt template contains variables (`${plan_artifact}`, `${build_artifact}`, etc.) that are substituted with the prior phase's artifact before the prompt is sent to the agent.
- The pipeline engine handles the substitution. The developer designs the templates with the right variable slots.

#### H2: The Full Artifact Chain
- Visual chain showing every phase's input and output:
  ```
  Issue Description
    | ${issue_description}
    v
  Plan --> produces $plan_artifact
    | ${plan_artifact}
    v
  Build --> produces $build_artifact
    | ${build_artifact}, ${plan_artifact}
    v
  Test --> produces $test_results
    | ${test_results}, ${build_artifact}
    v
  Review --> produces $review_results
    | ${review_results}
    v
  Document --> produces $doc_artifact
    | all artifacts
    v
  Deploy --> produces $deploy_artifact
    |
    v
  Monitor --> produces KPI data
    | KPI anomalies become new ${issue_description}
    v
  (back to Plan)
  ```

#### H2: The State Object
- The pipeline engine maintains a manifest/state object that tracks:
  - Current phase
  - Which artifacts exist and their content
  - Pass/fail status per phase
  - Loop iteration counts
  - Timestamps
- Example state object:
  ```json
  {
    "pipeline_id": "feat-auth-2026-03-10",
    "current_phase": "review",
    "artifacts": {
      "plan": { "status": "complete", "format": "markdown", "path": ".pipeline/plan.md" },
      "build": { "status": "complete", "format": "markdown", "path": ".pipeline/build.md" },
      "test": { "status": "complete", "format": "json", "path": ".pipeline/test-results.json" },
      "review": { "status": "in_progress", "format": "json" }
    },
    "loops": {
      "test_retry": { "iteration": 2, "max": 3 },
      "review_patch": { "iteration": 0, "max": 3 }
    }
  }
  ```

#### H2: Artifact Formats
- **Markdown** -- Use when the artifact is primarily human-consumed or when the consuming agent benefits from natural language. Phases: Plan, Build report, Document.
- **JSON** -- Use when the artifact is primarily machine-consumed or when structure matters for parsing. Phases: Test results, Review findings.
- **Hybrid** -- Some artifacts (like review results) benefit from JSON structure (severity, file, line) with markdown descriptions within fields.
- Rule: if the next consumer is an agent that needs to iterate over items (test failures, review issues), use JSON. If the next consumer needs narrative context (understanding a plan), use markdown.

#### H2: Template Variable Reference

| Variable | Producing Phase | Consuming Phase(s) | Format | Description |
|----------|----------------|--------------------|---------|----|
| `${issue_description}` | External (issue tracker) | Plan | Markdown | The task/bug/feature description |
| `${issue_type}` | External | Plan | String | `feature`, `bug`, `task`, or `patch` |
| `${plan_artifact}` | Plan | Build, Review | Markdown | Implementation plan with file targets and scope |
| `${build_artifact}` | Build | Test, Review, Document | Markdown | Summary of changes made, files modified, approach taken |
| `${test_commands}` | Build | Test | JSON array | E2E test commands to run |
| `${test_results}` | Test | Review, Build (on retry) | JSON | Test outcomes: pass/fail per test, coverage, errors |
| `${review_results}` | Review | Build (on patch), Document | JSON | Issues found: severity, file, line, description |
| `${doc_artifact}` | Document | Deploy | Markdown | Generated documentation and changelog |
| `${deploy_artifact}` | Deploy | Monitor | JSON | PR URL, commit SHAs, deploy metadata |
| `${previous_patches}` | Build (retry) | Build (next retry) | Markdown | What was tried in previous iterations |

#### H2: Designing Good Artifacts
- Be specific: include file paths and line numbers, not vague descriptions.
- Be structured: use headings, numbered lists, or JSON keys -- not walls of text.
- Be minimal: include only what the next phase needs. Do not dump the entire context.
- Be deterministic: the same plan should produce the same artifact structure every time. Use output format instructions in your prompt templates.

### UI Components
1. **Artifact chain visualization (animated SVG)** -- Vertical flow diagram with 7 phase nodes. Each node has an output arrow labeled with the variable name. Clicking a node shows the artifact format example in a popover.
2. **State object code block** -- JSON with syntax highlighting.
3. **Template variable reference table** -- Styled table with phase color dots for producing/consuming phases.
4. **Format comparison cards** -- Two side-by-side cards: "Markdown Artifact" (plan example) and "JSON Artifact" (test results example).

### Diagrams Needed
1. **Artifact Chain Flow (SVG, vertical, animated):** Seven phase nodes arranged vertically. Between each pair, a connecting line with an animated data packet (small dot moving along the line, using `flowPulse` animation). Each connection is labeled with the variable name (`$plan_artifact`, etc.). The Monitor node has a curved arrow back to Plan labeled `$issue_description`. Use phase colors for each node.

2. **State Object Lifecycle (SVG):** Horizontal timeline showing the state object evolving as each phase completes. Five snapshots of the state object, each adding a new artifact entry.

### Code/Prompt Examples

**Example: Build template consuming plan artifact**
```markdown
# Build Phase — Software Engineer

## Role
You are a Senior Software Engineer executing a plan.

## The Plan
${plan_artifact}

## Constraints
- Implement ONLY what the plan specifies
- Write tests FIRST, then implementation
- Reference specific file:line for all changes
- Do NOT deviate from the plan scope

## Output Format
Produce a build report:
1. Files created (with path)
2. Files modified (with path and line ranges)
3. Tests written (name, what they verify)
4. E2E commands to validate: ${test_commands}
```

**Example: Test results artifact (JSON)**
```json
{
  "summary": { "total": 14, "passed": 12, "failed": 2, "skipped": 0 },
  "coverage": { "lines": 87.3, "branches": 74.1 },
  "failures": [
    {
      "test": "test_auth_token_refresh",
      "file": "tests/auth/test_tokens.py:45",
      "expected": "200 OK with new token",
      "actual": "401 Unauthorized",
      "stack_trace": "...",
      "related_source": "src/auth/tokens.py:112-130"
    },
    {
      "test": "test_session_expiry",
      "file": "tests/auth/test_session.py:78",
      "expected": "Session invalidated after 30m",
      "actual": "Session still active at 31m",
      "stack_trace": "...",
      "related_source": "src/auth/session.py:55-67"
    }
  ]
}
```

### Cross-Links
- Links to: `/concepts/prompt-engineering` (template variable substitution technique), `/concepts/self-healing` (loops depend on artifact chaining for retry context), `/concepts/agentic-layer` (artifact formats are configured in the layer).
- Links to pipeline phases: all 7.

### Content Writer Notes
- **Tone:** Technical and precise. This page is for developers who want to understand the mechanics.
- **Emphasis:** The chain is what makes the pipeline more than a sequence of disconnected prompts. Without artifact chaining, each phase would start blind.
- **Analogy:** A relay race where runners pass a baton. The baton is the artifact. Without it, the next runner does not know when to start or which direction to go.
- **Avoid:** Do not conflate artifact chaining with agent memory or RAG. Artifacts are explicit, structured, and designed by the developer. They are not automatic recall.

---

## Page 5: `/concepts/prompt-engineering`

### Title
**Prompt Engineering Patterns**

### Purpose
Present seven reusable prompt techniques that work across any agent stack. These are the building blocks for writing effective phase templates.

### Content Outline

#### H2: Seven Patterns for Agentic Prompts
- Brief intro: these patterns are tool-agnostic. They work with Claude, Kiro, open-source models. The principles are universal.

#### H2: 1. Role Assignment
- **What:** Assign a distinct professional persona at the start of every prompt. "You are a Software Architect." "You are a QA Engineer."
- **Why:** Constrains the agent's behavior to that role's expectations. A QA Engineer focuses on edge cases; a Software Architect focuses on structure.
- **Before/After:**
  - Before: "Analyze this code and suggest improvements." (vague, unfocused)
  - After: "You are a Senior Security Engineer. Analyze this code for authentication vulnerabilities, injection risks, and data exposure. Ignore style and performance — those are handled by other reviewers." (focused, bounded)
- **Pattern:** Always place role assignment as the first section of the prompt. Include what the role IS and what it is NOT responsible for.

#### H2: 2. Structured Output Contracts
- **What:** Define the exact output format in the prompt. Tell the agent what shape the response must take.
- **Why:** Downstream consumers (other agents or humans) depend on predictable structure. If the plan artifact is free-form text one time and a numbered list the next, the Build template's `${plan_artifact}` substitution breaks.
- **JSON contract example:**
  ```json
  // Output must match this schema exactly:
  {
    "verdict": "pass | fail",
    "issues": [
      {
        "severity": "blocker | tech_debt | skippable",
        "file": "string",
        "line": "number",
        "description": "string",
        "suggested_fix": "string"
      }
    ]
  }
  ```
- **Markdown contract example:**
  ```markdown
  ## Output Format
  1. **Summary** — One paragraph describing the plan.
  2. **Files to Modify** — Bulleted list with `file:line` references.
  3. **Files to Create** — Bulleted list with purpose.
  4. **Out of Scope** — What we are NOT doing.
  5. **Test Strategy** — How to verify the implementation.
  ```

#### H2: 3. Anti-Scope-Creep Instructions
- **What:** Explicit "do NOT do" sections in the prompt. Boundary constraints.
- **Why:** Agents are eager to help. Given the Plan prompt, an agent might start implementing. Given the Review prompt, an agent might start fixing bugs. Explicit boundaries prevent this.
- **Example:**
  ```markdown
  ## What We Are NOT Doing
  - Do NOT modify files outside the plan scope
  - Do NOT refactor code that is not part of this task
  - Do NOT add features not requested in the issue
  - Do NOT fix pre-existing bugs you encounter
  - If you find issues outside scope, NOTE them in a
    "Future Work" section — do not act on them
  ```
- **Rule:** Every prompt template should have an explicit "What we are NOT doing" or "Constraints" section.

#### H2: 4. Conditional Documentation Loading
- **What:** Tell agents which files to read and which to ignore. Do not load the entire codebase into context.
- **Why:** Context windows are finite. Loading irrelevant files wastes tokens and introduces noise. The agent may get confused by unrelated code.
- **Pattern:**
  ```markdown
  ## Required Reading
  Read ONLY the following files before proceeding:
  - src/auth/tokens.py (the module being modified)
  - src/auth/session.py (related dependency)
  - tests/auth/test_tokens.py (existing tests)

  ## Do NOT Read
  - Any files outside src/auth/ and tests/auth/
  - Configuration files unless referenced in the plan
  ```
- **Advanced:** Use the plan artifact to dynamically determine which files to load. The Plan phase identifies target files; the Build template uses those as the conditional loading list.

#### H2: 5. Template Variable Substitution
- **What:** Use `${variable}` syntax to inject dynamic context into prompts. The pipeline engine substitutes these before sending to the agent.
- **Why:** Templates are reusable across tasks. The variables change; the structure stays the same.
- **Best practices:**
  - Use descriptive names: `${plan_artifact}` not `${input}`.
  - Document what each variable contains and its expected format.
  - Use fallback values for optional variables: `${branch_name:-main}`.
  - Never nest variables: `${${phase}_artifact}` is fragile. Use explicit names.

#### H2: 6. file:line Precision References
- **What:** Always reference specific file paths and line numbers in prompts and outputs. "Modify `src/auth/tokens.py:112`" not "update the auth module."
- **Why:** Precision dramatically improves agent execution accuracy. Vague references lead to the agent searching (wasting tokens), guessing (wrong file), or modifying the wrong code.
- **Pattern in prompts:**
  ```markdown
  ## Files to Modify
  - `src/auth/tokens.py:112-130` — Replace the token refresh logic
  - `src/auth/session.py:55` — Update the expiry check
  ```
- **Pattern in outputs:** Require the agent to produce file:line references in its own output so downstream phases have the same precision.

#### H2: 7. Issue-Type Routing
- **What:** Use different prompt templates (or template branches) for different issue types. Features, bugs, tasks, and patches each have different needs.
- **Why:** A feature needs user stories and acceptance criteria. A bug needs root cause analysis and minimal reproduction. A patch needs minimal-scope constraints. One-size-fits-all prompts produce mediocre results for all types.
- **The four templates:**
  - **Feature (EARS format):**
    ```markdown
    ## Feature Plan Template
    While [context], when [trigger], the system shall [action]
    so that [outcome].

    User stories:
    - As a [role], I want [capability] so that [benefit]

    Acceptance criteria:
    - Given [state], when [action], then [result]
    ```
  - **Bug (Root Cause Analysis):**
    ```markdown
    ## Bug Fix Template
    ### Symptoms
    ${issue_description}

    ### Root Cause Analysis
    1. Reproduce the bug (identify the trigger)
    2. Trace the execution path
    3. Identify the root cause (not just the symptom)
    4. Propose the minimal fix

    ### Constraints
    - Fix ONLY the root cause
    - Do NOT refactor surrounding code
    - Regression test: write a test that fails before
      the fix and passes after
    ```
  - **Patch (Minimal Scope):**
    ```markdown
    ## Patch Template
    ### Scope
    This is a minimal patch. Maximum 50 lines changed.

    ### Rules
    - Change the fewest files possible
    - No new dependencies
    - No refactoring
    - Must pass all existing tests
    ```
  - **Task (General Implementation):**
    ```markdown
    ## Task Template
    ### Objective
    ${issue_description}

    ### Implementation
    Follow standard implementation patterns.
    Reference existing code in the same module for style.

    ### Deliverables
    - Code changes with tests
    - Updated documentation if public API changes
    ```

### UI Components
1. **Seven technique cards** -- Grid of 7 cards (3 columns on desktop, 1 on mobile). Each card has a number badge, title, one-line description, and an "expand" toggle to show the full example.
2. **Code blocks** -- Multiple code blocks with syntax highlighting for each technique's examples.
3. **Before/After comparison** -- For Role Assignment, show a split card with "Before" (red-tinted border) and "After" (green-tinted border).
4. **Issue-type router** -- Tab component with 4 tabs (Feature, Bug, Patch, Task), each showing the corresponding template.

### Diagrams Needed
1. **Prompt Anatomy Diagram (SVG):** A vertical breakdown of a complete prompt template showing labeled sections: Role (top, purple), Context with variables (indigo), Constraints/Anti-scope (red), Required Reading (cyan), Output Format (green). Each section is a horizontal band with a label badge.

2. **Issue-Type Router Diagram (SVG):** A diamond decision node labeled `${issue_type}` with four arrows leading to four different template icons, each colored by type.

### Cross-Links
- Links to: `/concepts/artifact-chaining` (template variables are the mechanism), `/concepts/tool-permissions` (constraints section often mirrors permissions), `/concepts/agentic-layer` (templates live in the layer).
- Links to pipeline phases: Plan (role assignment, issue-type routing), Build (anti-scope-creep, file:line), Review (structured output), all phases (template variables).

### Content Writer Notes
- **Tone:** Instructional and pattern-focused. Each technique should feel like a tool the reader can grab and use immediately.
- **Emphasis:** These are not theoretical. Each one directly improves output quality. Show the concrete before/after difference.
- **Analogy:** Prompt engineering patterns are like design patterns in software -- named solutions to recurring problems. Role Assignment is the Strategy pattern. Structured Output is the Interface pattern.
- **Avoid:** Do not be preachy about prompt engineering. Assume the reader has written prompts before and wants to level up.

---

## Page 6: `/concepts/tool-permissions`

### Title
**Tool Permission Design**

### Purpose
Explain why applying the principle of least privilege to AI agents is critical for quality and safety, and provide the complete permission matrix.

### Content Outline

#### H2: The Principle of Least Privilege for AI Agents
- In traditional security, processes get only the access they need. The same applies to AI agents.
- An agent with too many tools will use them. A planner with write access will start implementing. A reviewer with execute access will start running (and potentially breaking) things.
- Permissions are a quality mechanism, not just a security mechanism. They enforce role discipline.

#### H2: Why It Matters
- **Quality:** A Review agent restricted to Read+Search produces findings. Give it Write access and it starts "fixing" issues -- producing unreviewed code that bypasses the Build/Test loop.
- **Predictability:** When you know an agent can only read, you know it cannot change your codebase. The blast radius is zero.
- **Debugging:** When something goes wrong, permissions narrow the investigation. If Plan is read-only, the Plan phase cannot have introduced a file modification.
- **Trust:** Each autonomy level (from Assisted to ASE) depends on trusting that agents stay within their bounds.

#### H2: The Permission Matrix

| Phase | Read | Search | Execute | Write | Rationale |
|-------|:----:|:------:|:-------:|:-----:|-----------|
| **Plan** | Yes | Yes | No | No | Research only. Read the codebase, search for patterns, but never modify anything. Planning and execution must be separate. |
| **Build** | Yes | Yes | Yes | Yes | Full access. The builder needs to read context, search for patterns, run tests during development, and write code. |
| **Test** | Yes | Yes | Yes | Yes | Must run test suites (Execute) and fix test failures in the retry loop (Write). Reads code and searches for context. |
| **Review** | Yes | Yes | No | No | Analysis only. Reads code and test results, searches for patterns. Never writes fixes (that is the Build agent's job in the patch loop). Never executes (could cause side effects). |
| **Document** | Yes | Yes | No | Yes | Reads the code and diffs, searches for patterns, writes documentation. Does not execute code -- documentation is generated from analysis, not from running the program. |
| **Deploy** | Yes | Yes | Yes | No | Reads final state, searches for issues, executes git commands and CI triggers. Does not write to source code -- the code is finalized. |
| **Monitor** | Yes | Yes | Yes | No | Reads metrics, searches logs, executes monitoring scripts and threshold checks. Does not modify code or configuration. |

#### H2: Tool Categories Explained
- **Read:** File reading, directory listing, reading environment variables, reading configuration. The most basic capability.
- **Search:** Grep, glob, find, AST search, semantic code search. Discovery and navigation.
- **Execute:** Running shell commands, test runners, linters, git commands, CI triggers, database queries. Actions with side effects.
- **Write:** File creation, file editing, file deletion. Permanent changes to the filesystem.

#### H2: Designing Permissions for Custom Phases
- If you add a custom phase (e.g., "Security Audit"), ask:
  1. Does this phase need to modify files? If no, deny Write.
  2. Does this phase need to run commands? If no, deny Execute.
  3. What is the worst thing this phase could do with each permission? If that risk is unacceptable, deny it.
- Start with Read+Search only. Add permissions only when the phase demonstrably needs them.

#### H2: Common Mistakes
- **Giving Review write access:** The reviewer starts "helpfully" fixing issues instead of reporting them. This bypasses the Build/Test cycle and produces unreviewed code.
- **Giving Plan execute access:** The planner starts building during the planning phase. Plans become coupled to implementation details instead of staying strategic.
- **Giving Deploy write access:** The deploy agent modifies source files after review. Changes go out unreviewed.
- **Not restricting Document from Execute:** The documentation agent tries to run the program to "understand it better," potentially causing side effects.

#### H2: Security Implications
- An agent with Execute+Write can install packages, modify configurations, create files, and run arbitrary commands. This is necessary for Build and Test, but dangerous for other phases.
- In high-security environments, consider sandboxing Execute to specific commands (e.g., only `npm test`, `pytest`, `git commit` -- not arbitrary shell access).
- Permission design becomes critical as you move up the autonomy scale (Level 3-4). At Level 4 (ASE), agents run without supervision -- permissions are your primary safety control.

### UI Components
1. **Interactive permission matrix table** -- Full-width table with phase color dots. Each cell is a styled permission badge (`.perm-allowed` or `.perm-denied`). On hover over any cell, a tooltip shows the rationale. On click of a row, the row expands to show the full explanation.
2. **Tool category cards** -- Four cards (Read, Search, Execute, Write), each with an icon, description, and risk level indicator (green/yellow/red border).
3. **Mistake scenario cards** -- Three cards showing the anti-pattern. Each has a red warning icon, the mistake, and the consequence.
4. **Permission builder** -- An interactive widget where users select a custom phase name and toggle permissions on/off. The widget shows a live "risk assessment" based on the selected permissions.

### Diagrams Needed
1. **Permission Matrix (SVG or styled HTML table):** Same as described in the table above, but as a visual matrix with colored cells. Green cells for allowed, red for denied. Phase names in the left column with their phase color dots. Tool categories across the top.

2. **Blast Radius Diagram (SVG):** Two concentric circles. Inner circle: "Read + Search" with a small radius labeled "Zero blast radius -- cannot change anything." Outer circle: "Execute + Write" with a large radius labeled "Full blast radius -- can modify codebase." Phases are positioned on the appropriate ring.

### Code/Prompt Examples

**Example: Tool permission configuration in pipeline.yaml**
```yaml
phases:
  plan:
    tools:
      read: true
      search: true
      execute: false
      write: false
    # Explicit deny with explanation
    deny_reasons:
      execute: "Plan phase must not run code — research only"
      write: "Plan phase must not modify files — read-only analysis"

  build:
    tools:
      read: true
      search: true
      execute: true
      write: true
    # Scoped execute permissions (advanced)
    execute_allowlist:
      - "npm test"
      - "npm run lint"
      - "git diff"
      - "git add"
      - "git commit"

  review:
    tools:
      read: true
      search: true
      execute: false
      write: false
    deny_reasons:
      execute: "Reviewers analyze, they don't run"
      write: "Reviewers report, they don't fix"
```

### Cross-Links
- Links to: `/concepts/agentic-layer` (permissions are part of the layer configuration), `/concepts/agent-patterns` (each agent in a multi-agent pattern inherits phase permissions), `/concepts/ase` (higher autonomy levels depend on correct permissions), `/concepts/self-healing` (patch loop agents get Build-phase permissions temporarily).
- Links to pipeline phases: all 7 (each phase page should show its permission set).

### Content Writer Notes
- **Tone:** Security-conscious but practical. Do not make this feel like a compliance checklist. Frame it as "this is how you keep agents focused."
- **Emphasis:** Permissions are a quality mechanism first, security mechanism second. The primary benefit is preventing agents from drifting out of their role.
- **Analogy:** A hospital operating room. The surgeon (Build) has access to everything. The radiologist (Review) reads scans but does not operate. The receptionist (Plan) reads patient records but does not prescribe treatment. Everyone has the access they need and nothing more.
- **Avoid:** Do not sound paranoid. Agents are not adversarial. They are overeager. Permissions are guardrails, not prison walls.

---

## Page 7: `/concepts/ase`

### Title
**Autonomous Software Engineering**

### Purpose
Present the four-level maturity model for graduating from human-driven to fully autonomous pipelines. Help teams assess their current level and understand what it takes to advance.

### Content Outline

#### H2: The Path from Manual to Autonomous
- Most teams start by running prompts manually and reviewing every output. This is fine. The goal is to graduate -- not to skip levels.
- Each level adds autonomy while maintaining (or increasing) safety through better gates, better templates, and better monitoring.

#### H2: Level 1 -- Assisted
- **Description:** The agent helps. The human drives. You run each phase manually, inspect every output, and decide whether to proceed.
- **How it works:** Developer writes an issue. Runs the Plan prompt. Reads the plan. Runs the Build prompt. Reads the code. Runs tests manually. Reviews manually. Ships manually.
- **Risk:** Low. The human is in full control at every step.
- **Use when:** Learning the framework. High-risk or regulated projects. New pipeline that hasn't been validated. Teams new to agentic workflows.
- **What you need:** A set of prompt templates. Basic tool configuration. No gates required (you are the gate).
- **Visual marker:** Muted border, L1 badge.

#### H2: Level 2 -- Supervised
- **Description:** The agent runs phases autonomously. The human approves at checkpoints between phases.
- **How it works:** Agent runs Plan and pauses. Human reviews plan, approves. Agent runs Build + Test (including retry loops). Human reviews test results, approves. Agent runs Review. Human reviews findings, approves. Agent runs Document + Deploy.
- **Risk:** Medium. The human validates at strategic checkpoints but does not inspect every line.
- **Use when:** Established templates with a track record. Moderate confidence in pipeline quality. Non-critical projects. Teams with some experience.
- **What you need:** Reliable prompt templates. Quality gates for Test and Review. A checkpoint approval mechanism.
- **Visual marker:** Glow/40 border, L2 badge.

#### H2: Level 3 -- Autonomous
- **Description:** The agent runs the entire pipeline end-to-end. The human reviews only the final output: the PR.
- **How it works:** Issue goes in. PR comes out. The human reviews the PR like any code review. Quality gates and self-healing loops are the safety net.
- **Risk:** Medium-high. If gates are misconfigured, bad code may reach the PR. But the PR review catches it.
- **Use when:** Mature pipeline with well-tuned gates. High-quality prompt templates. Strong test coverage on the target codebase. Teams confident in their pipeline.
- **What you need:** Comprehensive quality gates. Test coverage thresholds. Review severity configuration. Reliable self-healing loops. Monitoring of pipeline success rates.
- **Visual marker:** Full glow border with shadow, L3 badge.

#### H2: Level 4 -- Autonomous Software Engineering (ASE)
- **Description:** The agent runs. The gates pass. The PR auto-merges. No human in the loop.
- **How it works:** Issue goes in. Code goes to production. The Monitor phase watches for anomalies. If something breaks, a new issue is created automatically, and the pipeline runs again.
- **Risk:** High. Requires excellent gates, comprehensive monitoring, and automated rollback.
- **Use when:** Proven pipeline with a demonstrated track record (e.g., 95%+ success rate over 50+ runs). Low-risk changes (dependency updates, small patches, documentation). Strong monitoring and alerting. Automated rollback capability.
- **What you need:** Everything from Level 3, plus: auto-merge rules, production monitoring, automated rollback, anomaly detection, pipeline success rate tracking.
- **Visual marker:** Filled glow circle with shadow, L4 badge.

#### H2: Measuring Readiness
- **Gate quality metrics:**
  - What percentage of pipeline runs that pass all gates actually produce correct output? (Gate accuracy)
  - What percentage of issues caught by humans post-pipeline should have been caught by gates? (Gate coverage gap)
- **Pipeline metrics:**
  - Success rate (runs that reach Ship without human escalation).
  - Average loop iterations (higher = templates or tests need tuning).
  - Time to Ship (from issue to PR).
  - Cost per run (total agent invocations * cost per invocation).
- **Graduation criteria (table):**

| Metric | L1->L2 | L2->L3 | L3->L4 |
|--------|--------|--------|--------|
| Successful runs | 10+ | 50+ | 100+ |
| Gate accuracy | Any | >90% | >98% |
| Human override rate | Any | <20% | <5% |
| Average retries | Any | <2 | <1.5 |

#### H2: The Relationship Between Gate Quality and Autonomy
- You cannot skip levels by just "turning on auto-merge." The autonomy level must match the gate quality.
- If your gates catch 70% of issues, Level 2 is your ceiling. You need a human at every checkpoint to catch the other 30%.
- Investing in gate quality is investing in autonomy. Every issue your gates catch is a human review you eliminate.

#### H2: Why Most Teams Should Stay at Level 2-3
- For critical systems (payments, authentication, infrastructure), Level 2-3 with human oversight is the responsible choice.
- Level 4 is appropriate for: low-risk changes, proven pipelines, projects with comprehensive monitoring and rollback.
- The framework does not push teams toward Level 4. It supports whatever level matches the team's risk tolerance and gate maturity.

#### H2: The Monitor Phase as Safety Valve
- At Level 3-4, the Monitor phase becomes critical. It closes the outer loop.
- Production anomalies (error rate spikes, performance degradation, user complaints) automatically generate new issues that feed back into Plan.
- This means the pipeline is self-correcting at the production level, not just the code level.
- If Monitor detects a regression caused by a recent pipeline run, it can trigger: a revert, a hotfix pipeline run, or a human alert -- depending on configuration.

### UI Components
1. **Maturity stepper (large version)** -- Expand the vertical stepper from the landing page into a full-page component. Each level gets a full card with description, "How it works," "When to use," and "What you need." Use the same `step-connector` pattern but larger, with animated transitions between levels on scroll.
2. **Graduation criteria table** -- Styled table with metric thresholds. Cells that are "Any" are muted; cells with specific thresholds have colored backgrounds (green for easy, amber for moderate, red for strict).
3. **Risk meter per level** -- Four horizontal bars, each wider and more red than the last. L1: thin green. L2: medium amber. L3: wide orange. L4: full-width red.
4. **Monitor feedback loop visualization** -- An animated SVG showing the full cycle: Pipeline -> Deploy -> Production -> Monitor -> detect anomaly -> auto-create Issue -> Pipeline runs again. Use the `issues-arc` animation from the landing page pipeline.

### Diagrams Needed
1. **Maturity Pyramid (SVG):** Four horizontal bands stacked into a trapezoid/pyramid. Bottom (widest) = L1 Assisted. Top (narrowest) = L4 ASE. Each band is colored with increasing glow intensity. Arrow on the side pointing upward labeled "Increasing Autonomy." Arrow on the other side pointing upward labeled "Increasing Gate Quality Required."

2. **Human Involvement Per Level (SVG):** Four horizontal timelines, one per level. Each timeline shows the 7 pipeline phases as dots. Human intervention points are marked with a person icon above the dot. L1: person icon at every phase. L2: person icon at Plan approval, Test approval, Review approval. L3: person icon only at Ship (PR review). L4: no person icons.

3. **Monitor Safety Loop (SVG, animated):** Circular diagram: Pipeline -> Deploy -> Production -> Monitor. If Monitor detects anomaly, arrow back to Pipeline with a new issue. If no anomaly, green checkmark. Use the `issues-arc` animation with `#06B6D4` (monitor color) and `#EF4444` (fail color for anomaly).

### Code/Prompt Examples

**Example: Pipeline configuration for Level 2 (Supervised)**
```yaml
# pipeline.yaml — Level 2: Supervised
autonomy: supervised

checkpoints:
  after_plan:
    require: human_approval
    timeout: 24h
  after_test:
    require: human_approval
    timeout: 24h
  after_review:
    require: human_approval
    timeout: 24h

# Level 2 still uses all quality gates
gates:
  test:
    coverage_min: 80
    all_pass: true
  review:
    max_blockers: 0
    max_tech_debt: 5
```

**Example: Pipeline configuration for Level 4 (ASE)**
```yaml
# pipeline.yaml — Level 4: ASE
autonomy: ase

checkpoints: none  # No human approval required

gates:
  test:
    coverage_min: 90
    all_pass: true
    mutation_score_min: 70  # Stricter gates for zero-touch
  review:
    max_blockers: 0
    max_tech_debt: 2  # Lower tolerance
  deploy:
    require_linear_history: true
    max_files_changed: 20  # Safety limit

auto_merge:
  enabled: true
  require_ci_pass: true
  delay: 5m  # Wait 5 minutes before merging

monitor:
  anomaly_detection: true
  rollback_on: [error_rate_spike, latency_p99_increase]
  auto_create_issue: true
```

### Cross-Links
- Links to: `/concepts/self-healing` (loops are the mechanism that makes L3-L4 possible), `/concepts/tool-permissions` (permissions are the safety control at all levels), `/concepts/agentic-layer` (the layer quality determines the achievable autonomy level).
- Links to pipeline phases: Monitor (as safety valve), all phases (for checkpoint descriptions).

### Content Writer Notes
- **Tone:** Aspirational but grounded. Level 4 is exciting but not for everyone. The framework meets teams where they are.
- **Emphasis:** The maturity model is about gate quality, not ambition. You earn the right to remove humans from the loop by building gates that catch what humans would catch.
- **Analogy:** Self-driving cars. L1 = cruise control (driver does most work). L2 = lane assist + adaptive cruise (car handles some tasks, driver oversees). L3 = highway autopilot (car drives, human takes over when requested). L4 = fully autonomous (no driver needed in defined conditions). The conditions matter.
- **Avoid:** Do not promise or imply that Level 4 is the goal for every team. Frame it as the destination for teams that earn it through pipeline maturity. Do not minimize the risk.

---

## Concept Navigation Order

The 7 pages should be navigable in this order (prev/next links at page bottom):

1. The Agentic Layer (`/concepts/agentic-layer`)
2. Agent Orchestration Patterns (`/concepts/agent-patterns`)
3. Self-Healing Loops (`/concepts/self-healing`)
4. Artifact Chaining (`/concepts/artifact-chaining`)
5. Prompt Engineering Patterns (`/concepts/prompt-engineering`)
6. Tool Permission Design (`/concepts/tool-permissions`)
7. Autonomous Software Engineering (`/concepts/ase`)

This order moves from foundational (what is the agentic layer) through mechanics (how agents coordinate, how pipelines recover, how state flows) to techniques (prompt patterns, permission design) to the destination (ASE maturity model).

---

### Critical Files for Implementation
- `/Users/alejtr/Documents/obsidian/obsidian/agentic-layer-framework/website/index.html` - Design system source of truth: all Tailwind config, color tokens, component patterns (cards, code blocks, permission badges, pipeline SVGs, step connectors), animations, and layout conventions
- `/Users/alejtr/Documents/obsidian/obsidian/agentic-layer-framework/framework/Framework Overview.md` - Core philosophy and three-layer architecture text that Pages 1 and 7 must be consistent with
- `/Users/alejtr/Documents/obsidian/obsidian/agentic-layer-framework/pipeline/Pipeline Architecture.md` - Phase details, feedback loop definitions, and configuration points referenced across all 7 concept pages
- `/Users/alejtr/Documents/obsidian/obsidian/agentic-layer-framework/framework/Glossary.md` - Canonical term definitions that all concept pages must use consistently
- `/Users/alejtr/Documents/obsidian/obsidian/agentic-layer-framework/thinking/Open Questions.md` - Open design questions (orchestration model, state handling, config format) that concept pages now resolve with opinionated answersagentId: a798621e0ea2be6f7 (for resuming to continue this agent's work if needed)
<usage>total_tokens: 67039
tool_uses: 12
duration_ms: 404220</usage>