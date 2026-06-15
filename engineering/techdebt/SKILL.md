---
name: techdebt
description: Use when reducing technical debt by finding and safely removing dead code, unused imports, unused dependencies, duplicate implementations, commented-out code, or obsolete files. Also use for cleanup-focused refactors where deletion safety, reference tracing, test validation, and deletion notes matter more than feature work.
---

# Tech Debt Cleanup

## Overview

Use this skill to remove technical debt without breaking hidden contracts. Treat deletion as a behavior change: prove the code is unused, remove it in small batches, and verify the relevant runtime surface after each meaningful cleanup.

## Operating Rules

- Do not run cleanup during unstable feature work unless the user explicitly asks.
- Do not remove public API, routes, CLI commands, DI providers, schema fields, migrations, plugin hooks, generated files, or decorated functions based only on static unused-code output.
- Do not install new cleanup tools unless the user approves or the repo already documents them.
- Preserve unrelated user changes in the worktree.
- Prefer the repository's documented lint, typecheck, and test commands over generic commands.
- Commit only when the user asks for a commit.

## Workflow

### 1. Establish Scope

1. Inspect `git status --short --branch`.
2. Identify the requested cleanup target: imports, dead code, duplicates, dependencies, files, or broad audit.
3. Read repo guidance before changing code: `AGENTS.md`, README, package scripts, Makefile, CI config, or language-specific config.
4. Find the normal validation commands and note the smallest command set that covers the cleanup surface.

### 2. Detect Candidates

Run only tools that fit the repo. Examples:

- Python: `ruff check --select F`, `mypy`, `pytest`, project `make lint`, `uv run python -m pytest`.
- TypeScript: project `lint`, `typecheck`, `test`, `tsc --noEmit`, existing dead-code scripts if present.
- General: `rg`, import graph tools already configured in the repo, duplicate detectors already documented by the project.

Collect findings before editing. Group them by candidate type and affected boundary.

### 3. Classify Risk

Use this risk model before deleting:

- Safe: unused imports, unused local variables, unreachable branches, stale comments, private helpers with no references.
- Careful: private classes, test fixtures, feature flags, duplicate utilities, dependency entries, files not imported by obvious paths.
- Risky: public exports, API DTOs, route handlers, CLI commands, ORM models, Pydantic fields, DI registrations, migrations, graph nodes, plugin entrypoints, templates, config keys, generated code.

For careful or risky candidates, trace references with:

- Symbol search with `rg`.
- String-name search for dynamic usage.
- Import path search, including aliases and barrel exports.
- Registration search for decorators, routers, CLIs, dependency containers, plugin manifests, graph definitions, templates, and config.
- Git history when intent is unclear.

If usage remains plausible, keep the code and report the uncertainty.

### 4. Remove in Small Batches

Prefer this order:

1. Unused imports and local variables.
2. Clearly unreachable code and stale comments.
3. Unreferenced private helpers.
4. Duplicate implementation consolidation.
5. Unused files.
6. Unused dependencies.

After each meaningful batch, run the cheapest relevant validation before continuing. Use automated fixers only when they are already part of the repo workflow and their diff is reviewed.

### 5. Document Deletions

For substantial deletions, update the repo's existing deletion or maintenance log. If no convention exists and the cleanup is large, create `docs/DELETION_LOG.md` with:

- Date and cleanup scope.
- Files, symbols, or dependencies removed.
- Evidence used to prove non-use.
- Validation commands and results.
- Known residual risk.

For small import-only cleanup, a concise final summary is enough unless the repo requires a log.

### 6. Verify and Report

Before claiming completion:

1. Run `git diff --check`.
2. Run the selected lint, typecheck, and test commands.
3. Inspect the diff for accidental broad rewrites.
4. Report what was removed, what was validated, and any candidates intentionally kept.

## Hidden Usage Checklist

Search for these before deleting anything beyond obvious locals:

- `getattr`, `setattr`, `globals`, `locals`, `__import__`, `importlib`.
- String references to function, class, field, module, route, or command names.
- Decorators that register callbacks, tasks, routes, commands, signals, hooks, or jobs.
- Framework entrypoints in manifests, config files, templates, migrations, and generated registries.
- Tests that construct objects dynamically or access fields through serialization.
- Documentation or scripts that act as public examples.

## Dependency Cleanup

When removing dependencies:

1. Verify no imports, dynamic imports, CLI invocations, config references, extras, optional plugin paths, or generated code require the package.
2. Update the manifest and lockfile using the repo's package manager.
3. Run install or sync if that is the documented way to refresh lock state.
4. Run the relevant tests and startup checks.

## Duplicate Consolidation

When consolidating duplicates:

1. Compare behavior, type contracts, error handling, and call sites before choosing the survivor.
2. Prefer the implementation that is most complete, best tested, and closest to the dominant architecture.
3. Update imports in one batch.
4. Keep names stable when they are public; add compatibility wrappers only when required by public callers.
5. Delete the duplicate only after tests cover the redirected call sites.
