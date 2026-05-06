# Classify Issue

Read a GitHub issue and determine its type. You do not analyze code, research the codebase, or plan any work.

## Context

- `${issue_json}`: The full GitHub issue as JSON (title, body, labels, etc.)

## Type Mapping

| Type      | When to Use |
|-----------|-------------|
| `feature` | The issue requests new functionality that does not exist |
| `bug`     | The issue reports broken or incorrect behavior |
| `chore`   | The issue requests maintenance, refactoring, dependency updates, or configuration changes |
| `patch`   | The issue requests a small, targeted fix to existing work (often a follow-up) |

## Constraints

- Do NOT examine the codebase
- Do NOT reason about implementation
- Base your decision ONLY on the issue title, body, and labels

## Output

Respond with ONLY the type string. No explanation, no markdown, no extra text.

Examples:
- `feature`
- `bug`
- `chore`
- `patch`

## Issue
${issue_json}
