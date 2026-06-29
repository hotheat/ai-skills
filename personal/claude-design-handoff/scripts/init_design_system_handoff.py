#!/usr/bin/env python3
"""Prepare local records around Claude Code /design-sync for Claude Design."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


TEXT_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".css", ".scss", ".md", ".json", ".html", ".htm"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
TAILWIND_PATTERNS = (
    "tailwind.config.js",
    "tailwind.config.cjs",
    "tailwind.config.mjs",
    "tailwind.config.ts",
)


def resolve_repo_path(repo: Path, value: str) -> Path:
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


def copy_file(source: Path, target_dir: Path, *, allowed_extensions: set[str] | None = None) -> str:
    if not source.exists() or not source.is_file():
        raise SystemExit(f"file not found: {source}")
    if allowed_extensions is not None and source.suffix.lower() not in allowed_extensions:
        allowed = ", ".join(sorted(allowed_extensions))
        raise SystemExit(f"unsupported file extension for {source}; allowed: {allowed}")
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / source.name
    shutil.copy2(source, target)
    return target.name


def discover_tailwind(repo: Path) -> Path | None:
    for pattern in TAILWIND_PATTERNS:
        candidate = repo / pattern
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def build_summary_template() -> str:
    return """# Project Style Summary

Replace or refine this template after Claude Design syncs or reviews the project materials.
Keep it short enough to reuse in future component handoffs.

- Framework: React + TypeScript.
- Styling: describe Tailwind, CSS modules, global CSS, tokens, or component library.
- Layout: describe density, spacing, responsive behavior, and common page structure.
- Components: list common primitives such as cards, tabs, tables, badges, dialogs, and tooltips.
- Radius: describe standard border radius and whether pill-heavy UI is acceptable.
- Color: describe neutral surfaces, semantic colors, accent colors, and palettes to avoid.
- Typography: describe heading scale, body text, metadata text, and compact UI text.
- Data UX: describe whether the product is research, dashboard, workflow, or marketing oriented.
- States: loading, empty, error, selected, hover, focus, disabled.
- Mobile: describe stacking, navigation, density, and priority behavior.
- Implementation: Codex implements designs with existing components and tokens; Claude Design HTML is reference only.
"""


def build_brief(
    *,
    repo: Path,
    copied_package: str | None,
    copied_tailwind: str | None,
    global_css: list[str],
    token_files: list[str],
    components: list[str],
    screenshots: list[str],
) -> str:
    def lines(items: list[str]) -> str:
        return "\n".join(f"- `{item}`" for item in items) if items else "- None"

    package_line = f"- `{copied_package}`" if copied_package else "- Not found"
    tailwind_line = f"- `{copied_tailwind}`" if copied_tailwind else "- Not found"

    return f"""# Claude Design System Handoff

## Source Repo

- Repo: `{repo}`

## Purpose

Use these materials to document local style rules and support manual or fallback Claude Design setup. The primary Claude Design sync path is Claude Code `/design-sync`. This folder is not a component redesign artifact.

## Core Files

### package.json

{package_line}

### Tailwind config

{tailwind_line}

### Global CSS

{lines(global_css)}

### Tokens

{lines(token_files)}

### Representative Components

{lines(components)}

### Representative Screenshots

{lines(screenshots)}

## Expected Outcome

- Sync the project Design system with Claude Code `/design-sync`, or use these materials for manual fallback setup.
- Produce a concise 8-12 item Project Style Summary.
- Keep the style summary usable for future `prepare` handoffs.
"""


def build_sync_instructions(*, repo: Path, out_dir: Path) -> str:
    return f"""# Claude Design Sync

## Primary Sync

Run the actual Claude Design system sync from Claude Code:

```bash
cd {repo}
claude
/design-sync
```

If `/design-sync` is not available in Claude Code, run `/update`, exit, then start a new Claude Code session and retry `/design-sync`.

## Local Records

This directory records the local context used around the sync:

- `brief.md`: source files and representative materials collected for this setup.
- `design-system-summary.md`: style summary copy for this material bundle.
- `claude-design-system-prompt.md`: manual fallback prompt only.

After `/design-sync`, refine `docs/design/design-system-summary.md` in the repo from the synced Claude Design system. Future component handoffs can then reference the synced design system and this short summary instead of repeating global style rules.

## Validate Before Use

Create a small Claude Design test project that uses the synced design system. Check whether colors, typography, reusable components, spacing, and layout patterns match the source repo. If the organization setup exposes a Published toggle, publish only after the test project matches expectations.

## Fallback

Use `claude-design-system-prompt.md` and the collected files only when `/design-sync` is unavailable, blocked, or insufficient for the project.

Generated bundle: `{relative_to_repo(repo, out_dir)}`
"""


def build_prompt(
    *,
    copied_package: str | None,
    copied_tailwind: str | None,
    global_css: list[str],
    token_files: list[str],
    components: list[str],
    screenshots: list[str],
) -> str:
    def bullet(items: list[str]) -> str:
        return "\n".join(f"- `{item}`" for item in items) if items else "- None"

    package_line = f"- `{copied_package}`" if copied_package else "- Not available"
    tailwind_line = f"- `{copied_tailwind}`" if copied_tailwind else "- Not available"

    return f"""Use these frontend materials to review or manually update a Claude Design project Design system when `/design-sync` is unavailable or insufficient.

Uploaded materials:

package/framework:
{package_line}

Tailwind/config:
{tailwind_line}

Global CSS:
{bullet(global_css)}

Tokens:
{bullet(token_files)}

Representative components:
{bullet(components)}

Representative screenshots:
{bullet(screenshots)}

Task:
- Infer the project's reusable visual language, layout rules, density, typography, color usage, and state patterns.
- For the main sync path, use Claude Code `/design-sync` from the design-system or component-library repo.
- If manual fallback setup is needed, create or update the Claude Design system for this project from these materials.
- Generate an 8-12 item Project Style Summary that future component redesigns can reuse.
- Keep the summary concrete and implementation-aware.
- Do not create a specific component redesign in this step.

The React repo remains the implementation source of truth. Claude Design output is used as design reference; Codex will implement production changes later.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Frontend repository root. Defaults to current directory.")
    parser.add_argument("--out-dir", default="docs/design/design-system", help="Output directory, relative to repo or absolute.")
    parser.add_argument("--global-css", action="append", default=[], help="Global CSS file. Repeatable.")
    parser.add_argument("--token-file", action="append", default=[], help="Design token file. Repeatable.")
    parser.add_argument("--component", action="append", default=[], help="Representative component TSX/JSX/source file. Repeatable.")
    parser.add_argument("--screenshot", action="append", default=[], help="Representative page/component screenshot. Repeatable.")
    parser.add_argument("--package-json", help="Override package.json path.")
    parser.add_argument("--tailwind-config", help="Override tailwind config path.")
    parser.add_argument("--force", action="store_true", help="Allow writing into an existing output directory.")
    args = parser.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    if not repo.exists() or not repo.is_dir():
        raise SystemExit(f"repo not found: {repo}")

    out_dir = resolve_repo_path(repo, args.out_dir)
    if out_dir.exists() and not args.force:
        raise SystemExit(f"output directory already exists: {out_dir} (use --force to update)")
    out_dir.mkdir(parents=True, exist_ok=True)

    copied_package: str | None = None
    package_source = resolve_repo_path(repo, args.package_json) if args.package_json else repo / "package.json"
    if package_source.exists():
        copied_package = copy_file(package_source, out_dir, allowed_extensions={".json"})

    copied_tailwind: str | None = None
    tailwind_source = resolve_repo_path(repo, args.tailwind_config) if args.tailwind_config else discover_tailwind(repo)
    if tailwind_source and tailwind_source.exists():
        copied_tailwind = copy_file(tailwind_source, out_dir, allowed_extensions=TEXT_EXTENSIONS)

    css_dir = out_dir / "global-css"
    token_dir = out_dir / "tokens"
    components_dir = out_dir / "components"
    screenshots_dir = out_dir / "screenshots"

    global_css = [
        f"global-css/{copy_file(resolve_repo_path(repo, item), css_dir, allowed_extensions={'.css', '.scss'})}"
        for item in args.global_css
    ]
    token_files = [
        f"tokens/{copy_file(resolve_repo_path(repo, item), token_dir, allowed_extensions=TEXT_EXTENSIONS)}"
        for item in args.token_file
    ]
    components = [
        f"components/{copy_file(resolve_repo_path(repo, item), components_dir, allowed_extensions=TEXT_EXTENSIONS)}"
        for item in args.component
    ]
    screenshots = [
        f"screenshots/{copy_file(resolve_repo_path(repo, item), screenshots_dir, allowed_extensions=IMAGE_EXTENSIONS)}"
        for item in args.screenshot
    ]

    write_text(
        out_dir / "brief.md",
        build_brief(
            repo=repo,
            copied_package=copied_package,
            copied_tailwind=copied_tailwind,
            global_css=global_css,
            token_files=token_files,
            components=components,
            screenshots=screenshots,
        ),
    )
    write_text(
        out_dir / "claude-design-system-prompt.md",
        build_prompt(
            copied_package=copied_package,
            copied_tailwind=copied_tailwind,
            global_css=global_css,
            token_files=token_files,
            components=components,
            screenshots=screenshots,
        ),
    )
    write_text(out_dir / "design-sync.md", build_sync_instructions(repo=repo, out_dir=out_dir))

    summary_path = repo / "docs/design/design-system-summary.md"
    if not summary_path.exists():
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        write_text(summary_path, build_summary_template())
    shutil.copy2(summary_path, out_dir / "design-system-summary.md")

    print(f"created {out_dir}")
    print("next: run /design-sync in Claude Code for actual Claude Design sync")
    print(f"sync guide: {relative_to_repo(repo, out_dir / 'design-sync.md')}")
    print("fallback: use claude-design-system-prompt.md and collected materials for manual upload or review")
    print(f"style summary template: {relative_to_repo(repo, summary_path)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
