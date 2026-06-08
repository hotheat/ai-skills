# ai-skills-owner

Personal and shared AI skill repository.

## Directory Structure

```text
ai-skills-owner/
├── .codex/
├── AGENTS.md
├── personal/
├── team/
├── project/
├── README.md
└── ATTRIBUTION.md
```

## Directories

- `personal/`: Personal skills and workflow experiments.
- `team/`: Team-facing skills that can be shared, recommended, or required.
- `project/`: Project-specific skills tied to a repository, product, or delivery context.
- `.codex/docs/`: Progressive-disclosure documentation for repo-wide patterns and specialized guidance.

## Skills

### personal/agents-md-onboard

Create concise repository `AGENTS.md` guidance and `.codex/docs/architectural_patterns.md` from observed codebase structure, commands, and recurring patterns.

### personal/bilibili-render-pdf

Generate detailed Chinese LaTeX course notes and final PDFs from Bilibili videos, with subtitle/ASR fallback, cover image handling, key-frame extraction, and long-video segmented writing.

### personal/clean-git-branches

Safely clean stale local and remote Git branches with dry-run planning, protected-branch guards, merged-PR detection, and explicit confirmation.

### personal/doc-updater

Update repository documentation and codemaps from the current codebase, including READMEs, AGENTS.md, docs, docs/plans, .codex/docs, architecture docs, dependency maps, and `/update-codemaps` or `/update-docs` style refreshes.

### personal/clash-verge-proxy-manager

Maintain Clash Verge Rev proxy profiles and whitelist rules with synchronized config files, safe rule insertion, hot reload, and runtime verification.

### personal/executing-plans

Execute a written implementation plan with critical review, task-by-task progress, required verification, and explicit stop points for blockers.

### personal/export-flomo-to-obsidian

Export Flomo zip archives into Obsidian Markdown notes with frontmatter, tags, attachments, idempotent re-runs, and conservative related-note wikilinks.

### personal/nest-best-practices

Design, refactor, and review NestJS backends with clean architecture boundaries around Controller, UseCase, Service, Port, Adapter, DI, config, async, and testing.

### personal/planner

Create actionable implementation plans for complex features, architecture changes, and refactors. The workflow covers requirements analysis, architecture review, step breakdown, implementation ordering, testing strategy, risks, and success criteria.

### personal/pptd-template-pipeline

Generate a PPTD deck from source content and a PPT/PPTX template. The workflow covers template inspection, design-system extraction, outline planning, PPTD/page generation, checker repair loops, and final validation.

### personal/ppt-template-style-reflow

Rebuild a content deck in the visual style of a template deck while preserving the content deck's page count and substantive content. The workflow covers PPTD conversion, template style extraction, content page classification, reflow, validation, export, and visual QA.

### personal/react-best-practices

Create, refactor, extend, and review React SPA frontends with feature-based structure, shared UI primitives, Tailwind-first styling, state boundaries, forms, hooks, and data-flow rules.

### personal/receiving-code-review

Evaluate incoming code review feedback before implementing it. The workflow covers reading feedback, verifying it against the codebase, judging technical fit, responding with evidence, and implementing one item at a time.

### personal/requesting-code-review

Request focused code review before merging or after completing meaningful work. The workflow covers selecting a git range, preparing reviewer context, using the review checklist, and acting on feedback by severity.

### personal/systematic-debugging

Debug technical issues by tracing root cause before fixing symptoms. The workflow covers reproduction, evidence gathering, recent-change review, hypothesis testing, pattern comparison, and defense-in-depth validation.

### personal/test-driven-development

Implement features and bug fixes through red-green-refactor. The workflow covers writing a failing test first, verifying the failure, making the smallest passing change, refactoring safely, and avoiding testing anti-patterns.

### personal/verification-before-completion

Require fresh verification evidence before claiming work is complete, fixed, passing, committed, or ready for review.

## Attribution

Sources, inspirations, and adaptation history are recorded in `ATTRIBUTION.md`.
