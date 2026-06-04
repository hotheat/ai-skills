#!/usr/bin/env python3
"""Convert a PPTX into a lightweight PPTD-like project.

This is a baseline extractor for template-style reflow. It preserves enough
structure for inspection and regeneration: slide size, page order, text boxes,
images, basic shape bounds, and simple colors. It is not a full PowerPoint
layout engine.
"""

from __future__ import annotations

import argparse
import html
import os
from pathlib import Path
import posixpath
import re
import shutil
import sys
import zipfile
import xml.etree.ElementTree as ET


NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}

EMU_PER_INCH = 914400
DEFAULT_SIZE = (1280, 720)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert PPTX to PPTD-like files")
    parser.add_argument("pptx", help="Input .pptx file")
    parser.add_argument("-o", "--output", required=True, help="Output directory")
    parser.add_argument("--name", help="Output .pptd basename")
    return parser.parse_args()


def qn(prefix: str, name: str) -> str:
    return f"{{{NS[prefix]}}}{name}"


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def read_xml(zf: zipfile.ZipFile, name: str) -> ET.Element | None:
    try:
        return ET.fromstring(zf.read(name))
    except KeyError:
        return None


def rels_for(zf: zipfile.ZipFile, part_name: str) -> dict[str, str]:
    directory = posixpath.dirname(part_name)
    base = posixpath.basename(part_name)
    rel_path = posixpath.join(directory, "_rels", base + ".rels")
    root = read_xml(zf, rel_path)
    rels: dict[str, str] = {}
    if root is None:
        return rels
    for rel in root.findall("rel:Relationship", NS):
        rid = rel.attrib.get("Id")
        target = rel.attrib.get("Target")
        if not rid or not target:
            continue
        if target.startswith("/"):
            resolved = target.lstrip("/")
        else:
            resolved = posixpath.normpath(posixpath.join(directory, target))
        rels[rid] = resolved
    return rels


def presentation_info(zf: zipfile.ZipFile) -> tuple[tuple[int, int], list[str]]:
    root = read_xml(zf, "ppt/presentation.xml")
    if root is None:
        raise SystemExit("Invalid PPTX: missing ppt/presentation.xml")

    sld_sz = root.find("p:sldSz", NS)
    if sld_sz is not None:
        cx = int(sld_sz.attrib.get("cx", "0") or "0")
        cy = int(sld_sz.attrib.get("cy", "0") or "0")
        size = DEFAULT_SIZE if not cx or not cy else (DEFAULT_SIZE[0], round(DEFAULT_SIZE[0] * cy / cx))
    else:
        size = DEFAULT_SIZE

    pres_rels = rels_for(zf, "ppt/presentation.xml")
    slide_paths: list[str] = []
    sld_id_lst = root.find("p:sldIdLst", NS)
    if sld_id_lst is not None:
        for sld_id in sld_id_lst.findall("p:sldId", NS):
            rid = sld_id.attrib.get(qn("r", "id"))
            if rid and rid in pres_rels:
                slide_paths.append(pres_rels[rid])

    if not slide_paths:
        slide_paths = sorted(
            [name for name in zf.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)],
            key=lambda s: int(re.search(r"slide(\d+)\.xml", s).group(1)),
        )
    return size, slide_paths


def slide_emu_size(zf: zipfile.ZipFile) -> tuple[int, int]:
    root = read_xml(zf, "ppt/presentation.xml")
    sld_sz = root.find("p:sldSz", NS) if root is not None else None
    if sld_sz is None:
        return (13 * EMU_PER_INCH, int(7.3125 * EMU_PER_INCH))
    return (int(sld_sz.attrib.get("cx", "0")), int(sld_sz.attrib.get("cy", "0")))


def parse_bounds(el: ET.Element, slide_emu: tuple[int, int], slide_px: tuple[int, int]) -> list[float] | None:
    xfrm = el.find(".//a:xfrm", NS)
    if xfrm is None:
        return None
    off = xfrm.find("a:off", NS)
    ext = xfrm.find("a:ext", NS)
    if off is None or ext is None:
        return None
    sx = slide_px[0] / slide_emu[0] if slide_emu[0] else 1
    sy = slide_px[1] / slide_emu[1] if slide_emu[1] else 1
    vals = [
        float(off.attrib.get("x", "0")) * sx,
        float(off.attrib.get("y", "0")) * sy,
        float(ext.attrib.get("cx", "0")) * sx,
        float(ext.attrib.get("cy", "0")) * sy,
    ]
    return [round(v, 2) for v in vals]


def element_name(el: ET.Element, fallback: str) -> str:
    c_nv_pr = el.find(".//p:cNvPr", NS)
    raw = c_nv_pr.attrib.get("name") if c_nv_pr is not None else fallback
    raw = raw or fallback
    slug = re.sub(r"[^A-Za-z0-9_-]+", "_", raw).strip("_").lower()
    return slug or fallback


def text_from_shape(el: ET.Element) -> str:
    paragraphs: list[str] = []
    for para in el.findall(".//a:p", NS):
        parts: list[str] = []
        for node in para.iter():
            if local_name(node.tag) == "t" and node.text:
                parts.append(html.escape(node.text))
            elif local_name(node.tag) == "br":
                parts.append("<br/>")
        text = "".join(parts).strip()
        if text:
            paragraphs.append(f"<p>{text}</p>")
    return "\n".join(paragraphs)


def solid_fill(el: ET.Element) -> str | None:
    srgb = el.find(".//a:solidFill/a:srgbClr", NS)
    if srgb is not None and srgb.attrib.get("val"):
        return "#" + srgb.attrib["val"].upper()
    scheme = el.find(".//a:solidFill/a:schemeClr", NS)
    if scheme is not None and scheme.attrib.get("val"):
        return scheme.attrib["val"]
    return None


def text_style(el: ET.Element) -> tuple[float | None, str | None]:
    sizes = []
    colors = []
    for rpr in el.findall(".//a:rPr", NS):
        if rpr.attrib.get("sz"):
            sizes.append(int(rpr.attrib["sz"]) / 100)
        color = solid_fill(rpr)
        if color:
            colors.append(color)
    return (round(max(sizes), 1) if sizes else None, colors[0] if colors else None)


def yaml_scalar(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if re.fullmatch(r"[A-Za-z0-9_./:#-]+", text):
        return text
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def write_text_block(lines: list[str], indent: str, key: str, text: str) -> None:
    lines.append(f"{indent}{key}: |")
    if text:
        for line in text.splitlines():
            lines.append(f"{indent}  {line}")
    else:
        lines.append(f"{indent}  ")


def element_to_yaml(el: dict[str, object]) -> str:
    lines: list[str] = []
    lines.append(f"- elementId: {yaml_scalar(el['elementId'])}")
    lines.append(f"  elementType: {yaml_scalar(el['elementType'])}")
    if "bounds" in el:
        bounds = ", ".join(str(v) for v in el["bounds"])
        lines.append(f"  bounds: [{bounds}]")
    if el.get("elementType") == "image":
        lines.append(f"  src: {yaml_scalar(el['src'])}")
        lines.append("  fit:")
        lines.append("    mode: contain")
    elif el.get("elementType") == "shape":
        lines.append(f"  shapeName: {yaml_scalar(el.get('shapeName', 'rect'))}")
        color = el.get("color")
        if color:
            lines.append("  fill:")
            lines.append("    type: solid")
            lines.append(f"    color: {yaml_scalar(color)}")
    elif el.get("elementType") == "text":
        lines.append("  content:")
        lines.append("    align: [left, top]")
        if el.get("fontSize"):
            lines.append(f"    fontSize: {el['fontSize']}")
        if el.get("color"):
            lines.append(f"    color: {yaml_scalar(el['color'])}")
        write_text_block(lines, "    ", "text", str(el.get("text", "")))
    return "\n".join(lines)


def extract_slide(
    zf: zipfile.ZipFile,
    slide_path: str,
    out_images: Path,
    result_images_prefix: str,
    image_counter: list[int],
    slide_emu: tuple[int, int],
    slide_px: tuple[int, int],
) -> list[dict[str, object]]:
    root = read_xml(zf, slide_path)
    if root is None:
        return []
    rels = rels_for(zf, slide_path)
    elements: list[dict[str, object]] = []

    for child in root.findall(".//p:cSld/p:spTree/*", NS):
        tag = local_name(child.tag)
        bounds = parse_bounds(child, slide_emu, slide_px)
        if bounds is None:
            continue

        if tag == "pic":
            blip = child.find(".//a:blip", NS)
            rid = blip.attrib.get(qn("r", "embed")) if blip is not None else None
            media_path = rels.get(rid or "")
            if media_path and media_path in zf.namelist():
                suffix = Path(media_path).suffix or ".png"
                image_counter[0] += 1
                out_name = f"image_{image_counter[0]}{suffix}"
                with zf.open(media_path) as src, open(out_images / out_name, "wb") as dst:
                    shutil.copyfileobj(src, dst)
                elements.append(
                    {
                        "elementId": element_name(child, f"image_{image_counter[0]}"),
                        "elementType": "image",
                        "bounds": bounds,
                        "src": posixpath.join(result_images_prefix, out_name),
                    }
                )
            continue

        if tag == "sp":
            text = text_from_shape(child)
            if text:
                font_size, color = text_style(child)
                elements.append(
                    {
                        "elementId": element_name(child, f"text_{len(elements) + 1}"),
                        "elementType": "text",
                        "bounds": bounds,
                        "fontSize": font_size or 18,
                        "color": color or "#000000",
                        "text": text,
                    }
                )
            else:
                color = solid_fill(child)
                elements.append(
                    {
                        "elementId": element_name(child, f"shape_{len(elements) + 1}"),
                        "elementType": "shape",
                        "bounds": bounds,
                        "shapeName": "rect",
                        "color": color or "#FFFFFF",
                    }
                )
    return elements


def main() -> int:
    args = parse_args()
    pptx_path = Path(args.pptx).expanduser().resolve()
    out_dir = Path(args.output).expanduser().resolve()
    if not pptx_path.exists():
        print(f"Input PPTX not found: {pptx_path}", file=sys.stderr)
        return 2

    pages_dir = out_dir / "pages"
    images_dir = out_dir / "images"
    pages_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    stem = args.name or pptx_path.stem
    pptd_path = out_dir / f"{stem}.pptd"

    with zipfile.ZipFile(pptx_path) as zf:
        slide_px, slide_paths = presentation_info(zf)
        slide_emu = slide_emu_size(zf)
        image_counter = [0]
        page_refs: list[str] = []

        for index, slide_path in enumerate(slide_paths, 1):
            elements = extract_slide(
                zf,
                slide_path,
                images_dir,
                "images",
                image_counter,
                slide_emu,
                slide_px,
            )
            page_name = f"page{index}.page"
            page_refs.append(f"pages/{page_name}")
            lines = ["pageType: content", "elements:"]
            if elements:
                for element in elements:
                    lines.append(element_to_yaml(element))
            else:
                lines.append("[]")
            (pages_dir / page_name).write_text("\n".join(lines) + "\n", encoding="utf-8")

    pptd_lines = [
        f"size: [{slide_px[0]}, {slide_px[1]}]",
        "theme:",
        "  colors:",
        '    primary: "#244EB1"',
        '    secondary: "#ED7D31"',
        '    dark: "#000000"',
        '    light: "#FFFFFF"',
        "pages:",
    ]
    pptd_lines.extend(f"- {ref}" for ref in page_refs)
    pptd_path.write_text("\n".join(pptd_lines) + "\n", encoding="utf-8")

    print(f"Created: {pptd_path}")
    print(f"Pages: {len(page_refs)}")
    print(f"Images: {len(list(images_dir.iterdir()))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
