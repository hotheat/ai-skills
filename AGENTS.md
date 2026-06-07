# ai-skills-owner Agent Guide

## Project Overview

- This repository stores personal, team-facing, and project-specific Codex skills (`README.md:3`, `README.md:20`, `README.md:21`, `README.md:22`).
- A skill is primarily a folder with `SKILL.md` frontmatter plus procedural instructions (`personal/planner/SKILL.md:1`, `personal/test-driven-development/SKILL.md:1`, `project/kimi-ppt/pptd-template-pipeline/SKILL.md:1`).
- Source, inspiration, and adaptation history are tracked centrally in `ATTRIBUTION.md` (`ATTRIBUTION.md:1`, `ATTRIBUTION.md:5`).

## Tech Stack

- Markdown is the main implementation medium for skill instructions, references, and repo docs (`personal/planner/SKILL.md:11`, `project/kimi-ppt/pptd-template-pipeline/SKILL.md:12`).
- YAML appears in `SKILL.md` frontmatter and optional `agents/openai.yaml` metadata (`personal/planner/SKILL.md:1`, `personal/planner/agents/openai.yaml:1`).
- Script-backed skills use shell, Python, and JavaScript when deterministic helpers are useful (`project/kimi-ppt/ppt-template-style-reflow/SKILL.md:14`, `project/kimi-ppt/ppt-template-style-reflow/SKILL.md:16`, `project/kimi-ppt/ppt-template-style-reflow/SKILL.md:18`, `project/kimi-ppt/ppt-template-style-reflow/SKILL.md:19`).
- There is no repository-wide package manifest or single build runner; validation is per changed skill or helper.

## Key Directories

- `personal/`: personal skills and workflow experiments (`README.md:20`).
- `team/`: team-facing skills that can be shared, recommended, or required (`README.md:21`).
- `project/`: project-specific skills tied to a repository, product, or delivery context (`README.md:22`).
- `*/agents/openai.yaml`: optional UI metadata for skill lists and default prompts (`personal/planner/agents/openai.yaml:1`, `personal/requesting-code-review/agents/openai.yaml:1`).
- `.codex/docs/`: progressive-disclosure documentation for repo-wide patterns and specialized guidance (`README.md:23`).

## Essential Build/Test Commands

- Inspect current worktree first: `git status --short --branch`.
- Check whitespace and patch hygiene: `git diff --check`.
- Validate changed skills when the local skill-creator tool is available: `python "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" personal/<skill-name>`.
- Check shell helpers changed in a task: `bash -n path/to/script.sh`.
- Check JavaScript helpers changed in a task: `node --check path/to/script.js` or `node --check path/to/script.cjs`.
- Check Python helpers changed in a task: `python -m py_compile path/to/script.py`.
- For PPTD skills, run the checker or render commands documented by the changed skill before claiming deck output is valid (`project/kimi-ppt/ppt-template-style-reflow/SKILL.md:16`, `project/kimi-ppt/ppt-template-style-reflow/SKILL.md:20`, `project/kimi-ppt/pptd-template-pipeline/SKILL.md:42`).

## Additional Documentation

- `.codex/docs/architectural_patterns.md`: read when adding or changing a skill, adding references/scripts, moving files between `personal/`, `team/`, and `project/`, or updating repo-wide guidance.
