---
name: clean-git-branches
description: Use when cleaning stale Git local branches, remote branches, branches whose pull requests are already merged, missing remote tracking branches, or branches older than a retention window.
---

# Clean Git Branches

## Overview

Use this skill to safely clean local and remote Git branches. Prefer the bundled script because branch cleanup has destructive edge cases.

Git does not reliably store branch creation time. Treat age as:

- Local branch: earliest reflog timestamp when available, otherwise tip commit timestamp.
- Remote branch: tip commit timestamp.

## Workflow

1. Confirm the repository is clean with `git status --short`.
2. Fetch and prune first: `git fetch --all --prune`.
3. Run a dry run:
   `${SKILL_DIR}/scripts/clean_git_branches.sh --months 3`
4. Inspect the planned deletions, including branch name, inferred creation time, and deletion reason.
5. Execute only when the deletion plan is acceptable:
   `${SKILL_DIR}/scripts/clean_git_branches.sh --months 3 --execute`
6. Type `确认删除` when prompted. Any other input aborts deletion.

## Deletion Rules

Delete a branch when any condition is true:

- Its GitHub PR is already merged.
- Its remote branch no longer exists, then delete the local branch.
- Its local or remote age is older than the retention window, default 3 months.

Protected branches are never deleted:

- Current branch
- `main`, `master`, `develop`, `dev`, `release`, `staging`, `production`
- Branches matching `release/*`, `hotfix/*`, `prod/*`

## Safety Rules

- Do not delete branches before a dry run.
- Before deletion, print every selected local and remote branch with inferred creation time and deletion reason.
- Require explicit interactive confirmation by typing `确认删除`.
- Do not delete the current branch.
- Do not delete protected branches.
- If `gh` is unavailable or unauthenticated, skip PR-merged detection and continue with remote-missing and age checks.
- Use force deletion only for branches selected by PR-merged, remote-missing, or age rules after the dry run is reviewed.

## Common Commands

Dry run:

```bash
${SKILL_DIR}/scripts/clean_git_branches.sh
```

Execute:

```bash
${SKILL_DIR}/scripts/clean_git_branches.sh --execute
```

Use another remote or retention:

```bash
${SKILL_DIR}/scripts/clean_git_branches.sh --remote upstream --months 6 --execute
```
