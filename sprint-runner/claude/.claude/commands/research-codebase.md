---
description: <One-line description of what this prompt does. State that it researches and documents the codebase through parallel sub-agent analysis and synthesizes the findings into a single research document.>
model: <Model selector — typically a reasoning-capable model such as "opus" or "inherit".>
---

# Research Codebase

<Opening framing paragraph (1–2 sentences). State that the prompt conducts comprehensive research across the codebase to answer user questions by spawning parallel sub-agents and synthesizing their findings into a single research document.>

## CRITICAL: <State the documentarian-only rule — the sole job is to document and explain the codebase as it exists today.>

<Bulleted list of non-negotiable DO-NOTs that keep the prompt in documentarian mode rather than critic/improver mode. Cover: no improvement suggestions, no unsolicited root cause analysis, no future-enhancement proposals, no implementation critique, no refactoring/optimization/architecture recommendations, and a positive statement describing what the prompt DOES do.>

- <DO-NOT — suggest improvements or changes unless explicitly asked>
- <DO-NOT — perform root cause analysis unless explicitly asked>
- <DO-NOT — propose future enhancements unless explicitly asked>
- <DO-NOT — critique the implementation or identify problems>
- <DO-NOT — recommend refactoring, optimization, or architectural changes>
- <DO — describe what exists, where it exists, how it works, and how components interact>
- <DO — create a technical map / documentation of the existing system>

## Initial Setup:

<Short paragraph describing the intake contract. The research query is provided directly in this turn — no handshake is needed. Proceed straight to the steps below. Suppress any canned "ready to research" greeting; such greetings belong to interactive mode only.>

## Steps to follow after receiving the research query:

<Numbered list of the end-to-end research steps. Each step has a bolded title followed by sub-bullets describing concrete actions.>

1. **<Step title — e.g., context gathering>**:
   - <Sub-action — if the user mentions specific files (feature descriptions, docs, JSON), read them FULLY first>
   - <Anti-pattern reminder — use the Read tool without `limit`/`offset` to read entire files>
   - <Critical reminder — read these files yourself in the main context BEFORE spawning any sub-tasks>
   - <Project-entry-doc directive — read the entry doc (e.g., `README.md`) to understand project structure>
   - <ai-implementation-docs directive — read `.claude/commands/ai-implementation-docs.md` to check whether the research topic requires additional documentation>
   - <Rationale — ensures full context before decomposing the research>

2. **<Step title — e.g., analyze and decompose the research question>**:
   - <Sub-action — break the user's query into composable research areas>
   - <Sub-action — take time to ultrathink about underlying patterns, connections, and architectural implications>
   - <Sub-action — identify specific components, patterns, or concepts to investigate>
   - <Sub-action — create a research plan using a task tracker to track all subtasks>
   - <Sub-action — consider which directories, files, or architectural patterns are relevant>

3. **<Step title — e.g., spawn parallel sub-agent tasks for comprehensive research>**:
   - <Sub-action — create multiple Task agents to research different aspects concurrently>
   - <Sub-action — specialized agents exist for specific research tasks>

   **<Sub-section — for codebase research>**:
   - <Use the **codebase-locator** agent to find WHERE files and components live>
   - <Use the **codebase-analyzer** agent to understand HOW specific code works, without critiquing it>
   - <Use the **codebase-pattern-finder** agent to find examples of existing patterns with concrete code snippets, without evaluating them>

   <IMPORTANT reminder — all agents are documentarians, not critics; they describe what exists without suggesting improvements or identifying issues.>

   **<Sub-section — for web research (only if the user explicitly asks)>**:
   - <Use the **web-search-researcher** agent for external documentation and resources>
   - <Link-preservation directive — if web-research agents are used, they must return LINKS, and those links MUST be included in the final report>

   <Orchestration guidance bullets — how to use the agents intelligently: start with locators, then analyzers on promising findings, run agents in parallel for different questions, give specific goals rather than HOW-to-search prompts, remind agents they are documenting rather than evaluating.>

4. **<Step title — e.g., wait for all sub-agents to complete and synthesize findings>**:
   - <IMPORTANT reminder — wait for ALL sub-agent tasks to complete before proceeding>
   - <Sub-action — compile all sub-agent results>
   - <Sub-action — cross-reference findings with documentation identified via `.claude/commands/ai-implementation-docs.md`>
   - <Sub-action — connect findings across different components>
   - <Sub-action — include specific file paths and line numbers for reference>
   - <Sub-action — highlight patterns, connections, and architectural decisions>
   - <Sub-action — answer the user's specific questions with concrete evidence>

5. **<Step title — e.g., generate research document>**:
   - <Filename convention — `research/YYYY-MM-DD-<description>.md` where `YYYY-MM-DD` is today's date and `<description>` is a brief kebab-case topic descriptor>
   - <Examples — illustrative only; adapt to your project>

6. **<Step title — e.g., structure the document>**:
   <Preamble — the research document must follow the exact skeleton below. It provides a top-line metadata block, the original research question, a high-level summary, detailed findings grouped by component or area, a flat list of code references, an architecture documentation section, related documentation, related research links, and open questions.>

   ```markdown
   # Research: <User's question or topic>

   **Date**: <Current date and time with timezone>
   **Repository**: <Repository name if known>

   ## Research Question
   <Original user query, verbatim>

   ## Summary
   <High-level documentation of what was found, answering the user's question by describing what exists>

   ## Detailed Findings

   ### <Component or Area 1>
   - <Description of what exists, with inline file:line reference>
   - <How it connects to other components>
   - <Current implementation details, without evaluation>

   ### <Component or Area 2>
   ...

   ## Code References
   - `<path/to/file.ext>:<line>` - <Description of what's there>
   - `<path/to/another-file.ext>:<line-range>` - <Description of the code block>

   ## Architecture Documentation
   <Current patterns, conventions, and design implementations found in the codebase>

   ## Related Documentation
   <Relevant documentation identified via `.claude/commands/ai-implementation-docs.md`>
   - `<path/to/relevant-doc.md>` - <Context about topic X>
   - `<path/to/another-doc.md>` - <Context about topic Y>

   ## Related Research
   <Links to other research documents in the research directory>

   ## Open Questions
   <Any areas that need further investigation>
   ```

7. **<Step title — e.g., present findings>**:
   - <Sub-action — present a concise summary of findings to the user>
   - <Sub-action — include key file references for easy navigation>
   - <Sub-action — ask whether the user has follow-up questions or needs clarification>

8. **<Step title — e.g., handle follow-up questions>**:
   - <Sub-action — append follow-ups to the same research document rather than creating a new one>
   - <Sub-action — add a new `## Follow-up Research <timestamp>` section>
   - <Sub-action — spawn new sub-agents as needed for additional investigation>
   - <Sub-action — continue to update the document in place>

## Important notes:

<Bulleted list of cross-cutting rules reinforcing the behavior of the prompt. Cover: parallelism for efficiency, fresh research each run, use of the ai-implementation-docs index, concrete file:line references, self-contained research documents, read-only sub-agent focus, cross-component documentation, temporal context, main-agent-as-synthesizer discipline, documentarian re-affirmation, anti-drift rule (main agent doesn't call Read/Grep/Glob/Bash on source files — it spawns sub-agents), critical ordering of steps, and file-reading rules.>

- <Note — always use parallel Task agents to maximize efficiency and minimize context usage>
- <Note — always run fresh codebase research; never rely solely on existing research documents>
- <Note — use `.claude/commands/ai-implementation-docs.md` to identify relevant project documentation>
- <Note — focus on finding concrete file paths and line numbers for developer reference>
- <Note — research documents should be self-contained with all necessary context>
- <Note — each sub-agent prompt should be specific and focused on read-only documentation operations>
- <Note — document cross-component connections and how systems interact>
- <Note — include temporal context (when the research was conducted)>
- <Note — keep the main agent focused on synthesis, not deep file reading>
- <Note — have sub-agents document examples and usage patterns as they exist>
- <Anti-drift rule — if you find yourself about to call Read, Grep, Glob, or Bash on source files in the main context to answer the research question, STOP and spawn a sub-agent instead. The only files you read yourself are the ones named in step 1 (user-mentioned files, project entry doc, ai-implementation-docs.md). Everything else goes through sub-agents.>
- <CRITICAL — you and all sub-agents are documentarians, not evaluators>
- <REMEMBER — document what IS, not what SHOULD BE>
- <NO RECOMMENDATIONS — only describe the current state of the codebase>
- <File reading rule — always read mentioned files FULLY (no limit/offset) before spawning sub-tasks>
- <Critical ordering — always read mentioned files first (step 1) before spawning sub-tasks; always wait for all sub-agents to complete before synthesizing (step 4); NEVER write the research document with placeholder values>
