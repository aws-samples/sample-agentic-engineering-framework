---
description: <One-line description of what this prompt does. State that it conducts codebase research via parallel sub-agents and synthesizes their findings into a written research document.>
model: <Model selector — a specific model name (e.g., opus) or "inherit".>
---

# Research Codebase

<Opening task framing (1–2 sentences). Declare that the operator is conducting comprehensive research across the codebase to answer user questions by spawning parallel sub-agents and synthesizing their findings into a single document.>

## CRITICAL: YOUR ONLY JOB IS TO DOCUMENT AND EXPLAIN THE CODEBASE AS IT EXISTS TODAY
<List the hard scope boundaries as bullets. Use "DO NOT <overreach>" for behaviors the model is likely to slip into (suggesting improvements, performing root-cause analysis, proposing future enhancements, critiquing implementation, recommending refactors/optimization/architectural changes). Close with one "ONLY describe what exists, where it exists, how it works, and how components interact" bullet, plus a framing sentence reminding the operator they are building a technical map of the existing system. Aim for 6–8 bullets, one imperative sentence each.>

- <DO NOT directive>
- <DO NOT directive>
- <DO NOT directive>
- <ONLY <core permitted behavior> directive>
- <Framing sentence about creating a technical map/documentation of the existing system>

## Initial Setup:

<Short paragraph (2–3 sentences) telling the operator that the research query is provided directly in this turn and that no handshake is needed. Instruct the operator to proceed straight to the steps below and to suppress any canned "ready to research" greeting, noting that such a greeting belongs to interactive mode only.>

## Steps to follow after receiving the research query:

<Numbered list of 8 steps. Each step has a bolded title followed by a short imperative body (bullets or sub-bullets) describing what the operator does at that step. The sequence should move from context gathering → decomposition → parallel sub-agent spawning → waiting/synthesis → document generation → document structure → presentation → follow-up handling. Preserve the numbering and the exact step-title wording shown below.>

1. **Context Gathering:**
   - <Instruction to read user-mentioned files fully before doing anything else>
   - **IMPORTANT**: <Instruction about how to read files with the Read tool (no limit/offset parameters) so the whole file is ingested>
   - **CRITICAL**: <Instruction to do this reading in the main context BEFORE spawning any sub-tasks>
   - <Instruction to read the project-level orientation file, e.g., README>
   - <Instruction to read the implementation-docs index to discover supplementary documentation relevant to the topic>
   - <Closing rationale sentence explaining that this ensures full context before decomposition>

2. **Analyze and decompose the research question:**
   - <Bullet on breaking the query into composable research areas>
   - <Bullet nudging deep reasoning ("ultrathink") about underlying patterns, connections, and architectural implications>
   - <Bullet on identifying specific components, patterns, or concepts to investigate>
   - <Bullet on creating a research plan with TodoWrite to track subtasks>
   - <Bullet on considering which directories, files, or architectural patterns are relevant>

3. **Spawn parallel sub-agent tasks for comprehensive research:**
   - <Bullet on creating multiple Task agents to research different aspects concurrently>
   - <Bullet noting that specialized agents exist for specific research tasks>

   **For codebase research:**
   - Use the **<locator-agent-name>** agent to <describe its scope — finding WHERE files and components live>
   - Use the **<analyzer-agent-name>** agent to <describe its scope — understanding HOW specific code works, without critiquing it>
   - Use the **<pattern-finder-agent-name>** agent to <describe its scope — finding examples of existing patterns with concrete code snippets, without evaluating them>

   **IMPORTANT**: <Sentence reminding the operator that all agents are documentarians, not critics — they describe what exists without suggesting improvements or identifying issues.>

   **For web research (only if user explicitly asks):**
   - Use the **<web-research-agent-name>** agent for <external documentation and resources>
   - <Instruction that IF web-research agents are used, they must return LINKS, and those links MUST be included in the final report>

   <Short paragraph introducing the "use these agents intelligently" guidance, followed by 5–7 bullets covering: start with locators, then analyzers on promising findings, run agents in parallel for different questions, trust that each agent knows its job, avoid writing detailed HOW-to-search prompts, and remind agents they are documenting rather than evaluating.>
   - <Intelligent-use guideline>
   - <Intelligent-use guideline>
   - <Intelligent-use guideline>
   - <Intelligent-use guideline>

4. **Wait for all sub-agents to complete and synthesize findings:**
   - IMPORTANT: <Instruction to wait for ALL sub-agent tasks to complete before proceeding>
   - <Bullet on compiling all sub-agent results>
   - <Bullet on cross-referencing findings with documentation identified via the implementation-docs index>
   - <Bullet on connecting findings across different components>
   - <Bullet on including specific file paths and line numbers for reference>
   - <Bullet on highlighting patterns, connections, and architectural decisions>
   - <Bullet on answering the user's specific questions with concrete evidence>

5. **Generate research document:**
   - Filename: `<research-output-directory>/<YYYY-MM-DD-description>.md`
     - Format: `<YYYY-MM-DD-description>.md` where:
       - <Describe the date slot, e.g., YYYY-MM-DD is today's date>
       - <Describe the description slot, e.g., a brief kebab-case description of the research topic>
     - Examples:
       - `<example-date>-<example-topic-1>.md`
       - `<example-date>-<example-topic-2>.md`

6. **Structure the document:**
   <Short lead-in sentence noting that the research document must follow the exact skeleton below. Describe the skeleton's intent: a top-line metadata block, the original research question, a high-level summary, detailed findings grouped by component or area, a flat list of code references, an architecture documentation section, related documentation, related research links, and open questions.>
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
   <Relevant documentation identified via the implementation-docs index>
   - `<path/to/relevant-doc.md>` - <Context about topic X>
   - `<path/to/another-doc.md>` - <Context about topic Y>

   ## Related Research
   <Links to other research documents in the research directory>

   ## Open Questions
   <Any areas that need further investigation>
   ```

7. **Present findings:**
   - <Bullet on presenting a concise summary of findings to the user>
   - <Bullet on including key file references for easy navigation>
   - <Bullet on asking whether the user has follow-up questions or needs clarification>

8. **Handle follow-up questions:**
   - <Bullet on appending follow-ups to the same research document rather than creating a new one>
   - <Bullet on adding a new `## Follow-up Research <timestamp>` section>
   - <Bullet on spawning new sub-agents as needed for additional investigation>
   - <Bullet on continuing to update the document in place>

## Important notes:
<Bulleted list of cross-cutting directives the operator must hold throughout execution. Mix positive directives ("Always...") with scope reminders and critical-ordering rules. Preserve the bolded prefixes (**CRITICAL**, **REMEMBER**, **NO RECOMMENDATIONS**, **File reading**, **Critical ordering**) because callers and the model pattern-match on them. Include at minimum: parallel sub-agent usage for efficiency, always running fresh research rather than relying on stored documents, using the implementation-docs index to surface supplementary context, prioritizing concrete file:line references, keeping research documents self-contained, keeping sub-agent prompts specific and read-only, documenting cross-component connections, including temporal context, keeping the main agent focused on synthesis rather than deep file reading, and having sub-agents document examples and usage as they exist. Close with the bolded reinforcements and the ordering rules.>

- <Cross-cutting directive>
- <Cross-cutting directive>
- <Cross-cutting directive>
- <Cross-cutting directive>
- **CRITICAL**: <Scope-anchor reminder — you and all sub-agents are documentarians, not evaluators>
- **REMEMBER**: <Scope-anchor reminder — document what IS, not what SHOULD BE>
- **NO RECOMMENDATIONS**: <Scope-anchor reminder — only describe the current state of the codebase>
- **File reading**: <Directive to read mentioned files FULLY, with no limit/offset, before spawning sub-tasks>
- **Critical ordering**: <Lead-in to the numbered-step ordering rules>
  - <Ordering rule — read mentioned files before spawning sub-tasks (step 1)>
  - <Ordering rule — wait for all sub-agents to complete before synthesizing (step 4)>
  - <Ordering rule — never write the research document with placeholder values>
