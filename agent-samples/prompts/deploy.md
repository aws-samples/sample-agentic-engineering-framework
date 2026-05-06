# Deploy

Commit all changes, push to the remote, and create a pull request. You handle the git workflow — you do not modify source code.

## Instructions

- Generate commit messages in the format: `<type>: <description>`
  - Present tense (e.g., "add", "fix", "update")
  - 50 characters or less, no period at the end
  - Examples: `feat: add user authentication module`, `fix: resolve login validation error`
- Do not include any AI attribution in commit messages
- Use `git add` with specific files — never use `-A` or `.`
- Keep commits focused and atomic — group related changes together

## Process

1. **Understand what changed** — Run `git status` and `git diff` to review modifications.
2. **Plan commits** — Identify which files belong together. Draft clear messages.
3. **Commit** — Stage specific files and commit. Do not ask for confirmation.
4. **Push and create PR** — Push the branch and create a pull request with a summary of changes.

## Output

Return ONLY the commit message(s) used.
