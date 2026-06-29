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
    used_names: set[str] = set()
    for item in context_files:
        source = resolve_inside_repo(repo, item)
        if not source.exists() or not source.is_file():
            raise SystemExit(f"context file not found: {source}")
        if source.suffix.lower() not in TEXT_EXTENSIONS:
            raise SystemExit(f"refuse non-text context file: {source}")
        target = context_dir / unique_attachment_name(source, used_names)
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


def unique_attachment_name(source: Path, used_names: set[str]) -> str:
    candidate = source.name
    stem = source.stem or "attachment"
    suffix = source.suffix
    counter = 2
    while candidate in used_names:
        candidate = f"{stem}-{counter}{suffix}"
        counter += 1
    used_names.add(candidate)
    return candidate


def copy_attachments(repo: Path, out_dir: Path, attachments: list[str]) -> list[dict[str, str]]:
    copied: list[dict[str, str]] = []
    if not attachments:
        return copied

    attachments_dir = out_dir / "attachments"
    attachments_dir.mkdir(exist_ok=True)
    used_names: set[str] = set()
    for item in attachments:
        source = resolve_inside_repo(repo, item)
        if not source.exists() or not source.is_file():
            raise SystemExit(f"attachment not found: {source}")
        target = attachments_dir / unique_attachment_name(source, used_names)
        shutil.copy2(source, target)
        copied.append(
            {
                "path": target.relative_to(out_dir).as_posix(),
                "source": relative_to_repo(repo, source),
            }
        )

    manifest_lines = ["# Attachments", ""]
    manifest_lines.extend(f"- `{item['path']}` copied from `{item['source']}`" for item in copied)
    write_text(attachments_dir / "manifest.md", "\n".join(manifest_lines))
    return copied


def build_brief(
    *,
    component_rel: str,
    page: str,
    goal: str,
    layout: str,
    content: str,
    audience: str,
    viewports: list[str],
    out_dir_name: str,
    source_name: str,
    screenshot_name: str | None,
    rendered_html_name: str | None,
    design_system_summary: str | None,
    copied_context: list[str],
    copied_attachments: list[dict[str, str]],
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
    if copied_attachments:
        artifacts.append("- `attachments/`: upload-ready copied assets and manifest")

    context_items = list(copied_context)
    if design_system_summary:
        context_items.insert(0, design_system_summary)
    context_lines = "\n".join(f"- `{item}`" for item in context_items) or "- None"
    attachment_lines = "\n".join(
        f"- `{item['path']}` copied from `{item['source']}`" for item in copied_attachments
    ) or "- None"
    artifacts_text = "\n".join(artifacts)

    return f"""# {out_dir_name}

## Source

- Component: `{component_rel}`
- Page: {page or "Unknown"}
- Audience: {audience or "Unknown"}
- Viewport focus: {", ".join(viewports) if viewports else "Not specified"}

## Goal

{goal or "Redesign this component while preserving existing behavior."}

## Layout Intent

{layout or "Preserve the current information hierarchy unless the goal requires a clearer structure."}

## Content Scope

{content or "Use only fields and content visible in the current component, screenshots, source, or user brief."}

## Constraints

- Preserve existing props and API/data contracts.
- Do not change backend behavior.
- Prefer existing components, tokens, Tailwind classes, and local style conventions.
- Follow `docs/design/design-system-summary.md` when present; in Claude Design, prefer selecting the saved project Design system instead of repeating style rules.
- Keep the Claude Design prompt concise and focused on design direction.
- Ask for alternatives only when exploration is useful or requested.
- Treat Claude Design HTML as reference only; do not copy it directly into `src/`.

## Supporting Context

{context_lines}

## Upload-Ready Attachments

{attachment_lines}

## Design Artifacts

{artifacts_text}

## Implementation Notes

Implement from `design.png` for visual direction and `design.html` for layout intent. Map the design back to existing React component boundaries before editing. Keep production code idiomatic to this repo.
"""


def build_prompt(
    *,
    component_rel: str,
    page: str,
    goal: str,
    layout: str,
    content: str,
    audience: str,
    viewports: list[str],
    variations: int,
    source_name: str,
    screenshot_name: str | None,
    rendered_html_name: str | None,
    design_system_summary: str | None,
    copied_context: list[str],
    copied_attachments: list[dict[str, str]],
) -> str:
    upload_lines = [f"- `{source_name}`：当前 React 组件源码"]
    if screenshot_name:
        upload_lines.append(f"- `{screenshot_name}`：当前界面截图")
    if rendered_html_name:
        upload_lines.append(f"- `{rendered_html_name}`：当前 DOM/HTML 渲染快照")
    if design_system_summary:
        upload_lines.append(f"- `{design_system_summary}`：项目设计系统摘要")
    upload_lines.extend(f"- `{item}`：补充上下文" for item in copied_context)
    upload_lines.extend(
        f"- `{item['path']}`：已打包上传素材，来源 `{item['source']}`" for item in copied_attachments
    )
    uploads = "\n".join(upload_lines)
    style_instruction = (
        "请使用当前项目已选择的 Claude Design system。附带的 design-system-summary.md 可作为简短风格参考。"
        if design_system_summary
        else "请根据源码、截图和素材中体现的现有项目风格进行设计。"
    )
    design_need_lines = [
        f"- 源组件：`{component_rel}`",
        f"- 页面/场景：{page or '未指定'}",
        f"- 目标：{goal or '在不改变业务行为的前提下，提升可用性和视觉清晰度。'}",
    ]
    if audience:
        design_need_lines.append(f"- 目标用户：{audience}")
    if layout:
        design_need_lines.append(f"- 布局想法：{layout}")
    if content:
        design_need_lines.append(f"- 内容示例：{content}")
    if viewports:
        design_need_lines.append(f"- 视口重点：{', '.join(viewports)}")
    design_need = "\n".join(design_need_lines)
    variation_note = (
        f"请给出 {variations} 个视觉方向。"
        if variations
        else "如果某个方向明显更好，一个完整方案就够了；只有在有必要时再给多个备选方向。"
    )

    return f"""# Claude Design 提示词

请为这个 React 前端组件设计一个更强的视觉方向。

上传素材只作为示例和上下文，不要求严格照搬布局。重点探索构图、信息层级、间距、颜色、组件处理方式和整体产品气质。

## 素材

{uploads}

## 设计需求

{design_need}

## 风格上下文

{style_instruction}

## 设计重点

- 保留组件可识别的用途和产品场景。
- 内容以上传源码、截图、素材和 brief 为准。
- 在项目风格内自由探索视觉处理。
- 如果源码或风格摘要中能看到明确的 design-system 组件，请优先沿用这些组件名和风格。
- {variation_note}

## 边界

- 不要虚构新的后端/API 数据。
- 保留上传素材或用户 brief 中明确写出的硬性约束。
- HTML 只作为设计参考，后续会在真实 React 代码中实现。

## 输出

请输出一个独立的 HTML/CSS 设计概念，并用简短说明解释设计方向。
"""


def build_implementation_notes(component_rel: str) -> str:
    return f"""# Implementation Notes

- Implement the final design in `{component_rel}` or the nearest owning component.
- Preserve existing props, API contracts, routing, and data flow.
- Prefer existing components, tokens, Tailwind classes, and local styling conventions.
- Map `design.html` sections back to existing component boundaries before editing.
- Treat ungrounded text, data, and interactions in the design as suggestions, not requirements.
- Do not copy `design.html` directly into `src/`.
- Add or update tests only where the redesign changes observable behavior or layout-critical states.
- When the app can run locally, verify key desktop/mobile states after implementation.
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
    parser.add_argument("--layout", default="", help="Desired layout or information hierarchy.")
    parser.add_argument("--content", default="", help="Content and fields that must appear in the design.")
    parser.add_argument("--audience", default="", help="Target user or reviewer audience.")
    parser.add_argument("--viewport", action="append", default=[], help="Target viewport such as desktop, tablet, or mobile. Repeatable.")
    parser.add_argument("--variations", type=int, default=0, help="Number of layout alternatives to request before finalizing.")
    parser.add_argument("--context-file", action="append", default=[], help="Supporting text source/style file. Repeatable.")
    parser.add_argument("--attachment", action="append", default=[], help="Upload-ready asset to copy into attachments/. Repeatable.")
    parser.add_argument("--force", action="store_true", help="Allow writing into an existing output directory.")
    args = parser.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    if not repo.exists() or not repo.is_dir():
        raise SystemExit(f"repo not found: {repo}")
    if args.variations < 0:
        raise SystemExit("--variations must be 0 or greater")

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
        screenshot = resolve_inside_repo(repo, args.screenshot)
        if not screenshot.exists() or not screenshot.is_file():
            raise SystemExit(f"screenshot not found: {screenshot}")
        screenshot_name = "source.png" if screenshot.suffix.lower() == ".png" else f"source{screenshot.suffix.lower()}"
        shutil.copy2(screenshot, out_dir / screenshot_name)

    rendered_html_name: str | None = None
    if args.rendered_html:
        rendered_html = resolve_inside_repo(repo, args.rendered_html)
        if not rendered_html.exists() or not rendered_html.is_file():
            raise SystemExit(f"rendered HTML not found: {rendered_html}")
        if rendered_html.suffix.lower() not in {".html", ".htm"}:
            raise SystemExit(f"rendered HTML must be .html or .htm: {rendered_html}")
        rendered_html_name = "rendered.html"
        shutil.copy2(rendered_html, out_dir / rendered_html_name)

    design_system_summary = copy_design_system_summary(repo, out_dir)
    copied_context = copy_optional_context(repo, out_dir, args.context_file)
    copied_attachments = copy_attachments(repo, out_dir, args.attachment)
    component_rel = relative_to_repo(repo, component)

    write_text(
        out_dir / "brief.md",
        build_brief(
            component_rel=component_rel,
            page=args.page,
            goal=args.goal,
            layout=args.layout,
            content=args.content,
            audience=args.audience,
            viewports=args.viewport,
            out_dir_name=name,
            source_name=source_name,
            screenshot_name=screenshot_name,
            rendered_html_name=rendered_html_name,
            design_system_summary=design_system_summary,
            copied_context=copied_context,
            copied_attachments=copied_attachments,
        ),
    )
    write_text(
        out_dir / "claude-design-prompt.md",
        build_prompt(
            component_rel=component_rel,
            page=args.page,
            goal=args.goal,
            layout=args.layout,
            content=args.content,
            audience=args.audience,
            viewports=args.viewport,
            variations=args.variations,
            source_name=source_name,
            screenshot_name=screenshot_name,
            rendered_html_name=rendered_html_name,
            design_system_summary=design_system_summary,
            copied_context=copied_context,
            copied_attachments=copied_attachments,
        ),
    )
    write_text(out_dir / "implementation-notes.md", build_implementation_notes(component_rel))

    print(f"created {out_dir}")
    if copied_attachments:
        print("attachments: upload files under attachments/ along with claude-design-prompt.md")
    print("next: select the synced Claude Design system, paste claude-design-prompt.md, and upload the generated artifacts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
