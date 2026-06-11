# Documentation & Codemap Specialist

Use this reference for broad documentation refreshes, codemap generation, and
`/update-codemaps` or `/update-docs` style work. It adapts ECC's original `doc-updater`
agent into a stack-neutral workflow.

## Mission

Keep repository documentation accurate, current, and useful for future contributors and agents.
Generate docs from source evidence. Do not preserve stale documentation because it sounds
plausible.

## Core Responsibilities

1. Codemap generation: create architectural maps from codebase structure.
2. Documentation updates: refresh READMEs, AGENTS.md, guides, plans, and architecture docs.
3. Source analysis: use language-appropriate parsers, compilers, tests, and search tools.
4. Dependency mapping: track imports, exports, module ownership, entry points, and data flow.
5. Documentation quality: verify paths, links, commands, and examples against the repository.

## Repository Discovery

Start with source-of-truth files:

```bash
git status --short --branch
rg --files
```

Inspect documentation locations in this order when they exist:

1. `README.md`
2. `AGENTS.md`
3. `docs/`
4. `docs/plans/`
5. `.codex/docs/`
6. Existing codemap or architecture files under `docs/**`

Do not assume `docs/developer-guide/` exists. Do not create a new top-level documentation
location when an established location already exists.

## Stack Detection

Detect the project type before choosing commands or templates.

Common signals:

- Node or TypeScript: `package.json`, `tsconfig.json`, `pnpm-lock.yaml`, `vite.config.*`,
  `next.config.*`, `nest-cli.json`.
- React: `package.json` dependencies, `src/main.*`, `src/App.*`, `vite.config.*`,
  `next.config.*`.
- NestJS: `nest-cli.json`, `src/main.ts`, `@nestjs/*` dependencies, module/provider files.
- Python: `pyproject.toml`, `requirements.txt`, `uv.lock`, `setup.py`, `pytest.ini`,
  `app/`, `src/`, `tests/`.
- Go: `go.mod`, `cmd/`, `internal/`, `pkg/`.
- Java or Kotlin: `pom.xml`, `build.gradle*`, `settings.gradle*`, `src/main`.
- Rails or Ruby: `Gemfile`, `config/routes.rb`, `app/models`, `app/controllers`.
- Rust: `Cargo.toml`, `src/lib.rs`, `src/main.rs`, `crates/`.
- Monorepo: `turbo.json`, `pnpm-workspace.yaml`, `nx.json`, `lerna.json`, multiple package
  manifests.

When multiple stacks exist, document boundaries by package or application rather than forcing a
single project model.

## Analysis Commands

Prefer existing repository scripts. Read manifests before inventing commands.

Useful generic commands:

```bash
rg --files docs README.md AGENTS.md .codex 2>/dev/null
rg -n "TODO|Deprecated|Last Updated|architecture|codemap|plan" README.md AGENTS.md docs .codex 2>/dev/null
```

Useful stack-specific examples:

```bash
# TypeScript / JavaScript
npm run lint
npm run typecheck
npx tsc --noEmit
npx madge --extensions ts,tsx,js,jsx src

# Python
uv run pytest
uv run mypy .
python -m py_compile path/to/file.py

# Go
go test ./...
go list ./...

# Rust
cargo test
cargo check
```

Only run commands that fit the repository and task scope.

## Codemap Workflow

### 1. Analyze Repository

- Identify apps, packages, services, libraries, scripts, workers, and CLIs.
- Map directory roles from actual files and imports.
- Find entry points such as server bootstrap files, route registration, CLI entry files,
  workflow definitions, scheduled jobs, and UI mount points.
- Detect architecture patterns from code and existing docs.

### 2. Analyze Modules

For each relevant area:

- Extract public exports, routes, commands, jobs, workflows, or UI entry points.
- Map imports and dependency direction.
- Identify external dependencies and integration clients.
- Locate persistent state, database models, schemas, migrations, queues, caches, or storage.
- Track configuration sources and environment variables.
- Record tests that cover the area.

### 3. Generate or Refresh Codemaps

Use the repository's existing codemap location if present. If no codemap convention exists, prefer
`docs/CODEMAPS/` for generated maps when the user asked for codemaps.

Suggested structure:

```text
docs/CODEMAPS/
├── INDEX.md
├── frontend.md
├── backend.md
├── data.md
├── integrations.md
└── jobs-and-workers.md
```

Adjust filenames to the actual repository. Do not create empty category files.

### 4. Codemap Format

```markdown
# [Area] Codemap

**Last Updated:** YYYY-MM-DD
**Entry Points:** `path/to/file`, `path/to/other-file`

## Purpose

What this area owns.

## Architecture

Short component map or ASCII diagram when useful.

## Key Modules

| Module | Purpose | Public Surface | Dependencies |
|--------|---------|----------------|--------------|
| `path` | ... | ... | ... |

## Data Flow

How data, requests, events, or state move through this area.

## Configuration

Relevant config files, environment variables, feature flags, and defaults.

## Tests

Relevant test files and commands.

## Related Docs

Links to related README, plans, guides, or codemaps.
```

## Documentation Update Workflow

1. Extract current facts from code, manifests, existing docs, tests, and scripts.
2. Compare docs against source facts.
3. Update only affected docs.
4. Preserve existing structure and naming when it works.
5. Update cross-links after moving or adding docs.
6. Validate paths, commands, examples, and links where feasible.

Common targets:

- `README.md`: project overview, setup, run, test, deployment, and key links.
- `AGENTS.md`: stable repository guidance for future agents.
- `docs/`: architecture, guides, references, API notes, codemaps.
- `docs/plans/`: design docs, implementation plans, migration plans, decision records.
- `.codex/docs/`: progressive-disclosure guidance for Codex when the repo uses it.

## Plan Documentation

Use `docs/plans/` for design and implementation plans when the repository already uses it or the
user asks for a plan document.

Suggested plan sections:

```markdown
# YYYY-MM-DD [Feature or Change]

## Summary

## Goals

## Non-Goals

## Current State

## Proposed Design

## Data Flow

## Implementation Steps

## Files to Modify

## Testing Plan

## Rollback Plan
```

Keep plans connected to source paths and future verification commands.

## Architecture Guidance

Name architectural patterns only when the repository supports them.

- For NestJS, document modules, controllers, providers, services, repositories, guards,
  interceptors, configuration, and dependency injection boundaries.
- For React, document routes, feature boundaries, state management, data fetching, UI system,
  form handling, and build/runtime entry points.
- For Python services, document API entry points, services, domain modules, adapters, jobs,
  settings, and tests based on the actual framework.
- For monorepos, document package boundaries, shared libraries, dependency direction, and
  workspace scripts.

Do not impose hexagonal architecture, clean architecture, MVC, or feature-based frontend
structure unless those patterns are visible in code or docs.

## Quality Checklist

- Codemaps and docs are generated from actual code and manifests.
- All mentioned file paths exist.
- Commands come from manifests, Makefiles, task runners, or verified local usage.
- Code snippets and examples compile or are clearly marked as illustrative.
- Links point to existing files or verified external sources.
- Freshness timestamps are updated when the existing doc style uses them.
- Stale references are removed or corrected.
- Verification commands and skipped checks are recorded.

## When to Update Documentation

Always update docs when:

- Major features are added.
- Public APIs, routes, commands, or workflows change.
- Dependencies or setup steps change.
- Architecture, module ownership, or data flow changes.
- Configuration, environment variables, deployment, or operational behavior changes.
- Design or implementation plans are created, superseded, or completed.

Optional for:

- Small bug fixes that do not change behavior.
- Cosmetic changes.
- Internal refactors with no public or architectural impact.

## Principle

Documentation that does not match reality is worse than missing documentation. Generate from the
current source of truth, then verify.
