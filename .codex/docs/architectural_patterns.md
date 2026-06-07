# Architectural Patterns

## Skill Folder As Module Boundary

- Each reusable capability is packaged as a directory centered on `SKILL.md`; this pattern appears across personal and project skills (`personal/planner/SKILL.md:1`, `personal/test-driven-development/SKILL.md:1`, `project/kimi-ppt/pptd-template-pipeline/SKILL.md:1`).
- Optional `agents/openai.yaml` files sit inside the same skill folder and describe UI-facing metadata without changing the skill body (`personal/planner/agents/openai.yaml:1`, `personal/requesting-code-review/agents/openai.yaml:1`).

## Bucketed Ownership

- Top-level buckets separate personal experiments, team-facing skills, and project-specific skills (`README.md:20`, `README.md:21`, `README.md:22`).
- Project-bound skills can carry domain-specific toolchains and references under `project/<domain>/<skill>/`, while general workflows stay under `personal/` (`README.md:20`, `README.md:22`).

## Progressive Disclosure

- Large workflows keep `SKILL.md` as the entry point and direct Codex to read deeper references only when relevant (`project/kimi-ppt/pptd-template-pipeline/SKILL.md:12`, `project/kimi-ppt/pptd-template-pipeline/SKILL.md:16`, `project/kimi-ppt/pptd-template-pipeline/SKILL.md:21`).
- Supporting techniques are split into nearby Markdown files instead of being expanded inline (`personal/systematic-debugging/SKILL.md:114`, `personal/systematic-debugging/SKILL.md:278`, `personal/systematic-debugging/SKILL.md:282`).

## Workflow Contracts And Gates

- Skills define ordered workflows and explicit gates before moving to the next phase (`personal/brainstorming/SKILL.md:20`, `personal/brainstorming/SKILL.md:31`, `personal/systematic-debugging/SKILL.md:46`, `personal/systematic-debugging/SKILL.md:48`).
- Validation gates are stated as observable outcomes, such as passing tests or zero checker errors (`personal/test-driven-development/SKILL.md:31`, `personal/test-driven-development/SKILL.md:47`, `project/kimi-ppt/pptd-template-pipeline/SKILL.md:42`, `project/kimi-ppt/pptd-template-pipeline/SKILL.md:45`).

## Script-Backed Determinism

- Skills use scripts for repeatable conversions, checks, rendering, or exports when manual instructions would be fragile (`project/kimi-ppt/ppt-template-style-reflow/SKILL.md:14`, `project/kimi-ppt/ppt-template-style-reflow/SKILL.md:16`, `project/kimi-ppt/ppt-template-style-reflow/SKILL.md:20`).
- Runtime requirements are documented next to the script contract, keeping environment assumptions local to the skill (`project/kimi-ppt/ppt-template-style-reflow/SKILL.md:24`, `project/kimi-ppt/ppt-template-style-reflow/SKILL.md:26`, `project/kimi-ppt/ppt-template-style-reflow/SKILL.md:27`).

## Attribution And Provenance

- Repo-level attribution records whether a skill is original, inspired, adapted, or forked (`ATTRIBUTION.md:5`, `ATTRIBUTION.md:7`, `ATTRIBUTION.md:8`, `ATTRIBUTION.md:9`, `ATTRIBUTION.md:10`).
- Imported or adapted skills document source links and local adaptation notes (`ATTRIBUTION.md:61`, `ATTRIBUTION.md:64`, `ATTRIBUTION.md:66`, `ATTRIBUTION.md:71`, `ATTRIBUTION.md:74`, `ATTRIBUTION.md:76`).

## Relative Path Guidance

- Scoped `AGENTS.md` files can add narrower rules for a skill subtree without changing root behavior (`personal/receiving-code-review/AGENTS.md:1`, `personal/receiving-code-review/AGENTS.md:3`).
- Existing scoped guidance favors repo-relative file references for review output (`personal/receiving-code-review/AGENTS.md:5`, `personal/receiving-code-review/AGENTS.md:6`).
