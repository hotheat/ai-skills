#!/usr/bin/env python3
"""Static checker for PPTD-like projects used by ppt-template-style-reflow."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path
import re
import sys
from typing import Iterable


@dataclass
class Element:
    page: str
    element_id: str = "(unknown)"
    element_type: str = "(unknown)"
    bounds: list[float] | None = None
    src: str | None = None
    font_size: float | None = None
    text: str = ""
    start_line: int = 0


@dataclass
class Issue:
    severity: str
    code: str
    page: str
    element: str
    message: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check a PPTD-like project")
    parser.add_argument("pptd", help="Path to main .pptd file")
    parser.add_argument("--strict", action="store_true", help="Exit nonzero on warnings")
    return parser.parse_args()


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] in "'\"" and value[-1] == value[0]:
        return value[1:-1]
    return value


def parse_size(text: str) -> tuple[float, float]:
    match = re.search(r"^\s*size:\s*\[([^\]]+)\]", text, re.M)
    if not match:
        return (1280.0, 720.0)
    nums = [float(x.strip()) for x in match.group(1).split(",")[:2]]
    return (nums[0], nums[1])


def parse_pages(text: str) -> list[str]:
    pages: list[str] = []
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


def parse_page(path: Path, page_ref: str) -> list[Element]:
    elements: list[Element] = []
    current: Element | None = None
    collecting_text = False
    text_indent = 0
    text_lines: list[str] = []

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    for line_number, line in enumerate(lines, 1):
        if collecting_text:
            indent = len(line) - len(line.lstrip(" "))
            if line.strip() and indent > text_indent:
                text_lines.append(line[text_indent + 2 :] if len(line) >= text_indent + 2 else line.strip())
                continue
            if current is not None:
                current.text += "\n".join(text_lines)
            collecting_text = False
            text_lines = []

        match = re.match(r"^\s*-\s+elementId:\s*(.+?)\s*$", line)
        if match:
            current = Element(page=page_ref, element_id=strip_quotes(match.group(1)), start_line=line_number)
            elements.append(current)
            continue
        if current is None:
            continue

        match = re.match(r"^\s*elementType:\s*(.+?)\s*$", line)
        if match:
            current.element_type = strip_quotes(match.group(1))
            continue
        match = re.match(r"^\s*bounds:\s*(.+?)\s*$", line)
        if match:
            current.bounds = parse_bounds(match.group(1))
            continue
        match = re.match(r"^\s*src:\s*(.+?)\s*$", line)
        if match:
            current.src = strip_quotes(match.group(1))
            continue
        match = re.match(r"^\s*fontSize:\s*([0-9.]+)", line)
        if match:
            current.font_size = float(match.group(1))
            continue
        match = re.match(r"^(\s*)text:\s*\|\s*$", line)
        if match:
            collecting_text = True
            text_indent = len(match.group(1))
            text_lines = []
            continue
        match = re.match(r"^\s*text:\s*(.+?)\s*$", line)
        if match:
            current.text += strip_quotes(match.group(1))

    if collecting_text and current is not None:
        current.text += "\n".join(text_lines)

    return elements


def resolve_src(project_dir: Path, src: str) -> Path:
    src = src.strip()
    p = Path(src)
    if p.is_absolute():
        return p
    return project_dir / p


def visible_text_length(text: str) -> int:
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return len(text)


def text_capacity(bounds: list[float], font_size: float) -> int:
    _, _, width, height = bounds
    avg_char_width = max(font_size * 0.52, 1)
    line_height = max(font_size * 1.25, 1)
    chars_per_line = max(int(width / avg_char_width), 1)
    lines = max(int(height / line_height), 1)
    return chars_per_line * lines


def overlap(a: list[float], b: list[float]) -> float:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    x = max(0.0, min(ax + aw, bx + bw) - max(ax, bx))
    y = max(0.0, min(ay + ah, by + bh) - max(ay, by))
    return x * y


def check_elements(project_dir: Path, slide_size: tuple[float, float], elements: list[Element]) -> list[Issue]:
    issues: list[Issue] = []
    slide_w, slide_h = slide_size
    for el in elements:
        loc = f"{el.element_type}#{el.element_id}"
        if el.bounds is None:
            issues.append(Issue("warning", "MissingBoundsWarning", el.page, loc, "Element has no bounds"))
            continue
        x, y, w, h = el.bounds
        if w <= 0 or h <= 0:
            issues.append(Issue("error", "InvalidBoundsError", el.page, loc, f"Non-positive bounds {el.bounds}"))
        if x < 0:
            issues.append(Issue("warning", "BoundsOutsideWarning", el.page, loc, f"Element extends outside slide bounds (left) x={x}"))
        if y < 0:
            issues.append(Issue("warning", "BoundsOutsideWarning", el.page, loc, f"Element extends outside slide bounds (top) y={y}"))
        if x + w > slide_w:
            issues.append(Issue("warning", "BoundsOutsideWarning", el.page, loc, f"Element extends outside slide bounds (right) x+width({x+w:.2f}) > slideWidth({slide_w:g})"))
        if y + h > slide_h:
            issues.append(Issue("warning", "BoundsOutsideWarning", el.page, loc, f"Element extends outside slide bounds (bottom) y+height({y+h:.2f}) > slideHeight({slide_h:g})"))

        if el.element_type == "image":
            if not el.src:
                issues.append(Issue("error", "SrcMissingError", el.page, loc, "Image element has no src"))
            elif not resolve_src(project_dir, el.src).exists():
                issues.append(Issue("warning", "SrcNotFoundWarning", el.page, loc, f"Image source file not found (src='{el.src}')"))

        if el.element_type == "text":
            font_size = el.font_size or 18.0
            length = visible_text_length(el.text)
            capacity = text_capacity(el.bounds, font_size)
            if capacity and length > capacity:
                overflow = (length / capacity - 1) * 100
                issues.append(Issue("warning", "TextOverflowWarning", el.page, loc, f"Text likely overflows by {overflow:.1f}% ({length} chars > capacity {capacity})"))
            elif capacity and length > 0 and length < capacity * 0.08 and h > font_size * 4:
                issues.append(Issue("warning", "TextUnderfillWarning", el.page, loc, f"Text box may be too large ({length} chars for capacity {capacity})"))

    ordered = list(elements)
    for i, lower in enumerate(ordered):
        if lower.bounds is None:
            continue
        for upper in ordered[i + 1 :]:
            if upper.bounds is None:
                continue
            if lower.element_type != "text" and upper.element_type != "text":
                continue
            area = overlap(lower.bounds, upper.bounds)
            if area <= 0:
                continue
            text_el = lower if lower.element_type == "text" else upper if upper.element_type == "text" else None
            if text_el is None:
                continue
            text_area = max(text_el.bounds[2] * text_el.bounds[3], 1)
            ratio = area / text_area
            text_is_above_non_text = upper.element_type == "text" and lower.element_type != "text"
            if ratio > 0.35 and not text_is_above_non_text:
                issues.append(Issue("warning", "TextOcclusionWarning", text_el.page, f"text#{text_el.element_id}", f"Likely overlaps another element by {ratio*100:.1f}% of text bounds"))
            elif ratio > 0.05:
                issues.append(Issue("warning", "TextDriftWarning", text_el.page, f"text#{text_el.element_id}", f"Text intersects another element by {ratio*100:.1f}% of text bounds"))
    return issues


def print_issues(title: str, issues: Iterable[Issue]) -> None:
    issues = list(issues)
    if not issues:
        return
    print(f"\n{title} ({len(issues)}):")
    for issue in issues:
        print(f"  [{issue.code}] {issue.page} <{issue.element}> {issue.message}")


def main() -> int:
    args = parse_args()
    pptd_path = Path(args.pptd).expanduser().resolve()
    if not pptd_path.exists():
        print(f"PPTD file not found: {pptd_path}", file=sys.stderr)
        return 2

    project_dir = pptd_path.parent
    text = pptd_path.read_text(encoding="utf-8", errors="replace")
    slide_size = parse_size(text)
    pages = parse_pages(text)

    issues: list[Issue] = []
    if not pages:
        issues.append(Issue("error", "NoPagesError", str(pptd_path), "pptd", "No pages listed in main PPTD"))

    all_elements: list[Element] = []
    for page_ref in pages:
        page_path = project_dir / page_ref
        if not page_path.exists():
            issues.append(Issue("error", "PageNotFoundError", page_ref, "page", "Referenced page file not found"))
            continue
        elements = parse_page(page_path, page_ref)
        if not elements:
            issues.append(Issue("warning", "EmptyPageWarning", page_ref, "page", "No elements parsed from page"))
        all_elements.extend(elements)
        issues.extend(check_elements(project_dir, slide_size, elements))

    errors = [issue for issue in issues if issue.severity == "error"]
    warnings = [issue for issue in issues if issue.severity != "error"]

    print(f"Checking {pptd_path}...")
    print(f"Slides: {len(pages)}")
    print(f"Elements: {len(all_elements)}")
    print_issues("Repair Issues", errors)
    print_issues("Warnings", warnings)
    print(f"\nSummary: {len(errors)} error(s), {len(warnings)} warning(s)")

    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
