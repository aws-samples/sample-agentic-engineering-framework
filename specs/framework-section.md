I now have everything I need. Let me compile the complete spec. Here is the full framework section page spec:

---

# Framework Section Page Spec

**Document:** `website/specs/framework-section.md`
**Author:** Planning agent
**Date:** 2026-03-10
**Status:** Ready for implementation

---

## Shared Design System Reference

All three pages share the same design system established in `index.html`. This section documents the reusable patterns so they are not repeated per page.

### Technology Stack
- Tailwind CSS via CDN (`https://cdn.tailwindcss.com`)
- Fonts: IBM Plex Sans (body, weights 300-700), JetBrains Mono (code/headings, weights 400-700) via Google Fonts
- No JS framework. Vanilla JS for interactions.

### Tailwind Config (copy from `index.html`)
Colors: void `#09090B`, surface `#111113`, raised `#1A1A1F`, subtle `#232329`, primary `#F4F4F5`, secondary `#A1A1AA`, muted `#52525B`, glow `#6366F1`, glow-hover `#818CF8`, glow-faint `rgba(99,102,241,0.08)`, glow-10 `rgba(99,102,241,0.10)`, glow-20 `rgba(99,102,241,0.20)`, plan `#8B5CF6`, build `#F59E0B`, test `#10B981`, review `#3B82F6`, document `#A78BFA`, deploy `#F97316`, monitor `#06B6D4`, pass `#22C55E`, fail `#EF4444`, warning `#EAB308`

### Shared Page Shell
Each page includes:
1. **Navigation bar** -- Fixed top, `bg-void/80 backdrop-blur-md border-b border-subtle`. Logo on left (`AEF` in JetBrains Mono). Links: Framework (dropdown with Overview, Principles, Architecture), Pipeline, Concepts, Agentic Layer, Get Started button.
   - The Framework nav item should have a dropdown or show active state on all three framework pages.
   - Current page link gets `.active` class (underline glow animation).
2. **Footer** -- Same as landing page. Border-t, logo, nav links, tagline.
3. **Background treatments** -- `bg-void` body, dot-grid overlay on hero sections, ambient glow blobs positioned per page.
4. **Scroll reveal** -- All content sections use `.reveal` class with IntersectionObserver (same JS as landing page).
5. **Reduced motion** -- Respect `prefers-reduced-motion` for all animations.

### Reusable Component Patterns (from `index.html`)

| Component | Pattern |
|-----------|---------|
| **Section header** | `<p class="text-sm font-mono text-glow mb-3 tracking-wider uppercase">LABEL</p>` + `<h2 class="text-3xl sm:text-4xl lg:text-5xl font-bold text-primary mb-4">Title</h2>` + `<p class="text-secondary text-lg max-w-2xl mx-auto">Subtext</p>` |
| **Card** | `rounded-xl bg-surface border border-subtle hover:border-glow-faint hover:bg-raised transition-all duration-250` with `p-6 lg:p-8` |
| **Phase card** | Same as card plus `--phase-color` CSS variable, colored dot, number badge, permission badges |
| **Permission badge (allowed)** | `perm-allowed` class: green bg/text/border at low opacity |
| **Permission badge (denied)** | `perm-denied` class: red bg/text/border at low opacity |
| **Code block** | `.code-block` class: `bg-void border border-subtle rounded-lg p-6`, with `.var` (indigo), `.keyword` (purple), `.string` (green), `.comment` (muted), `.type` (cyan) syntax classes |
| **Annotation badge** | `inline-flex items-center gap-1.5 px-2.5 py-1 text-[10px] font-mono rounded` with phase-colored bg/text/border at ~8% opacity |
| **Icon container** | `w-10 h-10 rounded-lg bg-{color}/10 border border-{color}/20 flex items-center justify-center` |
| **Ambient glow** | `position: absolute; border-radius: 50%; filter: blur(120px); pointer-events: none;` with phase color at 3-4% opacity |
| **Section divider** | `border-t border-subtle` on `<section>` elements |
| **CTA button (primary)** | `inline-flex items-center gap-2 px-6 py-3 text-sm font-medium rounded-lg bg-glow hover:bg-glow-hover text-white transition-colors duration-200 shadow-[inset_0_1px_0_rgba(255,255,255,0.1),0_0_20px_rgba(99,102,241,0.15)]` |
| **CTA button (secondary)** | `inline-flex items-center gap-2 px-6 py-3 text-sm font-medium rounded-lg border border-subtle bg-surface/50 text-primary hover:bg-raised hover:border-glow-faint transition-all duration-200` |

### Breadcrumb Component (new, use on all 3 pages)
Add a breadcrumb below the nav, inside the hero/top section:
```
<nav class="text-xs font-mono text-muted mb-8">
  <a href="/" class="hover:text-secondary transition-colors">Home</a>
  <span class="mx-2">/</span>
  <a href="/framework/overview" class="hover:text-secondary transition-colors">Framework</a>
  <span class="mx-2">/</span>
  <span class="text-secondary">Current Page</span>
</nav>
```

### Sidebar Navigation (new, use on all 3 pages)
On `lg:` breakpoints and above, add a left sidebar for in-page and cross-page navigation within the framework section. Sticky, below the top nav.

```
Structure:
- Framework (heading)
  - Overview (link, active state)
  - Principles (link)
  - Architecture (link)
- On This Page (heading)
  - [Section anchors for current page]
```

Styling: `w-56 sticky top-20 text-sm`, links in `text-muted hover:text-primary`, active link gets `text-glow border-l-2 border-glow pl-3`. Section heading in `font-mono text-xs uppercase tracking-wider text-muted mb-3`.

On mobile (`< lg`), hide the sidebar. Optionally show a collapsible "On this page" menu at the top of content.

### Page Layout
```
<body class="bg-void text-primary font-sans antialiased">
  [Nav bar - shared]
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24">
    <div class="lg:flex lg:gap-12">
      [Sidebar - left, lg:w-56 flex-shrink-0]
      <article class="flex-1 min-w-0">
        [Page content]
      </article>
    </div>
  </main>
  [Footer - shared]
</body>
```

---

## Page 1: Framework Overview

### Metadata
- **URL:** `/framework/overview` (file: `website/framework/overview.html`)
- **Title:** `What is AEF | Agentic Engineering Framework`
- **Meta description:** "The Agentic Engineering Framework shifts developers from code authors to pipeline architects. Learn how the three-layer architecture works."

### Purpose
Explain what the Agentic Engineering Framework is, why it exists, and how its three-layer architecture works. This is the conceptual entry point for the entire framework section.

---

### Section 1: Hero / Intro

**Heading:** "What is the Agentic Engineering Framework?"
**Section label (mono uppercase):** "Framework Overview"

**Content to write:**
One clear paragraph (3-4 sentences) that defines AEF without jargon. Key points to hit:
- AEF is a structured system for building an "agentic layer" around any codebase
- It shifts the developer's role from writing code to defining how code gets written
- It provides opinionated templates, quality gates, and pipeline architecture that agents follow
- It works with any AI agent stack

**UI components:**
- Dot-grid background overlay at 40% opacity
- Ambient glow blob: glow color at 4% opacity, 600px, positioned top-right
- Breadcrumb navigation above the heading
- No CTA buttons in hero (this is a docs page, not a marketing page)

**Content writer notes:**
- Tone: Authoritative but accessible. This is the "explain it to a senior dev in 30 seconds" paragraph.
- Do NOT use hype language. No "revolutionary" or "game-changing." State what it is factually.
- The reader should finish this paragraph knowing: what AEF is, who it is for, and what it changes about their workflow.

---

### Section 2: The Problem

**Heading:** "Why Traditional SDLC Breaks with Agents"
**Section label:** "The Problem"

**Content to write:**
3 sub-problems, each as a card with icon, title, and 2-3 sentence description:

1. **Tribal Knowledge Doesn't Transfer** -- Every developer has their own way of prompting agents, structuring tasks, handling failures. When agents work without standardized instructions, quality depends on who wrote the prompt. New team members start from zero.

2. **Inconsistency at Scale** -- Without shared templates, the same type of task (e.g., "add a REST endpoint") gets built differently every time. Code style varies, test coverage varies, documentation quality varies. The agent is only as consistent as its instructions.

3. **Every Agent Reinvents the Wheel** -- Without a framework, every project recreates the same patterns: how to plan, how to test, how to review. Teams spend time on pipeline infrastructure instead of product work. There is no reusable layer.

**UI components:**
- 3-column grid on `lg:`, 1-column on mobile
- Standard card component (`bg-surface border border-subtle` with hover)
- Each card gets an icon container with a different phase color:
  - Tribal knowledge: `plan` color, users icon
  - Inconsistency: `warning` color, exclamation-triangle icon
  - Reinvention: `build` color, wrench icon

**Interactive elements:**
- Scroll-reveal with staggered delay (0ms, 100ms, 200ms)

**Content writer notes:**
- These are pain points. The reader should recognize their own experience.
- Be specific, not abstract. "Quality depends on who wrote the prompt" is better than "quality varies."
- Each problem should implicitly point to the solution (templates, pipeline, reusable layer).

---

### Section 3: The Shift

**Heading:** "Developers as Pipeline Architects"
**Section label:** "The Shift"

**Content to write:**
A before/after comparison, then the three-layer diagram with full explanations.

**Before/After block:**
Two side-by-side panels (or stacked on mobile):

| Before (Traditional) | After (AEF) |
|---|---|
| Developers write code | Developers write the layer that writes code |
| Tribal knowledge in heads | Encoded in prompt templates and quality gates |
| Manual review bottleneck | Autonomous review with self-healing loops |
| Every project starts fresh | Reusable agentic layer across all projects |
| Quality depends on the person | Quality depends on the pipeline |

**Three-Layer Diagram:**
Reuse the three-layer diagram from the landing page (`index.html` lines 414-472), but expand each layer with a detailed breakdown below it.

**Layer 1: Agentic Layer** (glow color, "HUMANS WORK HERE" badge)
Expandable or always-visible detail panel below the layer card. Content:
- **Prompt Templates:** One per phase. Define role, context, constraints, output format. These are the instructions agents follow.
- **Quality Gates:** Pass/fail criteria per phase. Coverage thresholds, review severity rules, completeness checks.
- **Tool Configurations:** Which tools each phase can access. File system, code execution, external APIs. Follows least-privilege.
- **Pipeline Config:** Loop limits, escalation rules, phase ordering, parallel execution settings.

**Layer 2: Pipeline Engine** (plan color, "FRAMEWORK RUNS HERE" badge)
- Orchestrates the 7-phase lifecycle from Plan through Monitor
- Manages state between phases via artifact chaining
- Runs feedback loops when phases fail (Test retry, Review patch)
- Handles escalation when loops exhaust
- Tracks metrics for pipeline health

**Layer 3: Your Codebase** (build color, "AGENTS WORK HERE" badge)
- Source code, tests, documentation, infrastructure-as-code
- Agents read, write, test, and ship code using the patterns defined in the agentic layer
- The codebase is the output, not the input. Developers do not directly collaborate on it.

**UI components:**
- Before/After: Two cards side by side. "Before" card has a subtle red-tinted border (`fail/20`). "After" card has a glow-tinted border (`glow/20`). Use a simple bullet list inside each.
- Three-layer diagram: Reuse exact HTML structure from landing page (the three stacked cards with down-arrows between them).
- Detail panels below each layer: Use a slightly indented card (`ml-16`) or an expandable accordion. Background `bg-raised` with `border-l-2 border-{layer-color}`. Content is a 2-column or 3-column grid of mini-cards for each sub-component.

**Interactive elements:**
- Scroll-reveal on the entire section
- The detail panels for each layer could be expandable (click to toggle) or always visible. Recommendation: always visible on this page since the purpose is full explanation. Use subtle fade-in animation when scrolling into view.

**Content writer notes:**
- The before/after should feel like a lightbulb moment. Keep it punchy -- short phrases, not sentences.
- When explaining layers, emphasize the separation of concerns. The human works at layer 1, the framework runs at layer 2, agents work at layer 3. Nobody crosses layers.
- Use the phrase "The code is output, not input" -- it is the project's tagline and appears in the footer.

---

### Section 4: What the Agentic Layer Contains

**Heading:** "What You Build: The Agentic Layer"
**Section label:** "The Layer"

**Content to write:**
Show the directory structure (reuse from landing page, the code block at lines 836-856) and then explain each component in detail.

5 component cards in a grid:

1. **Prompt Templates** (`prompts/`)
   - One markdown file per pipeline phase
   - Anatomy: Role assignment, context injection via template variables, constraints, output format contract
   - Versioned alongside your code. Diff-friendly. Reviewable in PRs.
   - Example: "The Plan prompt assigns the Software Architect role and constrains the agent to read-only operations."

2. **Quality Gates** (`gates/`)
   - YAML files defining pass/fail criteria per phase
   - Examples: minimum test coverage %, review severity thresholds, required documentation sections
   - Gates are the pipeline's guardrails. If a gate fails, the feedback loop activates.

3. **Tool Configurations** (`tools/`)
   - Define which tools each phase can access
   - Categories: file system, code execution, external APIs, context providers
   - Follows least-privilege principle: planners get read-only, builders get full access

4. **Commands and Skills** (`commands/`)
   - Reusable prompt+tool bundles for common operations
   - Commands are human-invoked, skills are agent-invoked
   - Examples: commit, security-audit, dependency-update

5. **Pipeline Config** (`pipeline.yaml`)
   - Orchestration rules: phase ordering, loop limits, escalation rules
   - Parallel execution settings
   - From minimal viable (3 phases) to full enterprise (7 phases with all loops)

**UI components:**
- Code block with directory tree (reuse exact styling from landing page: `.code-block` with syntax-colored spans)
- 3-column grid of cards below (`sm:grid-cols-2 lg:grid-cols-3`)
- Each card: Standard card component with a small colored dot or icon at top-left

**Content writer notes:**
- This section answers "what do I actually create?" Keep it concrete.
- Mention that the minimum viable agentic layer is just 2-3 prompt templates and one gate. Do not make it sound like a massive setup.

---

### Section 5: What the Pipeline Does

**Heading:** "What the Framework Runs: The Pipeline Engine"
**Section label:** "The Engine"

**Content to write:**
Brief description (2-3 sentences) of the pipeline engine's role, then a visual showing the 7 phases with key behaviors:

- **Orchestrates 7 phases:** Plan, Build, Test, Review, Document, Deploy, Monitor
- **Manages state:** Each phase produces artifacts that feed the next phase via template variables (`$plan_artifact`, `$build_artifact`, `$test_results`, etc.)
- **Self-heals:** When Test or Review fails, the pipeline automatically retries before escalating to a human
- **Tracks metrics:** Success rates, iteration counts, cost per pipeline run, drift detection

**UI components:**
- Reuse the pipeline SVG visualization from the landing page hero (lines 274-357). Place it here as a static reference.
- Below the SVG, a horizontal list of 7 small summary cards (one per phase), each showing: phase name, agent role, one-line description. Use phase colors for the dot/border.

**Content writer notes:**
- Keep this short. The detailed pipeline breakdown lives on the Architecture page. This is the "what it does at a glance" section.
- Link to `/framework/architecture` for the deep dive.

---

### Section 6: How Agents Work on Code

**Heading:** "How Agents Execute Against Your Codebase"
**Section label:** "Execution"

**Content to write:**
A walkthrough of a single pipeline run, told as a sequence. Show how a task goes from issue to PR:

1. **Issue arrives** -- A task, feature request, or bug report enters the pipeline
2. **Plan phase reads the codebase** -- The architect agent researches existing code (read-only), produces an implementation plan with file targets and acceptance criteria
3. **Build phase writes code** -- The engineer agent follows the plan exactly, writes tests first, then implementation. No scope creep.
4. **Test phase validates** -- Tests run. If they fail, the pipeline spawns a builder agent to fix, then re-tests (up to 3x).
5. **Review phase evaluates** -- The reviewer agent checks against quality gates. If blockers found, patches are applied, re-tested, re-reviewed (up to 3x).
6. **Document phase writes docs** -- Documentation is generated from the actual diffs, not from scratch.
7. **Deploy phase ships a PR** -- A structured pull request with code, test evidence, review summary, and docs is created.

**UI components:**
- Vertical timeline/stepper (reuse the maturity stepper pattern from landing page lines 898-946). Each step gets:
  - A numbered circle with the phase color
  - Phase name in bold
  - 1-2 sentence description
  - A small code snippet or example output where relevant (e.g., for step 2, show a snippet of a plan artifact)
- Connect steps with a gradient connector line

**Interactive elements:**
- Scroll-reveal with each step appearing as you scroll

**Content writer notes:**
- This is the "day in the life" section. Make it feel tangible.
- Use a concrete example throughout: "Imagine a feature request to add a /users endpoint..." -- carry this example through all 7 steps.
- Emphasize that the human did not write code at any point. They configured the layer; the pipeline did the rest.

---

### Section 7: Next Steps CTA

**Heading:** "Go Deeper"

**Content to write:**
Three link cards pointing to the other framework pages and the getting started guide:

1. **Design Principles** -- "The 8 principles that govern every pipeline decision." Links to `/framework/principles`.
2. **Architecture** -- "How the pipeline works as a state machine." Links to `/framework/architecture`.
3. **Get Started** -- "Build your first agentic layer in 15 minutes." Links to `/guides/getting-started` (future page).

**UI components:**
- 3-column grid of cards. Each card has an arrow icon on the right side. Hover lifts the card slightly (`hover:-translate-y-1`).
- The "Get Started" card uses the glow border to stand out.

---

### Cross-Links for Page 1
- **Inbound:** Landing page "Read the Framework" button, nav bar "Framework" link
- **Outbound:** `/framework/principles`, `/framework/architecture`, `/guides/getting-started`, landing page pipeline section

---

## Page 2: Design Principles

### Metadata
- **URL:** `/framework/principles` (file: `website/framework/principles.html`)
- **Title:** `Design Principles | Agentic Engineering Framework`
- **Meta description:** "8 design principles that govern the Agentic Engineering Framework: opinionated defaults, self-healing pipelines, TDD contracts, least privilege, and more."

### Purpose
Deep dive into the 8 design principles. Each principle gets a dedicated section with rationale, concrete examples, anti-patterns, and implementation guidance.

---

### Section 1: Hero / Intro

**Heading:** "Design Principles"
**Section label:** "Principles"

**Content to write:**
Brief intro (2-3 sentences): These are the non-negotiable design decisions that govern the framework. They are ordered by importance. Every feature, every default, every pipeline behavior traces back to one of these principles.

**UI components:**
- Same hero treatment as Page 1 (dot-grid, ambient glow, breadcrumb)
- Below the intro, a "jump to" grid: 8 small pill-shaped links (one per principle name), styled as annotation badges. Clicking scrolls to that principle's section.

**Content writer notes:**
- Frame these as engineering decisions, not marketing slogans. Each one has a "why" rooted in real failure modes.

---

### Section 2-9: Individual Principles

Each principle follows an identical layout. Here is the template, then the specific content for each.

#### Principle Section Template

**Layout:** Full-width section with `border-t border-subtle` separator. Contains:

1. **Principle header:** Number badge (circle with principle number, glow-colored) + principle name in `font-mono text-xl font-bold` + one-line summary in `text-secondary`
2. **"Why It Matters" block:** A card with a lightbulb or info icon. 2-3 paragraphs of rationale with a concrete example.
3. **"Anti-Pattern" block:** A card with a warning/fail icon and a `border-l-2 border-fail` left accent. Shows what violating this principle looks like. Titled with a short "Don't do this" label.
4. **"How to Implement" block:** A card with a check/pass icon and a `border-l-2 border-pass` left accent. Practical guidance, possibly including a code snippet or config example.

**UI components per principle:**
- Number badge: `w-10 h-10 rounded-full bg-glow/10 border border-glow/20 flex items-center justify-center text-sm font-mono text-glow`
- Rationale card: Standard card, `bg-surface border border-subtle`, normal padding
- Anti-pattern card: `bg-surface border border-subtle` with `border-l-2 border-fail`. Icon: red warning triangle.
- Implementation card: `bg-surface border border-subtle` with `border-l-2 border-pass`. Icon: green checkmark.
- Layout: On `lg:`, the rationale takes 1 full row, then anti-pattern and implementation sit side by side in a 2-column grid. On mobile, all stack vertically.

---

#### Principle 1: Opinionated but Evolvable

**One-line summary:** "Strong defaults for every phase. Everything configurable when you need it."

**Why it matters:**
The AI engineering space changes weekly. New models, new tools, new patterns. A framework that hardcodes opinions becomes tech debt within months. But a framework with no opinions provides no value -- developers end up making the same decisions from scratch every time.

AEF ships opinionated: TDD-first builds, structured review loops, PR-based shipping, 3-retry feedback loops. These are the defaults because they work for most teams. But every single opinion is a configuration point in `pipeline.yaml` or in the prompt templates.

*Example:* The default test retry limit is 3. A team working on a critical financial system might set it to 5. A team prototyping might set it to 1. The framework does not care -- it has a default, and you override when needed.

**Anti-pattern:** Hardcoding a test framework (e.g., "always use Jest"). Hardcoding a model provider. Requiring a specific CI/CD system. Any opinion that cannot be overridden is a wall, not a guardrail.

**How to implement:**
- Set all defaults in `pipeline.yaml` with clear comments explaining the rationale
- Every prompt template uses template variables for values that might change
- Document what each default is and how to override it
- Config example (code block):
```yaml
# pipeline.yaml
test:
  retry_limit: 3        # Override: set 1-10
  coverage_threshold: 80 # Override: set 0-100
  framework: auto        # Override: jest | pytest | go test | ...
```

---

#### Principle 2: Self-Healing Over Failure

**One-line summary:** "Pipelines diagnose and retry before escalating to a human."

**Why it matters:**
Autonomous pipelines that stop on the first failure are not autonomous -- they are automation with a human bottleneck. The whole point of autonomy is that the system handles routine failures on its own.

A test failure is not a crisis. It is a feedback signal. The pipeline spawns a builder agent, provides the failure context, and lets it attempt a fix. Only after exhausting retries does a human get involved.

*Example:* A build produces code that fails 2 of 15 unit tests. Instead of stopping, the pipeline: (1) analyzes the failure output, (2) spawns a builder agent with the failure context and the original plan, (3) the builder patches the code, (4) tests re-run. If all pass, the pipeline continues. If not, it retries up to 2 more times. Only then does it escalate.

**Anti-pattern:** A pipeline that fails and immediately opens a Slack thread to a human. A pipeline that has no retry logic. A pipeline that retries infinitely without limit (this is the opposite failure mode -- infinite loops burn tokens and time).

**How to implement:**
- Configure retry limits per loop type in `pipeline.yaml`
- Ensure failure context (error messages, stack traces, test output) flows into the retry prompt
- Set clear escalation rules: what context does the human see, what can they do
- Code block showing the feedback loop config:
```yaml
feedback_loops:
  test_retry:
    max_attempts: 3
    context_includes: [error_output, original_plan, changed_files]
  review_patch:
    max_attempts: 3
    context_includes: [review_issues, test_results, changed_files]
  escalation:
    notify: [slack, email]
    context_includes: [full_pipeline_state, all_attempts]
```

---

#### Principle 3: Plan-Before-Execute

**One-line summary:** "Research and plan are read-only. Never plan and build simultaneously."

**Why it matters:**
When agents plan and execute at the same time, they commit to an approach before understanding the problem. This leads to scope creep, wrong abstractions, and wasted tokens on code that gets thrown away.

The Plan phase is deliberately read-only. The planner agent can read every file, search the codebase, analyze dependencies -- but it cannot modify anything. This forces a complete understanding before any code is written.

*Example:* A feature request asks for "user authentication." Without plan-first, an agent might immediately start writing a JWT module. With plan-first, the planner discovers the codebase already uses session-based auth, identifies the specific files to modify, and produces a plan that extends the existing pattern instead of introducing a conflicting one.

**Anti-pattern:** An agent that reads an issue and immediately starts writing code. An agent that "plans" by creating placeholder files. Any workflow where the first file modification happens before a structured plan exists.

**How to implement:**
- Plan phase prompt template explicitly states: "Read-only. Do not modify any files."
- Plan phase tool permissions: `Read: allowed`, `Search: allowed`, `Execute: denied`, `Write: denied`
- Plan output is a structured artifact consumed by the Build phase
- Show permission badge examples (reuse from landing page phase cards)

---

#### Principle 4: Least Privilege

**One-line summary:** "Each phase gets only the tools it needs."

**Why it matters:**
Giving an agent access to tools it does not need is a security risk and a quality risk. A planner with write access might "helpfully" start modifying files. A reviewer with execute access might run tests instead of analyzing code.

Constraining tools per phase enforces the separation of concerns that makes the pipeline reliable.

*Example:* The Review phase has Read and Search permissions only. It cannot modify code, cannot execute tests, cannot deploy. It can only analyze. This means review findings are pure analysis, not influenced by "let me try fixing it."

**Anti-pattern:** Giving every phase full access to all tools. "The agent is smart enough to know what to use" -- it is not. Agents use tools that are available to them, and more tools means more surface area for unintended actions.

**How to implement:**
- Define a permission matrix in the agentic layer config
- Show the full phase-by-tool permission matrix (table):

| Phase | Read | Search | Execute | Write |
|-------|------|--------|---------|-------|
| Plan | Allowed | Allowed | Denied | Denied |
| Build | Allowed | Allowed | Allowed | Allowed |
| Test | Allowed | Allowed | Allowed | Allowed |
| Review | Allowed | Allowed | Denied | Denied |
| Document | Allowed | Allowed | Denied | Allowed |
| Deploy | Allowed | Allowed | Allowed | Denied |
| Monitor | Allowed | Allowed | Allowed | Denied |

- Use green `perm-allowed` and red `perm-denied` badge styling from the landing page

---

#### Principle 5: Test-Driven Contracts

**One-line summary:** "Tests are written first. They are the contract every subsequent phase validates against."

**Why it matters:**
Without tests-first, the Review phase has no objective baseline. "Does this code work?" becomes subjective. With tests-first, every phase has a concrete contract: the code must pass these tests.

Tests written before implementation also prevent scope creep. The builder agent knows exactly what "done" looks like -- all tests pass. It cannot over-build or under-build.

*Example:* The Build phase receives a plan for a new `/users` endpoint. Step 1: write tests for GET /users, POST /users, validation errors, auth requirements. Step 2: write code until all tests pass. The test suite is the contract.

**Anti-pattern:** Writing code first, then writing tests to match the code. This is backwards -- the tests just confirm what was already built, not what should have been built. Also: skipping tests entirely "because the agent got it right."

**How to implement:**
- Build prompt template explicitly orders: "Write tests first, then implementation"
- Test phase runs the test suite and reports structured results
- Quality gate: minimum coverage threshold (configurable, default 80%)
- Code block showing the build prompt structure:
```markdown
## Build Order
1. Write test files first (unit + integration)
2. Run tests — confirm they FAIL (red)
3. Write implementation
4. Run tests — confirm they PASS (green)
5. Never skip step 1-2
```

---

#### Principle 6: Structured Outputs

**One-line summary:** "Machine-readable for agents, human-readable for people."

**Why it matters:**
Pipeline phases consume each other's outputs. If the Plan phase outputs freeform prose, the Build phase has to interpret it. Interpretation means inconsistency.

Structured outputs (JSON, YAML, markdown with consistent headings) allow both machine parsing and human review. Template variables like `$plan_artifact` only work when the artifact has a predictable structure.

*Example:* The Plan phase outputs a structured spec with consistent sections: Summary, Files to Modify, Files to Create, What We Are NOT Doing, Test Strategy. The Build phase knows exactly where to find file targets. A human reviewing the plan finds the same sections every time.

**Anti-pattern:** A plan that is just a paragraph of text. Review findings as a chat message. Test results as raw console output without structured parsing. Any output that requires a human to interpret before the next phase can use it.

**How to implement:**
- Define output format contracts in each prompt template (under `## Output Format`)
- Use markdown with required headings for human-readable structured output
- For machine-consumed outputs, use JSON or YAML blocks within the markdown
- Show an example of a structured plan output in a code block

---

#### Principle 7: Ship Means PR

**One-line summary:** "'Done' is a reviewable change request, not a deploy."

**Why it matters:**
Deploying autonomously to production is a different risk profile than creating a PR. AEF's "Ship" phase produces a pull request or change request that contains all artifacts: code, test evidence, review summary, documentation.

This gives humans an audit trail and a merge decision point. Teams that trust their gates can auto-merge. Teams that want oversight review the PR. The framework supports both without changing the pipeline.

*Example:* The pipeline completes all phases. The Deploy phase creates a PR with: a descriptive title, a summary of changes, test results, review findings, documentation updates. The PR is the deliverable.

**Anti-pattern:** A pipeline that deploys directly to production without a reviewable artifact. A pipeline that commits directly to `main`. Any workflow where there is no audit trail of what was changed and why.

**How to implement:**
- Deploy phase creates a PR/CR via version control API
- PR includes structured sections: Summary, Changes, Test Evidence, Review Summary
- Auto-merge is a team-level configuration, not a framework default
- Show a code block with example PR body structure

---

#### Principle 8: Tool Agnostic

**One-line summary:** "Patterns transfer to any agent stack. The framework teaches structure, not a vendor."

**Why it matters:**
The AI landscape changes monthly. Tying a framework to a specific agent provider, a specific model, or a specific tool means rewriting everything when the landscape shifts.

AEF defines patterns (phases, loops, gates, artifact chaining) that work regardless of whether you use Claude, Kiro, open-source models, or a mix. The agentic layer is the abstraction boundary.

*Example:* A team using Cline today can switch to Kiro next month. The prompt templates, quality gates, and pipeline config remain the same. Only the tool integration layer changes.

**Anti-pattern:** A framework that only works with one agent provider. Prompt templates that use provider-specific syntax. Pipeline logic that depends on a specific model's capabilities.

**How to implement:**
- Prompt templates use generic markdown, not provider-specific formats
- Tool integrations are abstracted behind categories (file system, execution, search) rather than specific products
- Pipeline config references capabilities, not products
- Show a code block with the tool abstraction:
```yaml
# tools/file-system.yaml
category: file_system
capabilities:
  - read_file
  - write_file
  - list_directory
  - search_content
# Implementation maps to your specific agent's tools
```

---

### Section 10: Principles Summary Table

After all 8 principles, include a summary reference table:

| # | Principle | One-liner |
|---|-----------|-----------|
| 1 | Opinionated but Evolvable | Strong defaults, everything configurable |
| 2 | Self-Healing Over Failure | Diagnose and retry before escalating |
| 3 | Plan-Before-Execute | Research is read-only, plan before build |
| 4 | Least Privilege | Each phase gets only needed tools |
| 5 | Test-Driven Contracts | Tests first, they are the contract |
| 6 | Structured Outputs | Machine-readable and human-readable |
| 7 | Ship Means PR | Done = reviewable change request |
| 8 | Tool Agnostic | Patterns transfer to any agent stack |

**UI component:** A styled table with `bg-surface` background, `border border-subtle`, `font-mono` for the principle names. Numbers in glow-colored circles.

---

### Section 11: Next Steps CTA

Same pattern as Page 1: three link cards to Overview, Architecture, and Get Started.

---

### Cross-Links for Page 2
- **Inbound:** Landing page Principles section (link each principle card), Page 1 "Go Deeper" section, nav bar
- **Outbound:** `/framework/overview`, `/framework/architecture`, `/guides/getting-started`

---

## Page 3: Pipeline Architecture

### Metadata
- **URL:** `/framework/architecture` (file: `website/framework/architecture.html`)
- **Title:** `Pipeline Architecture | Agentic Engineering Framework`
- **Meta description:** "Technical architecture of the AEF pipeline: state machine, artifact chaining, feedback loops, escalation, quality gates, and phase execution model."

### Purpose
Technical deep dive into how the pipeline works as a system. This is the most detailed page in the framework section, aimed at developers who want to understand the machinery before building their agentic layer.

---

### Section 1: Hero / Intro

**Heading:** "Pipeline Architecture"
**Section label:** "Architecture"

**Content to write:**
Brief intro (2-3 sentences): The AEF pipeline is a state machine that moves a task through 7 phases, chains artifacts between them, self-heals when phases fail, and escalates when self-healing exhausts. This page covers the technical architecture.

**UI components:**
- Same hero treatment as other pages
- Breadcrumb: Home / Framework / Architecture
- Below intro, include the full pipeline SVG visualization from the landing page hero as a reference diagram

---

### Section 2: Pipeline State Machine

**Heading:** "The Pipeline as a State Machine"
**Section label:** "State Machine"

**Content to write:**

Explain that each pipeline run is a state machine with the following states:

- `PLANNING` -- Plan phase active
- `BUILDING` -- Build phase active
- `TESTING` -- Test phase active
- `TEST_RETRY` -- Test failed, builder agent fixing, will re-test
- `REVIEWING` -- Review phase active
- `REVIEW_PATCH` -- Review found blockers, patching, will re-test and re-review
- `FULL_REBUILD` -- Review found fundamental issues, returning to Build
- `DOCUMENTING` -- Document phase active
- `DEPLOYING` -- Deploy phase active (creating PR)
- `MONITORING` -- Monitor phase active
- `ESCALATED` -- Loop exhausted, human intervention needed
- `COMPLETE` -- PR created, pipeline done

**State transitions:**
Show a state transition diagram. Key transitions:
- `PLANNING` -> `BUILDING` (plan approved)
- `BUILDING` -> `TESTING` (build complete)
- `TESTING` -> `REVIEWING` (all tests pass)
- `TESTING` -> `TEST_RETRY` (tests fail, retries remaining)
- `TEST_RETRY` -> `TESTING` (fix applied, re-test)
- `TEST_RETRY` -> `ESCALATED` (retries exhausted)
- `REVIEWING` -> `DOCUMENTING` (review passes)
- `REVIEWING` -> `REVIEW_PATCH` (blockers found, retries remaining)
- `REVIEW_PATCH` -> `TESTING` (patch applied, re-test before re-review)
- `REVIEWING` -> `FULL_REBUILD` (fundamental issues, rebuild retries remaining)
- `FULL_REBUILD` -> `BUILDING` (feedback provided, rebuild)
- `REVIEW_PATCH` -> `ESCALATED` (retries exhausted)
- `DOCUMENTING` -> `DEPLOYING`
- `DEPLOYING` -> `MONITORING`
- `MONITORING` -> `COMPLETE`

**Pipeline Manifest concept:**
Explain that each pipeline run maintains a manifest/state object that tracks:
- Current state
- Phase history (which phases ran, how many iterations)
- Artifacts produced per phase
- Errors encountered and retries attempted
- Total token/cost accounting

**UI components:**
- State diagram: Build as an SVG. Nodes are rounded rectangles colored by their phase color. Transitions are arrows with labels. The retry/escalation paths should be visually distinct (dashed lines in test/review colors).
- Manifest example: A code block showing a sample JSON manifest:
```json
{
  "pipeline_id": "run_2026-03-10_001",
  "state": "REVIEWING",
  "phase_history": [
    {"phase": "plan", "status": "complete", "iterations": 1},
    {"phase": "build", "status": "complete", "iterations": 1},
    {"phase": "test", "status": "complete", "iterations": 2}
  ],
  "current_iteration": 1,
  "artifacts": {
    "plan": "$plan_artifact",
    "build": "$build_artifact",
    "test_results": "$test_results"
  },
  "total_retries": 1,
  "escalated": false
}
```

**Interactive elements:**
- The state diagram could highlight the current state on hover, showing which transitions are available from that state.

**Content writer notes:**
- This is the most technical section. Assume the reader knows what a state machine is.
- The manifest is a conceptual model. Note that specific implementations may vary but should track this information.

---

### Section 3: Artifact Chaining

**Heading:** "Artifact Chaining: The Pipeline's Memory"
**Section label:** "Artifacts"

**Content to write:**

Each phase produces a structured artifact that the next phase consumes via template variables. This is how state flows through the pipeline without requiring a shared database.

**The artifact chain:**

| Phase | Produces | Template Variable | Consumed By |
|-------|----------|-------------------|-------------|
| Plan | Implementation plan | `$plan_artifact` | Build |
| Build | Code changes + test suite | `$build_artifact` | Test |
| Build | E2E test commands | `$e2e_commands` | Test |
| Test | Test results + coverage | `$test_results` | Review |
| Review | Review verdict + issues | `$review_artifact` | Document, Deploy |
| Document | Docs + changelog | `$doc_artifact` | Deploy |
| Deploy | PR/CR reference | `$deploy_artifact` | Monitor |

**How variable substitution works:**
When a phase starts, its prompt template is hydrated with artifacts from previous phases. For example, the Build phase prompt contains `${plan_artifact}`, which is replaced with the actual plan output before the agent sees it.

**Example flow (show visually):**
```
Plan outputs:
  Summary: "Add GET /users endpoint"
  Files to modify: [src/routes.ts:45, src/controllers/user.ts]
  Test strategy: "Unit tests for controller, integration test for route"
         |
         v  ($plan_artifact injected into build.md template)
Build outputs:
  Changed files: [src/routes.ts, src/controllers/user.ts, tests/user.test.ts]
  Test commands: ["npm test -- --grep 'user'"]
         |
         v  ($build_artifact + $e2e_commands injected into test prompt)
Test outputs:
  Results: { passed: 14, failed: 1, coverage: 87% }
  Failure details: "user.test.ts:23 - Expected 200, got 404"
         |
         v  ($test_results injected into review prompt)
...continues through Review, Document, Deploy
```

**UI components:**
- The artifact chain should be visualized as a vertical or horizontal flow diagram. Each phase is a node (using phase colors). Between nodes, show the template variable name on the connecting arrow.
- Recommended: Build as an SVG. Horizontal flow on `lg:`, vertical on mobile.
- Each phase node: rounded rectangle with phase color border, phase name, and a small snippet of what the artifact contains.
- Connecting arrows: solid lines with the `$variable_name` label in `font-mono text-xs text-glow`.
- Below the diagram, show a code block with an example prompt template that uses variable substitution, highlighting the `${plan_artifact}` syntax.

**Interactive elements:**
- Hover on a phase node highlights its outgoing artifact and the consuming phase. The connecting arrow and variable name glow on hover.

**Content writer notes:**
- This is one of the most important concepts in the framework. Make the visual clear and self-explanatory.
- Emphasize that artifacts are structured (connects to Principle 6: Structured Outputs). If artifacts were freeform, variable substitution would not work.
- Use the `/users` endpoint example that was introduced on Page 1 for consistency.

---

### Section 4: Feedback Loops

**Heading:** "Self-Healing Feedback Loops"
**Section label:** "Feedback Loops"

**Content to write:**

Two distinct loop types, each with a dedicated flowchart.

#### Loop 1: Test Retry Loop

**Trigger:** Test phase reports failures.
**Flow:**
1. Test phase runs all tests
2. Tests fail -> analyze failure output
3. Spawn builder agent with: failure context, original plan, changed files
4. Builder agent applies fix
5. Re-run tests
6. If pass -> continue to Review
7. If fail -> repeat from step 3 (up to `max_attempts`, default 3)
8. If retries exhausted -> ESCALATE to human

**Flowchart (build as SVG):**
```
[Test Phase] -> tests pass? --YES--> [Review Phase]
      |
      NO (attempt < max)
      |
      v
[Analyze Failure] -> [Spawn Builder] -> [Apply Fix] -> [Re-run Tests]
      ^                                                      |
      |                                                      |
      +---------- still failing? (attempt < max) <----------+
                                    |
                              attempt >= max
                                    |
                                    v
                              [ESCALATE]
```

Colors: Test loop in `test` green. Builder spawns in `build` amber. Escalation in `fail` red.

#### Loop 2: Review-Patch Loop

**Trigger:** Review phase finds blocker-severity issues.
**Flow:**
1. Review phase analyzes code against quality gates
2. Blockers found -> produce structured issue list
3. Spawn builder agent with: review issues, current code, test results
4. Builder agent applies patches
5. Re-run tests (must still pass after patches)
6. Re-submit to Review
7. If review passes -> continue to Document
8. If blockers remain -> repeat from step 3 (up to `max_attempts`, default 3)
9. If retries exhausted -> ESCALATE to human

**Additional: Full Rebuild Loop**
If the review identifies fundamental/architectural issues (not patchable), the pipeline can loop all the way back to Build with new feedback. This is more expensive and has a lower retry limit (default: 1).

**Flowchart (build as SVG):**
```
[Review Phase] -> passes? --YES--> [Document Phase]
      |
      NO - blocker issues (attempt < max)
      |
      v
[Produce Issue List] -> [Spawn Builder] -> [Apply Patches] -> [Re-test] -> [Re-review]
      ^                                                                         |
      |                                                                         |
      +------------ still has blockers? (attempt < max) <----------------------+
                                    |
                              attempt >= max
                                    |
                                    v
                         [ESCALATE] or [FULL REBUILD]
```

Colors: Review loop in `review` blue. Builder in `build` amber. Re-test arrows in `test` green. Escalation in `fail` red.

**UI components:**
- Two side-by-side flowcharts on `lg:`, stacked on mobile. Each in its own card (`bg-surface border border-subtle rounded-xl p-6`).
- Flowcharts built as SVGs with phase-colored nodes and labeled arrows.
- Below each flowchart, a small config snippet showing how to customize the loop:
```yaml
# Test Retry Loop config
test_retry:
  max_attempts: 3
  escalation_action: notify_human
```

**Interactive elements:**
- Animated dashed lines along the loop paths (reuse `.loop-arc` animation from landing page)
- Hover on "ESCALATE" node shows a tooltip explaining what context the human receives

**Content writer notes:**
- Make the distinction between Test Retry (code is wrong) and Review Patch (code works but has quality issues) very clear.
- Emphasize that re-testing happens after review patches too. Patches must not break tests.
- The Full Rebuild Loop is a last resort. Frame it as expensive but necessary for fundamental issues.

---

### Section 5: Escalation

**Heading:** "Escalation: When the Pipeline Needs a Human"
**Section label:** "Escalation"

**Content to write:**

When feedback loops exhaust their retry limits, the pipeline enters the `ESCALATED` state. This is not a failure -- it is a designed handoff point.

**What the human receives (context package):**
- The original task/issue
- The plan that was produced
- The code that was built
- All test results (including from retry attempts)
- All review findings (including from patch attempts)
- A summary of what was tried and why it did not work
- The specific blocker that could not be resolved

**What the human can do:**
- Provide guidance and resume the pipeline from the current phase
- Override a quality gate and let the pipeline continue
- Modify the agentic layer (update a prompt, adjust a gate) and re-run
- Abort the pipeline

**UI components:**
- A single large card showing the escalation context package. Use a code-block style with labeled sections for each piece of context.
- Below it, a 4-item grid showing the 4 human response options, each as a small card with an icon.
- Color scheme: `warning` yellow for the escalation card border. The context package uses `muted` text for labels and `primary` for values.

**Content writer notes:**
- Escalation is a feature, not a failure. Frame it positively: "The pipeline tried everything it could, now it is giving you full context to make a decision."
- Emphasize that the pipeline provides full context -- the human never starts from zero.

---

### Section 6: Phase Execution Model

**Heading:** "Phase Execution Model"
**Section label:** "Execution"

**Content to write:**

**Sequential by default:**
Phases run in order: Plan -> Build -> Test -> Review -> Document -> Deploy -> Monitor. Each phase must complete before the next begins. This is the safest execution model.

**Parallelizable phases:**
Some phases can run in parallel when they have no data dependencies:
- Document and Deploy prep can overlap (documentation does not block PR creation structure)
- Within a phase, multiple agents can work in parallel (e.g., security reviewer and style reviewer run simultaneously during the Review phase)
- Monitor runs continuously, not just after Deploy

**Phase skipping:**
Some phases can be skipped for specific issue types:
- A documentation-only change might skip Build and Test
- A hotfix might use a minimal plan and skip Document
- Phase skipping is configured per issue-type in the pipeline config

**UI components:**
- A timeline/sequence diagram showing the default sequential flow
- Annotations showing which phases can overlap
- A small table showing issue-type routing:

| Issue Type | Plan | Build | Test | Review | Document | Deploy |
|-----------|------|-------|------|--------|----------|--------|
| Feature | Full | Full | Full | Full | Full | Full |
| Bug | Targeted | Targeted | Full | Full | Minimal | Full |
| Hotfix | Minimal | Targeted | Full | Minimal | Skip | Full |
| Docs-only | Skip | Skip | Skip | Full | Full | Full |

**Content writer notes:**
- Default is sequential. Parallelization is an optimization, not a starting point.
- Phase skipping should feel safe, not risky. Emphasize that Review still runs even on hotfixes.

---

### Section 7: Quality Gates

**Heading:** "Quality Gates: Pass/Fail Between Phases"
**Section label:** "Quality Gates"

**Content to write:**

Quality gates are the checkpoints between phases. A phase cannot hand off to the next phase until its gate passes.

**Gate types:**
1. **Coverage gate** (after Test): Minimum test coverage percentage. Default 80%.
2. **Test pass gate** (after Test): All tests must pass. No exceptions.
3. **Review severity gate** (after Review): No blocker-severity issues remaining.
4. **Documentation completeness gate** (after Document): Required sections present (summary, changes, references).
5. **PR structure gate** (after Deploy): PR has required sections, all artifacts attached.

**Gate configuration example:**
```yaml
# gates/test-coverage.yaml
gate: test_coverage
phase: test
criteria:
  min_coverage: 80          # percentage
  all_tests_pass: true
  new_code_covered: true     # new code specifically must be tested
on_fail: trigger_test_retry
on_exhaust: escalate
```

```yaml
# gates/review-severity.yaml
gate: review_severity
phase: review
criteria:
  max_blocker_count: 0       # zero blockers to pass
  max_critical_count: 2      # up to 2 critical (logged as tech debt)
  tech_debt_logged: true     # critical issues must be tracked
on_fail: trigger_review_patch
on_exhaust: escalate
```

**How gates connect to loops:**
When a gate fails, it triggers the corresponding feedback loop. When the loop exhausts, the gate triggers escalation. This is the mechanism that connects quality requirements to self-healing behavior.

**UI components:**
- Gate types as a vertical list of cards, each with a colored left border matching the phase it belongs to
- Config examples in code blocks with syntax highlighting
- A small diagram showing: Phase -> Gate -> (pass) -> Next Phase / (fail) -> Feedback Loop -> (retry) -> Phase -> Gate again

**Interactive elements:**
- Hover on a gate card highlights the corresponding phase in a mini pipeline diagram at the top of the section

**Content writer notes:**
- Gates are the enforcement mechanism for every principle. Connect them back: gates enforce TDD (coverage gate), gates enforce quality (review gate), gates enforce structure (PR gate).
- Make clear that all gate thresholds are configurable. The defaults are sensible starting points.

---

### Section 8: Putting It All Together

**Heading:** "Complete Pipeline Run: End to End"
**Section label:** "Full Example"

**Content to write:**

A complete walkthrough of a pipeline run for a feature request ("Add GET /users endpoint"), showing every state transition, artifact produced, gate check, and (one) retry.

Presented as a vertical timeline with expandable steps. Each step shows:
- State name and phase color
- What the agent did (1-2 sentences)
- Artifact snippet (in a small code block)
- Gate result (pass/fail badge)

Timeline:
1. `PLANNING` -- Architect agent reads codebase, produces plan. Gate: plan structure complete. PASS.
2. `BUILDING` -- Engineer agent writes tests first, then implementation. Gate: build complete. PASS.
3. `TESTING` -- QA agent runs tests. 14 pass, 1 fails. Gate: all tests pass. FAIL.
4. `TEST_RETRY` (iteration 1) -- Builder agent receives failure context, patches the route handler. 
5. `TESTING` (retry) -- All 15 tests pass, coverage 87%. Gate: coverage >= 80%. PASS.
6. `REVIEWING` -- Reviewer agent analyzes. No blockers. 1 tech-debt item logged. Gate: 0 blockers. PASS.
7. `DOCUMENTING` -- Writer agent generates docs from diffs. Gate: required sections present. PASS.
8. `DEPLOYING` -- PR created with all artifacts. Gate: PR structure valid. PASS.
9. `COMPLETE` -- Pipeline done. Total: 1 retry, 9 phase executions.

**UI components:**
- Vertical timeline using the maturity stepper pattern from the landing page
- Each step is a card with the phase color as left border
- Pass/fail badges next to gate checks (use `perm-allowed`/`perm-denied` styling)
- Small code snippets inside each card showing artifact fragments
- A summary box at the bottom with metrics: total phases, total retries, total gates passed

**Interactive elements:**
- Each step reveals on scroll
- Steps that involve a retry have a subtle amber highlight on the card background

**Content writer notes:**
- This is the payoff section. The reader should see all the concepts from the page coming together in one concrete example.
- Use the same `/users` endpoint example that has been threaded through the other pages.
- Keep artifact snippets short (3-5 lines each). Just enough to show the structure.

---

### Section 9: Next Steps CTA

Same pattern as other pages: three link cards to Overview, Principles, and Get Started.

---

### Cross-Links for Page 3
- **Inbound:** Page 1 "Go Deeper" section, Page 2 references to architecture, landing page pipeline section, nav bar
- **Outbound:** `/framework/overview`, `/framework/principles`, `/guides/getting-started`

---

## Content Writer Global Notes

### Tone
- **Authoritative but approachable.** Write like a senior engineer explaining to a peer, not like a marketing page selling to a prospect.
- **Concrete over abstract.** Every claim should have an example or a code snippet.
- **Direct.** Short sentences. Active voice. No hedging ("might," "could possibly").
- **Technical but not academic.** Use terms like "state machine" and "artifact" but explain them on first use.

### Key Messages to Reinforce Across All Three Pages
1. "The code is output, not input." -- Developers build the layer, agents write the code.
2. Self-healing is a design choice, not magic. It has limits (retry caps) and fallbacks (escalation).
3. Everything is configurable. Strong defaults, no walls.
4. The framework is tool-agnostic. Patterns, not products.

### Things to Avoid
- Hype language ("revolutionary," "game-changing," "next-gen")
- Vendor-specific references (do not mention Claude, Kiro, etc. by name except in the Tool Agnostic principle's example)
- Implying that autonomous means unsupervised. The pipeline has quality gates, retry limits, and escalation.
- Over-promising. The framework provides structure; the quality of outputs still depends on the agentic layer configuration.

### Formatting Conventions
- Code variables in backticks: `$plan_artifact`
- Phase names capitalized: Plan, Build, Test, Review, Document, Deploy, Monitor
- Pipeline refers to the full end-to-end flow
- Agentic layer is always two words, lowercase unless starting a sentence

---

### Critical Files for Implementation
- `/Users/alejtr/Documents/obsidian/obsidian/agentic-layer-framework/website/index.html` - Source of truth for all design system patterns, component HTML, Tailwind config, CSS animations, and JavaScript behaviors to replicate across the 3 new pages
- `/Users/alejtr/Documents/obsidian/obsidian/agentic-layer-framework/framework/Framework Overview.md` - Source content for Page 1 (overview) and Page 2 (principles): philosophy, core principles, architecture diagram, and the "what developers configure" table
- `/Users/alejtr/Documents/obsidian/obsidian/agentic-layer-framework/pipeline/Pipeline Architecture.md` - Source content for Page 3 (architecture): phase details, feedback loop definitions, agent team model, and configuration points
- `/Users/alejtr/Documents/obsidian/obsidian/agentic-layer-framework/thinking/Decisions Log.md` - Rationale behind key design decisions (TDD-first, Ship=PR, opinionated-but-configurable) used to write the "Why It Matters" sections for each principle on Page 2
- `/Users/alejtr/Documents/obsidian/obsidian/agentic-layer-framework/framework/Glossary.md` - Canonical definitions for all framework terms to ensure consistent terminology across all three pagesagentId: ab90ecd6ed005cec9 (for resuming to continue this agent's work if needed)
<usage>total_tokens: 66579
tool_uses: 14
duration_ms: 366873</usage>