#!/usr/bin/env python3
"""Run static checks for a paper-explore index.html."""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path


LOGGER = logging.getLogger("validate_index")


REQUIRED_SECTIONS = [
    "motivation",
    "method",
    "algorithm",
    "experiments",
    "critique",
]

SURVEY_REQUIRED_SECTION_ALIASES = [
    ("scope", "motivation"),
    ("inclusion", "method"),
    ("taxonomy",),
    ("matrix", "experiments"),
    ("evidence", "results"),
    ("critique",),
]

SECTION_ALIASES_BY_MODE = {
    "survey": [
        ("verdict",),
        ("scope", "motivation"),
        ("inclusion", "method"),
        ("taxonomy",),
        ("matrix", "experiments"),
        ("evidence", "results"),
        ("critique",),
    ],
    "benchmark": [
        ("verdict",),
        ("benchmark", "motivation"),
        ("protocol", "method"),
        ("metrics", "metric", "algorithm"),
        ("results", "experiments"),
        ("failure", "failures", "critique"),
    ],
    "method": [
        ("verdict", "tldr"),
        ("motivation",),
        ("method",),
        ("algorithm", "pipeline"),
        ("experiments", "results"),
        ("critique",),
    ],
    "position": [
        ("verdict",),
        ("thesis", "motivation"),
        ("argument", "method"),
        ("counterarguments", "counterexamples", "algorithm"),
        ("evidence", "results", "experiments"),
        ("critique",),
    ],
}

MODE_TEXT_REQUIREMENTS = {
    "survey": [
        ("verdict", "判定", "判断"),
        ("evidence ladder", "evidence strength", "证据强度", "证据等级"),
        ("coverage", "覆盖", "blind spot", "盲区"),
        ("structural", "bottleneck", "结构性", "瓶颈"),
        ("matrix", "ledger", "矩阵", "台账"),
    ],
    "benchmark": [
        ("verdict", "判定", "判断"),
        ("metric", "指标"),
        ("protocol", "评估协议", "evaluation protocol"),
        ("leaderboard", "results", "榜单", "结果"),
        ("failure", "失败", "failure mode"),
    ],
    "method": [
        ("verdict", "判定", "判断"),
        ("method", "方法"),
        ("algorithm", "算法", "pipeline", "流程"),
        ("experiment", "实验", "result", "结果"),
        ("critique", "批判", "局限"),
    ],
    "position": [
        ("verdict", "判定", "判断"),
        ("thesis", "论点", "主张"),
        ("assumption", "假设"),
        ("counter", "反例", "反驳"),
        ("evidence", "证据"),
    ],
}


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def has_section_id(lower: str, section: str) -> bool:
    return f'id="{section}"' in lower or f"id='{section}'" in lower


def css_rule_contains(text: str, selector_pattern: str, property_name: str) -> bool:
    pattern = rf"{selector_pattern}\s*\{{[^}}]*\b{re.escape(property_name)}\s*:"
    return re.search(pattern, text, flags=re.I | re.S) is not None


def detect_explicit_mode(lower: str) -> str | None:
    body_match = re.search(r"data-paper-type\s*=\s*['\"]([a-z-]+)['\"]", lower)
    if body_match:
        return normalize_mode(body_match.group(1))
    meta_match = re.search(
        r"<meta[^>]+name\s*=\s*['\"]paper-type['\"][^>]+content\s*=\s*['\"]([a-z-]+)['\"]",
        lower,
    )
    if meta_match:
        return normalize_mode(meta_match.group(1))
    return None


def normalize_mode(mode: str) -> str:
    if mode in {"survey", "taxonomy", "review", "landscape", "systematic-mapping"}:
        return "survey"
    if mode in {"benchmark", "dataset", "evaluation", "metric", "testbed"}:
        return "benchmark"
    if mode in {"method", "system", "theory", "empirical"}:
        return "method"
    if mode in {"position", "perspective", "agenda"}:
        return "position"
    return mode


def contains_any(lower: str, terms: tuple[str, ...]) -> bool:
    return any(term.lower() in lower for term in terms)


def validate(path: Path) -> list[str]:
    # 步骤1：读取目标 HTML
    LOGGER.info("步骤1：开始读取 HTML")
    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    LOGGER.info("步骤1：完成读取 HTML")

    failures: list[str] = []
    explicit_mode = detect_explicit_mode(lower)
    is_survey_mode = (
        explicit_mode == "survey"
        or "survey mode" in lower
        or "data-paper-type=\"survey\"" in lower
        or "detected paper type" in lower and "survey" in lower
        or "taxonomy overview" in lower and "inclusion" in lower
    )

    # 步骤2：检查单文件结构与核心依赖
    LOGGER.info("步骤2：开始检查结构与依赖")
    if "<!doctype html" not in lower:
        fail("missing <!doctype html>", failures)
    if "<html" not in lower or "</html>" not in lower:
        fail("missing html root", failures)
    if "katex" not in lower:
        fail("missing KaTeX dependency", failures)
    if "rendermathinelement" not in lower:
        fail("missing renderMathInElement call", failures)
    if "data-latex" not in lower:
        fail("missing data-latex attributes for copyable formulas", failures)
    if explicit_mode and 'id="verdict"' not in lower and "verdict-board" not in lower:
        fail("explicit paper mode pages must include a verdict board or id=\"verdict\"", failures)
    if not css_rule_contains(text, r"\.math-block\b", "color"):
        fail("missing explicit color on .math-block; formulas may inherit unreadable parent color", failures)
    if not css_rule_contains(text, r"\.math-block\s+\.katex\b", "color"):
        fail("missing explicit color on .math-block .katex; rendered KaTeX may be low contrast", failures)
    has_dark_math_context = (
        re.search(r"\.(band|dark|hero-dark|callout-dark|overlay)\b", lower) is not None
        and "math-block" in lower
    )
    has_dark_math_override = re.search(
        r"[^{}]*\.(band|dark|hero-dark|callout-dark|overlay)\s+\.math-block\b[^{}]*\{[^}]*\bcolor\s*:",
        text,
        flags=re.I | re.S,
    ) is not None
    if has_dark_math_context and not has_dark_math_override:
        fail("dark visual container present without local .math-block color override", failures)
    LOGGER.info("步骤2：完成检查结构与依赖")

    # 步骤3：检查内容区块
    LOGGER.info("步骤3：开始检查内容区块")
    if explicit_mode in SECTION_ALIASES_BY_MODE:
        for aliases in SECTION_ALIASES_BY_MODE[explicit_mode]:
            if not any(has_section_id(lower, section) for section in aliases):
                fail(f"missing required {explicit_mode} section id alias: {'/'.join(aliases)}", failures)
    elif is_survey_mode:
        for aliases in SURVEY_REQUIRED_SECTION_ALIASES:
            if not any(has_section_id(lower, section) for section in aliases):
                fail(f"missing required survey section id alias: {'/'.join(aliases)}", failures)
    else:
        for section in REQUIRED_SECTIONS:
            if not has_section_id(lower, section):
                fail(f"missing required section id: {section}", failures)
    if re.search(r"\bTODO\b|填入|placeholder", text, flags=re.I):
        fail("contains unresolved placeholder text", failures)
    if explicit_mode in MODE_TEXT_REQUIREMENTS:
        for terms in MODE_TEXT_REQUIREMENTS[explicit_mode]:
            if not contains_any(lower, terms):
                fail(f"missing {explicit_mode} mode signal: {'/'.join(terms)}", failures)
    LOGGER.info("步骤3：完成检查内容区块")

    # 步骤4：检查论文资产与表格信号
    LOGGER.info("步骤4：开始检查图表信号")
    if "arxiv.org/html/" not in lower and "<figure" not in lower:
        fail("no arXiv figure URL or figure block found", failures)
    if "<table" not in lower:
        table_reason = "representative work or evidence tables" if is_survey_mode else "key experiment tables"
        fail(f"no HTML table found; {table_reason} should be represented", failures)
    LOGGER.info("步骤4：完成检查图表信号")

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate paper-explore index.html.")
    parser.add_argument("html_path", type=Path)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING, format="%(levelname)s: %(message)s")

    if not args.html_path.exists():
        print(f"not found: {args.html_path}", file=sys.stderr)
        return 2

    failures = validate(args.html_path)
    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
    print("OK: index.html passed static paper-explore checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
