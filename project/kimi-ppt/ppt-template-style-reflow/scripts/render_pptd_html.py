#!/usr/bin/env python3
"""Render a PPTD-like project to an HTML preview."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import shutil
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render PPTD to HTML preview")
    parser.add_argument("pptd", help="Path to main .pptd file")
    parser.add_argument("-o", "--output", required=True, help="Output preview directory")
    return parser.parse_args()


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] in "'\"" and value[-1] == value[0]:
        return value[1:-1]
    return value


def parse_size(text: str) -> tuple[int, int]:
    match = re.search(r"^\s*size:\s*\[([^\]]+)\]", text, re.M)
    if not match:
        return (1280, 720)
    nums = [float(x.strip()) for x in match.group(1).split(",")[:2]]
    return (int(nums[0]), int(nums[1]))


def parse_pages(text: str) -> list[str]:
    pages = []
    in_pages = False
    for line in text.splitlines():
        if re.match(r"^\s*pages:\s*$", line):
            in_pages = True
            continue
        if in_pages:
            match = re.match(r"^\s*-\s+(.+?)\s*$", line)
            if match:
                pages.append(strip_quotes(match.group(1)))
            elif line and not line.startswith((" ", "\t")):
                in_pages = False
    return pages


def parse_bounds(value: str) -> list[float] | None:
    match = re.search(r"\[([^\]]+)\]", value)
    if not match:
        return None
    try:
        return [float(x.strip()) for x in match.group(1).split(",")[:4]]
    except ValueError:
        return None


def parse_page(path: Path) -> list[dict[str, object]]:
    elements: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    context = ""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        match = re.match(r"^\s*-\s+elementId:\s*(.+?)\s*$", line)
        if match:
            current = {"elementId": strip_quotes(match.group(1))}
            elements.append(current)
            context = ""
            i += 1
            continue
        if current is None:
            i += 1
            continue
        match = re.match(r"^\s*elementType:\s*(.+?)\s*$", line)
        if match:
            current["elementType"] = strip_quotes(match.group(1))
            context = ""
        elif (match := re.match(r"^\s*bounds:\s*(.+?)\s*$", line)):
            current["bounds"] = parse_bounds(match.group(1))
            context = ""
        elif (match := re.match(r"^\s*src:\s*(.+?)\s*$", line)):
            current["src"] = strip_quotes(match.group(1))
            context = ""
        elif (match := re.match(r"^\s*opacity:\s*([0-9.]+)", line)):
            current["opacity"] = float(match.group(1))
        elif re.match(r"^\s*fill:\s*$", line):
            context = "fill"
        elif re.match(r"^\s*content:\s*$", line):
            context = "content"
        elif (match := re.match(r"^\s*color:\s*(.+?)\s*$", line)):
            current["contentColor" if context == "content" else "fillColor"] = strip_quotes(match.group(1))
        elif (match := re.match(r"^\s*fontSize:\s*([0-9.]+)", line)):
            current["fontSize"] = float(match.group(1))
        elif (match := re.match(r"^\s*fontFamily:\s*(.+?)\s*$", line)):
            current["fontFamily"] = strip_quotes(match.group(1))
        elif (match := re.match(r"^\s*align:\s*\[([^\]]+)\]", line)):
            current["align"] = [x.strip() for x in match.group(1).split(",")]
        elif re.match(r"^\s*text:\s*\|\s*$", line):
            indent = len(line) - len(line.lstrip(" "))
            text_lines = []
            i += 1
            while i < len(lines):
                next_line = lines[i]
                next_indent = len(next_line) - len(next_line.lstrip(" "))
                if next_line.strip() and next_indent <= indent:
                    i -= 1
                    break
                text_lines.append(next_line[indent + 2 :] if len(next_line) >= indent + 2 else "")
                i += 1
            current["text"] = "\n".join(text_lines)
        i += 1
    return elements


def resolve_asset(project_dir: Path, out_dir: Path, src: str) -> str:
    source = Path(src)
    if not source.is_absolute():
        source = project_dir / src
    if not source.exists():
        return src
    assets = out_dir / "assets"
    assets.mkdir(exist_ok=True)
    dest = assets / source.name
    if not dest.exists():
        shutil.copy2(source, dest)
    return f"assets/{dest.name}"


def style(bounds: list[float], extra: str = "") -> str:
    x, y, w, h = bounds
    return f"left:{x}px;top:{y}px;width:{w}px;height:{h}px;{extra}"


def render_element(el: dict[str, object], project_dir: Path, out_dir: Path) -> str:
    bounds = el.get("bounds") or [0, 0, 0, 0]
    opacity = el.get("opacity")
    opacity_css = f"opacity:{opacity};" if opacity is not None else ""
    etype = el.get("elementType")
    if etype == "image":
        src = resolve_asset(project_dir, out_dir, str(el.get("src", "")))
        return f'<img class="el image" src="{src}" style="{style(bounds, opacity_css + "object-fit:contain;")}"/>'
    if etype == "shape":
        color = el.get("fillColor", "#FFFFFF")
        radius = "border-radius:50%;" if str(el.get("shapeName", "")) == "ellipse" else ""
        return f'<div class="el shape" style="{style(bounds, opacity_css + f"background:{color};" + radius)}"></div>'
    if etype == "text":
        color = el.get("contentColor", "#111111")
        font_size = el.get("fontSize", 18)
        family = el.get("fontFamily", "Arial, sans-serif")
        align = el.get("align") or ["left", "top"]
        justify = {"center": "center", "right": "flex-end"}.get(align[0], "flex-start")
        valign = {"middle": "center", "bottom": "flex-end"}.get(align[1] if len(align) > 1 else "top", "flex-start")
        text = str(el.get("text", ""))
        css = f"color:{color};font-size:{font_size}px;font-family:{family};display:flex;justify-content:{justify};align-items:{valign};overflow:hidden;"
        return f'<div class="el text" style="{style(bounds, css)}">{text}</div>'
    return ""


def main() -> int:
    args = parse_args()
    pptd_path = Path(args.pptd).expanduser().resolve()
    out_dir = Path(args.output).expanduser().resolve()
    if not pptd_path.exists():
        print(f"PPTD file not found: {pptd_path}", file=sys.stderr)
        return 2
    out_dir.mkdir(parents=True, exist_ok=True)
    project_dir = pptd_path.parent
    text = pptd_path.read_text(encoding="utf-8", errors="replace")
    width, height = parse_size(text)
    pages = parse_pages(text)

    body = []
    for index, page_ref in enumerate(pages, 1):
        page_path = project_dir / page_ref
        elements = parse_page(page_path) if page_path.exists() else []
        rendered = "\n".join(render_element(el, project_dir, out_dir) for el in elements)
        body.append(f'<section class="slide"><div class="label">Page {index}: {page_ref}</div>{rendered}</section>')

    html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<title>{pptd_path.name} preview</title>
<style>
body {{ margin:0; background:#202124; font-family:Arial, sans-serif; }}
.slide {{ position:relative; width:{width}px; height:{height}px; margin:28px auto; background:white; box-shadow:0 8px 30px rgba(0,0,0,.35); overflow:hidden; }}
.label {{ position:absolute; left:0; top:0; z-index:9999; padding:3px 8px; background:rgba(0,0,0,.55); color:white; font-size:11px; }}
.el {{ position:absolute; box-sizing:border-box; }}
.text p {{ margin:0 0 .35em 0; }}
.text ul {{ margin:0; }}
</style>
</head>
<body>
{''.join(body)}
</body>
</html>
"""
    (out_dir / "index.html").write_text(html, encoding="utf-8")
    print(f"Created: {out_dir / 'index.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
