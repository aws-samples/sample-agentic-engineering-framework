# Implementation Documentation Index

<Opening framing paragraph (1–2 sentences). State that this file is a registry of generated feature documentation under `ai_docs/` — one entry per doc produced by `/document` — and that planners, builders, and reviewers consult it to locate relevant prior work.>

## Purpose

<Short paragraph describing the role of this file: a running index of feature docs that grows organically as `/document` runs, with per-entry conditions so downstream agents can decide when each doc is worth reading.>

## Entry Format

<Short paragraph describing the per-entry shape — a path under `ai_docs/` followed by a `Context:` block listing the conditions under which the doc should be read.>

- `ai_docs/<feature-name>.md`
  - Context:
    - When working with `<feature area or component>`
    - When modifying `<related functionality>`
    - When referencing `<patterns or conventions established by this feature>`
    - When troubleshooting `<issues in this area>`

## Entries

<Lead-in sentence: add one bullet per generated feature doc. Entries below are illustrative placeholders. The list grows as `/document` runs.>

- `ai_docs/<example-feature-area-1>.md`
  - Context:
    - When working with `<the core domain or layer the feature touches>`
    - When implementing `<UI or flows directly related to the feature>`
    - When troubleshooting `<known failure modes in this area>`
    - When adding new `<entities, tables, or components following the established pattern>`

- `ai_docs/<example-feature-area-2>.md`
  - Context:
    - When working on `<a different feature area or layer>`
    - When modifying `<flows, dialogs, or navigation related to this feature>`
    - When adding `<new entry points that should integrate with the feature>`
    - When referencing `<patterns this feature established — validation, formatting, etc.>`
