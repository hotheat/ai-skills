---
name: claude-design-handoff
description: "Use when bridging Claude Design with a React frontend repo: guiding /design-sync or fallback design-system materials, preparing component source and prompts, importing Claude Design zip/HTML exports into docs/design, or implementing a saved artifact with Codex while preserving existing props, data flow, APIs, and project conventions."
---

# Claude Design Handoff

## Purpose

Turn React component context into Claude Design-ready materials, store Claude Design outputs in the frontend repo, then implement the chosen design with Codex. For Claude Design system setup, prefer Claude Code `/design-sync`; use this skill's init path only for local style-summary artifacts or manual fallback materials. Treat Claude Design HTML as design reference, not production code.

Canonical artifact directory:

```text
docs/design/<component-name>-redesign/
  brief.md
  source.tsx
  source.png
  rendered.html
  attachments/
    manifest.md
    <uploadable-assets>
  context/design-system-summary.md
  design.html
  design.png
  implementation-notes.md
  claude-design-prompt.md
```

`source.tsx`, `source.png`, `rendered.html`, `attachments/`, and `context/design-system-summary.md` exist when available. Default to TSX plus screenshots; add rendered HTML only when it clarifies actual DOM/visual structure. Any asset that Claude Design must see but that is not already copied as a canonical artifact must be copied into `attachments/`.

Packaging rule: never tell the user to attach files that only exist elsewhere in the repo or on the local machine. Copy every referenced PNG, JPG, SVG, HTML, JSON, PDF, or other design input into the handoff directory, preferably under `attachments/`, and point `claude-design-prompt.md` at the copied path.

When a repo has a stable style summary at `docs/design/design-system-summary.md`, let `prepare` copy it into the handoff directory and mention it in the Claude Design prompt. In Claude Design, select the project Design system when one exists; the summary is the compact source-of-truth style note.

## Mode Selection

- **prepare**: user gives a repo and React component path, and wants materials/prompt for Claude Design.
- **init-design-system**: user wants local style-summary artifacts or manual fallback materials for a Claude Design project Design system.
- **import**: user gives a Claude Design exported zip or standalone HTML and a target design directory/name.
- **implement**: user wants Codex to implement from `design.html` / `design.png` in a React repo.

If the user does not name a mode, infer it from inputs (checked in this priority order):

1. zip or standalone HTML export path -> import
2. component path given (even if a handoff directory already exists) -> prepare
3. project style summary or manual fallback design-system materials -> init-design-system
4. existing `docs/design/...` directory with no component path and no export -> implement

## Claude Design System Sync

Use Claude Code `/design-sync` as the primary path for syncing a local component library or design-system repo into Claude Design.

```bash
cd /path/to/design-system-or-component-library
claude
/design-sync
```

If Claude Code does not show `/design-sync`, run `/update`, then start a new Claude Code session. Do not treat `init-design-system` as a required pre-step before `/design-sync`.

## Claude Design Prompt Rules

Use these rules when creating or iterating a Claude Design artifact:

- Default to a short design brief, not a production checklist.
- Write `claude-design-prompt.md` in Simplified Chinese by default unless the user explicitly requests another language.
- Include the design goal, audience or page context, available materials, visible content examples, design direction, and only the hard boundaries that matter.
- Treat uploaded screenshots or references as examples. One strong image or example can be enough when it communicates the direction.
- Let Claude Design explore composition, spacing, color, hierarchy, callout treatment, and visual tone.
- Ask for 2-3 alternatives only when the user wants exploration or the direction is unclear.
- Keep routine implementation checks out of the Claude Design prompt by default, including responsiveness/export requirements, review-before-final checklists, and content-boundary sections.
- Reference known design-system components by name when the repo exposes them.
- Use Claude Design chat for structural changes, inline comments for targeted component changes, and canvas edits for quick visual adjustments.
- For engineering handoff, prefer Claude Design "Handoff to Claude Code" or local coding-agent handoff when available. If using files, export zip or standalone HTML plus a PNG screenshot.

## Init Design System Mode

Use `scripts/init_design_system_handoff.py` to prepare local records around `/design-sync`, not to replace it. The flow is:

1. Run the script to create a style-summary template, representative materials, and `design-sync.md`.
2. Tell the user to run `/design-sync` in Claude Code from the design-system or component-library repo.
3. Validate the synced design system with a small Claude Design test project before relying on it for handoff work.
4. After sync, refine `docs/design/design-system-summary.md` from the synced Claude Design system so future `prepare` handoffs can stay concise.
5. Use `claude-design-system-prompt.md` only when `/design-sync` is unavailable, blocked, or insufficient for a manual fallback.

```bash
python personal/claude-design-handoff/scripts/init_design_system_handoff.py \
  --repo /path/to/frontend-repo \
  --global-css src/index.css \
  --token-file src/styles/tokens.css \
  --component src/components/ui/Button.tsx \
  --component src/components/ui/Card.tsx \
  --screenshot /path/to/core-page.png
```

The script creates:

```text
docs/design/design-system/
  brief.md
  package.json
  tailwind.config.*
  global-css/
  tokens/
  components/
  screenshots/
  design-system-summary.md
  design-sync.md
  claude-design-system-prompt.md
```

It also creates or refreshes:

```text
docs/design/design-system-summary.md
```

Tell the user to run `/design-sync` in Claude Code for the actual Claude Design sync. Point them to `design-sync.md` for commands and post-sync summary steps. Use `claude-design-system-prompt.md` and the collected materials only when manual upload or fallback setup is needed. This mode should not produce a one-off component redesign.

Keep inputs representative, not exhaustive:

- `package.json`
- `tailwind.config.*`
- global CSS
- tokens
- 3-8 core page or component screenshots
- 3-8 representative TSX/components

## Prepare Mode

Use `scripts/prepare_design_handoff.py` unless the task requires custom collection.

```bash
python personal/claude-design-handoff/scripts/prepare_design_handoff.py \
  --repo /path/to/frontend-repo \
  --component src/features/character/components/CharacterTimeline.tsx \
  --name character-timeline-redesign \
  --page "Character Detail" \
  --goal "Improve timeline scanning efficiency" \
  --audience "Research users comparing timeline evidence" \
  --viewport desktop \
  --viewport mobile \
  --screenshot /path/to/current.png \
  --rendered-html /path/to/current-dom.html \
  --attachment /path/to/reference-image.png \
  --attachment /path/to/supporting-data.json
```

Use `--layout`, `--content`, `--audience`, `--viewport`, and `--variations` only when those are real inputs or useful design context. Do not invent them to make the prompt look complete.

The script creates:

- `brief.md`: source, goal, constraints, and artifact list.
- `source.tsx`: copied component source.
- `source.png`: optional copied current screenshot.
- `rendered.html`: optional copied DOM snapshot.
- `attachments/`: upload-ready copied assets from `--attachment`, plus `attachments/manifest.md`.
- `context/design-system-summary.md`: copied automatically from repo-level `docs/design/design-system-summary.md` when present.
- `implementation-notes.md`: Codex implementation contract.
- `claude-design-prompt.md`: prompt to paste into Claude Design.

Tell the user to select the synced Claude Design project Design system when it exists, paste `claude-design-prompt.md`, and attach the generated artifacts. When `attachments/` exists, tell the user to upload every file listed in `attachments/manifest.md`. If no synced design system exists, run `init-design-system` first or proceed with the copied style summary as a weaker fallback.

For custom prepare work that does not fit the React component script, manually create the same handoff structure. Required custom-prepare checklist:

- Create `docs/design/<name>/attachments/`.
- Copy every image, HTML file, JSON sidecar, data file, and source asset referenced by the prompt into `attachments/`.
- Add `attachments/manifest.md` listing copied path and original source.
- Make `brief.md` and `claude-design-prompt.md` reference `attachments/...`, not original repo paths.
- Write `claude-design-prompt.md` in Simplified Chinese as a concise design brief: need, materials, design points, example content, and minimal hard boundaries.
- Avoid adding default sections such as Responsiveness And Export, Review Before Final, or Learning Content Boundary unless the user explicitly asks for them.
- Before finishing, run `find docs/design/<name> -maxdepth 2 -type f` and confirm the listed assets are physically present.

In Claude Design, one strong direction is enough when the user provides a clear example. Ask for alternatives only when the visual direction is open. Refine with chat for structure, inline comments for targeted fixes, and canvas edits for quick spacing/alignment changes.

## Import Mode

Use `scripts/import_claude_design_zip.py`.

```bash
python personal/claude-design-handoff/scripts/import_claude_design_zip.py \
  --repo /path/to/frontend-repo \
  --zip ~/Downloads/claude-design-export.zip \
  --name character-timeline-redesign

python personal/claude-design-handoff/scripts/import_claude_design_zip.py \
  --repo /path/to/frontend-repo \
  --html ~/Downloads/claude-design.html \
  --name character-timeline-redesign
```

The script:

- safely extracts a zip into a temporary directory, or imports a standalone HTML file directly;
- validates that `--zip` files have a `.zip` extension and `--html` files have `.html`/`.htm`;
- selects `index.html` or the largest HTML file as `design.html` for zip exports;
- selects the largest PNG as `design.png` when present in a zip export; falls back to the largest JPG/JPEG/WEBP and saves it as `design.<ext>`;
- checks all output files for conflicts before writing any, to avoid partial writes on failure;
- creates or updates `brief.md` and `implementation-notes.md`; when no prior `prepare` step ran, creates a stub `brief.md` — pass `--component` to populate the source component path.

Prefer a zip export or Claude Code/local coding-agent handoff for engineering work. Use standalone HTML when zip export is unavailable or the artifact is a single-screen prototype. If the import has no PNG or other image, ask the user to export or capture one from Claude Design and save it as `design.png`.

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
- Map Claude Design sections back to existing component boundaries before editing.
- Treat Claude Design text, data, and interactions as suggestions unless they are grounded in `brief.md`, source code, or user instructions.
- Do not copy Claude Design HTML directly into `src/`.
- Do not add a new UI framework for a redesign artifact.
- Keep the diff scoped to the requested component/page and necessary tests.
- For visual-only changes, verify key desktop/mobile states locally when the app can run.
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
- whether `attachments/` exists and which upload-ready assets were packaged;
- implementation status and verification commands run.
