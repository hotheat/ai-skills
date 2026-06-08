---
name: doc-updater
description: Documentation and codemap maintenance for repositories. Use when Codex needs to update codemaps, READMEs, AGENTS.md, docs/* files, docs/plans/*, .codex/docs/*, architecture documentation, module maps, dependency maps, or run documentation refresh workflows such as /update-codemaps and /update-docs from the actual codebase.
---

# Doc Updater

## Overview

Maintain repository documentation from evidence in the current codebase. Prefer source-backed
updates over inferred summaries, and keep docs aligned with actual modules, commands, and
architecture boundaries.

This skill adapts the original ECC `doc-updater` agent into a reusable Codex skill. The detailed
generic workflow is in `references/agent-prompt.md`; read it when the task requires comprehensive
codemap generation, broad documentation refreshes, or `/update-codemaps` and `/update-docs`
behavior.

## Workflow

1. Inspect the repository state.
   Run `git status --short --branch`, list relevant docs with `rg --files`, and read existing
   `README.md`, `AGENTS.md`, `docs/`, `docs/plans/`, `.codex/docs/`, codemap files, dependency
   manifests, and representative source files before writing.

2. Determine the documentation scope.
   Identify whether the user asked for codemaps, README updates, agent instructions, API docs,
   implementation plans, architecture docs, or broad `/update-codemaps` and `/update-docs` style
   refreshes. Load `references/agent-prompt.md` for broad updates or when matching the original
   `doc-updater` behavior matters.

3. Analyze code before editing docs.
   Detect the stack from source-of-truth files before choosing tools or templates. Use `rg`, AST
   or compiler tools, dependency inspection, tests, and existing scripts where available. Track
   module ownership, dependency direction, entry points, services, agents, workflows, settings,
   and external integrations from source files rather than stale docs.

4. Update only the needed docs.
   Keep existing documentation structure when it is coherent. Refresh codemaps, READMEs,
   developer guides, templates, and related docs with current paths, commands, public entry
   points, data flow, and dependency flow. Remove or correct stale claims.

5. Preserve architecture rules.
   Infer the project's architecture from existing docs and code before naming patterns. Document
   dependency direction explicitly only when the codebase supports that interpretation.

6. Verify documentation quality.
   Run lightweight checks such as `git diff --check`, docs-specific scripts, markdown linters, or
   repository validation commands discovered during inspection. If generated docs have scripts,
   run the relevant script instead of hand-editing generated output.

## Documentation Standards

- Cite file paths and commands that were actually inspected.
- Prefer concise structural maps over long prose.
- Keep generated guidance actionable for future agents.
- Update cross-links when files move or new docs are added.
- Do not invent build, test, runtime, or architecture facts.
- Note verification commands and any checks that could not be run.

## Resource

- `references/agent-prompt.md`: generic `doc-updater` workflow adapted from ECC's original
  `doc-updater` agent and revised for multi-stack repositories.
