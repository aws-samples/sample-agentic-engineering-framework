I now have a complete understanding of all source materials. Here is the full page spec.

---

# Pipeline Section Page Spec

**Target file:** `/Users/alejtr/Documents/obsidian/obsidian/agentic-layer-framework/website/specs/pipeline-section.md`

This spec covers 8 HTML pages: 1 pipeline overview and 7 phase deep-dives. It is intended for a developer (to build the HTML/CSS/JS) and a tech content writer (to refine copy and prompt templates).

---

## Global Design System Reference

All pages inherit from the landing page at `/website/index.html`.

**Colors:**
- Background: Void `#09090B`, Surface `#111113`, Raised `#1A1A1F`, Subtle `#232329`
- Text: Primary `#F4F4F5`, Secondary `#A1A1AA`, Muted `#52525B`
- Accent: Glow `#6366F1`, Glow-hover `#818CF8`
- Phase colors: Plan `#8B5CF6`, Build `#F59E0B`, Test `#10B981`, Review `#3B82F6`, Document `#A78BFA`, Deploy `#F97316`, Monitor `#06B6D4`
- Status: Pass `#22C55E`, Fail `#EF4444`, Warning `#EAB308`

**Fonts:** IBM Plex Sans (body), JetBrains Mono (code, headings, badges)

**Shared Components (from landing page):**
- `.phase-card`: Surface bg, Subtle border, hover reveals `--phase-color` border
- `.perm-allowed` / `.perm-denied`: Green/red permission badges
- `.code-block`: Void bg, Subtle border, syntax classes `.var` `.keyword` `.string` `.comment` `.type`
- `.reveal`: Scroll-triggered fade-up animation
- `.flow-line` / `.pipeline-node` / `.loop-arc`: SVG animation keyframes
- `.nav-link`: Underline-on-hover nav links
- `.ambient-glow`: Blurred colored orbs for background atmosphere
- `.dot-grid`: Subtle dot pattern overlay

**Shared Layout for All 8 Pages:**
- Same `<nav>` as landing page. Add "Pipeline" as active link with dropdown listing all 7 phases.
- Same `<footer>` as landing page.
- Max-width container: `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8`
- Section padding: `py-24 sm:py-32`

---

## Page 1: Pipeline Overview

### URL and Title
- **URL:** `/pipeline/index.html` (or `/pipeline/`)
- **Title:** `Pipeline Architecture | Agentic Engineering Framework`

### Purpose
The central reference for the full 7-phase pipeline. Provides a large interactive diagram, artifact flow visualization, and summary table, then links to each phase deep-dive.

### Content Outline

#### Section 1: Hero Header
- **Heading:** `The Autonomous Pipeline`
- **Subheading:** `Seven phases. Three feedback loops. One PR at the end.`
- **Breadcrumb:** `AEF > Pipeline`
- **Ambient glow:** Glow indigo, top-center

#### Section 2: Interactive Pipeline Diagram
- **Description:** Full-width SVG, significantly larger and more detailed than the hero SVG on the landing page. Each phase node is clickable (links to phase page). Nodes use phase colors for stroke. Show role persona label beneath each node (Architect, Engineer, QA, Reviewer, Writer, Release, Ops).
- **Feedback loops:** Three animated dashed arcs:
  1. **Test Loop** (green `#10B981`): Test -> Build, label "retry (3x)"
  2. **Review-Patch Loop** (blue `#3B82F6`): Review -> Build, label "patch (3x)"
  3. **Monitor -> Plan Loop** (red `#EF4444`): Monitor -> Plan, label "issues"
- **Artifact labels on flow lines:** Between each pair of nodes, show the artifact name on the connecting line: `spec` (Plan->Build), `code + tests` (Build->Test), `test report` (Test->Review), `review verdict` (Review->Document), `docs` (Document->Deploy), `PR/commits` (Deploy->Monitor).
- **Interactive behavior:** Hover on a node highlights its incoming/outgoing connections and dims others. Click navigates to phase page.
- **Animation:** `flowPulse` on connections, `nodeBreath` on phase nodes, `dashFlow` on feedback arcs. All respect `prefers-reduced-motion`.

#### Section 3: Artifact Chain Visualization
- **Description:** Horizontal strip below the diagram showing a card for each artifact that flows between phases. Each card has:
  - Phase-colored left border
  - Artifact name in JetBrains Mono
  - Brief description (1 line)
  - Format badge (JSON, Markdown, Mixed)
- **Artifacts:** Plan Spec, Build Report, Test Report, Review Verdict, Documentation, Commit Log, KPI Report

#### Section 4: Summary Table
- **Description:** Full-width responsive table on Raised background.
- **Columns:** Phase | Role | Input | Output | Tools | Feedback Loop?
- **Rows:** One per phase. Phase name in phase color. Tools column uses permission badge components. Loop column shows "Test Loop (3x)" / "Review-Patch Loop (3x)" or em-dash for none.

| Phase | Role | Input | Output | Tools | Loop? |
|---|---|---|---|---|---|
| Plan | Software Architect | Task description, codebase context | Structured spec with file:line refs | Read, Search | -- |
| Build | Software Engineer | Approved plan | Code changes, tests, build report | Read, Search, Execute, Write | -- |
| Test | QA Engineer | Code changes, test suite | Test report (JSON + MD) | Read, Search, Execute, Write | Test Loop (3x) |
| Review | Senior Reviewer | Code changes, test results, plan | Review verdict JSON | Read, Search | Review-Patch Loop (3x) |
| Document | Technical Writer | Final changes, review summary | Updated docs, architecture notes | Read, Search, Write | -- |
| Deploy | Release Engineer | All artifacts | Atomic commits, PR | Read, Search, Execute | -- |
| Monitor | Operations | PR/merge data, pipeline metadata | KPI report | Read, Search, Execute | Issues -> Plan |

#### Section 5: Feedback Loops Deep-Dive
- **Description:** Three cards, one per loop type. Each card has:
  - Colored header bar (Test=green, Review=blue, Monitor=red)
  - Trigger condition
  - Action sequence (numbered steps)
  - Retry limit (configurable, default 3)
  - Escalation behavior
  - Small inline SVG flowchart

#### Section 6: Phase Grid (Quick Navigation)
- **Description:** 7 phase cards identical in structure to the landing page phase cards. Each links to the phase deep-dive page. Reuse the `.phase-card` component with colored dot, number, name, role, short description, and permission badges.

### UI Components
- Interactive SVG diagram (custom, phase-colored nodes, animated arcs)
- Artifact chain strip (horizontal scroll on mobile, flex on desktop)
- Summary table (`.code-block` style background, responsive)
- Feedback loop cards (Surface bg, phase-colored top border)
- Phase navigation grid (reuse `.phase-card` from landing page)
- Breadcrumb component (muted text, `>` separator)

### Interactive Elements
- **Sidebar (desktop):** Fixed left sidebar with vertical phase list. Each phase has a colored dot and name. Clicking scrolls to that phase's card or navigates to its page. Current page highlighted.
- **SVG hover:** Highlight connections on node hover. CSS transitions on opacity.
- **SVG click:** Navigate to `/pipeline/{phase-name}/`
- **Table row hover:** Row highlights with phase color at 8% opacity.

### Cross-Links
- Each phase name links to `/pipeline/{phase-name}/`
- "Self-Healing Loops" links to `/concepts/self-healing-loops/` (future)
- "Artifact Chaining" links to `/concepts/artifact-chaining/` (future)
- Back to landing page via nav logo

### Content Writer Notes
- **Tone:** Authoritative, concise, technical but approachable. Think senior engineer explaining architecture to a new team member.
- **Emphasis:** The pipeline is not linear -- the feedback loops are the differentiator. Make them visually prominent.
- **What makes this page unique:** It is the architectural map. Every other pipeline page links back here. It should feel like a control panel overview.

---

## Page 2: Plan Phase

### URL and Title
- **URL:** `/pipeline/plan/index.html`
- **Title:** `Plan Phase | Software Architect | AEF Pipeline`
- **Phase color:** `#8B5CF6` (Plan purple)

### Purpose
Deep-dive into the Plan phase: read-only research, issue-type routing, multi-agent research pattern, and structured spec output.

### Content Outline

#### Section 1: Phase Header
- **Phase badge:** `01` in Plan purple with glowing dot
- **Heading:** `Plan` (JetBrains Mono, Plan purple)
- **Role:** `Software Architect`
- **One-liner:** `Research first, plan second. Read-only always.`
- **Permission badge row:** `Read` (allowed), `Search` (allowed), `Execute` (denied), `Write` (denied)
- **Left border:** 4px Plan purple on the header card

#### Section 2: Why This Phase Exists
- **Heading:** `Why This Phase Exists`
- **Content:**
  - The most common failure mode in agentic development is agents that start building before they understand the codebase. They hallucinate file paths, miss existing patterns, and create solutions that conflict with the architecture.
  - Plan exists to enforce a research-then-decide discipline. By making this phase strictly read-only, we guarantee the agent cannot modify anything while it is still forming its understanding.
  - Positioned first because every downstream phase depends on a well-scoped specification. A bad plan cascades: the Build creates the wrong thing, Test validates the wrong behavior, Review flags fundamental issues, and the entire pipeline loops back.

#### Section 3: Methodology
- **Heading:** `Methodology`
- **Content:** Step-by-step numbered list:
  1. **Receive task description** -- Parse the issue/ticket/request. Identify issue type (feature, bug, task, patch).
  2. **Route to issue-type template** -- Different issue types require different planning approaches. Features need EARS user stories and architecture analysis. Bugs need root cause analysis. Tasks need scope boundaries. Patches need minimal-change analysis.
  3. **Research phase (parallel subagents)** -- Spawn 3 subagents simultaneously:
     - **Locator:** Find all files relevant to the task using Glob and Search. Map the dependency graph.
     - **Analyzer:** Read the identified files. Understand current patterns, conventions, test structure.
     - **Pattern Finder:** Search for similar implementations in the codebase. Identify reusable patterns.
  4. **Synthesize findings** -- Main agent consolidates subagent results into a coherent picture.
  5. **Generate specification** -- Produce the structured plan with file:line references, change list, anti-scope-creep section, and test strategy.
  6. **Self-validate** -- Review the spec against the original task. Check completeness. Verify all referenced files exist.

#### Section 4: Inputs & Outputs
- **Heading:** `Inputs & Outputs`
- **Inputs card:** (Surface bg, left border Plan purple)
  - Task description (from user/ticket system)
  - Issue type: feature | bug | task | patch
  - Branch name
  - Codebase context (agentic layer config, project docs)
  - Source: External (user, ticket system, or Monitor phase feedback)
- **Outputs card:** (Surface bg, left border Build amber -- because it flows to Build)
  - Structured specification (Markdown)
  - Contains: Summary, files to modify (with line refs), files to create, "What we are NOT doing" section, test strategy, acceptance criteria
  - Consumed by: Build phase as `$plan_artifact`
- **Output format:** Show a code block with the plan output template:

```
# Plan: ${issue_title}

## Summary
[1-2 paragraph description of what will be built and why]

## Issue Type
${issue_type}  # feature | bug | task | patch

## Files to Modify
- `src/auth/login.ts:42-67` — Refactor token validation logic
- `src/auth/types.ts:12` — Add new TokenConfig interface

## Files to Create
- `src/auth/__tests__/login.test.ts` — Unit tests for new validation
- `src/auth/token-config.ts` — Configuration module

## What We Are NOT Doing
- Not refactoring the entire auth module
- Not changing the session management layer
- Not updating API contracts

## Test Strategy
- Unit tests for token validation edge cases
- Integration test for login flow with new config

## Acceptance Criteria
- [ ] Token validation handles expired tokens gracefully
- [ ] Existing tests continue to pass
- [ ] New tests cover all edge cases listed above
```

#### Section 5: Agent Pattern
- **Heading:** `Agent Pattern`
- **Pattern:** Multi-agent (parallel research fan-out)
- **Diagram:** SVG showing:
  - Main Planner agent at top
  - Three subagents below in parallel: Locator, Analyzer, Pattern Finder
  - Arrows from subagents back up to Main Planner
  - Final output arrow from Main Planner down to "Plan Spec"
- **When to use which pattern:**
  - Small tasks (patches, tiny bugs): Single agent is sufficient. Skip the parallel fan-out.
  - Medium tasks (features, larger bugs): Full 3-subagent pattern.
  - Large tasks (multi-system features): Add domain-specific subagents (e.g., "API Analyzer", "Database Analyzer").

#### Section 6: Tool Permissions
- **Heading:** `Tool Permissions`
- **Badge row:** `Read` (green), `Search` (green), `Glob` (green), `Git log/diff` (green), `Execute` (red), `Write` (red), `Git commit` (red)
- **Rationale:** The Plan phase is deliberately read-only. Allowing write access creates a temptation for the agent to "just fix this quick thing" while planning, which breaks the separation of concerns. Execute is denied because running tests or scripts could have side effects, and the Planner does not need empirical validation -- it needs structural understanding.
- **What "limited git" means:** `git log`, `git diff`, `git status`, `git show` are allowed. `git add`, `git commit`, `git push`, `git checkout` are denied.

#### Section 7: Prompt Template
- **Heading:** `Prompt Template`
- **Description:** Full annotated prompt displayed in a code-block component with syntax highlighting. Template variables in `.var` (indigo). Keywords in `.keyword` (violet). Strings/constraints in `.string` (emerald). Comments as annotations in `.comment` (muted).

**Sample Prompt Template (Plan Phase -- Feature variant):**

```
# Plan Phase — Software Architect

## Role
You are a Software Architect. Your job is to research the
codebase and produce a detailed implementation plan.

You do NOT write code. You do NOT modify files. You are
read-only. Your output is a specification that a Software
Engineer will execute.

## Context
Issue: ${issue_description}
Type: ${issue_type}                     # feature | bug | task | patch
Branch: ${branch_name}
Repository: ${repo_name}
Agentic Layer Config: ${agentic_layer_path}

## Issue-Type Routing

### If feature:
- Write EARS-format user stories (stimulus-response)
- Analyze architectural impact across modules
- Identify integration points with existing systems
- Propose test strategy: unit, integration, E2E

### If bug:
- Perform root cause analysis
- Trace the bug from symptom to source
- Identify minimal fix surface (fewest files touched)
- Check for similar bugs elsewhere in the codebase

### If task:
- Define clear scope boundaries
- Identify dependencies and ordering constraints
- List files affected with specific line ranges

### If patch:
- Identify exact lines to change
- Verify no side effects in adjacent code
- Minimal change only — no refactoring

## Research Protocol
Before planning, you MUST complete these research steps:

1. Use Glob to find all files related to the task area
2. Read each relevant file to understand current patterns
3. Search for similar implementations in the codebase
4. Check existing test patterns for the affected modules
5. Review recent git history for the affected files

## Constraints
- Read-only. Do not modify any files.
- Research before planning. Never plan and execute simultaneously.
- Reference specific file:line locations for every change.
- Every file you reference MUST exist. Verify with Read.
- Do not add scope. If the issue says "fix login timeout",
  do not also refactor the auth module.

## Output Format
Produce a structured specification with these exact sections:

1. **Summary** — What will change and why (2-3 sentences)
2. **Files to Modify** — Each with file:line range and description
3. **Files to Create** — Each with purpose and location
4. **What We Are NOT Doing** — Explicit anti-scope-creep
5. **Test Strategy** — What tests to write, what they validate
6. **Acceptance Criteria** — Checkboxes, verifiable conditions
7. **Risk Assessment** — What could go wrong, mitigation steps

## Quality Checks (Self-Validation)
Before submitting your plan, verify:
- [ ] Every referenced file exists (you read it)
- [ ] Line numbers are accurate (you checked them)
- [ ] The plan addresses the full issue, nothing more
- [ ] Test strategy covers happy path and edge cases
- [ ] "What we are NOT doing" section is present and specific
```

- **Annotations panel** (below code block, using annotation badges from landing page):
  - `Role Assignment` (Plan purple bg) -- Establishes persona and read-only constraint upfront
  - `Template Variables` (Glow indigo bg) -- `${issue_description}`, `${issue_type}`, `${branch_name}`, `${repo_name}`, `${agentic_layer_path}`
  - `Issue-Type Routing` (amber bg) -- Conditional logic based on issue type
  - `Anti-Scope-Creep` (red bg) -- Explicit "What we are NOT doing" output section
  - `Self-Validation` (green bg) -- Checklist the agent runs against its own output

#### Section 8: Best Practices
- **Heading:** `Best Practices`
- **Do's** (green left border):
  - Do read every file you reference before citing it
  - Do include line numbers for every modification target
  - Do write an explicit anti-scope-creep section
  - Do route different issue types to different planning approaches
  - Do validate that your plan addresses the complete issue
- **Don'ts** (red left border):
  - Do not modify any files during planning
  - Do not plan and build in the same agent invocation
  - Do not reference files you have not read
  - Do not expand scope beyond the original issue
  - Do not skip the research phase for "simple" tasks

#### Section 9: Nuances
- **Heading:** `Nuances`
- **Content:**
  - **EARS user stories for features:** Use the Easy Approach to Requirements Syntax. Format: "When [stimulus], the system shall [response]." This gives Build agents testable, unambiguous acceptance criteria.
  - **Root cause analysis for bugs:** Do not stop at the symptom. Trace the call chain from where the bug manifests to where the defect originates. The plan should target the root, not the symptom.
  - **Plan validation by second agent:** In multi-agent setups, a second agent can review the plan before it passes to Build. This catches hallucinated file paths, unrealistic scope, and missing test strategies.
  - **Context window management:** For large codebases, the Planner should not try to read everything. The parallel subagent pattern (Locator, Analyzer, Pattern Finder) distributes the reading load across separate context windows.
  - **Issue-type templates are extensible:** The four types (feature, bug, task, patch) are defaults. Teams can add custom types (e.g., "refactor", "security-fix", "performance") with their own planning templates.

### UI Components
- Phase header card with Plan purple left border and glowing dot
- Permission badge row (reuse `.perm-allowed` / `.perm-denied`)
- Input/Output artifact cards with phase-colored left borders
- Code block for output format template (`.code-block` with syntax highlighting)
- Large code block for prompt template (`.code-block`, full width)
- Annotation badges below prompt template
- Do/Don't cards with green/red left borders
- Multi-agent diagram (inline SVG, Plan purple nodes)

### Interactive Elements
- **Phase sidebar (desktop):** Fixed left sidebar listing all 7 phases with colored dots. Plan is highlighted/active. Clicking any phase navigates to that phase page.
- **Prompt template viewer:** Code block with line numbers. Hover on template variables highlights them in glow color. Optional "Copy" button top-right.
- **Issue-type tabs:** Within the Methodology section, tabs for Feature / Bug / Task / Patch showing the routing difference for each type.
- **Agent pattern diagram:** Hover to see data flow labels.

### Cross-Links
- Previous phase: None (Plan is first)
- Next phase: `/pipeline/build/` (Build)
- Back to overview: `/pipeline/`
- Related concepts: Artifact Chaining, Prompt Engineering Patterns, Tool Permission Design

### Content Writer Notes
- **Tone:** Calm, deliberate. This phase is about restraint -- the agent is powerful but we are holding it back on purpose.
- **Emphasis:** Read-only is non-negotiable. The anti-scope-creep section is the most important output. Issue-type routing is a key differentiator.
- **What makes this phase unique:** It is the only phase that produces no code. Its entire value is in the quality of its specification. A perfect plan makes every subsequent phase easier.

---

## Page 3: Build Phase

### URL and Title
- **URL:** `/pipeline/build/index.html`
- **Title:** `Build Phase | Software Engineer | AEF Pipeline`
- **Phase color:** `#F59E0B` (Build amber)

### Purpose
Deep-dive into the Build phase: TDD-first methodology, single-agent with builder subagent delegation, full tool access, and structured build report output.

### Content Outline

#### Section 1: Phase Header
- Phase badge `02`, Build amber, glowing dot
- Heading: `Build` / Role: `Software Engineer`
- One-liner: `TDD-first. Follow the plan. No improvising.`
- Permission badges: Read (allowed), Search (allowed), Execute (allowed), Write (allowed)

#### Section 2: Why This Phase Exists
- Agents without a plan tend to hallucinate solutions. Build exists to execute a pre-validated specification with discipline.
- It is positioned after Plan because the spec is its contract. Without a spec, Build has no objective completion criteria.
- TDD-first means the agent writes its own success criteria before writing the solution. This is the quality contract every downstream phase validates against.

#### Section 3: Methodology
1. **Receive plan artifact** -- Parse `$plan_artifact` from Plan phase. Verify it includes file targets, change descriptions, and test strategy.
2. **Read existing code** -- Before modifying any file, read it in full. Understand the current implementation, patterns, imports, and adjacent code.
3. **Write tests first** -- Based on the plan's test strategy, write failing tests. These tests define the build's success criteria.
4. **Implement changes** -- Write code to make the tests pass. Follow the plan's file:line targets exactly. Track every file and line modified.
5. **Run tests locally** -- Execute the test suite to verify the implementation passes.
6. **Generate build report** -- Produce structured output listing all changes, verification steps, and any deviations from the plan.

#### Section 4: Inputs & Outputs
- **Inputs:** Plan artifact (`$plan_artifact`) from Plan phase, codebase access
- **Outputs:** Modified code, new test files, Build Report (Markdown)
- **Build Report format:**

```
# Build Report

## Status: ${build_status}  # complete | partial | blocked

## Changes Made
| File | Lines | Action | Description |
|------|-------|--------|-------------|
| src/auth/login.ts | 42-67 | Modified | Refactored token validation |
| src/auth/token-config.ts | 1-45 | Created | New configuration module |
| src/auth/__tests__/login.test.ts | 1-120 | Created | Unit tests for validation |

## Tests Written
- test_expired_token_returns_401 — PASS
- test_valid_token_refreshes_session — PASS
- test_malformed_token_throws — PASS

## Verification Steps
1. Run: npm test -- --testPathPattern=auth
2. Expected: 3 tests pass, 0 failures

## Deviations from Plan
- None (or list any necessary deviations with justification)
```

#### Section 5: Agent Pattern
- **Pattern:** Single agent with builder subagent delegation
- **Diagram:** Main Build agent at top. Arrow down to Builder Subagent. Arrow back up with "completed changes". Reason: context window protection. The main agent holds the plan and tracks progress. The subagent does the actual file editing, which consumes context window rapidly.
- **When to use delegation:** When the plan involves more than 3-4 files, delegate to a subagent. For tiny patches (1-2 files), single agent is sufficient.

#### Section 6: Tool Permissions
- **Badge row:** Read (green), Search (green), Execute (green), Write (green) -- all allowed
- **Rationale:** Build is the only phase (along with Test) that needs full access. It must read existing code, write new code, and execute tests to verify. This is the phase where work happens.
- **Caveat:** Full access does not mean unrestricted behavior. The plan is the constraint. The agent should only modify files listed in the plan.

#### Section 7: Prompt Template

```
# Build Phase — Software Engineer

## Role
You are a Software Engineer. Your job is to implement the
changes described in the plan below. You follow TDD: write
tests first, then implementation.

You do NOT deviate from the plan. You do NOT add features
the plan didn't ask for. You do NOT refactor code outside
the plan's scope.

## Context
Plan Artifact:
${plan_artifact}

Branch: ${branch_name}
Test Command: ${test_command}          # e.g., npm test, pytest, go test
Working Directory: ${working_directory}

## Methodology — TDD First

### Step 1: Read Before Writing
For every file listed in the plan's "Files to Modify" section,
read the full file first. Understand:
- Current implementation and patterns
- Import structure and dependencies
- Adjacent code that might be affected
- Existing test patterns for this module

### Step 2: Write Tests
Based on the plan's Test Strategy, create test files:
- One test per acceptance criterion
- Follow existing test patterns in the codebase
- Tests MUST fail initially (they test unwritten code)
- Name tests descriptively: test_[scenario]_[expected_result]

### Step 3: Implement
Write code to make the failing tests pass:
- Follow existing code patterns and conventions
- Import style matches the rest of the codebase
- Only modify files listed in the plan
- Track every file:line you change

### Step 4: Verify
Run the test command: ${test_command}
- All new tests must pass
- All existing tests must still pass
- If tests fail, fix the implementation (not the tests)

## Constraints
- Follow the plan exactly. No scope creep.
- Read existing code before modifying it.
- Write tests before implementation.
- Track every file and line number changed.
- Do not modify files not listed in the plan.
- Do not refactor adjacent code "while you're in there."

## Output Format
Produce a Build Report with:
1. **Status** — complete | partial | blocked
2. **Changes Made** — Table: File | Lines | Action | Description
3. **Tests Written** — List with names and pass/fail status
4. **Verification Steps** — Commands to run, expected results
5. **Deviations from Plan** — Any necessary deviations with justification
```

- **Annotations:** `Role Assignment`, `Template Variables` (`${plan_artifact}`, `${branch_name}`, `${test_command}`, `${working_directory}`), `TDD Protocol`, `Anti-Scope-Creep`, `Structured Output`

#### Section 8: Best Practices
- **Do's:** Read every file before modifying it. Write tests before implementation. Track every change with file:line precision. Follow existing code patterns. Run tests after every significant change.
- **Don'ts:** Do not add features not in the plan. Do not refactor code outside the plan scope. Do not skip the test-first step. Do not use `git add -A`. Do not assume file contents -- always read first.

#### Section 9: Nuances
- **"Read existing code before modifying"** is the single most impactful instruction. Without it, agents overwrite existing logic, break imports, and create style inconsistencies.
- **Context window protection:** For large builds, the main agent should delegate to a subagent. The subagent does the editing work (which consumes tokens rapidly). The main agent retains the plan and overall progress state.
- **Handling plan ambiguity:** If the plan is unclear about a specific implementation detail, the Build agent should choose the most conservative approach and note the ambiguity in the Deviations section. Never guess.
- **Partial completion:** If the Build cannot complete all changes (e.g., blocked by missing dependency), it should produce a `partial` status with clear documentation of what was completed and what remains.

### UI Components
- Phase header card with Build amber left border
- Full permission badge row (all green)
- Input/Output cards
- Code block for Build Report template
- Agent delegation diagram (inline SVG)
- Prompt template viewer (full-width code block)
- Do/Don't cards

### Interactive Elements
- Phase sidebar (Build highlighted)
- Prompt template with copyable code and variable highlighting
- Methodology step-through: clickable numbered steps that expand detail

### Cross-Links
- Previous: `/pipeline/plan/`
- Next: `/pipeline/test/`
- Overview: `/pipeline/`
- Related: TDD-first (Decisions Log 003), Artifact Chaining

### Content Writer Notes
- **Tone:** Disciplined, methodical. This is a craftsman following blueprints precisely.
- **Emphasis:** TDD-first is the core identity. The plan is sacred -- deviation is failure.
- **Unique:** This is the only phase where code actually gets written. All other phases read, analyze, or ship.

---

## Page 4: Test Phase

### URL and Title
- **URL:** `/pipeline/test/index.html`
- **Title:** `Test Phase | QA Engineer | AEF Pipeline`
- **Phase color:** `#10B981` (Test emerald)

### Purpose
Deep-dive into the Test phase: run-everything-first methodology, failure categorization, self-healing retry loop, and dual-format test report.

### Content Outline

#### Section 1: Phase Header
- Phase badge `03`, Test emerald
- Heading: `Test` / Role: `QA Engineer`
- One-liner: `Run everything. Analyze all failures. Fix one at a time.`
- Permissions: Read (allowed), Search (allowed), Execute (allowed), Write (allowed)

#### Section 2: Why This Phase Exists
- Agents produce code that often passes their own narrow tests but breaks integration points. Test exists as an independent validation gate.
- It is positioned after Build to validate the entire implementation as a unit, not just individual files.
- The self-healing loop means most test failures never reach a human. The pipeline fixes itself.

#### Section 3: Methodology
1. **Receive build artifacts** -- Code changes, new tests, build report, test commands.
2. **Run full test suite** -- Execute ALL tests, not just new ones. Capture complete output.
3. **Analyze ALL failures at once** -- Do not fix the first failure and re-run. Read every failure first. Categorize them.
4. **Categorize failures:**
   - **Test bug:** The test itself is wrong (bad assertion, wrong expectation).
   - **Implementation bug:** The code does not match the plan's intent.
   - **Integration issue:** The change broke something in an adjacent module.
5. **Fix one issue at a time** -- Starting with the most fundamental. Re-run after each fix.
6. **Re-validate** -- After all fixes, run the full suite again to confirm no regressions.
7. **Generate test report** -- Dual format: JSON for machine consumption, Markdown for human review.

#### Section 4: Inputs & Outputs
- **Inputs:** Code changes from Build, test suite, test commands, build report
- **Outputs:** Test Report (dual format)
- **JSON format:**

```json
{
  "status": "pass",
  "total_tests": 47,
  "passed": 47,
  "failed": 0,
  "skipped": 0,
  "iterations": 2,
  "fixes_applied": [
    {
      "file": "src/auth/__tests__/login.test.ts",
      "line": 34,
      "category": "test_bug",
      "description": "Fixed assertion to match updated return type"
    }
  ],
  "coverage": {
    "statements": 94.2,
    "branches": 88.1,
    "functions": 96.7,
    "lines": 93.8
  }
}
```

- **Markdown format:**

```
# Test Report

## Result: PASS ✅
- Total: 47 | Passed: 47 | Failed: 0 | Skipped: 0
- Iterations: 2 (1 self-healing fix applied)

## Fixes Applied
1. `src/auth/__tests__/login.test.ts:34` — Test bug: fixed
   assertion to match updated return type

## Coverage
| Metric | Value |
|--------|-------|
| Statements | 94.2% |
| Branches | 88.1% |
| Functions | 96.7% |
| Lines | 93.8% |
```

#### Section 5: Agent Pattern
- **Pattern:** Single agent with conditional builder subagent for fixes
- **Diagram:** Test Agent runs tests. On failure, spawns Builder Subagent to fix. Re-runs tests. Loop arrow with "max 3x" label.

#### Section 6: Tool Permissions
- **Badge row:** All allowed (Read, Search, Execute, Write)
- **Rationale:** Test needs Execute to run test suites and Write to fix issues during self-healing. Without Write, the self-healing loop would be impossible.

#### Section 7: Prompt Template

```
# Test Phase — QA Engineer

## Role
You are a QA Engineer. Your job is to validate the
implementation by running all tests, analyzing failures
systematically, and fixing issues one at a time.

You are methodical. You never fix multiple issues at once.
You always run the full suite first, analyze everything,
then fix sequentially.

## Context
Build Report:
${build_report}

Test Command: ${test_command}
Coverage Command: ${coverage_command}   # optional
Working Directory: ${working_directory}
Max Retry Iterations: ${max_retries}    # default: 3

## Methodology — Systematic Validation

### Step 1: Run Everything
Execute: ${test_command}
Capture the full output. Do NOT stop at the first failure.

### Step 2: Analyze ALL Failures
For each failing test, determine:
- Is this a TEST BUG? (wrong assertion, outdated expectation)
- Is this an IMPLEMENTATION BUG? (code doesn't match spec)
- Is this an INTEGRATION ISSUE? (change broke adjacent module)

### Step 3: Fix One at a Time
Starting with the most fundamental issue:
1. Fix the single issue
2. Re-run the full test suite
3. Verify the fix didn't introduce new failures
4. Move to the next issue

### Step 4: Coverage Check (if coverage command provided)
Run: ${coverage_command}
Report coverage metrics in the output.

## Self-Healing Loop
If tests fail after your fixes:
- Iteration 1: Analyze and fix
- Iteration 2: Re-analyze remaining failures
- Iteration 3: Final attempt
- After ${max_retries} iterations: ESCALATE with full context

## Failure Categorization Rules
- TEST BUG: The test asserts the wrong thing. Fix the test.
- IMPLEMENTATION BUG: The code is wrong. Fix the implementation.
  Refer back to ${plan_artifact} for intended behavior.
- INTEGRATION ISSUE: The change broke something else. This may
  need to go back to Build for a broader fix.

## Constraints
- Run the FULL test suite first. Do not run partial tests.
- Analyze ALL failures before fixing any.
- Fix ONE issue at a time. Re-run after each fix.
- Never fix multiple issues in a single edit.
- Track every fix with file:line and category.
- Distinguish test bugs from implementation bugs.

## Output Format
Produce a Test Report in BOTH formats:

### JSON (for machine consumption):
{
  "status": "pass|fail",
  "total_tests": N,
  "passed": N,
  "failed": N,
  "skipped": N,
  "iterations": N,
  "fixes_applied": [
    {"file": "", "line": N, "category": "", "description": ""}
  ],
  "coverage": {"statements": N, "branches": N, "functions": N, "lines": N},
  "escalation_needed": false,
  "escalation_reason": ""
}

### Markdown (for human review):
Summary table, fixes list, coverage table.
```

- **Annotations:** `Role Assignment`, `Template Variables`, `Failure Categorization`, `Self-Healing Protocol`, `Dual Output Format`

#### Section 8: Best Practices
- **Do's:** Run full suite first. Categorize every failure. Fix one issue per iteration. Track all fixes. Generate both output formats.
- **Don'ts:** Do not stop at the first failure. Do not fix multiple issues at once. Do not skip the full re-run after each fix. Do not change test assertions to make them pass without understanding why they fail.

#### Section 9: Feedback Loop
- **Heading:** `Self-Healing Loop`
- **Flowchart diagram** (inline SVG, Test emerald colored):

```
[Run Tests] --> {All Pass?}
  YES --> [Generate Report] --> DONE
  NO  --> [Analyze Failures] --> [Fix One Issue] --> [Re-run Tests]
        --> {All Pass?}
          YES --> [Generate Report] --> DONE
          NO  --> {Iteration < Max?}
            YES --> [Analyze Remaining] --> [Fix Next Issue] --> loop
            NO  --> [ESCALATE] --> Generate report with escalation_needed: true
```

- **Retry limit:** Default 3, configurable via `${max_retries}`
- **Escalation:** After max retries, produce full report with `escalation_needed: true`, include all attempted fixes, remaining failures, and suggested root causes.

#### Section 10: Nuances
- **"Analyze all failures first"** prevents cascading fix attempts. Often, 5 test failures share one root cause. Fixing that root cause resolves all 5.
- **Test bugs vs implementation bugs:** The agent must distinguish between "the test is wrong" and "the code is wrong." Without this distinction, agents default to making tests pass by weakening assertions.
- **Integration issues are special:** If a change in `auth/login.ts` breaks a test in `billing/invoice.ts`, that is an integration issue. It may require going back to Build for a broader fix rather than patching in Test.
- **Coverage is advisory, not blocking:** Coverage metrics are reported but do not fail the phase by default. Teams can configure coverage thresholds in quality gates.

### Interactive Elements
- Phase sidebar (Test highlighted)
- Feedback loop flowchart with animated dashed lines
- Toggle between JSON and Markdown output format views
- Iteration counter animation showing retry loop in action

### Cross-Links
- Previous: `/pipeline/build/`
- Next: `/pipeline/review/`
- Overview: `/pipeline/`
- Related: Self-Healing Loops concept, Test Loop (Glossary)

### Content Writer Notes
- **Tone:** Systematic, patient. This phase is about thoroughness, not speed.
- **Emphasis:** The "fix one at a time" discipline is the core insight. The dual output format serves two audiences (agents and humans).
- **Unique:** This is the first feedback loop in the pipeline. The self-healing mechanism is what makes the pipeline autonomous rather than just automated.

---

## Page 5: Review Phase

### URL and Title
- **URL:** `/pipeline/review/index.html`
- **Title:** `Review Phase | Senior Reviewer | AEF Pipeline`
- **Phase color:** `#3B82F6` (Review blue)

### Purpose
Deep-dive into the Review phase: read-only analysis, issue severity classification, review-patch loop, and parallel subagent pattern for large diffs.

### Content Outline

#### Section 1: Phase Header
- Phase badge `04`, Review blue
- Heading: `Review` / Role: `Senior Reviewer`
- One-liner: `Read-only analysis. Compare implementation against plan.`
- Permissions: Read (allowed), Search (allowed), Execute (denied), Write (denied)

#### Section 2: Why This Phase Exists
- Even with TDD and self-healing tests, agents can produce code that technically works but is architecturally wrong, insecure, or misaligned with the plan.
- Review is the second read-only gate (after Plan). It cannot modify code -- it can only judge and report. This separation prevents the reviewer from "just fixing it," which would bypass the disciplined Build->Test cycle.
- Positioned after Test because passing tests are a prerequisite. There is no value in reviewing code that does not work.

#### Section 3: Methodology
1. **Receive artifacts** -- Code changes (diff), test results, original plan, build report.
2. **Compare implementation against plan** -- Does the code do what the plan specified? Are all planned changes present? Are there unplanned changes?
3. **Analyze code quality** -- Correctness, security, style, performance, test coverage adequacy.
4. **Classify issues** by severity:
   - **Blocker:** Must be fixed before the pipeline continues. Security vulnerabilities, logic errors, missing functionality.
   - **Tech Debt:** Real issues that should be tracked but do not block this PR. Suboptimal patterns, missing edge case tests, documentation gaps.
   - **Skippable:** Stylistic preferences, minor naming suggestions. Logged but not actioned.
5. **Generate review verdict** -- JSON output with success boolean, issues array, and severity classification.
6. **Trigger patch loop if blockers found** -- Blockers generate a patch context that goes back to Build, then Test, then re-Review.

#### Section 4: Inputs & Outputs
- **Inputs:** Code diff, test report, plan artifact, build report
- **Outputs:** Review Verdict (JSON)
- **Output format:**

```json
{
  "success": false,
  "summary": "Implementation correct but missing input validation on token endpoint",
  "issues": [
    {
      "severity": "blocker",
      "file": "src/auth/login.ts",
      "line": 55,
      "description": "Token endpoint accepts malformed JWT without validation",
      "suggestion": "Add JWT format validation before processing"
    },
    {
      "severity": "tech_debt",
      "file": "src/auth/token-config.ts",
      "line": 12,
      "description": "Magic number 3600 should be a named constant",
      "suggestion": "Extract to TOKEN_EXPIRY_SECONDS constant"
    }
  ],
  "stats": {
    "blockers": 1,
    "tech_debt": 1,
    "skippable": 0
  },
  "patch_context": "Add JWT format validation in login.ts:55 before the existing token processing logic. Use the jsonwebtoken library's decode() with { complete: true } to verify structure before verify()."
}
```

#### Section 5: Agent Pattern
- **Pattern:** Single agent for normal diffs. Parallel subagents for large diffs.
- **Parallel pattern:** For large PRs (50+ files), spawn specialized reviewers:
  - Backend Reviewer -- focuses on API, database, business logic
  - Frontend Reviewer -- focuses on UI, state management, accessibility
  - Test Coverage Reviewer -- focuses on test adequacy, edge cases, coverage gaps
  - Main Reviewer -- synthesizes subagent findings into the final verdict
- **Diagram:** SVG showing main reviewer delegating to 3 parallel subagents, collecting results, producing final verdict.

#### Section 6: Tool Permissions
- **Badge row:** Read (green), Search (green), Execute (red), Write (red)
- **Rationale:** Review is deliberately read-only. If the reviewer could fix issues directly, it would bypass the Build->Test cycle. By limiting to Read/Search, we force all fixes through the disciplined patch loop. The reviewer's power is in its judgment, not its hands.

#### Section 7: Prompt Template

```
# Review Phase — Senior Reviewer

## Role
You are a Senior Reviewer. Your job is to analyze the
implementation and compare it against the original plan.

You do NOT modify code. You do NOT run tests. You analyze
and produce a verdict. If blockers are found, you provide
patch context for the Build agent to act on.

## Context
Plan Artifact:
${plan_artifact}

Build Report:
${build_report}

Test Report:
${test_report}

Code Diff:
${code_diff}

Review Iteration: ${review_iteration}   # 1, 2, or 3
Max Review Iterations: ${max_review_iterations}  # default: 3

## Review Checklist

### 1. Plan Compliance
- Does the implementation match the plan's specification?
- Are all planned files modified/created?
- Are there unplanned changes? (flag as potential scope creep)

### 2. Correctness
- Does the logic correctly implement the intended behavior?
- Are edge cases handled?
- Are error paths handled gracefully?

### 3. Security
- Input validation on all external data?
- No hardcoded secrets or credentials?
- No SQL injection, XSS, or path traversal vectors?
- Authentication/authorization checks in place?

### 4. Code Quality
- Follows existing codebase patterns and conventions?
- No unnecessary complexity or over-engineering?
- Functions are focused and testable?
- No dead code or commented-out blocks?

### 5. Test Adequacy
- Do tests cover the happy path?
- Do tests cover error/edge cases?
- Are test assertions specific (not just "no error thrown")?
- Does coverage meet the project threshold?

## Issue Classification
Classify every issue into exactly one category:

- BLOCKER: Must fix now. Security issues, logic errors,
  missing functionality, failing edge cases.
- TECH_DEBT: Real issue, but does not block this change.
  Log it for a future task.
- SKIPPABLE: Style preference, minor naming. Note it but
  do not action it.

## Patch Context (for blockers only)
For each blocker, provide a "patch context" string that
gives the Build agent enough information to fix the issue
without re-reading the entire codebase:
- What file and line to change
- What the current code does wrong
- What the fix should accomplish
- Any relevant code snippets

## Visual Review (if UI changes detected)
If ${code_diff} includes changes to UI files (.tsx, .vue,
.html, .css):
- Note that visual review via browser automation should be
  performed by the team's visual review process
- Flag any accessibility concerns visible in the code

## Constraints
- Read-only. Do not modify any files.
- Do not run tests. Trust the Test Report.
- Classify EVERY issue. No unclassified findings.
- Provide patch context for every blocker.
- Be specific: file:line references for every issue.

## Output Format
Produce a Review Verdict in JSON:
{
  "success": true/false,
  "summary": "One-sentence overall assessment",
  "issues": [
    {
      "severity": "blocker|tech_debt|skippable",
      "file": "path/to/file.ts",
      "line": N,
      "description": "What is wrong",
      "suggestion": "How to fix it"
    }
  ],
  "stats": {"blockers": N, "tech_debt": N, "skippable": N},
  "patch_context": "Combined patch instructions for all blockers"
}

success = true only when blockers == 0.
```

- **Annotations:** `Role Assignment`, `Template Variables`, `Issue Classification`, `Patch Context Pattern`, `Visual Review`, `Structured Output`

#### Section 8: Best Practices
- **Do's:** Compare against the plan, not your personal preference. Classify every issue. Provide specific file:line references. Write actionable patch context for every blocker.
- **Don'ts:** Do not try to fix code yourself. Do not flag style preferences as blockers. Do not ignore security concerns. Do not rubber-stamp -- actually read the diff.

#### Section 9: Feedback Loop
- **Heading:** `Review-Patch Loop`
- **Flowchart:**

```
[Review] --> {Blockers Found?}
  NO  --> [Pass Verdict] --> Document Phase
  YES --> [Generate Patch Context] --> [Build: Apply Patches]
        --> [Test: Re-validate] --> [Review: Re-review]
        --> {Blockers Found?}
          NO  --> [Pass Verdict] --> Document Phase
          YES --> {Iteration < Max?}
            YES --> loop
            NO  --> [ESCALATE to Human]
```

- **Retry limit:** Default 3, configurable
- **Escalation:** After max review iterations, the full context (plan, build report, test report, review history) is surfaced to a human reviewer.

#### Section 10: Nuances
- **Visual review via browser automation:** For UI changes, some teams use Playwright or similar tools to take screenshots and compare against expectations. This is not built into the Review phase but is flagged as a team-level enhancement.
- **The "patch context" concept:** When the reviewer finds a blocker, it does not just say "this is wrong." It provides a mini-specification for the fix: what file, what line, what is wrong, and what the fix should accomplish. This gives the Build agent enough context to fix the issue without re-reading the entire codebase.
- **Parallel reviewers for large diffs:** When a PR touches 50+ files across multiple domains, a single reviewer agent may miss domain-specific issues. Spawning specialized subagents (backend, frontend, test coverage) ensures thorough review.
- **Tech debt tracking:** Tech debt issues should be logged in a format that can be automatically converted to tickets. The Review phase generates the data; the Monitor or Deploy phase can create the tickets.

### Interactive Elements
- Phase sidebar (Review highlighted)
- Issue severity filter: toggle to show only Blockers, only Tech Debt, or All
- Review-Patch loop flowchart with animated arcs
- Code diff viewer mockup showing review annotations inline

### Cross-Links
- Previous: `/pipeline/test/`
- Next: `/pipeline/document/`
- Overview: `/pipeline/`
- Related: Self-Healing Loops, Review Loop (Glossary), Tool Permission Design

### Content Writer Notes
- **Tone:** Authoritative, rigorous. This is the gatekeeper.
- **Emphasis:** The severity classification system is key. Not everything is a blocker -- that distinction makes the pipeline practical.
- **Unique:** This is the second read-only phase. The duality with Plan (both read-only, both produce structured analysis) is worth highlighting. The patch context mechanism is a novel pattern.

---

## Page 6: Document Phase

### URL and Title
- **URL:** `/pipeline/document/index.html`
- **Title:** `Document Phase | Technical Writer | AEF Pipeline`
- **Phase color:** `#A78BFA` (Document lavender)

### Purpose
Deep-dive into the Document phase: diff-based documentation generation, multi-agent pattern for large changes, and structured output with architecture decisions.

### Content Outline

#### Section 1: Phase Header
- Phase badge `05`, Document lavender
- Heading: `Document` / Role: `Technical Writer`
- One-liner: `Generate from diffs, not from scratch.`
- Permissions: Read (allowed), Search (allowed), Execute (denied), Write (allowed)

#### Section 2: Why This Phase Exists
- Documentation is the most-skipped step in traditional development. By making it an autonomous pipeline phase, it happens consistently on every change.
- Positioned after Review because it documents the final, approved state. Documenting before review wastes effort if reviewers request changes.
- The agent generates documentation from diffs, not from a blank slate. This ensures accuracy -- the docs describe what actually changed, not what someone thinks changed.

#### Section 3: Methodology
1. **Receive artifacts** -- Code diff, build report, review verdict, plan artifact.
2. **Analyze the diff** -- Understand what changed, what was added, what was removed.
3. **Identify documentation targets** -- Which existing docs need updating? Which new docs need creating?
4. **Route documentation** -- Different change types produce different documentation:
   - Architecture change -> Architecture Decision Record (ADR)
   - New feature -> Feature documentation
   - Bug fix -> Changelog entry
   - API change -> API docs update
5. **Generate documentation** -- Produce structured docs with file:line references back to the implementation.
6. **Write documentation files** -- Update existing docs or create new ones.

#### Section 4: Inputs & Outputs
- **Inputs:** Code diff, build report, review verdict, plan artifact
- **Outputs:** Updated/new documentation files, architecture decision notes
- **Output structure:**

```
## Documentation Generated

### Architecture Decisions
- Added JWT format validation as a pre-processing step
  before token verification (src/auth/login.ts:55)

### Implementation Details
- Token validation now uses two-phase approach:
  1. Structural validation (decode with { complete: true })
  2. Cryptographic verification (verify with secret)

### Files Updated
- docs/auth/token-flow.md — Updated validation sequence diagram
- CHANGELOG.md — Added entry for token validation improvement

### Files Created
- docs/decisions/007-jwt-prevalidation.md — ADR for new validation approach
```

#### Section 5: Agent Pattern
- **Pattern:** Single agent for small diffs. Multi-agent for large diffs.
- **Multi-agent pattern:** For changes spanning 20+ files:
  - Analysis Subagent 1: Backend changes documentation
  - Analysis Subagent 2: Frontend changes documentation
  - Analysis Subagent 3: Test changes / coverage notes
  - Main Writer: Synthesizes into coherent documentation
- **Conditional documentation routing:** Subagents only read docs relevant to their domain. The backend analyst does not read frontend docs and vice versa.

#### Section 6: Tool Permissions
- **Badge row:** Read (green), Search (green), Execute (red), Write (green)
- **Rationale:** Document needs Write to create/update documentation files. Execute is denied because this phase does not need to run tests or scripts -- it only reads and writes text.

#### Section 7: Prompt Template

```
# Document Phase — Technical Writer

## Role
You are a Technical Writer. Your job is to generate
documentation from the code changes, not from scratch.

You document what actually changed. You reference specific
files and lines. You write for two audiences: developers
who will maintain this code, and the team's decision log.

## Context
Plan Artifact:
${plan_artifact}

Build Report:
${build_report}

Review Verdict:
${review_verdict}

Code Diff:
${code_diff}

Existing Docs Directory: ${docs_directory}
Changelog Path: ${changelog_path}

## Documentation Routing

### If architecture change detected:
- Create an Architecture Decision Record (ADR)
- Format: docs/decisions/NNN-title.md
- Include: Context, Decision, Consequences

### If new feature:
- Update relevant feature documentation
- Add usage examples if applicable
- Update API documentation if endpoints changed

### If bug fix:
- Add CHANGELOG entry
- Update any docs that described the incorrect behavior

### If API change:
- Update API reference docs
- Note breaking changes prominently
- Include migration notes if applicable

## Methodology
1. Read the code diff to understand what changed
2. Read existing documentation to find what needs updating
3. Generate new documentation from the diff
4. Reference specific file:line locations in your docs
5. Write documentation files

## Constraints
- Generate from the diff, not from imagination.
- Every claim in the docs must trace to a code change.
- Reference specific file:line for implementation details.
- Follow existing documentation style and structure.
- Do not document code that didn't change.
- Keep it concise. Engineers read docs when stuck, not for fun.

## Output Format
1. **Architecture Decisions** — Key decisions with rationale
2. **Implementation Details** — What changed and why
3. **Files Updated** — Existing docs modified
4. **Files Created** — New documentation files
5. **Changelog Entry** — Formatted for the project's changelog
```

- **Annotations:** `Role Assignment`, `Template Variables`, `Documentation Routing`, `Diff-Based Generation`, `ADR Pattern`

#### Section 8: Best Practices
- **Do's:** Generate from diffs. Reference specific file:line. Follow existing doc style. Create ADRs for architectural decisions. Keep it concise.
- **Don'ts:** Do not document code that did not change. Do not write aspirational documentation. Do not duplicate information already in code comments. Do not skip the changelog entry.

#### Section 9: Nuances
- **"Generate from diffs, not from scratch"** is the core principle. Traditional documentation asks agents to describe code from memory. This phase works from the actual diff, ensuring accuracy.
- **Conditional documentation routing:** In a large monorepo, the Document agent should not read all documentation. Route it: backend changes -> backend docs, frontend changes -> frontend docs. This keeps context windows focused.
- **Architecture Decision Records (ADRs):** When the plan or review identified an architectural choice, the Document phase captures it as a formal ADR. This builds an audit trail automatically.
- **Documentation as a non-blocking phase:** If Document fails, the pipeline should still be able to proceed to Deploy. Documentation is important but not critical-path.

### Interactive Elements
- Phase sidebar (Document highlighted)
- Documentation routing flowchart
- Toggle between ADR template and Feature doc template

### Cross-Links
- Previous: `/pipeline/review/`
- Next: `/pipeline/deploy/`
- Overview: `/pipeline/`
- Related: Artifact Chaining, Prompt Engineering Patterns

### Content Writer Notes
- **Tone:** Pragmatic, precise. Documentation that is useful, not verbose.
- **Emphasis:** The diff-based approach is the innovation. The conditional routing prevents wasted context.
- **Unique:** This is the only phase whose output is intended for human consumption long-term (docs persist). Every other artifact is transient pipeline state.

---

## Page 7: Deploy Phase

### URL and Title
- **URL:** `/pipeline/deploy/index.html`
- **Title:** `Deploy Phase | Release Engineer | AEF Pipeline`
- **Phase color:** `#F97316` (Deploy orange)

### Purpose
Deep-dive into the Deploy phase: atomic commits, conventional commit messages, structured PRs, and remote/local fallback flow.

### Content Outline

#### Section 1: Phase Header
- Phase badge `06`, Deploy orange
- Heading: `Deploy` / Role: `Release Engineer`
- One-liner: `Atomic commits. Structured PRs. Never git add -A.`
- Permissions: Read (allowed), Search (allowed), Execute (allowed), Write (denied)

#### Section 2: Why This Phase Exists
- Sloppy commit history and PR structure makes rollbacks, bisects, and audits harder. Deploy exists to enforce commit discipline.
- Positioned after Document because documentation updates are part of the commit.
- "Ship means PR" (Decision 004) -- the pipeline's output is a reviewable change request, not a deployment.

#### Section 3: Methodology
1. **Receive all artifacts** -- Code changes, docs, test evidence, review verdict, plan artifact.
2. **Stage changes atomically** -- Group related files into logical commits. Never `git add -A`.
3. **Write conventional commit messages** -- Format: `type(scope): description`. Types: feat, fix, refactor, test, docs, chore.
4. **Create commits** -- One commit per logical change unit.
5. **Push and create PR (remote flow)** -- Push branch, create PR with structured body referencing plan artifact.
6. **Or merge locally (local flow)** -- For local-only workflows, merge to target branch.
7. **Generate deploy report** -- List of commits with hashes, or PR URL.

#### Section 4: Inputs & Outputs
- **Inputs:** All artifacts from previous phases, code changes, documentation updates
- **Outputs:** Commit list + PR URL (remote) or merge hash (local)
- **PR body format:**

```markdown
## Summary
${plan_summary}

## Changes
- Refactored token validation in auth module
- Added JWT format pre-validation step
- Created comprehensive test suite (47 tests)
- Updated documentation and ADR

## Test Evidence
- All 47 tests passing
- Coverage: 94.2% statements, 88.1% branches
- Self-healing: 1 fix applied during test phase

## Review Status
- 0 blockers, 1 tech debt item logged
- Review passed on iteration 1

## Plan Reference
${plan_artifact_link}
```

#### Section 5: Agent Pattern
- **Pattern:** Single agent. Deploy is straightforward and does not benefit from multi-agent coordination.
- **Diagram:** Linear flow: Stage -> Commit -> Push -> PR Create

#### Section 6: Tool Permissions
- **Badge row:** Read (green), Search (green), Execute (green), Write (red)
- **Rationale:** Execute is needed for git operations (commit, push, PR creation via CLI). Write (file editing) is denied because no code should be modified at this stage -- all changes were finalized in earlier phases. If something needs editing, it should go back to Build.

#### Section 7: Prompt Template

```
# Deploy Phase — Release Engineer

## Role
You are a Release Engineer. Your job is to create clean,
atomic commits and a structured PR from the completed
implementation.

You do NOT modify code. All code changes are finalized.
You package and ship them with proper commit discipline.

## Context
Plan Artifact:
${plan_artifact}

Build Report:
${build_report}

Test Report:
${test_report}

Review Verdict:
${review_verdict}

Branch: ${branch_name}
Target Branch: ${target_branch}        # e.g., main, develop
Remote: ${remote_name}                 # e.g., origin
PR Workflow: ${pr_workflow}            # remote | local

## Commit Strategy

### Conventional Commit Prefixes
- feat: New feature
- fix: Bug fix
- refactor: Code restructuring
- test: Test additions or changes
- docs: Documentation updates
- chore: Build process, tooling changes

### Atomic Commits
Each commit represents ONE logical change:
- Implementation changes: feat(auth): add JWT pre-validation
- Test additions: test(auth): add token validation test suite
- Documentation: docs(auth): update token flow documentation

### NEVER Do This
- git add -A (bulk staging)
- git add . (bulk staging)
- Single commit with all changes
- Commit message without type prefix

## Methodology
1. Review all changed files from the Build Report
2. Group files into logical commit units
3. For each commit unit:
   a. Stage specific files: git add path/to/file1 path/to/file2
   b. Commit with conventional message
4. Push to remote (if remote workflow)
5. Create PR with structured body
6. Report commit list and PR URL

## Remote/Local Fallback
### If ${pr_workflow} == "remote":
1. git push -u ${remote_name} ${branch_name}
2. Create PR via gh pr create or equivalent
3. PR body references plan artifact

### If ${pr_workflow} == "local":
1. git checkout ${target_branch}
2. git merge ${branch_name}
3. Report merge commit hash

## Constraints
- Never git add -A or git add .
- Every commit is atomic and meaningful.
- Conventional commit prefixes required.
- PR body must reference the plan artifact.
- Do not modify any files. If something needs changing,
  escalate back to Build.

## Output Format
### Remote:
- Commit list: hash, message, files for each commit
- PR URL: ${pr_url}

### Local:
- Commit list: hash, message, files for each commit
- Merge hash: ${merge_hash}
```

- **Annotations:** `Role Assignment`, `Template Variables`, `Conventional Commits`, `Atomic Staging`, `Remote/Local Fallback`

#### Section 8: Best Practices
- **Do's:** Stage files individually. Use conventional commit prefixes. Reference the plan in the PR body. Include test evidence in the PR.
- **Don'ts:** Never `git add -A`. Never `git add .`. Never create a single monolithic commit. Never skip the PR body.

#### Section 9: Nuances
- **"Never bulk-add files"** is the single most important constraint. Bulk staging leads to accidental inclusion of debug files, unrelated changes, and sensitive files.
- **Each commit is atomic and meaningful.** If someone runs `git bisect`, each commit should be a self-contained, buildable state.
- **PR body references plan artifact.** This creates traceability: from the original task/issue, through the plan, to the final PR. Auditors and future developers can trace any change back to its intent.
- **Remote/local fallback:** Not all teams use GitHub/GitLab. The Deploy phase should support local-only workflows where the output is a merge commit rather than a PR.

### Interactive Elements
- Phase sidebar (Deploy highlighted)
- Commit log visualization: mock git log with colored commit types
- PR preview card showing the structured PR body

### Cross-Links
- Previous: `/pipeline/document/`
- Next: `/pipeline/monitor/`
- Overview: `/pipeline/`
- Related: Ship = PR (Decision 004)

### Content Writer Notes
- **Tone:** Precise, disciplined. This is about craftsmanship in packaging.
- **Emphasis:** Atomic commits and structured PRs are the differentiator. The "never git add -A" rule is the defining constraint.
- **Unique:** This is the only phase that interacts with version control. It is the boundary between the pipeline's internal state and the external world.

---

## Page 8: Monitor Phase

### URL and Title
- **URL:** `/pipeline/monitor/index.html`
- **Title:** `Monitor Phase | Operations | AEF Pipeline`
- **Phase color:** `#06B6D4` (Monitor cyan)

### Purpose
Deep-dive into the Monitor phase: KPI tracking, lifecycle loop closure (feeding issues back to Plan), streak calculations, and best-effort recording.

### Content Outline

#### Section 1: Phase Header
- Phase badge `07`, Monitor cyan
- Heading: `Monitor` / Role: `Operations`
- One-liner: `Track KPIs. Close the loop. Feed issues back to Plan.`
- Permissions: Read (allowed), Search (allowed), Execute (allowed), Write (denied)

#### Section 2: Why This Phase Exists
- Without metrics, teams cannot tell if their agentic layer is improving or degrading over time. Monitor exists to track pipeline health across workflows.
- Positioned last because it observes the completed pipeline run. It also closes the lifecycle loop: issues discovered in production feed back to Plan, starting a new pipeline run.
- The Monitor -> Plan feedback arc is what transforms the pipeline from a one-shot tool into a continuous improvement system.

#### Section 3: Methodology
1. **Collect pipeline metadata** -- Duration, cost, turns, tokens consumed.
2. **Collect workflow metrics** -- Plan size (number of files targeted), diff stats (lines added/removed), patch iterations (Test and Review loops), success/failure status.
3. **Calculate derived metrics** -- Success streak (consecutive successful workflows), average patch iterations, cost per workflow.
4. **Store KPI data** -- Append to the project's metrics file/database.
5. **Identify issues for feedback** -- If the workflow failed or required excessive patching, generate an issue description to feed back to Plan.
6. **Generate KPI report** -- Summary tables and per-workflow data.

#### Section 4: Inputs & Outputs
- **Inputs:** All pipeline artifacts, pipeline execution metadata (timing, cost, turns)
- **Outputs:** KPI Report
- **Output format:**

```
# KPI Report — Workflow ${workflow_id}

## Summary
| Metric | Value |
|--------|-------|
| Status | Success |
| Duration | 4m 32s |
| Total Turns | 23 |
| Cost | $0.47 |
| Plan Size | 4 files |
| Diff Stats | +187 / -42 lines |
| Test Iterations | 2 |
| Review Iterations | 1 |
| Success Streak | 7 |

## Per-Phase Breakdown
| Phase | Duration | Turns | Cost |
|-------|----------|-------|------|
| Plan | 45s | 4 | $0.08 |
| Build | 1m 52s | 8 | $0.18 |
| Test | 1m 05s | 6 | $0.12 |
| Review | 32s | 3 | $0.06 |
| Document | 12s | 1 | $0.02 |
| Deploy | 6s | 1 | $0.01 |

## Feedback Issues
- None (clean run)
```

#### Section 5: Agent Pattern
- **Pattern:** Single agent. Monitor is a data collection and reporting task.

#### Section 6: Tool Permissions
- **Badge row:** Read (green), Search (green), Execute (green), Write (red)
- **Rationale:** Execute is needed to run metric collection scripts or API calls. Write (file editing) is denied because Monitor should not modify source code or pipeline configuration. Its data output goes through Execute (appending to metrics store).

#### Section 7: Prompt Template

```
# Monitor Phase — Operations

## Role
You are an Operations agent. Your job is to collect metrics
from the completed pipeline run, calculate KPIs, and
identify any issues that should feed back to the Plan phase.

You do NOT modify code or pipeline configuration. You
observe, measure, and report.

## Context
Workflow ID: ${workflow_id}
Pipeline Start Time: ${pipeline_start_time}
Pipeline End Time: ${pipeline_end_time}

Plan Artifact:
${plan_artifact}

Build Report:
${build_report}

Test Report:
${test_report}

Review Verdict:
${review_verdict}

Deploy Report:
${deploy_report}

Previous KPI Data: ${kpi_history_path}   # path to metrics file

## Metrics to Collect

### Per-Workflow Metrics
- Status: success | failure | escalated
- Duration: end_time - start_time
- Total turns across all phases
- Estimated cost (based on token usage)
- Plan size: number of files targeted
- Diff stats: lines added, lines removed
- Test iterations: how many retry loops
- Review iterations: how many patch loops

### Derived Metrics
- Success streak: consecutive successful workflows
- Average test iterations (rolling 10 workflows)
- Average cost per workflow (rolling 10 workflows)
- Failure rate (rolling 30 days)

### Feedback Detection
If any of these conditions are true, generate a feedback
issue to feed back to Plan:
- Workflow failed after max retries
- Test iterations >= 3 (maxed out retry loop)
- Review iterations >= 3 (maxed out patch loop)
- Cost exceeded ${cost_threshold} (configurable)

## Methodology
1. Read all pipeline artifacts to extract metrics
2. Calculate per-phase breakdowns
3. Read previous KPI data for streak/rolling calculations
4. Identify feedback issues (if any)
5. Generate KPI report
6. Append data to metrics store

## Constraints
- Best-effort recording. If a metric is unavailable, skip
  it and note it as "N/A". Never fail the pipeline because
  of a missing metric.
- Do not modify source code or pipeline configuration.
- Feedback issues are suggestions, not commands.
- Non-fatal on failure. If Monitor itself errors, the
  pipeline still succeeded.

## Output Format
Produce a KPI Report with:
1. **Summary Table** — Key metrics for this workflow
2. **Per-Phase Breakdown** — Duration, turns, cost per phase
3. **Rolling Metrics** — Streaks, averages (if history available)
4. **Feedback Issues** — Issues to feed back to Plan (if any)
```

- **Annotations:** `Role Assignment`, `Template Variables`, `Metrics Collection`, `Feedback Detection`, `Best-Effort Pattern`

#### Section 8: Best Practices
- **Do's:** Collect every available metric. Calculate streaks and rolling averages. Generate feedback issues when thresholds are exceeded. Treat monitoring as non-fatal.
- **Don'ts:** Do not fail the pipeline if monitoring fails. Do not modify code or config. Do not generate feedback issues for minor threshold violations.

#### Section 9: Nuances
- **Best-effort recording** is critical. If the Monitor phase cannot access a particular metric (e.g., cost data is unavailable), it should skip that metric and note it as "N/A" rather than failing. The pipeline succeeded; monitoring is observational.
- **Streak calculations** motivate teams. Seeing "Success Streak: 15" builds confidence in the agentic layer. A broken streak signals that something changed.
- **The Monitor -> Plan feedback arc** closes the lifecycle loop. When Monitor detects a pattern (e.g., auth module consistently requires 3 test iterations), it generates an issue that feeds back to Plan. This creates a self-improving system: the pipeline learns from its own history.
- **Cost tracking:** In a world of API-based AI agents, cost-per-workflow is a critical metric. Teams need to understand the ROI of their agentic layer.
- **Non-fatal failure:** Monitor is the only phase where failure does not affect the pipeline outcome. If Deploy succeeded, the PR is ready regardless of whether metrics were collected.

### Interactive Elements
- Phase sidebar (Monitor highlighted)
- KPI dashboard mockup with metrics cards
- Feedback loop arc visualization (Monitor -> Plan, animated red dashed line)
- Streak counter animation

### Cross-Links
- Previous: `/pipeline/deploy/`
- Next: Loops back to `/pipeline/plan/` (Monitor -> Plan feedback)
- Overview: `/pipeline/`
- Related: Feedback Loops (Glossary), Full lifecycle diagram

### Content Writer Notes
- **Tone:** Analytical, observational. This phase watches and reports.
- **Emphasis:** The lifecycle closure (Monitor -> Plan) is the most important concept. Best-effort is the key design decision.
- **Unique:** This is the only phase that looks backward at the entire pipeline run. It is also the phase that transforms a linear pipeline into a continuous loop.

---

## Shared Interactive Elements Across All Phase Pages

### Phase Sidebar (Desktop)
- **Position:** Fixed left, below nav, 240px wide
- **Content:** Vertical list of all 7 phases, each with:
  - Phase-colored dot (8px, with subtle glow shadow)
  - Phase name (JetBrains Mono, 12px)
  - Role subtitle (IBM Plex Sans, 10px, muted)
- **Active state:** Current phase has a brighter dot, phase-colored left border (3px), name in phase color instead of primary
- **Hover:** Name shifts to phase color, dot brightens
- **Mobile:** Horizontal scrolling tab bar at top of content area (below nav), dots + names only

### Prompt Template Viewer Component
- **Shared across all 7 phase pages**
- Full-width code block using `.code-block` styling
- Line numbers in muted color on the left gutter
- Template variables (`${...}`) highlighted in `.var` (indigo/glow-hover `#818CF8`)
- Keywords (section headers) in `.keyword` (violet `#8B5CF6`)
- Strings/literals in `.string` (emerald `#10B981`)
- Comments in `.comment` (muted `#52525B`)
- "Copy Template" button: top-right, subtle border, monospace text
- Phase-colored left border (4px) on the code block container

### Breadcrumb Component
- Format: `AEF > Pipeline > {Phase Name}`
- Text: muted, 12px, JetBrains Mono
- `>` separator: muted
- Phase name: phase color
- Each segment is a link

---

### Critical Files for Implementation
- `/Users/alejtr/Documents/obsidian/obsidian/agentic-layer-framework/website/index.html` - The design system reference: all Tailwind config, CSS classes, component patterns, SVG diagrams, and animations to replicate across the 8 new pages
- `/Users/alejtr/Documents/obsidian/obsidian/agentic-layer-framework/pipeline/Pipeline Architecture.md` - Source of truth for pipeline structure, phase details, feedback loop definitions, and configuration points
- `/Users/alejtr/Documents/obsidian/obsidian/agentic-layer-framework/framework/Glossary.md` - Terminology definitions that must be used consistently across all page copy
- `/Users/alejtr/Documents/obsidian/obsidian/agentic-layer-framework/thinking/Decisions Log.md` - ADRs that provide rationale for key design choices referenced in phase pages (TDD-first, Ship=PR, opinionated-but-configurable)
- `/Users/alejtr/Documents/obsidian/obsidian/agentic-layer-framework/framework/Framework Overview.md` - Philosophy and principles that inform the tone and framing of each phase pageagentId: af702b1e3c8cb8da6 (for resuming to continue this agent's work if needed)
<usage>total_tokens: 70241
tool_uses: 11
duration_ms: 427011</usage>