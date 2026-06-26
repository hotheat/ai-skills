---
name: claude-design-handoff
description: "Use when bridging Claude Design with a React frontend repo: preparing component source, screenshots, and prompts for Claude Design; importing Claude Design zip exports into docs/design; or implementing a saved Claude Design artifact with Codex while preserving existing React props, data flow, APIs, and project conventions."
---

# Claude Design Handoff

## Purpose

Turn React component context into Claude Design-ready materials, store Claude Design outputs in the frontend repo, then implement the chosen design with Codex. Treat Claude Design HTML as design reference, not production code.

Canonical artifact directory:

```text
docs/design/<component-name>-redesign/
  brief.md
  source.tsx
  source.png
  rendered.html
  context/design-system-summary.md
  design.html
  design.png
  implementation-notes.md
  claude-design-prompt.md
```

`source.tsx`, `source.png`, `rendered.html`, and `context/design-system-summary.md` exist when available. Default to TSX plus screenshots; add rendered HTML only when it clarifies actual DOM/visual structure.

When a repo has a stable style summary at `docs/design/design-system-summary.md`, let `prepare` copy it into the handoff directory and mention it in the Claude Design prompt. In Claude Design, select the project Design system when one exists; the summary is the compact source-of-truth style note.

## Mode Selection

- **prepare**: user gives a repo and React component path, and wants materials/prompt for Claude Design.
- **import**: user gives a Claude Design exported zip and a target design directory/name.
- **implement**: user wants Codex to implement from `design.html` / `design.png` in a React repo.

If the user does not name a mode, infer it from inputs:

- component path only -> prepare
- zip path -> import
- existing `docs/design/...` directory -> implement

## Prepare Mode

Use `scripts/prepare_design_handoff.py` unless the task requires custom collection.

```bash
python personal/claude-design-handoff/scripts/prepare_design_handoff.py \
  --repo /path/to/frontend-repo \
  --component src/features/character/components/CharacterTimeline.tsx \
  --name character-timeline-redesign \
  --page "Character Detail" \
  --goal "Improve timeline scanning efficiency" \
  --screenshot /path/to/current.png \
  --rendered-html /path/to/current-dom.html
```

The script creates:

- `brief.md`: source, goal, constraints, and artifact list.
- `source.tsx`: copied component source.
- `source.png`: optional copied current screenshot.
- `rendered.html`: optional copied DOM snapshot.
- `context/design-system-summary.md`: copied automatically from repo-level `docs/design/design-system-summary.md` when present.
- `implementation-notes.md`: Codex implementation contract.
- `claude-design-prompt.md`: prompt to paste into Claude Design.

Tell the user to upload/paste the generated prompt and artifacts into Claude Design. If a Claude Design project Design system exists, tell them to select it so future handoffs do not repeat global style rules.

## Import Mode

Use `scripts/import_claude_design_zip.py`.

```bash
python personal/claude-design-handoff/scripts/import_claude_design_zip.py \
  --repo /path/to/frontend-repo \
  --zip ~/Downloads/claude-design-export.zip \
  --name character-timeline-redesign
```

The script:

- safely extracts the zip into a temporary directory;
- selects `index.html` or the largest HTML file as `design.html`;
- selects the largest PNG as `design.png` when present;
- updates `brief.md` and `implementation-notes.md`.

If the zip has no PNG, ask the user to export or capture one from Claude Design and save it as `design.png`.

## Implement Mode

Read, in order:

1. `brief.md`
2. `implementation-notes.md`
3. `design.png` if present
4. `design.html`
5. the real source component path from `brief.md`

Then implement in the actual React codebase.

Rules:

- Preserve existing props, API contracts, routing, and data flow unless the user explicitly asks otherwise.
- Prefer existing components, design tokens, Tailwind classes, and local styling conventions.
- Follow `docs/design/design-system-summary.md` if present.
- Do not copy Claude Design HTML directly into `src/`.
- Do not add a new UI framework for a redesign artifact.
- Keep the diff scoped to the requested component/page and necessary tests.
- Run the repo's relevant lint/test/typecheck commands when discoverable.

Suggested implementation prompt for Codex:

```text
Use $claude-design-handoff implement with docs/design/<component-name>-redesign.
Implement the saved Claude Design artifact in the real React component.
Preserve existing props, API contract, and data flow.
Prefer existing components, tokens, and Tailwind classes.
Do not copy design.html directly into src/.
Run relevant lint/test/typecheck.
```

## Output Summary

End with:

- artifact directory path;
- files created or imported;
- whether `design.png` exists;
- implementation status and verification commands run.
