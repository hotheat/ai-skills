---
name: agents-md-onboard
description: Create concise repository AGENTS.md guidance and progressive-disclosure Codex docs from an existing codebase. Use when the user asks to analyze a repo and create or refresh AGENTS.md, agent instructions, repository guidance, or .codex/docs architectural pattern documentation.
---

# AGENTS.md Onboard

## Overview

Create a short, evidence-backed `AGENTS.md` for a repository and move specialized guidance into `.codex/docs/`. Keep root guidance broadly useful, verifiable, and easy for future Codex sessions to scan.

## Workflow

1. Inspect the repository before writing.
   Read the current worktree state, root docs, dependency manifests, build configs, existing `AGENTS.md` files, and representative source or skill files. Use `rg --files` first, then read targeted files.

2. Identify stable facts.
   Record only facts supported by file references: project purpose, tech stack, directory roles, and available build/test commands. Use `file:line` references instead of code snippets.

3. Create or update `AGENTS.md`.
   Keep it under 150 lines. Use this structure:
   - Project Overview
   - Tech Stack
   - Key Directories
   - Essential Build/Test Commands
   - Additional Documentation

4. Apply progressive disclosure.
   Keep root `AGENTS.md` universal. Put specialized topics under `.codex/docs/` and list each file in the `Additional Documentation` section with when to read it.

5. Create `.codex/docs/architectural_patterns.md`.
   Document architectural patterns, design decisions, and conventions that appear in multiple files. Include evidence with `file:line` references. Do not document one-off implementation details as patterns.

6. Validate.
   Run `wc -l AGENTS.md`, `git diff --check`, and any repository-specific validation commands discovered during inspection. Verify every additional documentation file referenced by `AGENTS.md` exists.

## AGENTS.md Rules

- Include only universally applicable guidance.
- Cover WHAT, WHY, and HOW: project overview, tech stack, structure, purpose, and build/test commands.
- Do not include formatting or style rules when linters or formatters already cover them.
- Prefer exact commands from manifests, Makefiles, task runners, or docs. If no repo-wide runner exists, state that and provide targeted validation commands.
- Use relative paths in repository guidance.
- Preserve narrower scoped `AGENTS.md` files. Root guidance should not duplicate or override subtree-specific rules.

## Architectural Pattern Rules

- Only include patterns with evidence from multiple files.
- Explain the pattern, where it appears, and what Codex should infer when editing nearby code or docs.
- Keep examples as references, not pasted code.
- Prefer categories such as module boundaries, dependency injection, state management, API design, validation gates, script-backed workflows, documentation layering, and ownership boundaries.

## Final Checks

- `AGENTS.md` is under 150 lines.
- `AGENTS.md` references `.codex/docs/architectural_patterns.md` in `Additional Documentation`.
- `.codex/docs/architectural_patterns.md` exists and only documents recurring patterns.
- `git diff --check` passes.
