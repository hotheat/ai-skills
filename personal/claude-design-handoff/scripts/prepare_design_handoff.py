#!/usr/bin/env python3
"""Prepare React component artifacts for Claude Design."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


TEXT_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".css", ".scss", ".md", ".json", ".html", ".htm"}
DESIGN_SYSTEM_SUMMARY = Path("docs/design/design-system-summary.md")


def slug_from_component(component: Path) -> str:
    stem = component.stem
    chars: list[str] = []
    for index, char in enumerate(stem):
        if char.isupper() and index > 0 and (not stem[index - 1].isupper()):
            chars.append("-")
        if char.isalnum():
            chars.append(char.lower())
        elif char in {"-", "_", " "}:
            chars.append("-")
    slug = "".join(chars).strip("-")
    return f"{slug or 'component'}-redesign"


def resolve_inside_repo(repo: Path, value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = repo / path
    return path.resolve()


def relative_to_repo(repo: Path, path: Path) -> str:
    try:
        return path.relative_to(repo).as_posix()
    except ValueError:
        return path.as_posix()


def write_text(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def copy_optional_context(repo: Path, out_dir: Path, context_files: list[str]) -> list[str]:
    copied: list[str] = []
    if not context_files:
        return copied

    context_dir = out_dir / "context"
    context_dir.mkdir(exist_ok=True)
    for item in context_files:
        source = resolve_inside_repo(repo, item)
        if not source.exists() or not source.is_file():
            raise SystemExit(f"context file not found: {source}")
        if source.suffix.lower() not in TEXT_EXTENSIONS:
            raise SystemExit(f"refuse non-text context file: {source}")
        target = context_dir / source.name
        shutil.copy2(source, target)
        copied.append(target.relative_to(out_dir).as_posix())
    return copied


def copy_design_system_summary(repo: Path, out_dir: Path) -> str | None:
    source = repo / DESIGN_SYSTEM_SUMMARY
    if not source.exists():
        return None
    if not source.is_file():
        raise SystemExit(f"design system summary is not a file: {source}")
    context_dir = out_dir / "context"
    context_dir.mkdir(exist_ok=True)
    target = context_dir / "design-system-summary.md"
    shutil.copy2(source, target)
    return target.relative_to(out_dir).as_posix()


def build_brief(
    *,
    component_rel: str,
    page: str,
    goal: str,
    out_dir_name: str,
    source_name: str,
    screenshot_name: str | None,
    rendered_html_name: str | None,
    design_system_summary: str | None,
    copied_context: list[str],
) -> str:
    artifacts = [f"- `{source_name}`: copied component source"]
    if screenshot_name:
        artifacts.append(f"- `{screenshot_name}`: current UI screenshot")
    if rendered_html_name:
        artifacts.append(f"- `{rendered_html_name}`: optional rendered DOM snapshot")
    if design_system_summary:
        artifacts.append(f"- `{design_system_summary}`: repo-level project style summary")
    artifacts.extend(
        [
            "- `claude-design-prompt.md`: prompt for Claude Design",
            "- `design.html`: Claude Design HTML export, added in import mode",
            "- `design.png`: Claude Design visual reference, added in import mode",
            "- `implementation-notes.md`: Codex implementation contract",
        ]
    )
    if copied_context:
        artifacts.append("- `context/`: copied supporting source/style files")

    context_items = list(copied_context)
    if design_system_summary:
        context_items.insert(0, design_system_summary)
    context_lines = "\n".join(f"- `{item}`" for item in context_items) or "- None"
    artifacts_text = "\n".join(artifacts)

    return f"""# {out_dir_name}

## Source

- Component: `{component_rel}`
- Page: {page or "Unknown"}

## Goal

{goal or "Redesign this component while preserving existing behavior."}

## Constraints

- Preserve existing props and API/data contracts.
- Do not change backend behavior.
- Prefer existing components, tokens, Tailwind classes, and local style conventions.
- Follow `docs/design/design-system-summary.md` when present; in Claude Design, prefer selecting the saved project Design system instead of repeating style rules.
- Cover desktop and mobile states when relevant.
- Treat Claude Design HTML as reference only; do not copy it directly into `src/`.

## Supporting Context

{context_lines}

## Design Artifacts

{artifacts_text}

## Implementation Notes

Implement from `design.png` for visual direction and `design.html` for layout intent. Keep production code idiomatic to this repo.
"""


def build_prompt(
    *,
    component_rel: str,
    page: str,
    goal: str,
    source_name: str,
    screenshot_name: str | None,
    rendered_html_name: str | None,
    design_system_summary: str | None,
    copied_context: list[str],
) -> str:
    upload_lines = [f"- `{source_name}`: current React component source"]
    if screenshot_name:
        upload_lines.append(f"- `{screenshot_name}`: current UI screenshot")
    if rendered_html_name:
        upload_lines.append(f"- `{rendered_html_name}`: optional rendered DOM snapshot")
    if design_system_summary:
        upload_lines.append(f"- `{design_system_summary}`: stable repo design-system summary")
    upload_lines.extend(f"- `{item}`: supporting context" for item in copied_context)
    uploads = "\n".join(upload_lines)
    style_instruction = (
        "Use the selected Claude Design system for this repo. "
        "The attached design-system-summary.md is the source-of-truth style summary."
        if design_system_summary
        else "Use the existing project style and component constraints implied by the source and screenshots."
    )

    return f"""You are redesigning a React frontend component for a real codebase.

Source component: `{component_rel}`
Page/context: {page or "Unknown"}
Goal: {goal or "Improve usability and visual clarity without changing business behavior."}

Uploaded materials:
{uploads}

Style context:
{style_instruction}

Please produce a focused design fragment for this component.

Requirements:
- Preserve the existing information structure and business fields.
- Do not invent new backend/API fields.
- Cover desktop and mobile behavior when relevant.
- Follow the selected project Design system and attached style summary when provided.
- Output a usable HTML design fragment/prototype.
- Provide or export a PNG visual reference.
- Include short implementation notes mapping the design back to the existing component structure.

The HTML is for design reference only. Production implementation will be done separately in the React codebase.
"""


def build_implementation_notes(component_rel: str) -> str:
    return f"""# Implementation Notes

- Implement the final design in `{component_rel}` or the nearest owning component.
- Preserve existing props, API contracts, routing, and data flow.
- Prefer existing components, tokens, Tailwind classes, and local styling conventions.
- Do not copy `design.html` directly into `src/`.
- Add or update tests only where the redesign changes observable behavior or layout-critical states.
- Run the repo's relevant lint, typecheck, and test commands before completion.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Frontend repository root. Defaults to current directory.")
    parser.add_argument("--component", required=True, help="React component path, relative to repo or absolute.")
    parser.add_argument("--name", help="Design directory name. Defaults to component-name-redesign.")
    parser.add_argument("--out-root", default="docs/design", help="Output root relative to repo.")
    parser.add_argument("--screenshot", help="Optional current UI screenshot.")
    parser.add_argument("--rendered-html", help="Optional rendered DOM/HTML snapshot.")
    parser.add_argument("--page", default="", help="Page or feature context.")
    parser.add_argument("--goal", default="", help="Design goal.")
    parser.add_argument("--context-file", action="append", default=[], help="Supporting text source/style file. Repeatable.")
    parser.add_argument("--force", action="store_true", help="Allow writing into an existing output directory.")
    args = parser.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    if not repo.exists() or not repo.is_dir():
        raise SystemExit(f"repo not found: {repo}")

    component = resolve_inside_repo(repo, args.component)
    if not component.exists() or not component.is_file():
        raise SystemExit(f"component not found: {component}")

    name = args.name or slug_from_component(component)
    out_root = resolve_inside_repo(repo, args.out_root)
    out_dir = out_root / name
    if out_dir.exists() and not args.force:
        raise SystemExit(f"output directory already exists: {out_dir} (use --force to update)")
    out_dir.mkdir(parents=True, exist_ok=True)

    source_name = "source.tsx" if component.suffix == ".tsx" else f"source{component.suffix}"
    shutil.copy2(component, out_dir / source_name)

    screenshot_name: str | None = None
    if args.screenshot:
        screenshot = Path(args.screenshot).expanduser().resolve()
        if not screenshot.exists() or not screenshot.is_file():
            raise SystemExit(f"screenshot not found: {screenshot}")
        screenshot_name = "source.png" if screenshot.suffix.lower() == ".png" else f"source{screenshot.suffix.lower()}"
        shutil.copy2(screenshot, out_dir / screenshot_name)

    rendered_html_name: str | None = None
    if args.rendered_html:
        rendered_html = Path(args.rendered_html).expanduser().resolve()
        if not rendered_html.exists() or not rendered_html.is_file():
            raise SystemExit(f"rendered HTML not found: {rendered_html}")
        if rendered_html.suffix.lower() not in {".html", ".htm"}:
            raise SystemExit(f"rendered HTML must be .html or .htm: {rendered_html}")
        rendered_html_name = "rendered.html"
        shutil.copy2(rendered_html, out_dir / rendered_html_name)

    design_system_summary = copy_design_system_summary(repo, out_dir)
    copied_context = copy_optional_context(repo, out_dir, args.context_file)
    component_rel = relative_to_repo(repo, component)

    write_text(
        out_dir / "brief.md",
        build_brief(
            component_rel=component_rel,
            page=args.page,
            goal=args.goal,
            out_dir_name=name,
            source_name=source_name,
            screenshot_name=screenshot_name,
            rendered_html_name=rendered_html_name,
            design_system_summary=design_system_summary,
            copied_context=copied_context,
        ),
    )
    write_text(
        out_dir / "claude-design-prompt.md",
        build_prompt(
            component_rel=component_rel,
            page=args.page,
            goal=args.goal,
            source_name=source_name,
            screenshot_name=screenshot_name,
            rendered_html_name=rendered_html_name,
            design_system_summary=design_system_summary,
            copied_context=copied_context,
        ),
    )
    write_text(out_dir / "implementation-notes.md", build_implementation_notes(component_rel))

    print(f"created {out_dir}")
    print("next: paste claude-design-prompt.md into Claude Design and upload the generated artifacts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
