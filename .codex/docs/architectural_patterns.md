# Architectural Patterns

## Skill Folder As Module Boundary

- Each reusable capability is packaged as a directory centered on `SKILL.md`; this pattern appears across personal and project skills (`personal/engineering/planner/SKILL.md:1`, `personal/engineering/test-driven-development/SKILL.md:1`, `project/kimi-ppt/pptd-template-pipeline/SKILL.md:1`).
- Optional `agents/openai.yaml` files sit inside the same skill folder and describe UI-facing metadata without changing the skill body (`personal/engineering/planner/agents/openai.yaml:1`, `personal/engineering/requesting-code-review/agents/openai.yaml:1`).

## Bucketed Ownership

- Top-level buckets separate personal experiments, team-facing skills, and project-specific skills (`README.md:23`, `README.md:26`, `README.md:27`).
- General personal skills are further split into `personal/engineering/`, `personal/productivity/`, and `personal/personal/` by use case (`README.md:23`, `README.md:24`, `README.md:25`).
- Project-bound skills can carry domain-specific toolchains and references under `project/<domain>/<skill>/`, while general workflows stay under the appropriate `personal/<category>/` bucket (`README.md:23`, `README.md:27`).

## Progressive Disclosure

- Large workflows keep `SKILL.md` as the entry point and direct Codex to read deeper references only when relevant (`project/kimi-ppt/pptd-template-pipeline/SKILL.md:12`, `project/kimi-ppt/pptd-template-pipeline/SKILL.md:16`, `project/kimi-ppt/pptd-template-pipeline/SKILL.md:21`).
- Supporting techniques are split into nearby Markdown files instead of being expanded inline (`personal/engineering/systematic-debugging/SKILL.md:114`, `personal/engineering/systematic-debugging/SKILL.md:278`, `personal/engineering/systematic-debugging/SKILL.md:282`).

## Workflow Contracts And Gates

- Skills define ordered workflows and explicit gates before moving to the next phase (`personal/productivity/brainstorming/SKILL.md:20`, `personal/productivity/brainstorming/SKILL.md:31`, `personal/engineering/systematic-debugging/SKILL.md:46`, `personal/engineering/systematic-debugging/SKILL.md:48`).
- Validation gates are stated as observable outcomes, such as passing tests or zero checker errors (`personal/engineering/test-driven-development/SKILL.md:31`, `personal/engineering/test-driven-development/SKILL.md:47`, `project/kimi-ppt/pptd-template-pipeline/SKILL.md:42`, `project/kimi-ppt/pptd-template-pipeline/SKILL.md:45`).

## Script-Backed Determinism

- Skills use scripts for repeatable conversions, checks, rendering, or exports when manual instructions would be fragile (`project/kimi-ppt/ppt-template-style-reflow/SKILL.md:14`, `project/kimi-ppt/ppt-template-style-reflow/SKILL.md:16`, `project/kimi-ppt/ppt-template-style-reflow/SKILL.md:20`).
- Runtime requirements are documented next to the script contract, keeping environment assumptions local to the skill (`project/kimi-ppt/ppt-template-style-reflow/SKILL.md:24`, `project/kimi-ppt/ppt-template-style-reflow/SKILL.md:26`, `project/kimi-ppt/ppt-template-style-reflow/SKILL.md:27`).

## Attribution And Provenance

- Repo-level attribution records whether a skill is original, inspired, adapted, or forked (`ATTRIBUTION.md:7`, `ATTRIBUTION.md:9`, `ATTRIBUTION.md:10`, `ATTRIBUTION.md:11`, `ATTRIBUTION.md:12`).
- Imported or adapted skills document source links and local adaptation notes (`ATTRIBUTION.md:70`, `ATTRIBUTION.md:73`, `ATTRIBUTION.md:78`, `ATTRIBUTION.md:80`).

## Relative Path Guidance

- Scoped `AGENTS.md` files can add narrower rules for a skill subtree without changing root behavior (`personal/engineering/receiving-code-review/AGENTS.md:1`, `personal/engineering/receiving-code-review/AGENTS.md:3`).
- Existing scoped guidance favors repo-relative file references for review output (`personal/engineering/receiving-code-review/AGENTS.md:5`, `personal/engineering/receiving-code-review/AGENTS.md:6`).
