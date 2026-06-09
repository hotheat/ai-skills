#!/usr/bin/env python3
"""Collect figure and table candidates from an arXiv HTML page."""

from __future__ import annotations

import argparse
import html
import json
import logging
import re
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict


LOGGER = logging.getLogger("collect_arxiv_assets")


@dataclass
class FigureAsset:
    index: int
    src: str
    alt: str
    caption: str
    suggested_url: str


@dataclass
class TableAsset:
    index: int
    caption: str
    text_preview: str


def strip_tags(value: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", " ", value, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def fetch_html(arxiv_id: str) -> tuple[str, str]:
    # 步骤1：读取 arXiv HTML
    # 1.1 规范化 ID，兼容用户传入 URL 或裸 ID
    LOGGER.info("步骤1：开始读取 arXiv HTML")
    arxiv_id = arxiv_id.strip().rstrip("/")
    if "/" in arxiv_id and arxiv_id.startswith("http"):
        arxiv_id = arxiv_id.split("/")[-1]
    url = f"https://arxiv.org/html/{arxiv_id}"
    request = urllib.request.Request(url, headers={"User-Agent": "paper-explore/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8", errors="replace")
    LOGGER.info("步骤1：完成读取 arXiv HTML")
    return url, body


def collect_figures(base_url: str, body: str) -> list[FigureAsset]:
    # 步骤2：提取图片与说明
    LOGGER.info("步骤2：开始提取图片")
    figures: list[FigureAsset] = []
    figure_blocks = re.findall(r"<figure\b[\s\S]*?</figure>", body, flags=re.I)
    blocks = figure_blocks or re.findall(r"<img\b[^>]*>", body, flags=re.I)

    for block in blocks:
        image_matches = re.findall(r"<img\b([^>]*)>", block, flags=re.I)
        for attrs in image_matches:
            src_match = re.search(r"\bsrc=[\"']([^\"']+)[\"']", attrs, flags=re.I)
            if not src_match:
                continue
            alt_match = re.search(r"\balt=[\"']([^\"']*)[\"']", attrs, flags=re.I)
            src = urllib.parse.urljoin(base_url, html.unescape(src_match.group(1)))
            alt = html.unescape(alt_match.group(1)) if alt_match else ""
            caption_match = re.search(r"<figcaption\b[^>]*>([\s\S]*?)</figcaption>", block, flags=re.I)
            caption = strip_tags(caption_match.group(1)) if caption_match else ""
            index = len(figures) + 1
            suggested_url = f"{base_url}/x{index}.png"
            figures.append(FigureAsset(index=index, src=src, alt=alt, caption=caption, suggested_url=suggested_url))

    LOGGER.info("步骤2：完成提取图片，共 %s 张", len(figures))
    return figures


def collect_tables(body: str) -> list[TableAsset]:
    # 步骤3：提取表格候选
    LOGGER.info("步骤3：开始提取表格")
    tables: list[TableAsset] = []
    for index, block in enumerate(re.findall(r"<table\b[\s\S]*?</table>", body, flags=re.I), start=1):
        previous = body[max(0, body.find(block) - 2500): body.find(block)]
        caption_match = re.search(r"<figcaption\b[^>]*>([\s\S]*?)</figcaption>\s*$", previous, flags=re.I)
        caption = strip_tags(caption_match.group(1)) if caption_match else ""
        preview = strip_tags(block)[:800]
        tables.append(TableAsset(index=index, caption=caption, text_preview=preview))
    LOGGER.info("步骤3：完成提取表格，共 %s 个", len(tables))
    return tables


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect arXiv HTML figure and table candidates.")
    parser.add_argument("arxiv_id", help="arXiv ID or https://arxiv.org/html/<id> URL")
    parser.add_argument("--output", "-o", help="Write JSON to this path instead of stdout")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    parser.add_argument("--verbose", action="store_true", help="Enable progress logs")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING, format="%(levelname)s: %(message)s")

    try:
        base_url, body = fetch_html(args.arxiv_id)
        payload = {
            "source": base_url,
            "figures": [asdict(item) for item in collect_figures(base_url, body)],
            "tables": [asdict(item) for item in collect_tables(body)],
        }
    except Exception as exc:  # noqa: BLE001
        print(f"collect_arxiv_assets failed: {exc}", file=sys.stderr)
        return 1

    text = json.dumps(payload, ensure_ascii=False, indent=2 if args.pretty else None)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
