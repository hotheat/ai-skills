---
name: code-review-toolkit
description: |
  Unified local code review toolkit. Use when the user wants to inspect repository changes directly: review a git diff, review specific files, summarize a commit, or invoke codex-cli review. Trigger on requests like "review diff", "review these files", "review commit", "codex review", "run code review", "check this PR diff", or comparisons against a base branch. Not for requesting external review workflows; use requesting-code-review for that.
---

# Code Review Toolkit

Review code changes locally from git output and source files.

## Distinction from requesting-code-review

- `requesting-code-review`: Use when you have just completed work and want to formally request a focused review before merging. It gathers context (what was implemented, plan, base/head SHA) and dispatches a dedicated reviewer subagent.
- `code-review-toolkit`: Use when the user wants to directly inspect or analyze code that is already in scope — a diff, a set of files, a commit, or via codex-cli. No external reviewer dispatch.

## Requirements

- Requires `git` for diff and commit modes.
- Requires `codex-cli` only for codex review mode.

## Modes

Detect the user's intent and run the matching mode. If ambiguous, ask which mode.

### 1. Diff review (`review diff` / `git diff review`)

Triggered by: "review diff", "review my changes", "check the diff", "review current diff", etc.

Steps:
1. Determine base ref in this order:
   - User-provided ref, branch, commit SHA, or range.
   - Upstream merge-base from `@{upstream}` when available.
   - Remote default branch from `origin/HEAD` when available.
   - `origin/main` only when it exists.
   - `HEAD~1` as the last fallback.
2. Run `git diff --stat <base>` and `git diff <base>`.
3. Review the diff yourself. Focus on correctness, regressions, architecture, async I/O, resource management, security, and missing tests.
4. Output:
   - Summary of changes
   - Findings by severity
   - Verdict: ready to commit / needs fixes / do not commit

### 2. Files review (`review files`)

Triggered by: "review files", "review these files", "check these files", paths ending in `.py`/`.ts`/etc.

Steps:
1. Collect file paths from arguments. If none, ask.
2. Read the target files and nearby related code needed to understand call chains.
3. Review the implementation yourself against project standards and local patterns.
4. Output findings by severity with file:line references.

### 3. Commit summary (`review commit` / `commit summary`)

Triggered by: "review commit", "summarize commit", "commit summary", with a commit SHA argument.

Steps:
1. Get commit SHA from argument. Default to `HEAD` if omitted.
2. Run `git show --stat <sha>` and `git show <sha>`.
3. Produce a developer-readable summary:
   - One-sentence overview
   - Key files and changes
   - Business impact / problem solved
   - Code quality notes
   - Risk points

### 4. Codex review (`codex review` / `codex-review`)

Triggered by: "codex review", "run codex review", "codex-cli review".

Steps:
1. Determine target: PR number, diff range, or file paths from arguments.
2. Use the codex-cli skill (`Skill(codex-cli)`) or run `codex-cli review` if available.
3. Present results concisely.

## Review Standards

Apply these review standards in every mode. Prioritize findings in this order:

1. Functional bugs, regressions, incomplete planned behavior
2. Architecture violations (port-adapter, dependency flow, infra imports)
3. Async blocking I/O, concurrency, retry, resource management
4. Error handling, type safety, defensive programming, edge cases
5. Security, secret handling, performance risks
6. Missing or weak tests for changed behavior

## Output Format

Use this structure unless the mode dictates otherwise:

```markdown
## Overview
[What was reviewed and why it matters]

## Findings
- **Critical**: [must fix — bugs, security, data loss]
- **Important**: [should fix — architecture, missing tests, error handling]
- **Suggestion**: [nice to have — clarity, minor optimization]

## Risks
[Residual risks, plan mismatches, testing gaps]

## Verdict / Next Steps
[Ready to commit / needs fixes / do not commit, with concrete actions]
```

## Critical Rules

- Never say "looks good" without reviewing the actual diff or files.
- Always reference file paths and line numbers when possible.
- Skip pure style nits unless they hide a correctness issue.
- For architecture violations, explain why the rule exists and what to change.
- If the implementation deviates from the plan, ask whether the deviation was intentional.
