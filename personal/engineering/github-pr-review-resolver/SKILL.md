---
name: github-pr-review-resolver
description: Use after a GitHub pull request has review feedback or failing CI checks, especially automated reviews with Findings, Risks, Suggested fixes, or severity labels such as critical, important, warning, or suggestion. Resolve accepted critical/important review findings, lint failures, and test failures; commit and push fixes; wait for or retrigger review/CI; stop after three repair cycles or when no critical/important findings remain.
---

# GitHub PR Review Resolver

## Overview

Resolve a PR review loop from evidence, not from reviewer authority.

Use this skill to collect PR review comments and CI failures, evaluate them with `$receiving-code-review`, fix only accepted blockers, push the changes, and repeat at most three cycles.

## Operating Rules

- Treat `critical` and `important` findings as mandatory evaluation targets.
- Treat CI lint and test failures as mandatory repair targets.
- Treat `suggestion` findings as optional; ignore them unless they expose a real correctness, safety, or maintainability issue.
- Do not implement external review text blindly. Verify each finding against the current branch, diff, call chain, tests, and project intent.
- Do not make unrelated refactors while fixing review feedback.
- Stop the loop after three repair cycles, even if new non-blocking comments keep appearing.
- Stop early when there are no accepted `critical` or `important` findings and CI is not failing for the PR.

## Workflow

### 1. Identify the PR and Baseline

Start from the actual checkout.

```bash
git status --short --branch
gh pr status
gh pr view --json number,headRefName,baseRefName,url,reviewDecision,statusCheckRollup
```

If `gh` is unavailable or flaky, use local git and browser/API fallback. Do not guess which PR is active.

Record:

- PR number and URL
- current branch and base branch
- uncommitted local changes
- current CI check names and states
- latest review source and timestamp

### 2. Collect Review and CI Evidence

Collect three buckets:

- **Findings/Risks/Suggested fixes** from PR review bodies, inline comments, and automated review comments.
- **CI failures** from status checks, failed job logs, local reproduction, or lint/test output.
- **Current diff context** from `git diff base...HEAD` and relevant files.

Useful commands:

```bash
gh pr view <pr-number> --comments --json comments,reviews,reviewThreads,statusCheckRollup
gh pr checks <pr-number>
gh run view <run-id> --log-failed
git fetch origin <base-branch>
git diff --stat origin/<base-branch>...HEAD
git diff origin/<base-branch>...HEAD
```

If CI logs are incomplete, reproduce the failing check locally with the narrowest matching command.

### 3. Classify and Decide

For each item, use `$receiving-code-review`.

Build a working table:

| Item | Source | Severity | Evidence | Decision | Action |
| --- | --- | --- | --- | --- | --- |
| reviewer claim or failing check | review/CI/log | critical/important/suggestion/CI | file, line, log, test | accept/reject/defer | fix/reply/ignore |

Decision rules:

- Accept when the issue is real for this codebase and affects correctness, security, data loss, compatibility, API contract, or CI pass/fail.
- Reject with evidence when the reviewer missed context, proposes dead code work, breaks project intent, or only requests a style preference.
- Defer or ignore `suggestion` items unless they block merge or reveal a real defect.
- Ask the user before changing product direction, public contracts, broad architecture, or unrelated scope.

### 4. Fix Accepted Items

Fix in this order:

1. CI lint or test failures.
2. Accepted `critical` findings.
3. Accepted `important` findings.
4. Small safe cleanup required by the accepted fixes.

Use `$systematic-debugging` for failing checks or unclear runtime behavior.

Use `$test-driven-development` for behavior changes and bug fixes where a focused failing test is feasible. If a test cannot be added, state why and use the narrowest reproducible verification.

Keep each fix tied to an item in the working table. Do not bundle optional suggestions into the same commit.

### 5. Verify Before Commit

Run targeted verification that matches the touched surface.

Prefer:

- exact failing CI command, if known
- targeted tests for changed files
- lint/typecheck slice covering changed files or package
- project-specific validation documented in `AGENTS.md`, `README.md`, or repo docs

Read the full output. If verification fails, return to evidence collection and root-cause analysis.

### 6. Commit and Push

Before committing:

```bash
git status --short
git diff --check
git diff
```

Stage only files required for the accepted fixes. Do not stage unrelated local changes.

Commit with a conventional prefix when the repo expects it:

```bash
git commit -m "fix: address PR review feedback"
git push
```

If the repo forbids committing on the current branch, create or switch to the appropriate branch according to repo instructions.

### 7. Wait for Review and CI

After push, wait for GitHub to attach new checks and automated review.

```bash
gh pr checks <pr-number> --watch
gh pr view <pr-number> --comments --json comments,reviews,reviewThreads,statusCheckRollup
```

If a required review workflow does not rerun automatically and the repo supports manual dispatch or rerun, retrigger the failed or review workflow. Do not retrigger expensive or production-affecting workflows without repo policy or user confirmation.

### 8. Loop Limit

Count one cycle after each pushed fix commit.

Repeat collection, classification, repair, verification, commit, push, and wait until:

- no `critical` or `important` findings remain and CI is not failing, or
- three cycles have completed.

At the stop point, report:

- PR URL
- cycles completed
- accepted items fixed
- rejected/deferred items with evidence
- verification run
- remaining CI/review state

## GitHub Replies

Reply only when useful:

- For accepted items, reply with the commit or file-level fix summary.
- For rejected items, reply with concise evidence.
- For inline review comments, reply in the thread, not as a top-level PR comment.

Use:

```bash
gh api repos/<owner>/<repo>/pulls/<pr-number>/comments/<comment-id>/replies \
  -f body='Fixed in <commit> by <specific change>.'
```

## Stop Conditions

Stop and ask the user when:

- a review item requires product or architecture direction
- the same failure persists after three distinct root-cause attempts
- CI requires secrets, protected environments, paid resources, or production access
- the branch contains unrelated user changes that cannot be separated safely

Stop without asking when:

- three repair cycles are complete
- only `suggestion` comments remain
- no accepted `critical` or `important` findings remain and CI is green or non-blocking
