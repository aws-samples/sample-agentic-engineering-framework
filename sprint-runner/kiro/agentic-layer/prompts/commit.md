---
description: <One-line description of the prompt's purpose. Frame it in terms of what the agent will produce and the completeness guarantee (e.g., that every change in the working tree is accounted for).>
---

# /<command-name>

<Opening instruction (2–3 sentences). State what the agent is being asked to produce and the scope discipline that governs the task. Use a bolded imperative to anchor the non-negotiable behavior — for a commit prompt, that the agent must **account for every modified and untracked file**, not cherry-pick by relevance.>

## Variables

<List each `$ARGUMENT` slot the prompt consumes, one per line, in the form `<name>: $ARGUMENT`. For any argument that is optional or that should NOT drive decisions (e.g., a task description that might mislead the agent into filtering files), say so explicitly on the same line.>

<variable_name_1>: $ARGUMENT
<variable_name_2>: $ARGUMENT
<variable_name_3>: $ARGUMENT — <qualifier, e.g., OPTIONAL hint for X only. Do NOT use this to Y. The Z is the source of truth.>

## Process

<Short lead-in (1 sentence) telling the agent to work through the steps in order. Call out any step that the agent is likely to skip and forbid skipping it.>

### 1. <Orientation step name, e.g., "Observe">

<Describe what the agent inspects first. For a working-tree command, list the exact shell commands to run as a bullet list. Close with a sentence establishing the "universe" of items the agent is responsible for — the set that step 2 must fully cover.>

- `<command to run for observation>`
- `<command to run for observation>`
- `<command to run for observation>`

<Sentence defining the completeness invariant: every item surfaced here must appear in exactly one bucket in the next step — no silent omissions.>

### 2. <Enumeration / classification step name>

<Instruct the agent to print one line per item from step 1, tagged with an inclusion decision and a reason. Provide the exact line format inside a fenced block.>

```
<bucket_a>: <item>  — <why it belongs>
<bucket_b>: <item>  — <concrete reason it does not belong>
```

**<Bolded default rule, e.g., "Inclusion is the default.">** <Sentence stating that the agent may only place an item in the exclusion bucket if it can name a specific, concrete reason. Then list 3–4 valid reasons as bullets.>

- <Valid exclusion reason>
- <Valid exclusion reason>
- <Valid exclusion reason>

<Lead-in sentence for reasons that are NOT valid. List 3–4 invalid reasons as bullets — these are the excuses the model is most likely to reach for and must be rejected.>

- <Invalid reason the model might invent>
- <Invalid reason the model might invent>
- <Invalid reason the model might invent>
- <Invalid reason the model might invent>

**<Bolded restatement of the completeness invariant, e.g., "Omission is not the same as exclusion.">** <Sentence reinforcing that failing to mention an item at all is a bug, not a valid form of exclusion.>

### 3. <Staging / preparation step name>

<Instruct the agent how to act on the inclusion decisions from step 2. Give the exact command shape inside a fenced block, with `<angle-bracket>` placeholders for the items.>

```
<command to apply the inclusion decisions with explicit item references>
```

- <Hard rule — forbid sloppy shortcuts such as wildcard-stage-all flags. Name the forbidden flags explicitly.>
- <Permissive rule — what is acceptable (e.g., passing many explicit paths on one line).>

### 4. <Composition step name, e.g., "Compose the commit message">

<Describe the output artifact's format. Give a fenced-format template for the subject line (or headline) that references the variables from the Variables section.>

Format: `<template showing how variables slot into the artifact, e.g., <variable_1>: <variable_2>: <subject line>>`

<Bulleted list of rules for the artifact. Cover: tense/mood, length limit, what the content must describe (the actual produced diff, not the task description), and a tie-breaker rule for when an input argument conflicts with the observed reality.>

- <Rule about tense/mood/formatting>
- <Rule about length limit and punctuation>
- <Rule tying the artifact to the observed reality rather than the input description>
- <Tie-breaker rule for input-vs-reality conflicts>

<Optional sentence permitting a longer body/extended form when the change spans multiple logical pieces, with guidance on how to structure it.>

Examples:
- `<realistic example of the artifact>`
- `<realistic example of the artifact>`
- `<realistic example of the artifact>`

### 5. <Finalization step name, e.g., "Commit, push, confirm">

<Numbered or bulleted list of the exact commands that finalize the work and confirm it landed. Each bullet is one command with a short note on why.>

- `<finalize command>`
- `<publish command>`
- `<confirmation command>` <short note on what success looks like>

### 6. <Verification step name>

<Instruct the agent to re-run the observation command from step 1 and compare the result against its own step 2 decisions. State the exact pass condition: the only items still outstanding must be the ones the agent explicitly put in the exclusion bucket. Describe the failure recovery — typically "return to step 2 and redo the enumeration."">

## Important:

<Bulleted list of non-negotiable constraints that apply across the whole task. Use "NEVER" and "Do not" framings. These are the rules the agent must honor even when other instructions seem to suggest otherwise. Typical content: authorship/attribution rules, forbidden metadata lines, voice requirements for the produced artifact.>

- **<NEVER rule about attribution or authorship>**
- <Rule about who the artifact should appear to be authored by>
- <Rule about what must not be attributed>
- <Rule about forbidden metadata lines>
- <Rule about voice/tone for the artifact>
- <Cleanup rule removing any forbidden content from produced output>

## Report

<State exactly what the agent returns to the caller. Keep it minimal — for a commit prompt, just the commit message that was used, with no surrounding prose. Use "ONLY" to lock the scope of the response.>
