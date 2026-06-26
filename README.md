# ai-skills-owner

Personal and shared AI skill repository.

## Directory Structure

```text
ai-skills-owner/
├── .codex/
├── AGENTS.md
├── engineering/
├── productivity/
├── personal/
├── team/
├── project/
├── README.md
└── ATTRIBUTION.md
```

## Directories

- `engineering/`: Engineering, codebase, review, testing, planning, and architecture skills.
- `productivity/`: Learning, thinking, interviewing, and decision-clarification skills.
- `personal/`: Personal content, local workflow, and individual productivity skills.
- `team/`: Team-facing skills that can be shared, recommended, or required.
- `project/`: Project-specific skills tied to a repository, product, or delivery context.
- `.codex/docs/`: Progressive-disclosure documentation for repo-wide patterns and specialized guidance.

## Skills

### Engineering

#### engineering/agents-md-onboard

Create concise repository `AGENTS.md` guidance and `.codex/docs/architectural_patterns.md` from observed codebase structure, commands, and recurring patterns.

#### engineering/clean-git-branches

Safely clean stale local and remote Git branches with dry-run planning, protected-branch guards, merged-PR detection, and explicit confirmation.

#### engineering/code-review-toolkit

Review repository changes directly from local artifacts, including git diffs, specific files, commit summaries, and optional codex-cli review output, with review findings reported in Simplified Chinese by default.

#### engineering/doc-updater

Update repository documentation and codemaps from the current codebase, including READMEs, AGENTS.md, docs, docs/plans, .codex/docs, architecture docs, dependency maps, and `/update-codemaps` or `/update-docs` style refreshes.

#### engineering/executing-plans

Execute a written implementation plan with critical review, task-by-task progress, required verification, and explicit stop points for blockers.

#### engineering/frontend-design

Design distinctive, production-grade agent-facing experiences, tools, workflows, deliverables, and interfaces with strong visual direction, clear state, and polished implementation details.

#### engineering/github-pr-review-resolver

Resolve GitHub PR review and CI repair loops by evaluating findings, fixing accepted critical or important issues, committing, pushing, and rechecking up to a configurable cycle limit that defaults to one.

#### engineering/grill-with-docs

Stress-test a plan against project language, `CONTEXT.md`, ADRs, and code, while updating glossary terms and architecture decisions as they crystallize.

#### engineering/nest-best-practices

Design, refactor, and review NestJS backends with clean architecture boundaries around Controller, UseCase, Service, Port, Adapter, DI, config, async, and testing.

#### engineering/planner

Create actionable implementation plans for complex features, architecture changes, and refactors. The workflow covers requirements analysis, architecture review, step breakdown, implementation ordering, testing strategy, risks, and success criteria.

#### engineering/react-best-practices

Create, refactor, extend, and review React SPA frontends with feature-based structure, shared UI primitives, Tailwind-first styling, state boundaries, forms, hooks, and data-flow rules.

#### engineering/receiving-code-review

Evaluate incoming code review feedback before implementing it. The workflow covers reading feedback, verifying it against the codebase, judging technical fit, responding with evidence, and implementing one item at a time.

#### engineering/requesting-code-review

Request focused code review before merging or after completing meaningful work. The workflow covers selecting a git range, preparing reviewer context, using the review checklist, and acting on feedback by severity.

#### engineering/systematic-debugging

Debug technical issues by tracing root cause before fixing symptoms. The workflow covers reproduction, evidence gathering, recent-change review, hypothesis testing, pattern comparison, and defense-in-depth validation.

#### engineering/techdebt

Safely reduce technical debt by finding and removing dead code, unused imports, unused dependencies, duplicate implementations, obsolete files, and stale comments with risk classification and verification gates.

#### engineering/test-driven-development

Implement features and bug fixes through red-green-refactor. The workflow covers writing a failing test first, verifying the failure, making the smallest passing change, refactoring safely, and avoiding testing anti-patterns.

#### engineering/verification-before-completion

Require fresh verification evidence before claiming work is complete, fixed, passing, committed, or ready for review.

### Productivity

#### productivity/brainstorming

Collaboratively clarify ideas, explore solution directions, and produce a spec after explicit design confirmation.

#### productivity/deep-understanding

Teach and test understanding incrementally with explanation levels, comprehension checks, and interactive questioning.

#### productivity/grill-me

Pressure-test a plan or design through focused questioning, resolving decision-tree branches one at a time and checking the codebase when questions can be answered from implementation.

#### productivity/plan-interviewer

Interview the user in Chinese to turn a rough plan, spec, PRD, or design document into a clearer implementation spec and write it back to the target file.

#### productivity/teach

Teach a new skill or concept over multiple sessions inside a stateful learning workspace with a mission, resources, reference documents, learning records, notes, and HTML lessons.

### Personal

#### personal/baoyu-design

Create polished self-contained HTML design artifacts, prototypes, wireframes, app screens, dashboards, landing pages, decks, and reusable design systems across portable agent harnesses.

#### personal/bilibili-render-pdf

Generate detailed Chinese LaTeX course notes and final PDFs from Bilibili videos, with subtitle/ASR fallback, cover image handling, key-frame extraction, and long-video segmented writing.

#### personal/claude-design-handoff

Bridge Claude Design and React repos by preparing component materials, importing design exports into `docs/design`, and guiding Codex implementation from saved artifacts.

#### personal/clash-verge-proxy-manager

Maintain Clash Verge Rev proxy profiles and whitelist rules with synchronized config files, safe rule insertion, hot reload, and runtime verification.

#### personal/drawio-skill

Generate draw.io diagrams from natural language or codebase structure, with bundled shape search, AI logo helpers, auto-layout, validation, and local export workflows.

#### personal/export-flomo-to-obsidian

Export Flomo zip archives into Obsidian Markdown notes with frontmatter, tags, attachments, idempotent re-runs, and conservative related-note wikilinks.

#### personal/paper-explore

Turn academic papers, arXiv IDs, PDFs, DOIs, and paper URLs into polished Chinese interactive `index.html` pages with figures, formulas, experiment analysis, reproducibility notes, and critique.

#### personal/read-paper-zh

Read academic papers in Chinese as text-first deep technical reports with author-reasoning reconstruction, evidence classification, method explanation, weakest-assumption critique, reproduction planning, counterexample design, and follow-up research ideas.

### Project

#### project/kimi-ppt/pptd-template-pipeline

Generate a PPTD deck from source content and a PPT/PPTX template. The workflow covers template inspection, design-system extraction, outline planning, PPTD/page generation, checker repair loops, and final validation.

#### project/kimi-ppt/ppt-template-style-reflow

Rebuild a content deck in the visual style of a template deck while preserving the content deck's page count and substantive content. The workflow covers PPTD conversion, template style extraction, content page classification, reflow, validation, export, and visual QA.

## Attribution

Sources, inspirations, and adaptation history are recorded in `ATTRIBUTION.md`.
