Good -- only the landing page exists so far. I now have a thorough understanding of:

1. The design system (colors, fonts, component patterns from the HTML)
2. The framework concepts (from Framework Overview, Pipeline Architecture, Glossary)
3. The existing UI components (phase cards with permission badges, code blocks with syntax highlighting, tabbed interfaces, directory tree visualizations, maturity stepper)
4. The tone (hands-on, concise, opinionated but configurable)

Now I have all the information I need to write the comprehensive spec. Since this is a READ-ONLY task, I will present the complete spec as my output rather than writing it to a file.

---

Here is the complete page spec for the Agentic Layer section. This should be saved to `/Users/alejtr/Documents/obsidian/obsidian/agentic-layer-framework/website/specs/agentic-layer-section.md`.

---

# Agentic Layer Section -- Page Spec

> **Section purpose:** This is the "what you actually build" section of the AEF website. Five pages covering the concrete artifacts engineers create. Every example is copy-paste-adaptable. Tone is hands-on and practical.

> **Design system reference:** All pages inherit from the landing page at `/website/index.html`. Colors, fonts, component patterns, and layout conventions are defined there. See the Tailwind config and CSS custom classes in that file.

---

## Shared Design Patterns (all 5 pages)

### Layout
- Fixed nav (same as landing page)
- Page hero: section label (uppercase mono, glow color) + h1 + subtitle paragraph
- Max content width: `max-w-4xl` for prose sections, `max-w-3xl` for code blocks
- Section separators: `border-t border-subtle` between major sections
- Ambient glow blobs used sparingly (1-2 per page)
- Footer identical to landing page

### Typography
- Section labels: `text-sm font-mono text-glow tracking-wider uppercase`
- Page title: `text-3xl sm:text-4xl lg:text-5xl font-bold text-primary`
- Section headings: `text-2xl sm:text-3xl font-bold text-primary`
- Subsection headings: `text-xl font-semibold text-primary`
- Body: `text-sm text-secondary leading-relaxed` (IBM Plex Sans)
- Code/mono: `font-mono text-sm` (JetBrains Mono)

### Code Block Component
```html
<div class="code-block p-6 overflow-x-auto">
  <!-- Optional: phase-colored left border via border-l-2 border-{phase} -->
  <pre class="font-mono text-sm leading-relaxed"><code>...</code></pre>
</div>
```
Syntax classes: `.var` (indigo #818CF8), `.keyword` (purple #8B5CF6), `.string` (green #10B981), `.comment` (muted #52525B), `.type` (cyan #06B6D4)

### Annotation Badges
```html
<span class="inline-flex items-center gap-1.5 px-2.5 py-1 text-[10px] font-mono rounded bg-{color}/8 text-{color} border border-{color}/15">
  Label
</span>
```

### Card Component
```html
<div class="p-5 rounded-xl bg-surface border border-subtle hover:border-glow-faint transition-all duration-250">
  <h4 class="font-mono text-sm font-semibold text-primary mb-2">Title</h4>
  <p class="text-xs text-secondary leading-relaxed">Description</p>
</div>
```

### Tabbed Interface
Reuse the pattern from the prompt template showcase on the landing page: tab bar with `border-b border-subtle`, active tab with phase-colored `border-b-2`, content panel below.

### Cross-link Pattern
Internal links styled as: `text-glow hover:text-glow-hover underline decoration-glow/30 hover:decoration-glow/60 transition-all duration-200`

### Sidebar Navigation (new for inner pages)
Left sidebar on desktop (hidden on mobile, toggle button) listing all 5 pages in this section with active state indicator. Sticky at `top-20`.

---

## Page 1: `/agentic-layer/prompt-templates`

### Page URL and Title
- **URL:** `/agentic-layer/prompt-templates`
- **Title:** Prompt Templates -- The Core Artifact

### Purpose
Teach engineers how to write, structure, version, and evolve prompt templates -- the most important artifact in the agentic layer. This page makes the abstract concept of "prompt engineering" concrete and actionable.

### Content Outline

#### Section 1: Hero
- **Label:** THE AGENTIC LAYER
- **Heading:** Prompt Templates
- **Subtitle:** "A prompt template is a structured instruction set that defines how an agent behaves within a pipeline phase. It is the single most important artifact in your agentic layer."

#### Section 2: What Is a Prompt Template
- **Heading:** `## What Is a Prompt Template`
- **Content:** One-paragraph definition. A prompt template is not a one-off chat message. It is a reusable, versioned, parameterized document that transforms a generic AI model into a specialist with a specific role, bounded scope, and predictable output format. It sits in your repo alongside your code.
- **Callout box** (raised bg, glow-faint border): "Think of prompt templates as job descriptions for agents. A job description defines the role, the context the employee needs, what they are and are not allowed to do, and what deliverables they must produce. Prompt templates do the same thing."

#### Section 3: Prompt Anatomy -- The 4 Essential Sections
- **Heading:** `## Anatomy of a Prompt Template`
- **Subtitle:** "Every template needs four sections. Miss one and the agent drifts."
- **UI Component:** Four stacked cards, each with a numbered indicator, section name, and description. Each card has a colored left border (plan, build, test, review colors respectively).

**Card 1 -- Role**
- Number: `01`
- Title: Role
- Description: Who the agent is. A persona assignment that sets behavioral expectations. "You are a Software Architect" is fundamentally different from "You are a QA Engineer." The role determines what the agent prioritizes, how it communicates, and what it considers important.
- Example snippet (inline code): `You are a Senior Software Engineer specializing in test-driven development.`

**Card 2 -- Context**
- Number: `02`
- Title: Context
- Description: What the agent knows. Template variables inject dynamic information at runtime: the issue description, branch name, prior phase artifacts, relevant files. Without context, agents hallucinate. With too much context, they lose focus.
- Example snippet: `Issue: ${issue_description}` / `Plan: ${plan_artifact}`

**Card 3 -- Constraints**
- Number: `03`
- Title: Constraints
- Description: What the agent can and cannot do. Tool permissions, scope boundaries, anti-patterns to avoid. Constraints are the guardrails that prevent scope creep, unauthorized file modifications, and architectural drift.
- Example snippet: `- Read-only. Do not modify any files.` / `- Do NOT add new dependencies without explicit approval in the plan.`

**Card 4 -- Output Format**
- Number: `04`
- Title: Output Format
- Description: What the agent produces. A JSON schema, markdown template, or specific structure that downstream phases can parse. Structured outputs enable artifact chaining -- the pipeline's memory.
- Example snippet: `Produce a JSON object with keys: summary, files_modified, files_created, test_strategy`

#### Section 4: Template Variables
- **Heading:** `## Template Variables`
- **Subtitle:** "Variables are how the pipeline injects runtime data into templates."
- **UI Component:** Three-column table (on desktop; stacked cards on mobile)

| Category | Variables | Description |
|----------|-----------|-------------|
| **Static** | `${issue_type}`, `${branch_name}`, `${issue_description}`, `${project_name}` | Set once when the pipeline starts. Come from the issue tracker or user input. |
| **Artifact** | `${plan_artifact}`, `${build_artifact}`, `${test_results}`, `${review_results}`, `${doc_artifact}` | Output from a previous phase. This is artifact chaining in action. |
| **Context** | `${codebase_summary}`, `${relevant_files}`, `${test_commands}`, `${dependency_graph}`, `${recent_changes}` | Dynamically gathered from the codebase at runtime. Context providers populate these. |

- **Subsection: How Variables Get Substituted**
- Paragraph explaining: Before a template is sent to the agent, the pipeline engine performs variable substitution. Every `${variable_name}` is replaced with its runtime value. If a variable is undefined, the pipeline should either use a default or fail loudly (never send raw `${...}` to an agent).
- Code block showing before/after substitution:

```
# BEFORE substitution (template on disk)
Issue: ${issue_description}
Type:  ${issue_type}
Prior plan: ${plan_artifact}

# AFTER substitution (what the agent receives)
Issue: Add pagination to the /users API endpoint
Type:  feature
Prior plan: ## Implementation Plan
  1. Add `page` and `limit` query params to GET /users
  2. Update UserRepository.findAll() to accept pagination
  3. Add tests for boundary conditions (page 0, negative limit)
  ...
```

#### Section 5: Template Gallery
- **Heading:** `## Template Gallery`
- **Subtitle:** "Complete, annotated templates for three phases. Copy, adapt, use."
- **UI Component:** Tabbed interface (same pattern as landing page) with three tabs: `plan.md`, `build.md`, `review.md`. Each tab shows a full template in a code block with a phase-colored left border, followed by an annotation panel.

**Tab 1: plan.md** (left border: plan purple #8B5CF6)
```markdown
# Plan Phase — Software Architect

## Role
You are a Software Architect. Your job is to research the
codebase and produce a detailed implementation plan for the
task described below. You do not write code. You plan it.

## Context
Issue: ${issue_description}
Type: ${issue_type}                    # feature | bug | task | patch
Branch: ${branch_name}
Project: ${project_name}

### Codebase Context
${codebase_summary}

### Relevant Files
${relevant_files}

## Constraints
- READ-ONLY. Do not create, modify, or delete any files.
- Research the codebase thoroughly before proposing changes.
- Never plan and execute simultaneously.
- Reference specific file paths and line numbers.
- If the issue is ambiguous, state your assumptions explicitly.
- Do NOT expand scope beyond what the issue describes.

## Anti-Scope-Creep
The following are explicitly OUT OF SCOPE for this plan:
- Refactoring code not directly related to the issue
- Upgrading dependencies unless required by the fix
- Adding features not described in the issue
- Changing configuration files unless the issue requires it

## Output Format
Produce a structured implementation plan with these sections:

### 1. Summary
One paragraph describing the change and its purpose.

### 2. Files to Modify
| File | Lines | Change Description |
|------|-------|--------------------|
| path/to/file.ts | 42-58 | Description of change |

### 3. Files to Create
| File | Purpose |
|------|---------|
| path/to/new-file.ts | Description |

### 4. What We Are NOT Doing
Bullet list of out-of-scope items the agent considered and rejected.

### 5. Test Strategy
- Unit tests to write
- Integration tests to write
- Edge cases to cover

### 6. Risk Assessment
- What could go wrong
- Dependencies on external systems
- Breaking change potential: yes/no
```

Annotations below the code block:
- `Role Assignment` (plan color badge)
- `Template Variables` (glow color badge)
- `Anti-Scope-Creep` (fail color badge)
- `Structured Output Contract` (test color badge)
- `Read-Only Constraint` (warning color badge)

**Tab 2: build.md** (left border: build amber #F59E0B)
```markdown
# Build Phase — Software Engineer

## Role
You are a Senior Software Engineer. You implement the plan
produced by the Plan phase. You follow Test-Driven Development:
write tests first, then write code to pass them.

## Context
Issue: ${issue_description}
Type: ${issue_type}
Branch: ${branch_name}

### Implementation Plan
${plan_artifact}

### Codebase Context
${codebase_summary}

### Test Commands
${test_commands}

## Constraints
- Follow the plan EXACTLY. Do not add, remove, or change scope.
- Write tests FIRST. Run them. Confirm they fail. Then write code.
- Do NOT modify files not listed in the plan.
- Do NOT add new dependencies unless the plan explicitly approves them.
- Make atomic commits — one logical change per commit.
- If you discover the plan has a gap, STOP and report it.
  Do not improvise a solution.

## Anti-Patterns to Avoid
- Bulk file creation without running tests between changes
- Modifying test assertions to make them pass instead of fixing code
- Using `any` types, `// @ts-ignore`, or suppression comments
- Adding TODO comments instead of implementing the feature
- Catching and swallowing errors silently

## Output Format
After implementation, produce a build report:

### Build Report
**Files Modified:** (list with brief description per file)
**Files Created:** (list with brief description per file)
**Tests Written:** (count and list)
**Tests Passing:** (count, should match tests written)
**Commands to Run Tests:**
```bash
# Unit tests
${test_commands}
# Integration tests (if applicable)
```

### Deviations from Plan
(List any deviations. If none, write "None — plan followed exactly.")
```

Annotations:
- `TDD-First` (build color badge)
- `Plan Adherence` (plan color badge)
- `Anti-Pattern Guard` (fail color badge)
- `Build Report Output` (test color badge)

**Tab 3: review.md** (left border: review blue #3B82F6)
```markdown
# Review Phase — Senior Code Reviewer

## Role
You are a Senior Code Reviewer with 10+ years of experience.
Your job is to review the implementation against the plan,
identify issues, and classify their severity. You do NOT
fix issues — you report them.

## Context
Issue: ${issue_description}
Type: ${issue_type}

### Original Plan
${plan_artifact}

### Build Report
${build_artifact}

### Test Results
${test_results}

## Constraints
- READ-ONLY. Do not modify any files.
- Review ONLY the files listed in the build report.
- Compare implementation against the plan, not your preferences.
- Every issue must have a severity classification.
- Be specific: reference file paths and line numbers.

## Review Checklist
1. **Plan Adherence** — Does the implementation match the plan?
2. **Test Coverage** — Are all acceptance criteria tested?
3. **Error Handling** — Are errors caught, logged, and surfaced?
4. **Security** — No hardcoded secrets, no injection vulnerabilities,
   no unsafe deserialization.
5. **Performance** — No N+1 queries, no unbounded loops,
   no missing pagination.
6. **Code Style** — Consistent with existing codebase conventions.
7. **Documentation** — Public APIs documented, complex logic commented.

## Severity Classifications
- **blocker** — Must fix before merge. Security issues, broken
  functionality, data loss risk, test failures.
- **tech-debt** — Should fix but not blocking. Performance concerns,
  minor style issues, missing edge case tests.
- **nitpick** — Optional. Naming suggestions, formatting preferences.
  These do NOT trigger the patch loop.

## Output Format
Produce a structured review:

### Review Verdict: PASS | FAIL

### Issues Found
| # | File | Line | Severity | Description | Suggested Fix |
|---|------|------|----------|-------------|---------------|
| 1 | path/to/file.ts | 42 | blocker | Description | Fix suggestion |

### Summary
- Blockers: (count)
- Tech Debt: (count)
- Nitpicks: (count)
- Recommendation: PASS / FAIL (with blockers) / FAIL (architectural)

### What Was Done Well
(2-3 positive observations — reviewers should reinforce good patterns)
```

Annotations:
- `Read-Only Analysis` (review color badge)
- `Severity Classification` (warning color badge)
- `Structured Verdict` (test color badge)
- `Plan Comparison` (plan color badge)

#### Section 6: Versioning Templates Like Code
- **Heading:** `## Versioning Templates`
- **Subtitle:** "Templates are code. Treat them like code."
- **UI Component:** Four-item list with icon bullets (checkmark icons)

1. **Store in version control** -- Templates live in `agentic-layer/prompts/` alongside your codebase. Every change is tracked, diffable, and revertable.
2. **Review template changes like code changes** -- A changed prompt can alter agent behavior across every pipeline run. PR reviews for templates are essential.
3. **Test template changes against sample inputs** -- Before merging a template change, run it against 2-3 representative issues. Compare output quality before/after.
4. **Maintain a changelog per template** -- Add a comment block at the top of each template with version history. Example:

```markdown
<!-- Changelog
  v3 - 2026-03-08 - Added anti-scope-creep section after agents kept expanding scope
  v2 - 2026-02-15 - Added risk assessment output section
  v1 - 2026-01-20 - Initial template
-->
```

#### Section 7: Template Evolution
- **Heading:** `## Template Evolution`
- **Subtitle:** "Start simple. Add constraints as you discover edge cases."

- **Progression diagram** -- Visual showing template growth over time:
  - v1: Role + Context + Output (10 lines) -- "Your first template"
  - v2: + Constraints section (15 lines) -- "After agents drifted off-scope"
  - v3: + Anti-scope-creep (20 lines) -- "After agents added unrequested features"
  - v4: + Anti-patterns list (30 lines) -- "After agents used bad patterns"
  - v5: Issue-type routing (4 templates) -- "After one template couldn't handle all issue types"

- **Subsection: When to Split a Template**
  - Paragraph: When your constraints section has multiple conditional blocks ("if this is a bug, do X; if this is a feature, do Y"), it is time to split.
  - Example: `plan.md` becomes `plan-feature.md`, `plan-bug.md`, `plan-task.md`, `plan-patch.md`
  - The pipeline config routes to the correct template based on `${issue_type}`

- **Code block** showing routing config:
```yaml
# pipeline.yaml — issue-type routing
templates:
  plan:
    feature: prompts/plan-feature.md
    bug: prompts/plan-bug.md
    task: prompts/plan-task.md
    patch: prompts/plan-patch.md
    default: prompts/plan.md       # fallback
```

### UI Components Summary
- Callout box (1)
- Numbered cards with colored left borders (4)
- Three-column responsive table (1)
- Code blocks with before/after comparison (1)
- Tabbed interface with 3 tabs (1) -- the main template gallery
- Annotation badge panels (3, one per tab)
- Icon-bulleted list (1)
- Progression diagram (1) -- can be a simple vertical stepper like the maturity path on the landing page
- YAML code block (1)

### Interactive Elements
- **Tabbed template gallery:** Click plan.md / build.md / review.md to switch displayed template
- **Expandable annotations:** Each annotation badge in the panel, when clicked, shows a tooltip or expands to explain what that technique does and why it matters

### Cross-Links
- Pipeline phases: link to individual phase pages when referencing Plan, Build, Review
- Concepts > Artifact Chaining: link when discussing template variables and `${plan_artifact}`
- Concepts > Prompt Engineering Patterns: link from the anatomy section
- Agentic Layer > Pipeline Config: link from the routing config example
- Agentic Layer > Quality Gates: link from the "structured output" discussion (gates parse these outputs)

### Content Writer Notes
- This is the highest-traffic page in the section. It must be excellent.
- Tone: practical instructor. "Here is what to write. Here is why. Here is what happens if you skip it."
- Every template in the gallery must be complete enough to copy into a repo and use with minor adaptation. No `...` or `[insert here]` placeholders.
- The anti-scope-creep section resonates strongly -- call it out as a key differentiator. Agents without it reliably expand scope.
- Variable substitution before/after example is critical for understanding. Do not skip it.
- Avoid referencing any specific AI tool or IDE. Say "the agent" or "the pipeline engine," never a product name.

---

## Page 2: `/agentic-layer/commands-skills`

### Page URL and Title
- **URL:** `/agentic-layer/commands-skills`
- **Title:** Custom Commands & Skills

### Purpose
Explain the difference between commands (human-invoked) and skills (agent-invoked), show how to create both, and demonstrate composability -- how commands use skills internally.

### Content Outline

#### Section 1: Hero
- **Label:** THE AGENTIC LAYER
- **Heading:** Custom Commands & Skills
- **Subtitle:** "Commands are what humans type. Skills are what agents call. Together they make your agentic layer interactive and composable."

#### Section 2: Commands vs Skills
- **Heading:** `## Commands vs Skills`
- **UI Component:** Two-column comparison (side by side on desktop, stacked on mobile). Each column is a raised card with colored top border.

**Left card -- Commands** (glow color top border)
- Title: Commands
- Subtitle: Human-invoked
- Description: A human types a command, and an agent executes it. Commands are the interface between your team and the agentic layer. Think of them as named, parameterized entry points.
- Examples: `/plan`, `/build`, `/test`, `/commit`, `/explain`, `/security-audit`
- When to use: When a human wants to trigger a specific agent behavior on demand, outside the full pipeline.

**Right card -- Skills** (build color top border)
- Title: Skills
- Subtitle: Agent-invoked
- Description: One agent calls another agent's capability programmatically. Skills are the composability layer -- they let agents delegate sub-tasks. The calling agent receives structured output it can parse and act on.
- Examples: `run-tests`, `lint-check`, `dependency-check`, `generate-commit-message`
- When to use: When a pipeline phase needs to delegate a sub-task to a specialized capability.

#### Section 3: Anatomy of a Command
- **Heading:** `## Anatomy of a Command`
- **UI Component:** Code block with annotations

```markdown
---
name: commit
description: Stage changes, generate a conventional commit message, and commit.
parameters:
  - name: scope
    type: string
    required: false
    description: "Conventional commit scope (e.g., auth, api, ui)"
tools:
  - file_system.read
  - file_system.search
  - code_execution.shell
---

# /commit Command

## Role
You are a Release Engineer. Your job is to create a clean,
conventional commit from the current staged changes.

## Context
Current diff:
${git_diff_staged}

Recent commit history:
${recent_commits}

Scope (if provided): ${scope}

## Constraints
- Use Conventional Commits format: type(scope): description
- Types: feat, fix, refactor, test, docs, chore, perf, ci
- Subject line max 72 characters
- Body should explain WHY, not WHAT (the diff shows what)
- Do NOT amend previous commits
- Do NOT force push
- If no files are staged, tell the user and stop

## Output
1. Show the generated commit message to the user
2. Ask for confirmation (y/n)
3. If confirmed, execute: git commit -m "<message>"
4. Show the commit hash and summary
```

Annotation badges below:
- `YAML Frontmatter` (muted color)
- `Tool Permissions` (fail color)
- `Parameter Declaration` (glow color)
- `Confirmation Step` (warning color)

#### Section 4: Anatomy of a Skill
- **Heading:** `## Anatomy of a Skill`
- **UI Component:** Code block with annotations

```markdown
---
name: run-tests
description: Execute the test suite and return structured results.
trigger: called by build, test, or review phases
output_format: json
tools:
  - code_execution.shell
  - file_system.read
---

# run-tests Skill

## Role
You are a Test Runner. Execute the project's test suite and
return structured results that the calling agent can parse.

## Context
Test commands:
${test_commands}

Project type: ${project_type}      # node | python | go | rust | java

## Constraints
- Run ALL test suites, not just unit tests
- Do NOT modify test files or source code
- Do NOT skip failing tests
- If a test command fails to execute (not test failure,
  but command error), report it separately
- Timeout per test suite: 120 seconds

## Output Format
Return a JSON object:
```json
{
  "status": "pass | fail | error",
  "suites": [
    {
      "name": "unit",
      "command": "npm test",
      "passed": 42,
      "failed": 1,
      "skipped": 0,
      "duration_ms": 3200,
      "failures": [
        {
          "test": "UserService.create should validate email",
          "file": "src/services/__tests__/user.test.ts",
          "line": 28,
          "error": "Expected 'invalid' to throw ValidationError",
          "type": "assertion"
        }
      ]
    }
  ],
  "coverage": {
    "lines": 84.2,
    "branches": 71.5,
    "functions": 89.1
  },
  "total_passed": 42,
  "total_failed": 1,
  "total_skipped": 0
}
```

Annotation badges:
- `Structured JSON Output` (test color)
- `Agent-Parseable` (glow color)
- `No Code Modification` (fail color)

#### Section 5: More Example Commands
- **Heading:** `## Example Commands`
- **UI Component:** Tabbed interface with 3 tabs

**Tab: /security-audit**
```markdown
---
name: security-audit
description: Scan the codebase for OWASP Top 10 vulnerabilities.
parameters:
  - name: target
    type: string
    required: false
    description: "Specific directory or file to audit (default: entire project)"
tools:
  - file_system.read
  - file_system.search
  - code_execution.shell
---

# /security-audit Command

## Role
You are a Security Engineer specializing in application security.
Scan the codebase for vulnerabilities from the OWASP Top 10.

## Context
Project: ${project_name}
Target: ${target}
Language: ${primary_language}

### Codebase Summary
${codebase_summary}

## Constraints
- READ-ONLY. Do not modify any files.
- Focus on the OWASP Top 10 2021 categories:
  1. Broken Access Control
  2. Cryptographic Failures
  3. Injection (SQL, NoSQL, OS command, LDAP)
  4. Insecure Design
  5. Security Misconfiguration
  6. Vulnerable and Outdated Components
  7. Identification and Authentication Failures
  8. Software and Data Integrity Failures
  9. Security Logging and Monitoring Failures
  10. Server-Side Request Forgery (SSRF)
- Prioritize findings by severity: critical, high, medium, low
- Do NOT report false positives — if unsure, mark as "needs review"

## Output Format
### Security Audit Report

**Overall Risk Level:** CRITICAL | HIGH | MEDIUM | LOW | CLEAN

| # | Category | Severity | File | Line | Finding | Remediation |
|---|----------|----------|------|------|---------|-------------|

### Summary
- Critical: (count)
- High: (count)
- Medium: (count)
- Low: (count)
- Needs Review: (count)

### Recommended Next Steps
(Prioritized list of remediations)
```

**Tab: /explain**
```markdown
---
name: explain
description: Explain a function, module, or architecture decision with full context.
parameters:
  - name: target
    type: string
    required: true
    description: "File path, function name, or module to explain"
  - name: depth
    type: string
    required: false
    description: "brief | detailed | architecture (default: detailed)"
tools:
  - file_system.read
  - file_system.search
---

# /explain Command

## Role
You are a Senior Software Architect explaining code to a
colleague. Be clear, precise, and contextual.

## Context
Target: ${target}
Depth: ${depth}

### File Contents
${target_file_contents}

### Call Graph
${call_graph}

### Related Files
${related_files}

## Constraints
- READ-ONLY. Do not modify any files.
- Explain the WHAT, the WHY, and the HOW.
- Reference the actual code — use line numbers.
- If the target depends on other modules, explain the relationship.
- Adjust depth based on the depth parameter:
  - brief: 2-3 sentences, what it does and why
  - detailed: full walkthrough with code references
  - architecture: how it fits into the broader system

## Output Format
### ${target}

**Purpose:** (one sentence)

**How It Works:**
(Explanation at the requested depth level)

**Dependencies:**
- (list of modules/functions this depends on)

**Called By:**
- (list of modules/functions that call this)

**Key Design Decisions:**
- (why was it built this way, not another way)
```

#### Section 6: More Example Skills
- **Heading:** `## Example Skills`
- **UI Component:** Tabbed interface with 2 tabs

**Tab: lint-check**
```markdown
---
name: lint-check
description: Run linter and categorize issues by severity.
trigger: called by build or review phases
output_format: json
tools:
  - code_execution.shell
  - file_system.read
---

# lint-check Skill

## Role
You are a Code Quality Analyst. Run the project's linter
and return categorized results.

## Context
Lint command: ${lint_command}
Project type: ${project_type}
Files changed: ${changed_files}

## Constraints
- Run the linter ONLY on changed files (if supported by the linter)
- Do NOT auto-fix issues — report only
- Do NOT modify any files
- Categorize issues: error (must fix), warning (should fix), info (optional)

## Output Format
```json
{
  "status": "clean | warnings | errors",
  "issues": [
    {
      "file": "src/services/user.ts",
      "line": 15,
      "column": 8,
      "severity": "error",
      "rule": "no-unused-vars",
      "message": "'tempData' is defined but never used"
    }
  ],
  "summary": {
    "errors": 1,
    "warnings": 3,
    "info": 0
  }
}
```

**Tab: dependency-check**
```markdown
---
name: dependency-check
description: Analyze dependencies for known vulnerabilities and outdated packages.
trigger: called by review or monitor phases
output_format: json
tools:
  - code_execution.shell
  - file_system.read
---

# dependency-check Skill

## Role
You are a Dependency Analyst. Check the project's dependencies
for known vulnerabilities, outdated versions, and license issues.

## Context
Package file: ${package_file}          # package.json, requirements.txt, go.mod, etc.
Project type: ${project_type}

## Constraints
- Do NOT install or update any packages
- Do NOT modify lock files
- Use the project's native audit tool when available:
  - Node: npm audit / yarn audit
  - Python: pip-audit / safety
  - Go: govulncheck
  - Rust: cargo audit
- If no native tool exists, analyze the manifest file directly

## Output Format
```json
{
  "status": "secure | vulnerable | unknown",
  "vulnerabilities": [
    {
      "package": "lodash",
      "installed_version": "4.17.15",
      "patched_version": "4.17.21",
      "severity": "high",
      "cve": "CVE-2021-23337",
      "description": "Prototype pollution in lodash"
    }
  ],
  "outdated": [
    {
      "package": "express",
      "installed": "4.17.1",
      "latest": "4.18.2",
      "update_type": "minor"
    }
  ],
  "summary": {
    "total_dependencies": 142,
    "vulnerabilities_critical": 0,
    "vulnerabilities_high": 1,
    "vulnerabilities_medium": 3,
    "outdated_major": 2,
    "outdated_minor": 8
  }
}
```

#### Section 7: Composability
- **Heading:** `## Composability: Commands Use Skills`
- **Subtitle:** "Commands and skills compose. A command invokes skills internally, chaining structured outputs."
- **UI Component:** Visual flow diagram (simple, using the same SVG style as the landing page pipeline)

Diagram shows:
```
Human types /build
       │
       ▼
┌─────────────┐     ┌──────────┐
│   /build    │────▶│run-tests │ (skill)
│  (command)  │     └──────────┘
│             │     ┌──────────┐
│             │────▶│lint-check│ (skill)
│             │     └──────────┘
│             │
│  Build      │
│  Report     │
└─────────────┘
```

- Paragraph explaining: The `/build` command's template can reference skills by name. When the build agent reaches the testing step, it invokes the `run-tests` skill, receives structured JSON back, and uses that data to decide whether to continue or report failures. The `lint-check` skill runs separately. The command orchestrates; the skills execute.

#### Section 8: Creating Your Own
- **Heading:** `## How to Create Your Own`
- **UI Component:** Directory tree + step-by-step list

Directory structure:
```
agentic-layer/
├── commands/
│   ├── commit.md
│   ├── security-audit.md
│   ├── explain.md
│   └── your-command.md        # ← add here
├── skills/
│   ├── run-tests.md
│   ├── lint-check.md
│   ├── dependency-check.md
│   └── your-skill.md          # ← add here
```

Steps:
1. **Choose command or skill.** If a human triggers it, it is a command. If an agent triggers it, it is a skill.
2. **Create the file.** Markdown with YAML frontmatter. Name it descriptively: the filename becomes the invocation name.
3. **Define the frontmatter.** Name, description, parameters (commands only), trigger conditions (skills only), tool access, output format.
4. **Write the prompt.** Follow the 4-section anatomy: Role, Context, Constraints, Output Format.
5. **Test it.** Run the command/skill against 2-3 representative inputs. Verify the output structure matches your spec.
6. **Commit and share.** The command/skill is now available to your entire team.

- **Naming conventions** callout box:
  - Commands: lowercase, hyphenated. `security-audit`, not `SecurityAudit` or `SECURITY_AUDIT`.
  - Skills: lowercase, hyphenated. `run-tests`, not `runTests`.
  - Filenames match invocation names: `security-audit.md` is invoked as `/security-audit`.

### UI Components Summary
- Two-column comparison cards (1)
- Code blocks with annotation panels (2 -- command anatomy, skill anatomy)
- Tabbed interfaces (2 -- example commands, example skills)
- SVG flow diagram (1)
- Directory tree code block (1)
- Numbered step list (1)
- Callout box (1)

### Interactive Elements
- **Tabbed command gallery:** switch between /security-audit, /explain
- **Tabbed skill gallery:** switch between lint-check, dependency-check
- **Composability diagram:** static SVG, but hoverable nodes that highlight the flow

### Cross-Links
- Agentic Layer > Prompt Templates: link from "Follow the 4-section anatomy" in the creation steps
- Agentic Layer > Tool Integrations: link from tool access in frontmatter
- Agentic Layer > Pipeline Config: link from "the pipeline can route to commands"
- Pipeline > Build phase: link from /build command example
- Pipeline > Test phase: link from run-tests skill
- Concepts > Artifact Chaining: link from composability section

### Content Writer Notes
- The command vs skill distinction is the key conceptual takeaway. Make it crystal clear in the comparison cards.
- Every example must have realistic YAML frontmatter. This is the file format readers will actually use.
- The composability section is where "aha" moments happen. Show how the pieces connect.
- Skills output JSON because agents parse JSON. Commands output human-readable text because humans read text. Make this explicit.

---

## Page 3: `/agentic-layer/tool-integrations`

### Page URL and Title
- **URL:** `/agentic-layer/tool-integrations`
- **Title:** Tool Integrations

### Purpose
Define what "tools" mean in the agentic context (capabilities, not products), explain the 4 categories, and show how to configure tool access per phase.

### Content Outline

#### Section 1: Hero
- **Label:** THE AGENTIC LAYER
- **Heading:** Tool Integrations
- **Subtitle:** "Tools are capabilities you give to agents. File reading, code execution, API access, context gathering. Not IDEs. Not products. Capabilities."

#### Section 2: What Are Tools
- **Heading:** `## What Are Tools in This Context`
- Paragraph: In the agentic engineering framework, a "tool" is a capability boundary. It defines what an agent can do in the environment. Reading a file is a tool. Running a shell command is a tool. Creating a pull request is a tool. The framework organizes these into 4 categories and controls which phases get access to which categories.
- **Callout box:** "Tools are not products. 'File system access' is a tool category. A specific editor, IDE, or CLI is a product that provides that tool category. The framework defines the categories; your tooling stack provides the implementations."

#### Section 3: The 4 Categories
- **Heading:** `## The Four Tool Categories`
- **UI Component:** Four expandable cards, each with an icon, title, description, sub-items, and a "used by phases" badge row.

**Card 1: File System Access** (icon: folder, color: glow)
- **Sub-capabilities:**
  - **Read:** Read file contents, list directory structures, check file existence
  - **Write:** Create new files, edit existing files, delete files
  - **Search:** Pattern matching (grep/glob), find files by name, AST-based code search
- **Phase usage badges:** Plan (Read, Search), Build (All), Test (Read, Search, Write), Review (Read, Search), Document (Read, Search, Write), Deploy (Read, Search), Monitor (Read, Search)
- **Config example:**
```yaml
# tools/file-system.yaml
file_system:
  read:
    enabled: true
    allowed_paths:
      - "src/**"
      - "tests/**"
      - "docs/**"
    denied_paths:
      - ".env"
      - "**/*.secret"
      - "node_modules/**"
  write:
    enabled: true
    allowed_paths:
      - "src/**"
      - "tests/**"
    denied_paths:
      - "src/config/production.ts"
      - "**/*.lock"
  search:
    enabled: true
    max_results: 100
    timeout_ms: 5000
```

**Card 2: Code Execution** (icon: terminal, color: build)
- **Sub-capabilities:**
  - **Shell:** Run arbitrary commands (with sandboxing)
  - **Test runners:** Execute test suites -- jest, pytest, go test, cargo test, etc.
  - **Linters/formatters:** eslint, prettier, ruff, gofmt, rustfmt, etc.
  - **Build tools:** Compile, bundle, type-check -- tsc, webpack, cargo build, etc.
- **Phase usage badges:** Build (All), Test (All), Deploy (Shell, Build tools), Monitor (Shell)
- **Security callout box** (fail-colored border):
  "Code execution is the most powerful and most dangerous tool category. Always sandbox agent execution environments. Agents should never: run commands that modify system-level configuration, access network resources not explicitly allowed, execute commands that delete files outside the project directory, install global packages."
- **Config example:**
```yaml
# tools/code-execution.yaml
code_execution:
  shell:
    enabled: true
    sandbox: true
    timeout_ms: 120000
    allowed_commands:
      - "npm *"
      - "npx *"
      - "node *"
      - "git *"
      - "tsc *"
    denied_commands:
      - "rm -rf /*"
      - "sudo *"
      - "curl * | bash"
      - "npm publish"
  test_runners:
    enabled: true
    commands:
      unit: "npm test"
      integration: "npm run test:integration"
      e2e: "npm run test:e2e"
    timeout_ms: 300000
  linters:
    enabled: true
    commands:
      lint: "npm run lint"
      format_check: "npm run format:check"
  build:
    enabled: true
    commands:
      typecheck: "npx tsc --noEmit"
      build: "npm run build"
```

**Card 3: External APIs** (icon: globe/link, color: deploy)
- **Sub-capabilities:**
  - **Version control:** git operations, branch management, PR creation, merge
  - **CI/CD:** Trigger pipelines, check build status, read logs
  - **Issue trackers:** Read issues, update status, create sub-tasks, add comments
  - **Browser automation:** E2E testing, visual review, screenshot comparison
- **Phase usage badges:** Deploy (git, CI/CD), Monitor (issue trackers, CI/CD), Review (browser automation), Plan (issue trackers -- read only)
- **Config example:**
```yaml
# tools/external-apis.yaml
external_apis:
  version_control:
    enabled: true
    provider: git               # tool-agnostic: just git
    operations:
      - branch_create
      - branch_switch
      - commit
      - push
      - pull_request_create
      - pull_request_update
    protected_branches:
      - main
      - production
  ci_cd:
    enabled: true
    operations:
      - trigger_pipeline
      - check_status
      - read_logs
    auto_trigger: false          # require explicit invocation
  issue_tracker:
    enabled: true
    operations:
      - read_issue
      - update_status
      - add_comment
      - create_subtask
  browser:
    enabled: false               # enable for visual review
    operations:
      - navigate
      - screenshot
      - visual_diff
```

**Card 4: Context Providers** (icon: database/brain, color: plan)
- **Sub-capabilities:**
  - **Codebase indexing:** AST parsing, dependency graphs, symbol tables, call graphs
  - **Documentation loaders:** Read relevant docs on demand, API references, README files
  - **Dependency analyzers:** Package relationships, version compatibility, vulnerability databases
- **Phase usage badges:** Plan (heavily), Build (moderate), Review (moderate), Monitor (light)
- **Why context management matters** paragraph: Agents with too much context perform worse. Context providers are not "dump everything" -- they are intelligent retrievers that surface only relevant information. A Plan agent analyzing a bug in the auth module does not need the entire codebase. It needs the auth module, its tests, its dependencies, and the relevant issue history.
- **Config example:**
```yaml
# tools/context-providers.yaml
context_providers:
  codebase_index:
    enabled: true
    index_type: ast                # ast | text | hybrid
    languages:
      - typescript
      - python
    max_context_tokens: 8000       # per-request limit
    relevance_threshold: 0.7
  documentation:
    enabled: true
    sources:
      - path: "docs/**/*.md"
      - path: "README.md"
      - path: "ARCHITECTURE.md"
    max_docs_per_request: 5
  dependency_analyzer:
    enabled: true
    manifest_files:
      - "package.json"
      - "tsconfig.json"
```

#### Section 4: Permission Matrix
- **Heading:** `## Permission Matrix: Tools by Phase`
- **UI Component:** Full-width table with phase names as columns and tool sub-capabilities as rows. Cells contain green checkmark (allowed) or red X (denied). Uses the `perm-allowed` / `perm-denied` badge CSS classes from the landing page.

| Tool | Plan | Build | Test | Review | Document | Deploy | Monitor |
|------|------|-------|------|--------|----------|--------|---------|
| file.read | yes | yes | yes | yes | yes | yes | yes |
| file.write | no | yes | yes | no | yes | no | no |
| file.search | yes | yes | yes | yes | yes | yes | yes |
| exec.shell | no | yes | yes | no | no | yes | yes |
| exec.test | no | yes | yes | no | no | no | no |
| exec.lint | no | yes | no | no | no | no | no |
| exec.build | no | yes | no | no | no | yes | no |
| api.git | no | no | no | no | no | yes | no |
| api.ci | no | no | no | no | no | yes | yes |
| api.issues | yes | no | no | no | no | no | yes |
| api.browser | no | no | no | yes | no | no | no |
| ctx.index | yes | yes | yes | yes | no | no | no |
| ctx.docs | yes | yes | no | yes | yes | no | no |
| ctx.deps | yes | yes | no | yes | no | no | yes |

- Below the table, a paragraph: "This is the default matrix. Override per-project in your pipeline.yaml. The principle is least privilege: each phase gets only what it needs. Planners cannot execute code. Reviewers cannot write files. This is not a limitation -- it is a safety pattern."

#### Section 5: Adding a New Tool Integration
- **Heading:** `## Adding a New Tool Integration`
- **UI Component:** Three-step process with numbered cards

1. **Define the config file** -- Create a YAML file in `agentic-layer/tools/` describing the tool's capabilities, allowed operations, and security boundaries.
2. **Declare permissions per phase** -- In `pipeline.yaml`, specify which phases can access the new tool. Default to denied; explicitly grant.
3. **Reference in templates** -- Update the relevant prompt templates to inform the agent about the new capability. An agent cannot use a tool it does not know exists.

```yaml
# pipeline.yaml — adding a custom tool
tools:
  file_system: tools/file-system.yaml
  code_execution: tools/code-execution.yaml
  external_apis: tools/external-apis.yaml
  context_providers: tools/context-providers.yaml
  custom_analytics: tools/analytics.yaml    # ← your new tool

phase_tools:
  plan: [file_system.read, file_system.search, context_providers, custom_analytics.read]
  build: [file_system, code_execution, context_providers]
  # ... etc
```

### UI Components Summary
- Callout boxes (2)
- Expandable category cards with config code blocks (4)
- Full-width permission matrix table (1)
- Three-step numbered process cards (1)
- YAML code blocks (6 total)

### Interactive Elements
- **Expandable category cards:** Click to expand/collapse the sub-capabilities and config example
- **Permission matrix:** Hoverable rows highlight the entire row; hoverable column headers highlight the entire column
- **Tab or toggle for config examples:** If showing multiple project types (Node, Python, Go), use tabs within each category card

### Cross-Links
- Concepts > Tool Permission Design: link from the permission matrix section
- Agentic Layer > Pipeline Config: link from the "Override per-project in your pipeline.yaml" paragraph
- Agentic Layer > Quality Gates: link from the security callout (gates enforce that tool boundaries are respected)
- Pipeline > each phase: link phase names in the permission matrix to phase pages
- Agentic Layer > Commands & Skills: link from "skills use these tools internally"

### Content Writer Notes
- This page is reference material. Readers will come back to it repeatedly. Optimize for scannability.
- The permission matrix is the centerpiece. Make it visually clear and easy to read.
- Security callout for code execution is critical. Do not bury it.
- Config examples must be realistic but simple. Show Node.js/TypeScript as the default; note that the pattern transfers to any stack.
- Emphasize tool-agnostic throughout. "git" is fine (it is a standard). "GitHub CLI" is an implementation detail -- say "version control API" instead.
- Context providers section should stress the "less is more" principle. This is counterintuitive to most readers.

---

## Page 4: `/agentic-layer/quality-gates`

### Page URL and Title
- **URL:** `/agentic-layer/quality-gates`
- **Title:** Quality Gates

### Purpose
Explain what quality gates are, why they are the mechanism that enables autonomy, and how to write custom gates. Show complete examples for each phase.

### Content Outline

#### Section 1: Hero
- **Label:** THE AGENTIC LAYER
- **Heading:** Quality Gates
- **Subtitle:** "Pass/fail criteria that must be satisfied before a phase completes. Better gates mean higher autonomy. Gates are the reason you can trust the pipeline."

#### Section 2: What Are Quality Gates
- **Heading:** `## What Are Quality Gates`
- Paragraph: A quality gate is a set of pass/fail criteria evaluated after a pipeline phase completes. If the gate passes, the pipeline moves to the next phase. If it fails, the gate triggers an action: retry the phase, patch and re-run, or escalate to a human. Gates are what make autonomous pipelines trustworthy.
- **Callout box** (glow border): "Quality gates are the most important factor in determining your autonomy level. Weak gates force you to stay at Level 1-2 (human reviews everything). Strong, comprehensive gates let you graduate to Level 3-4 (autonomous / ASE). Invest in your gates."

#### Section 3: Gate Anatomy
- **Heading:** `## Anatomy of a Quality Gate`
- **UI Component:** Four horizontal cards in a row (responsive: 2x2 on tablet, stacked on mobile)

| Component | Description |
|-----------|-------------|
| **Trigger** | Which phase this gate runs after. E.g., `after-test`, `after-review`, `after-document`. |
| **Criteria** | What conditions must be met. A list of key-value assertions against phase output. |
| **Action on Fail** | What happens when criteria are not met: `retry` (loop), `patch` (fix and re-run), `escalate` (human). |
| **Severity** | `blocker` (must pass to proceed) or `warning` (log and continue). |

- Followed by a single annotated gate example:
```yaml
gate: test-coverage
version: 1
trigger: after-test
severity: blocker

criteria:
  all_tests_pass: true
  coverage_minimum: 80
  no_skipped_tests: true
  no_snapshot_regressions: true

on_fail: retry
max_retries: 3

escalation:
  after_retries_exhausted: human
  context:
    - test_results
    - build_report
    - failure_history
```

Annotation badges:
- `Trigger Binding` (test color)
- `Criteria Assertions` (glow color)
- `Retry Logic` (warning color)
- `Escalation Path` (fail color)

#### Section 4: Example Gates Per Phase
- **Heading:** `## Gate Examples by Phase`
- **UI Component:** Tabbed interface with 5 tabs, one per phase that typically has a gate

**Tab: After Test**
```yaml
# gates/test-coverage.yaml
gate: test-coverage
version: 1
trigger: after-test
severity: blocker

criteria:
  all_tests_pass: true
  coverage_minimum: 80             # percentage
  no_skipped_tests: true
  max_test_duration_ms: 300000     # 5 minutes
  no_snapshot_regressions: true

on_fail: retry
max_retries: 3
retry_strategy: rebuild            # triggers build agent to fix failures

escalation:
  after_retries_exhausted: human
  message: "Tests failed after {retries} attempts. Manual review needed."
  context:
    - test_results
    - build_report
    - failure_history
```

**Tab: After Review**
```yaml
# gates/review-severity.yaml
gate: review-severity
version: 1
trigger: after-review
severity: blocker

criteria:
  no_blockers: true                # zero blocker-severity issues
  tech_debt_max: 5                 # max 5 tech-debt items allowed
  security_issues: 0               # zero tolerance for security findings
  plan_adherence: true             # implementation matches the plan

on_fail: patch
max_retries: 3
retry_strategy: rebuild_and_retest  # fix issues, re-test, then re-review

escalation:
  after_retries_exhausted: human
  message: "Review found {blocker_count} blockers after {retries} patch cycles."
  context:
    - review_results
    - build_report
    - test_results
    - original_plan
```

**Tab: After Document**
```yaml
# gates/doc-completeness.yaml
gate: doc-completeness
version: 1
trigger: after-document
severity: blocker

criteria:
  has_changelog_entry: true
  all_public_apis_documented: true
  no_broken_links: true
  readme_updated_if_needed: true

on_fail: retry
max_retries: 2
retry_strategy: redocument          # re-run document phase

escalation:
  after_retries_exhausted: human
  message: "Documentation incomplete after {retries} attempts."
  context:
    - doc_artifact
    - build_report
```

**Tab: After Build (Warning Gate)**
```yaml
# gates/build-lint.yaml
gate: build-lint
version: 1
trigger: after-build
severity: warning                   # does NOT block pipeline

criteria:
  lint_errors: 0
  lint_warnings_max: 10
  type_check_pass: true

on_fail: log                        # log warning, continue to Test phase
notify: true                        # include in final PR summary
```

**Tab: After Deploy**
```yaml
# gates/deploy-readiness.yaml
gate: deploy-readiness
version: 1
trigger: after-deploy
severity: blocker

criteria:
  pr_created: true
  all_commits_signed: true
  branch_up_to_date: true
  no_merge_conflicts: true
  ci_pipeline_pass: true

on_fail: retry
max_retries: 2
retry_strategy: resolve_conflicts

escalation:
  after_retries_exhausted: human
  message: "Deploy preparation failed. Merge conflicts or CI failure."
  context:
    - deploy_report
    - ci_logs
```

#### Section 5: Custom Gates
- **Heading:** `## Writing Custom Gates`
- **Subsection: The Criteria Format**
  - Criteria are key-value assertions. Keys reference fields in the phase's output artifact. Values are the expected state.
  - Supported assertion types:

| Type | Example | Meaning |
|------|---------|---------|
| Boolean | `all_tests_pass: true` | Field must be exactly true |
| Numeric minimum | `coverage_minimum: 80` | Field must be >= 80 |
| Numeric maximum | `tech_debt_max: 5` | Field must be <= 5 |
| Numeric exact | `security_issues: 0` | Field must be exactly 0 |
| String match | `verdict: "PASS"` | Field must match string |
| Exists | `has_changelog_entry: true` | Field must exist and be truthy |

- **Subsection: Combining Criteria (AND/OR)**
```yaml
# Default: all criteria are AND (all must pass)
criteria:
  all_tests_pass: true
  coverage_minimum: 80

# Explicit OR: use any_of
criteria:
  any_of:
    - coverage_minimum: 80
    - coverage_minimum: 60
      has_integration_tests: true    # 60% OK if integration tests exist

# Nested: AND groups within OR
criteria:
  any_of:
    - all_of:
        - coverage_minimum: 80
        - no_skipped_tests: true
    - all_of:
        - coverage_minimum: 90       # higher coverage forgives skipped tests
```

- **Subsection: Referencing Phase Output**
  - Gate criteria reference the structured output produced by the phase. This is why the Output Format section in prompt templates matters -- gates parse it.
  - Example: If the test phase's `run-tests` skill outputs `{ "total_failed": 1, "coverage": { "lines": 84.2 } }`, then:
    - `all_tests_pass: true` checks `total_failed == 0`
    - `coverage_minimum: 80` checks `coverage.lines >= 80`

#### Section 6: Gates Determine Autonomy
- **Heading:** `## Gate Quality Determines Autonomy Level`
- **UI Component:** A visual diagram showing the relationship. Use the stepper pattern from the landing page maturity section but horizontal, with gate quality on the X axis and autonomy level on the Y axis.

| Gate Quality | Autonomy Level | What It Looks Like |
|-------------|----------------|-------------------|
| No gates | Level 1 -- Assisted | Human must review every output manually |
| Basic gates (tests pass) | Level 2 -- Supervised | Human approves between phases, gates catch obvious failures |
| Strong gates (coverage, security, lint, plan adherence) | Level 3 -- Autonomous | Pipeline runs end-to-end, human reviews final PR only |
| Comprehensive gates + monitoring | Level 4 -- ASE | Pipeline runs, gates pass, auto-merge. Zero touch. |

- Paragraph: "The path from Level 1 to Level 4 is a path of gate maturity. You do not need to trust AI more. You need to build better gates."

#### Section 7: Anti-Patterns
- **Heading:** `## Gate Anti-Patterns`
- **UI Component:** Three cards with warning-colored left border

**Card 1: Gates That Always Pass**
- Title: The Rubber Stamp
- Description: A gate with criteria so loose it never fails. `coverage_minimum: 0`, `tech_debt_max: 999`. This gate adds pipeline overhead without adding safety. Remove it or tighten it.
- Fix: Set criteria based on your team's actual quality bar. Start conservative, relax only with data.

**Card 2: Gates That Are Too Strict**
- Title: The Perfectionist
- Description: A gate that rarely passes. `coverage_minimum: 100`, `lint_warnings_max: 0`. The pipeline exhausts retries and escalates every run. Developers lose trust in the system.
- Fix: Use `severity: warning` for aspirational criteria. Reserve `severity: blocker` for true blockers.

**Card 3: Gates Without Retry Logic**
- Title: The Glass Cannon
- Description: A gate with `max_retries: 0` or no retry strategy. A single flaky test stops the entire pipeline. No self-healing, no recovery.
- Fix: Always include retry logic. Even 1 retry catches most transient failures. Use `max_retries: 3` as a default.

### UI Components Summary
- Callout box (1)
- Four horizontal anatomy cards (1 set)
- Annotated YAML code block (1)
- Tabbed interface with 5 tabs (1)
- Criteria assertion type table (1)
- YAML code blocks for AND/OR logic (1)
- Autonomy-gate relationship table (1)
- Three anti-pattern warning cards (1 set)

### Interactive Elements
- **Tabbed gate gallery:** Switch between After Test / After Review / After Document / After Build / After Deploy
- **Expandable AND/OR criteria examples:** Collapsed by default, expand to show nested logic

### Cross-Links
- Concepts > Self-Healing Loops: link from retry logic and feedback loop discussion
- Concepts > Autonomous Software Engineering: link from the autonomy level section
- Agentic Layer > Prompt Templates: link from "Output Format section matters because gates parse it"
- Agentic Layer > Pipeline Config: link from gate file references in pipeline.yaml
- Agentic Layer > Commands & Skills: link from run-tests skill output being parsed by gates
- Pipeline > Test, Review, Document phases: link from example gates

### Content Writer Notes
- The "gates determine autonomy" section is the key strategic insight. Readers should leave understanding that gate quality is the bottleneck to autonomy, not AI capability.
- Anti-patterns section should be memorable. Use vivid names (Rubber Stamp, Perfectionist, Glass Cannon).
- All YAML examples must be syntactically valid and internally consistent. A reader should be able to copy them into a file and have them parse correctly.
- The AND/OR criteria section is the most technically dense. Use concrete examples, not abstract descriptions.

---

## Page 5: `/agentic-layer/pipeline-config`

### Page URL and Title
- **URL:** `/agentic-layer/pipeline-config`
- **Title:** Pipeline Configuration

### Purpose
Show the central orchestration config file (pipeline.yaml), explain every configuration option, and provide side-by-side minimal vs enterprise configs. This is the "glue" page that ties all other agentic layer artifacts together.

### Content Outline

#### Section 1: Hero
- **Label:** THE AGENTIC LAYER
- **Heading:** Pipeline Configuration
- **Subtitle:** "One file orchestrates the entire pipeline. Phase ordering, loop limits, gate bindings, tool permissions, template routing. This is the control plane."

#### Section 2: The Central Config
- **Heading:** `## pipeline.yaml -- The Control Plane`
- Paragraph: The pipeline.yaml file is the central orchestration config for your agentic layer. It defines which phases run, in what order, how many retries each loop gets, what happens on failure, and which gates and templates apply. Every other artifact in the agentic layer is referenced from here.

#### Section 3: Minimal vs Full Config
- **Heading:** `## Minimum Viable vs Full Enterprise`
- **UI Component:** Side-by-side code blocks (two-column on desktop, stacked on mobile). Left is "Minimal" with a green badge, right is "Enterprise" with a glow badge.

**Left: Minimum Viable Config**
```yaml
# pipeline.yaml — minimum viable config
# Enough to run the pipeline with defaults

version: 1

phases:
  - plan
  - build
  - test
  - review
  - deploy

# Everything else uses framework defaults:
# - Loop limits: 3
# - Escalation: human
# - Gates: built-in
# - Templates: prompts/{phase}.md
```

**Right: Full Enterprise Config**
```yaml
# pipeline.yaml — full enterprise config

version: 1

# ── Phase Ordering ──────────────────────────
phases:
  - plan
  - build
  - test
  - review
  - document
  - deploy
  - monitor

# ── Template Routing ────────────────────────
templates:
  plan:
    feature: prompts/plan-feature.md
    bug: prompts/plan-bug.md
    task: prompts/plan-task.md
    patch: prompts/plan-patch.md
    default: prompts/plan.md
  build: prompts/build.md
  test: prompts/test.md
  review: prompts/review.md
  document: prompts/document.md
  deploy: prompts/deploy.md
  monitor: prompts/monitor.md

# ── Feedback Loops ──────────────────────────
loops:
  test_retry:
    max: 3
    trigger: test.fail
    action: rebuild
    cooldown_ms: 5000               # wait between retries
  review_patch:
    max: 3
    trigger: review.blockers
    action: rebuild_and_retest
    cooldown_ms: 5000
  full_rebuild:
    max: 1
    trigger: review.architectural
    action: replan_and_rebuild

# ── Escalation ──────────────────────────────
escalation:
  handler: human
  timeout_hours: 24                  # auto-close if no response
  notification:
    channel: engineering             # your notification channel
  context:
    - plan
    - build_report
    - test_results
    - review_issues
    - failure_history

# ── Quality Gates ───────────────────────────
gates:
  after_build: gates/build-lint.yaml
  after_test: gates/test-coverage.yaml
  after_review: gates/review-severity.yaml
  after_document: gates/doc-completeness.yaml
  after_deploy: gates/deploy-readiness.yaml

# ── Tool Permissions ────────────────────────
tools:
  configs:
    file_system: tools/file-system.yaml
    code_execution: tools/code-execution.yaml
    external_apis: tools/external-apis.yaml
    context_providers: tools/context-providers.yaml

  phase_overrides:
    plan:
      code_execution: disabled       # planners cannot execute
      file_system.write: disabled    # planners cannot write
    review:
      code_execution: disabled       # reviewers cannot execute
      file_system.write: disabled    # reviewers cannot write

# ── Parallel Execution ──────────────────────
parallel:
  - [document, deploy_prepare]       # doc can start while deploy prepares

# ── Monitoring ──────────────────────────────
monitoring:
  track:
    - pipeline_success_rate
    - average_iterations_per_loop
    - phase_duration_ms
    - cost_per_run
    - escalation_rate
  alert_on:
    escalation_rate_above: 0.3       # alert if >30% of runs escalate
    avg_iterations_above: 2.5        # alert if loops averaging >2.5 retries
```

#### Section 4: Configuration Options (Detailed)
- **Heading:** `## Configuration Reference`
- **UI Component:** Expandable accordion sections, one per config category

**Accordion 1: Phase Ordering**
- Description: Define which phases run and in what order. You can skip phases or reorder them.
- Default: plan, build, test, review, document, deploy, monitor
- Example: Skipping document phase for quick patches:
```yaml
phases:
  - plan
  - build
  - test
  - review
  - deploy    # skip document for speed
```

**Accordion 2: Loop Limits**
- Description: Maximum retries per feedback loop. When exhausted, triggers escalation.
- Default: 3 for all loops
- Risk guidance: Too few (1) = every transient failure escalates. Too many (10) = pipeline burns time and cost on unfixable issues.
```yaml
loops:
  test_retry:
    max: 3
  review_patch:
    max: 3
  full_rebuild:
    max: 1     # full rebuilds are expensive — keep low
```

**Accordion 3: Escalation Rules**
- Description: What happens when loops exhaust. Who gets notified, what context they receive, how long before auto-close.
```yaml
escalation:
  handler: human                     # human | auto_close | fallback_pipeline
  timeout_hours: 24
  notification:
    channel: engineering
    mention: "@oncall"
  context:
    - plan
    - build_report
    - test_results
    - review_issues
    - failure_history
```

**Accordion 4: Parallel Execution**
- Description: Phases that can run concurrently. By default all phases run sequentially. Parallel groups execute simultaneously.
```yaml
parallel:
  - [document, deploy_prepare]       # these two can run at the same time
```
- Note: Only phases without data dependencies can run in parallel. Document needs review results, so it can start once review passes. Deploy preparation (branch cleanup, conflict check) has no dependency on document.

**Accordion 5: Gate Configuration**
- Description: Map gate files to phase triggers. Can reference gate files or inline criteria.
```yaml
gates:
  after_test: gates/test-coverage.yaml
  after_review: gates/review-severity.yaml
  after_document:
    inline:                          # inline gate definition
      criteria:
        has_changelog_entry: true
      on_fail: retry
      max_retries: 1
```

**Accordion 6: Tool Permissions Per Phase**
- Description: Override the default tool permission matrix for specific projects.
```yaml
tools:
  phase_overrides:
    review:
      external_apis.browser: enabled  # enable visual review for this project
    build:
      external_apis.git: disabled     # builds should not touch git directly
```

**Accordion 7: Template Overrides**
- Description: Use custom templates instead of defaults. Supports issue-type routing.
```yaml
templates:
  plan:
    feature: prompts/plan-feature.md
    bug: prompts/plan-bug.md
    default: prompts/plan.md
  build: prompts/custom-build.md     # project-specific build template
```

#### Section 5: The Directory Structure (Expanded)
- **Heading:** `## The Complete Directory Structure`
- **UI Component:** Full directory tree in a code block, with color-coded categories

```
agentic-layer/
├── prompts/                          # Prompt templates
│   ├── plan.md                       # Default plan template
│   ├── plan-feature.md               # Issue-type routing variants
│   ├── plan-bug.md
│   ├── plan-task.md
│   ├── plan-patch.md
│   ├── build.md
│   ├── test.md
│   ├── review.md
│   ├── document.md
│   ├── deploy.md
│   └── monitor.md
├── gates/                            # Quality gate definitions
│   ├── test-coverage.yaml
│   ├── review-severity.yaml
│   ├── doc-completeness.yaml
│   ├── build-lint.yaml
│   └── deploy-readiness.yaml
├── tools/                            # Tool integration configs
│   ├── file-system.yaml
│   ├── code-execution.yaml
│   ├── external-apis.yaml
│   └── context-providers.yaml
├── commands/                         # Human-invoked commands
│   ├── commit.md
│   ├── security-audit.md
│   └── explain.md
├── skills/                           # Agent-invoked skills
│   ├── run-tests.md
│   ├── lint-check.md
│   └── dependency-check.md
└── pipeline.yaml                     # Central orchestration config
```

- Below the tree, a summary table:

| Directory | Contents | Count (typical) |
|-----------|----------|-----------------|
| `prompts/` | One markdown file per phase, plus routing variants | 7-15 files |
| `gates/` | One YAML file per quality gate | 3-5 files |
| `tools/` | One YAML file per tool category | 4 files |
| `commands/` | One markdown file per custom command | 3-10 files |
| `skills/` | One markdown file per reusable skill | 3-10 files |
| Root | pipeline.yaml | 1 file |

#### Section 6: Configuration by Team Size
- **Heading:** `## Configuration by Team Size`
- **UI Component:** Three-column comparison (cards on mobile)

**Column 1: Solo Developer**
- Phase config: Skip document, lightweight gates
- Loop limits: 2 (save time/cost)
- Gates: test-coverage only
- Templates: defaults, no routing
- Tools: minimal config
- Total files: ~10
```yaml
# Solo: fast and lean
phases: [plan, build, test, review, deploy]
loops:
  test_retry: { max: 2 }
  review_patch: { max: 2 }
gates:
  after_test: gates/test-coverage.yaml
```

**Column 2: Small Team (3-8 engineers)**
- Phase config: Full pipeline with document
- Loop limits: 3 (standard)
- Gates: test-coverage + review-severity + doc-completeness
- Templates: defaults + 2-3 issue-type variants
- Tools: standard config with security boundaries
- Total files: ~20
```yaml
# Small team: balanced
phases: [plan, build, test, review, document, deploy]
loops:
  test_retry: { max: 3 }
  review_patch: { max: 3 }
gates:
  after_test: gates/test-coverage.yaml
  after_review: gates/review-severity.yaml
  after_document: gates/doc-completeness.yaml
templates:
  plan:
    feature: prompts/plan-feature.md
    bug: prompts/plan-bug.md
    default: prompts/plan.md
```

**Column 3: Enterprise (20+ engineers)**
- Phase config: Full pipeline + monitor + parallel execution
- Loop limits: 3 with strict escalation
- Gates: all 5 gates, strict criteria, audit logging
- Templates: full issue-type routing, per-team overrides
- Tools: strict security, branch protection, PR approval workflows
- Total files: ~40
```yaml
# Enterprise: comprehensive
phases: [plan, build, test, review, document, deploy, monitor]
loops:
  test_retry: { max: 3, cooldown_ms: 5000 }
  review_patch: { max: 3, cooldown_ms: 5000 }
  full_rebuild: { max: 1 }
gates:
  after_build: gates/build-lint.yaml
  after_test: gates/test-coverage.yaml
  after_review: gates/review-severity.yaml
  after_document: gates/doc-completeness.yaml
  after_deploy: gates/deploy-readiness.yaml
escalation:
  handler: human
  timeout_hours: 24
  notification:
    channel: engineering
    mention: "@oncall"
parallel:
  - [document, deploy_prepare]
monitoring:
  track: [pipeline_success_rate, escalation_rate, cost_per_run]
  alert_on:
    escalation_rate_above: 0.3
```

### UI Components Summary
- Side-by-side code blocks (1 -- minimal vs enterprise)
- Expandable accordion sections (7)
- YAML code blocks (12+ total)
- Full directory tree with color coding (1)
- Summary table (1)
- Three-column comparison cards with embedded code (1)

### Interactive Elements
- **Side-by-side comparison:** Toggle or slider to switch between minimal and enterprise configs
- **Accordion config reference:** Expand/collapse each config category independently
- **Team size toggle:** Three buttons (Solo / Small Team / Enterprise) that switch the displayed config

### Cross-Links
- Agentic Layer > Prompt Templates: link from template routing config
- Agentic Layer > Quality Gates: link from gate binding config
- Agentic Layer > Tool Integrations: link from tool permission overrides
- Agentic Layer > Commands & Skills: link from directory structure (commands/ and skills/)
- Pipeline > all phases: link phase names in phase ordering config
- Concepts > Self-Healing Loops: link from loop limits config
- Adopt > Maturity Path: link from team size section (solo = L2, enterprise = L3-L4)

### Content Writer Notes
- This is the "glue" page. It references every other page in the section. Make sure cross-links are plentiful and accurate.
- The side-by-side minimal vs enterprise comparison is the most impactful visual on the page. The contrast should be stark: 8 lines vs 80 lines, both valid.
- The directory structure must exactly match what appears on the landing page and across all other pages. Any inconsistency will confuse readers.
- Accordion reference section is for return visitors. First-time readers will scan the side-by-side and team-size comparisons.
- All YAML must be syntactically valid. All file paths referenced in config must match the directory structure shown.
- Team size section should feel aspirational: "Here is where you start. Here is where you grow."

---

## Navigation & Information Architecture

### Section Sidebar (all 5 pages)
```
THE AGENTIC LAYER
├── Prompt Templates        ← /agentic-layer/prompt-templates
├── Commands & Skills       ← /agentic-layer/commands-skills
├── Tool Integrations       ← /agentic-layer/tool-integrations
├── Quality Gates           ← /agentic-layer/quality-gates
└── Pipeline Configuration  ← /agentic-layer/pipeline-config
```

Active page highlighted with glow-colored left border and glow text color.

### Breadcrumbs
Each page shows: `AEF > Agentic Layer > Page Name`

### Next/Previous Navigation
Bottom of each page, two buttons:
- Previous page (left arrow + name)
- Next page (right arrow + name)

Following the order: Prompt Templates -> Commands & Skills -> Tool Integrations -> Quality Gates -> Pipeline Config

### Landing Page Integration
The five cards in the "What You Actually Build" section on the landing page should link to these five pages respectively.

---

### Critical Files for Implementation
- `/Users/alejtr/Documents/obsidian/obsidian/agentic-layer-framework/website/index.html` - Design system reference: all Tailwind config, CSS classes, component patterns, and tone
- `/Users/alejtr/Documents/obsidian/obsidian/agentic-layer-framework/framework/Framework Overview.md` - Core concepts and architecture that all 5 pages reference
- `/Users/alejtr/Documents/obsidian/obsidian/agentic-layer-framework/pipeline/Pipeline Architecture.md` - Pipeline phases, feedback loops, and directory structure that pages must stay consistent with
- `/Users/alejtr/Documents/obsidian/obsidian/agentic-layer-framework/framework/Glossary.md` - Term definitions that must be used consistently across all page contentagentId: a8fe1f7e7f9525efb (for resuming to continue this agent's work if needed)
<usage>total_tokens: 69911
tool_uses: 9
duration_ms: 403828</usage>