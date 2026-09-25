---
name: pr-rules
description: PR drafting rules for this project — confirming new branch names and commit messages with the user before creating them, and signing PR/issue comments posted in auto mode. Use whenever creating a new git branch, writing a commit message, drafting/opening a pull request, or posting a PR/issue comment via gh.
---

# PR drafting rules

- When creating a new branch, confirm the branch name with the user before creating it (e.g. via `git checkout -b` or `git switch -c`).
- Before committing, confirm the commit message/description with the user rather than committing straight away.
- When in auto mode, any PR/issue comment posted via `gh` (e.g. review replies) is attributed to the user's own GitHub account since it uses their authenticated token — there's no separate bot identity. To distinguish agent-authored comments, append a signature line to the comment body: `— claude-agent`.
