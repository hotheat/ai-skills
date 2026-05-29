#!/usr/bin/env python3
"""Generate a PPTD project from a compact JSON page plan.

This is a reusable scaffold for Kimi-style "template style + content reflow"
work. Agents should customize the generated pages after reading the actual
template and content decks.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
import shutil
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate PPTD pages from a JSON plan")
    parser.add_argument("--plan", required=True, help="JSON plan file")
    parser.add_argument("-o", "--output", required=True, help="Output PPTD project directory")
    parser.add_argument("--name", default="result", help="Main .pptd basename")
    parser.add_argument("--copy-images", action="append", default=[], help="Image file or directory to copy into result/images")
    return parser.parse_args()


def yaml_scalar(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if text.startswith("#"):
        return f'"{text}"'
    if all(c.isalnum() or c in "._/-:#" for c in text):
        return text
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def block(lines: list[str], indent: str, key: str, value: str) -> None:
    lines.append(f"{indent}{key}: |")
    value = value or ""
    for line in value.splitlines() or [""]:
        lines.append(f"{indent}  {line}")


def text_html(text: str) -> str:
    parts = [p.strip() for p in str(text or "").splitlines() if p.strip()]
    if not parts:
        return ""
    return "\n".join(f"<p>{html.escape(part)}</p>" for part in parts)


def text_el(element_id: str, bounds: list[float], text: str, font_size: int = 18, color: str = "#222222", align: str = "left", valign: str = "top", bold: bool = False) -> str:
    content = text_html(text)
    if bold:
        content = content.replace("<p>", "<p><strong>").replace("</p>", "</strong></p>")
    lines = [
        f"- elementId: {yaml_scalar(element_id)}",
        "  elementType: text",
        f"  bounds: [{', '.join(str(x) for x in bounds)}]",
        "  content:",
        f"    align: [{align}, {valign}]",
        f"    fontSize: {font_size}",
        "    fontFamily: Arial, Microsoft YaHei",
        f"    color: {yaml_scalar(color)}",
    ]
    block(lines, "    ", "text", content)
    return "\n".join(lines)


def shape_el(element_id: str, bounds: list[float], color: str, shape: str = "rect", opacity: float | None = None) -> str:
    lines = [
        f"- elementId: {yaml_scalar(element_id)}",
        "  elementType: shape",
        f"  bounds: [{', '.join(str(x) for x in bounds)}]",
        f"  shapeName: {shape}",
        "  fill:",
        "    type: solid",
        f"    color: {yaml_scalar(color)}",
    ]
    if opacity is not None:
        lines.insert(3, f"  opacity: {opacity}")
    return "\n".join(lines)


def image_el(element_id: str, bounds: list[float], src: str, fit: str = "contain", opacity: float | None = None) -> str:
    lines = [
        f"- elementId: {yaml_scalar(element_id)}",
        "  elementType: image",
        f"  bounds: [{', '.join(str(x) for x in bounds)}]",
    ]
    if opacity is not None:
        lines.append(f"  opacity: {opacity}")
    lines.extend([
        f"  src: {yaml_scalar(src)}",
        "  fit:",
        f"    mode: {fit}",
    ])
    return "\n".join(lines)


def title_bar(title: str, theme: dict[str, str], logo: str | None = None) -> list[str]:
    parts = [
        shape_el("title_bar", [0, 0, 1280, 78], theme.get("primary", "#244EB1")),
        text_el("page_title", [48, 14, 960, 48], title, 26, "#FFFFFF", "left", "middle", True),
    ]
    if logo:
        parts.append(image_el("logo", [1110, 16, 130, 48], logo, "contain"))
    return parts


def bullet_text(page: dict) -> str:
    if page.get("body"):
        return str(page["body"])
    bullets = page.get("bullets") or []
    return "\n".join(f"• {item}" for item in bullets)


def page_elements(page: dict, theme: dict[str, str], logo: str | None) -> list[str]:
    page_type = page.get("pageType", "standard")
    title = page.get("title", "")
    accent = theme.get("secondary", "#ED7D31")
    primary = theme.get("primary", "#244EB1")

    if page_type == "cover":
        parts = [
            shape_el("cover_bg", [0, 0, 1280, 720], "#FFFFFF"),
            shape_el("cover_bar", [0, 470, 1280, 80], primary),
            shape_el("accent_line", [96, 558, 520, 6], accent),
            text_el("cover_title", [96, 180, 900, 120], title, 38, primary, "left", "middle", True),
            text_el("cover_subtitle", [96, 315, 900, 80], page.get("subtitle", ""), 22, "#333333"),
        ]
        if logo:
            parts.append(image_el("logo", [1080, 28, 150, 58], logo, "contain"))
        return parts

    if page_type == "section":
        parts = [
            shape_el("section_bg", [0, 0, 1280, 720], "#FFFFFF"),
            shape_el("section_circle", [820, 80, 380, 380], primary, "ellipse", 0.12),
            text_el("section_number", [80, 165, 150, 90], str(page.get("number", "")), 58, accent, "left", "middle", True),
            text_el("section_title", [240, 180, 800, 90], title, 36, primary, "left", "middle", True),
            text_el("section_subtitle", [245, 280, 760, 80], page.get("subtitle", ""), 20, "#333333"),
        ]
        if logo:
            parts.append(image_el("logo", [1080, 28, 150, 58], logo, "contain"))
        return parts

    if page_type == "process":
        parts = title_bar(title, theme, logo)
        items = page.get("items") or []
        x_positions = [70, 365, 660, 955]
        for index, item in enumerate(items[:4]):
            x = x_positions[index]
            parts.append(shape_el(f"step{index+1}_card", [x, 170, 240, 310], "#F3F7FF"))
            parts.append(shape_el(f"step{index+1}_head", [x, 170, 240, 46], primary))
            parts.append(text_el(f"step{index+1}_title", [x + 16, 176, 208, 34], item.get("title", f"Step {index+1}"), 16, "#FFFFFF", "center", "middle", True))
            parts.append(text_el(f"step{index+1}_body", [x + 18, 238, 204, 210], item.get("text", ""), 14, "#222222"))
        return parts

    if page_type == "final":
        parts = [
            shape_el("final_bg", [0, 0, 1280, 720], "#FFFFFF"),
            shape_el("blue_bar", [70, 346, 1140, 36], primary),
            text_el("thankyou_text", [70, 342, 1140, 44], title or "Thank You!", 32, "#FFFFFF", "center", "middle", True),
        ]
        if logo:
            parts.append(image_el("logo", [1080, 28, 150, 58], logo, "contain"))
        return parts

    parts = title_bar(title, theme, logo)
    parts.append(shape_el("accent_line", [48, 96, 260, 5], accent))
    parts.append(text_el("content_text", [72, 130, 1136, 520], bullet_text(page), int(page.get("fontSize", 18)), "#222222"))
    if page.get("image"):
        parts.append(image_el("content_image", page.get("imageBounds", [720, 170, 430, 300]), page["image"], "contain"))
    return parts


def copy_images(paths: list[str], images_dir: Path) -> None:
    for raw in paths:
        src = Path(raw).expanduser()
        if not src.exists():
            print(f"Warning: image source not found: {src}", file=sys.stderr)
            continue
        if src.is_dir():
            for child in src.iterdir():
                if child.is_file():
                    shutil.copy2(child, images_dir / child.name)
        else:
            shutil.copy2(src, images_dir / src.name)


def main() -> int:
    args = parse_args()
    plan_path = Path(args.plan).expanduser().resolve()
    out_dir = Path(args.output).expanduser().resolve()
    pages_dir = out_dir / "pages"
    images_dir = out_dir / "images"
    pages_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    copy_images(args.copy_images, images_dir)

    size = plan.get("size", [1280, 720])
    theme = {
        "primary": "#244EB1",
        "secondary": "#ED7D31",
        "dark": "#000000",
        "light": "#FFFFFF",
        **(plan.get("theme") or {}),
    }
    logo = plan.get("logo")
    page_refs = []
    for index, page in enumerate(plan.get("pages", []), 1):
        page_name = f"page{index}.page"
        page_refs.append(f"pages/{page_name}")
        lines = [f"pageType: {page.get('pageType', 'standard')}", "elements:"]
        lines.extend(page_elements(page, theme, logo))
        (pages_dir / page_name).write_text("\n".join(lines) + "\n", encoding="utf-8")

    pptd = [
        f"size: [{size[0]}, {size[1]}]",
        "theme:",
        "  colors:",
    ]
    for key, value in theme.items():
        pptd.append(f"    {key}: {yaml_scalar(value)}")
    pptd.append("pages:")
    pptd.extend(f"- {ref}" for ref in page_refs)
    pptd_path = out_dir / f"{args.name}.pptd"
    pptd_path.write_text("\n".join(pptd) + "\n", encoding="utf-8")
    print(f"Created: {pptd_path}")
    print(f"Pages: {len(page_refs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
