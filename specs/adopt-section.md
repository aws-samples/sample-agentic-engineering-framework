# Adopt Section -- Page Spec

**Author:** Planning Agent
**Date:** 2026-03-10
**Status:** Draft
**Target directory:** `/website/specs/`

## Design System Reference

All pages inherit the design system defined in `/website/index.html`:

| Token | Value | Usage |
|---|---|---|
| Void | `#09090B` | Page background |
| Surface | `#111113` | Card backgrounds |
| Raised | `#1A1A1F` | Hover / elevated surfaces |
| Subtle | `#232329` | Borders, dividers |
| Primary | `#F4F4F5` | Headings, body text |
| Secondary | `#A1A1AA` | Descriptions, supporting text |
| Muted | `#52525B` | Labels, metadata |
| Glow | `#6366F1` | Accent, active states, CTAs |
| Phase colors | `plan:#8B5CF6` `build:#F59E0B` `test:#10B981` `review:#3B82F6` `document:#A78BFA` `deploy:#F97316` `monitor:#06B6D4` | Phase-specific UI |
| Pass / Fail | `#22C55E` / `#EF4444` | Gate results, permission badges |
| Body font | IBM Plex Sans | All body text |
| Code/heading font | JetBrains Mono | Code blocks, labels, phase names, step indicators |

Shared component patterns (from `index.html`):
- **Cards**: `rounded-xl bg-surface border border-subtle hover:border-glow-faint transition-all`
- **Code blocks**: `.code-block` class -- `bg-void border border-subtle rounded-lg`, syntax highlight classes `.var .keyword .string .comment .type`
- **Permission badges**: `.perm-allowed` (green) / `.perm-denied` (red)
- **Section headings**: mono uppercase label (`text-sm font-mono text-glow tracking-wider uppercase`) above an `h2`
- **Stepper/timeline**: circle indicators with `step-connector` vertical lines
- **CTA buttons**: Primary (`bg-glow hover:bg-glow-hover text-white rounded-lg`), Secondary (`border border-subtle hover:bg-raised`)
- **Scroll reveal**: `.reveal` class for entrance animations
- **Tab bar**: row of `button` elements with `border-b-2` active indicator

### Shared Navigation

All Adopt pages share the site navigation from `index.html`. The "Adopt" nav link becomes a dropdown or section with sub-links:
- Getting Started
- By Team Size
- Maturity Path
- Customization

---

## Page 1: `/adopt/getting-started`

### Title
Getting Started -- Minimum Viable Agentic Layer

### Purpose
Take a developer from zero to a working agentic layer in one sitting. This is the single most important page for adoption. Every instruction must be copy-paste ready. No ambiguity.

### Content Outline

#### Section 1: Hero / 5-Minute Overview
**Heading:** `Getting Started` (h1, JetBrains Mono)
**Subheading:** "Build your first agentic layer in one sitting. Three prompt templates, one quality gate, one manual run."

**UI Component:** Summary card (raised surface with glow border) containing:
- What you will build: 3 prompt templates + 1 quality gate
- What you will learn: The Plan, Build, Test loop -- the core of every agentic pipeline
- Time estimate: 30-60 minutes for setup, then one manual run

**Content writer notes:** This opening must feel achievable. The reader should think "I can do this today." No prerequisites beyond what is listed below.

#### Section 2: Prerequisites
**Heading:** `## Prerequisites`

**UI Component:** Three-card horizontal grid (same pattern as Value Props on landing page)

Card 1: **A Codebase**
- Any language, any size, any age
- You need at least one existing test to validate the quality gate
- If you have no tests, that is fine -- your first agentic task can be "add a test"

Card 2: **An AI Agent**
- Any provider that can read files, write files, and execute commands
- Examples (clearly labeled as examples, not endorsements): Cline, Kiro, or any LLM with tool use
- The framework is tool agnostic. The patterns work with any agent.

Card 3: **Git**
- A version control system (git is assumed throughout, but the pattern applies to any VCS)
- A branch to work on (never work directly on main)

**Content writer notes:** Keep this to three items. Do not add "familiarity with X" or other soft prerequisites. The point is: you already have everything you need.

#### Section 3: Step 1 -- Create the Directory Structure
**Heading:** `## Step 1: Create the directory structure`

**UI Component:** Numbered step indicator (circle with "1" in glow color, same stepper pattern as maturity levels on landing page)

**Code block:**
```
mkdir -p agentic-layer/{prompts,gates}
```

**Annotation below code block:** "That's it. Two directories. `prompts/` holds your phase templates. `gates/` holds your quality criteria. You can add `tools/`, `commands/`, and `pipeline.yaml` later."

**Directory tree visualization** (code block with `.type .var .comment` classes):
```
agentic-layer/
├── prompts/          # One template per pipeline phase
│   ├── plan.md       # You'll write this in Step 2
│   └── build.md      # You'll write this in Step 3
└── gates/            # Quality criteria
    └── test-pass.md  # You'll write this in Step 4
```

#### Section 4: Step 2 -- Write Your Plan Template
**Heading:** `## Step 2: Write your Plan template`

**UI Component:** Numbered step indicator (circle with "2")

**Introductory text:** "The Plan template tells your agent how to research and plan before writing any code. This is the most important template because it prevents the number one agentic failure: the agent starts building before it understands the problem."

**Code block** (full file, copy-paste ready, with syntax highlighting):
```markdown
# Plan Phase -- Software Architect

## Role
You are a Software Architect. Research the codebase
and produce a detailed implementation plan.

## Context
Issue: ${issue_description}
Type: ${issue_type}

## Constraints
- Read-only. Do not modify any files.
- Research before planning. Read relevant source files,
  tests, and documentation before proposing changes.
- Reference specific file:line locations.
- Do NOT plan changes beyond the stated issue.

## Output
1. Summary of changes (2-3 sentences)
2. Files to modify (with line numbers)
3. Files to create (if any)
4. What we are NOT doing (anti-scope-creep)
5. Test strategy (what tests prove this works)
```

**Annotations** (tag badges below code block):
- `Role Assignment` -- Gives the agent a persona with clear boundaries
- `Template Variables` -- `${issue_description}` and `${issue_type}` are replaced at runtime
- `Read-Only Constraint` -- Prevents the agent from building during planning
- `Anti-Scope-Creep` -- Explicitly states what is out of scope
- `Structured Output` -- Machine-readable sections the Build phase can consume

**Callout box** (raised surface with `border-l-4 border-plan`):
"Save this as `agentic-layer/prompts/plan.md`. You will feed this to your agent in Step 5."

#### Section 5: Step 3 -- Write Your Build Template
**Heading:** `## Step 3: Write your Build template`

**UI Component:** Numbered step indicator (circle with "3")

**Introductory text:** "The Build template tells your agent how to implement the plan. Notice it references `${plan_artifact}` -- this is artifact chaining. The output of Plan becomes the input of Build."

**Code block:**
```markdown
# Build Phase -- Software Engineer

## Role
You are a Software Engineer. Implement the plan
exactly as specified.

## Context
Plan: ${plan_artifact}
Issue: ${issue_description}

## Constraints
- Follow the plan. Do not add features, refactor
  unrelated code, or deviate from the spec.
- Write tests FIRST, then implementation.
- Only modify files listed in the plan.
- Make atomic, focused changes.

## Output
1. Tests written (file paths)
2. Implementation changes (file paths)
3. Commands to run tests
4. Any assumptions or deviations from plan (explain why)
```

**Annotations:**
- `Artifact Chaining` -- `${plan_artifact}` links Build to the Plan output
- `TDD-First` -- Tests before implementation, the contract for every subsequent phase
- `Scope Lock` -- Only files listed in the plan. No improvising.

**Callout box** (raised surface with `border-l-4 border-build`):
"Save this as `agentic-layer/prompts/build.md`."

#### Section 6: Step 4 -- Write Your First Quality Gate
**Heading:** `## Step 4: Write your first quality gate`

**UI Component:** Numbered step indicator (circle with "4")

**Introductory text:** "A quality gate defines pass/fail criteria for a pipeline phase. Your first gate is simple: do the tests pass?"

**Code block:**
```markdown
# Test Pass Gate

## Criteria
- All existing tests pass (zero failures)
- All new tests written by the Build phase pass
- No test was deleted or skipped to achieve a pass

## Pass
All criteria met. Proceed to next phase.

## Fail
One or more criteria not met.
Action: Feed test output + build template back to the
agent for a retry. Maximum 3 retries before escalating
to human.
```

**Callout box** (raised surface with `border-l-4 border-test`):
"Save this as `agentic-layer/gates/test-pass.md`. This is your safety net."

#### Section 7: Step 5 -- Run It Manually
**Heading:** `## Step 5: Run your first pipeline -- manually`

**UI Component:** Numbered step indicator (circle with "5", glow effect)

**Sub-steps** (indented timeline, smaller step indicators):

**5a. Plan**
- Give your agent the Plan template (`agentic-layer/prompts/plan.md`)
- Replace `${issue_description}` with a real issue from your project (pick something small)
- Replace `${issue_type}` with the type (bug, feature, task, patch)
- Let the agent research and produce a plan
- Read the plan. Does it make sense? Does it reference real files and lines?

**5b. Build**
- Give your agent the Build template (`agentic-layer/prompts/build.md`)
- Replace `${plan_artifact}` with the plan output from step 5a
- Replace `${issue_description}` with the same issue description
- Let the agent write tests and then implementation

**5c. Test (apply the gate)**
- Run the test commands the agent provided
- Check the gate criteria from `agentic-layer/gates/test-pass.md`
- If **pass**: You are done. You just completed your first agentic pipeline run.
- If **fail**: Give the agent the test output + the build template. Say "Tests failed. Here are the results. Fix the implementation following the build template." This is the self-healing loop. Retry up to 3 times.

**Success callout** (raised surface with `border-l-4 border-pass`, pass-green accent):
"Congratulations. You just ran the Plan, Build, Test loop manually. That is your minimum viable agentic layer. Three templates, one gate, one loop. Everything else in the framework builds on this foundation."

#### Section 8: What's Next
**Heading:** `## What's next`

**UI Component:** Four-card grid linking to deeper content

Card 1: **Add more phases** -- Review, Document, Deploy. Link to Pipeline deep-dive.
Card 2: **Configure self-healing loops** -- Automate the retry. Link to Self-Healing Loops concept page.
Card 3: **Customize for your stack** -- Language-specific constraints, team conventions. Link to `/adopt/customization`.
Card 4: **Graduate autonomy** -- Move from L1 to L2 and beyond. Link to `/adopt/maturity-path`.

#### Section 9: Common First Mistakes
**Heading:** `## Common first mistakes`

**UI Component:** Three expandable accordion sections with warning-yellow accent

**Mistake 1: Templates too vague**
- Bad: "Write good code that follows best practices"
- Good: "Follow the plan in ${plan_artifact}. Write tests first. Modify only the files listed."
- Why: Vague instructions give the agent room to improvise. Specificity is control.

**Mistake 2: Giving Plan execute permissions**
- What happens: The agent starts building during planning.
- Fix: Your Plan template says "Read-only. Do not modify any files."
- Why: Planning and building are separate cognitive modes.

**Mistake 3: No anti-scope-creep instructions**
- What happens: You ask for a bug fix, the agent refactors three files and adds a feature.
- Fix: "Do NOT plan/implement changes beyond the stated issue" + the "What we are NOT doing" output section.

**Cross-links:** Framework Overview, Pipeline Architecture, Glossary, Prompt Engineering Patterns, Artifact Chaining

---

## Page 2: `/adopt/by-team-size`

### Title
Adoption by Team Size

### Purpose
Help readers find the right adoption strategy based on their team size. Different scales need different infrastructure, governance, and process.

### Content Outline

#### Section 1: Header
**Heading:** `Adoption by Team Size` (h1)
**Subheading:** "The framework scales from solo developer to enterprise platform. Your team size determines your starting point, not your ceiling."

#### Section 2: Tab Selector
**UI Component:** Horizontal tab bar. Three tabs: `Solo Developer` | `Small Team (2-10)` | `Enterprise (10+)`

#### Section 3: Solo Developer
**Badge:** "Setup: 1-2 hours"

- You ARE the team. You configure the layer, agents execute it.
- Recommended pipeline: Plan, Build, Test, Deploy (skip Review, Document, Monitor)
- Lightweight gates: test-pass gate is sufficient
- No orchestration complexity -- one agent, one pipeline
- Focus on: prompt templates that encode YOUR coding standards
- Maturity target: L2-L3, L4 for routine work

**Minimal pipeline.yaml:**
```yaml
phases: [plan, build, test, deploy]
loops:
  test: { max_retries: 3, on_exhaust: escalate }
gates:
  test: { criteria: test-pass }
```

#### Section 4: Small Team (2-10 Engineers)
**Badge:** "Setup: 1-2 days"

- Agentic layer becomes a shared artifact. Store in repo.
- Full 7-phase pipeline, standard gates
- Template changes go through PR review
- Focus on: consistency across team members
- Senior engineers maintain templates, all engineers use them
- Maturity target: L2-L3, L4 for routine

**Division of labor table:**

| Senior Engineers | All Engineers |
|---|---|
| Write and maintain prompt templates | Use templates for daily work |
| Configure quality gates | Run pipelines against issues |
| Tune loop limits and escalation | Report template issues |
| Review template change PRs | Propose improvements |

#### Section 5: Enterprise (10+ Engineers, Multiple Teams)
**Badge:** "Setup: 1-2 weeks for base layer"

- Agentic layer becomes a platform
- Shared base templates + team-specific overrides
- Strict gates for high-risk, lighter for internal tools
- Audit logging, template approval workflows

**Key practices:**
1. Base layer + team overrides directory pattern
2. Risk-based gate configuration (critical/standard/low-risk profiles)
3. KPI monitoring across teams

#### Section 6: Comparison Table

| Dimension | Solo | Small Team | Enterprise |
|---|---|---|---|
| Setup time | 1-2 hours | 1-2 days | 1-2 weeks |
| Pipeline phases | 4 | All 7 | All 7 + custom |
| Gate complexity | 1 gate | 2-3 gates | Risk-tiered |
| Template ownership | You | Senior engineers | Platform team |
| Maturity target | L2-L3 | L2-L3 | L2-L4 tiered by risk |

**Cross-links:** Getting Started, Customization, Maturity Path, Pipeline Architecture

---

## Page 3: `/adopt/maturity-path`

### Title
Maturity Path -- From Assisted to ASE

### Purpose
Expand the L1-L4 stepper from the landing page into a full operational guide with graduation criteria at each level.

### Content Outline

#### Section 1: Header
**Heading:** `Maturity Path` (h1)
**Subheading:** "Start where you are. Graduate when your gates prove you are ready. Not every team needs Level 4."

#### Section 2: Overview Stepper
**UI Component:** Same stepper as landing page (L1/L2/L3/L4 circles with connectors), serving as anchor navigation to sections below.

#### Section 3: Level 1 -- Assisted
**Badge:** "Duration: 1-2 weeks"

- How it works: Human runs each phase manually, reviews every output
- What you learn: Whether templates produce good output, which constraints are missing
- Day-in-the-life narrative walkthrough
- **Graduation checklist:**
  - [ ] Plan templates consistently produce actionable specs
  - [ ] Build output passes tests on first or second try (>70%)
  - [ ] Identified and fixed at least 3 template weaknesses
  - [ ] Completed 10+ successful manual pipeline runs
  - [ ] Test-pass quality gate catches real failures

#### Section 4: Level 2 -- Supervised
**Badge:** "Duration: 2-4 weeks"

- How it works: Agent runs phases, human approves at checkpoints (after Plan, after Test, after Review)
- Self-healing loops run without human intervention
- **Checkpoint diagram:** `Plan → [APPROVE] → Build → Test ⟲ → [APPROVE] → Review ⟲ → [APPROVE] → Document → Deploy`
- **Graduation checklist:**
  - [ ] Self-healing loops resolve 70%+ of failures
  - [ ] Quality gates have <20% false positive rate
  - [ ] No surprises in last 20 pipeline runs
  - [ ] Trust the Review phase output
  - [ ] Checkpoint approvals becoming rubber stamps

#### Section 5: Level 3 -- Autonomous
**Badge:** "Duration: 1-3 months"

- How it works: Agent runs full pipeline, human reviews only the PR
- Quality gates are the safety net
- **When to stay at L3:** Most teams operate here for majority of work. This is not a failure.
- **Graduation checklist:**
  - [ ] 95%+ pipeline runs complete without intervention
  - [ ] PRs consistently meet quality standards
  - [ ] Monitor phase configured and catching regressions
  - [ ] Rollback procedures tested
  - [ ] Team agreed on risk profile for auto-merge

#### Section 6: Level 4 -- Autonomous Software Engineering (ASE)
**Badge:** "The destination -- for the right work"

- How it works: Agent runs, gates pass, auto-merge. No human in the loop.
- **When appropriate:** Low-risk changes, well-understood patterns, excellent monitoring
- **When NOT appropriate** (warning callout): Security-sensitive code, breaking API changes, new architectural patterns, regulatory areas
- "Most teams operate at L2-L3 for critical paths and L4 for routine maintenance. That is good engineering."

#### Section 7: Measuring Progress

**Metrics table:**

| Metric | L1 | L2 | L3 | L4 |
|---|---|---|---|---|
| Pipeline success rate | Track manually | >70% | >90% | >95% |
| Avg loop count | N/A | <3 | <2 | <1.5 |
| Escalation rate | 100% | <30% | <10% | <5% |
| Human intervention | Every phase | Checkpoints | PR review | None |

**Dashboard mockup:** Four metric cards (success rate, loop count, escalation rate, time-to-PR)

**Cross-links:** Getting Started (L1 start), By Team Size (maturity targets), Self-Healing Loops, Quality Gates

---

## Page 4: `/adopt/customization`

### Title
Customization Guide

### Purpose
Show developers how to adapt defaults to their specific codebase, language, team, and workflow.

### Content Outline

#### Section 1: Header
**Heading:** `Customization Guide` (h1)
**Subheading:** "The defaults get you started. Customization makes the framework yours."

#### Section 2: Adapting Templates for Your Codebase
- What to add: project structure context, language constraints, team conventions, domain knowledge
- **Before/after example:** Generic Plan template vs. React + TypeScript customized version (side-by-side code blocks)
- Key additions highlighted: role specialization, project structure, architectural patterns, testing tools, domain-specific output sections

#### Section 3: Adding Custom Phases
- When to add: recurring step that doesn't fit defaults, has its own gate, needs different persona/tools
- **Example: Security Audit phase**
  - Step 1: Create template (`security-audit.md`)
  - Step 2: Create gate (`security-audit.yaml`)
  - Step 3: Update `pipeline.yaml`
  - Full code for all three files provided

#### Section 4: Creating Custom Agent Roles
- A role = persona + tool permissions + output format
- **Example roles** (three cards): Database Migration Specialist, API Contract Validator, Accessibility Auditor

#### Section 5: Issue-Type Routing
- Different work types need different templates
- Default routing table: feature/bug/task/patch
- How to add custom types: hotfix, migration, refactor, spike
- Pipeline.yaml routing config example
- Spike type can skip Build phase entirely

#### Section 6: Integrating with Your CI/CD
- Artifact flow table (phase → artifact → CI/CD integration)
- Pattern: PR-driven workflow (pipeline creates PR, CI validates, merge)
- Pattern: event-driven triggering (new issue → pipeline → PR)
- **Tool agnostic:** Say "your CI pipeline" not specific providers

#### Section 7: Team-Specific Overrides
- Base layer + team overrides directory pattern
- Merge strategy: team templates replace base for same phase, team gates are additive
- Pipeline.yaml teams config example

**Cross-links:** Getting Started (starting templates), By Team Size (when to use overrides), Pipeline Architecture, Prompt Engineering Patterns, Tool Permission Design

---

## Global Content Writer Notes

**Tone:** Welcoming, practical, direct. Be the experienced colleague showing you the ropes.

**Jargon rule:** Every framework term (agentic layer, quality gate, feedback loop, artifact chaining, escalation) must be linked to its definition on first use per page.

**Code blocks:** Every code block must be copy-paste ready. No pseudocode, no "..." elisions. Use `${variable_name}` for replaceable values.

**Tool agnosticism:** Never recommend a specific tool. Use: "For example, if you are using [tool category], you would [action]."

**Cross-linking pattern:** Descriptive link text: "Learn more about [quality gates](/concepts/quality-gates)"

**Accessibility:** All diagrams must have text alternatives. All interactive elements must be keyboard navigable.
