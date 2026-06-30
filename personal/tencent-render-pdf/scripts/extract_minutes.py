#!/usr/bin/env python3
"""Export Tencent Meeting minutes JSON pages to SRT/Markdown/text."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def format_srt_time(ms: int) -> str:
    seconds, millis = divmod(max(0, int(ms)), 1000)
    minutes, sec = divmod(seconds, 60)
    hours, minute = divmod(minutes, 60)
    return f"{hours:02d}:{minute:02d}:{sec:02d},{millis:03d}"


def format_hms(ms: int) -> str:
    seconds = max(0, int(ms)) // 1000
    minutes, sec = divmod(seconds, 60)
    hours, minute = divmod(minutes, 60)
    return f"{hours:02d}:{minute:02d}:{sec:02d}"


def paragraph_text(paragraph: dict[str, Any]) -> str:
    parts: list[str] = []
    for sentence in paragraph.get("sentences") or []:
        words = sentence.get("words") or []
        if words:
            parts.append("".join(str(word.get("text", "")) for word in words))
        elif sentence.get("text"):
            parts.append(str(sentence["text"]))
    if not parts and paragraph.get("text"):
        parts.append(str(paragraph["text"]))
    return "".join(parts).strip()


def find_paragraphs(obj: Any) -> list[dict[str, Any]]:
    if isinstance(obj, list):
        if all(isinstance(item, dict) and ("sentences" in item or "text" in item) for item in obj):
            return obj
        found: list[dict[str, Any]] = []
        for item in obj:
            found.extend(find_paragraphs(item))
        return found
    if not isinstance(obj, dict):
        return []

    candidates = [
        obj.get("paragraphs"),
        obj.get("minutes", {}).get("paragraphs") if isinstance(obj.get("minutes"), dict) else None,
        obj.get("data", {}).get("paragraphs") if isinstance(obj.get("data"), dict) else None,
    ]
    data = obj.get("data")
    if isinstance(data, dict) and isinstance(data.get("minutes"), dict):
        candidates.append(data["minutes"].get("paragraphs"))

    for candidate in candidates:
        if isinstance(candidate, list):
            return [item for item in candidate if isinstance(item, dict)]

    found: list[dict[str, Any]] = []
    for value in obj.values():
        found.extend(find_paragraphs(value))
    return found


def load_paragraphs(args: argparse.Namespace) -> list[dict[str, Any]]:
    raw: list[dict[str, Any]] = []
    if args.paragraphs_json:
        raw.extend(find_paragraphs(json.loads(Path(args.paragraphs_json).read_text(encoding="utf-8"))))
    if args.minutes_dir:
        for path in sorted(Path(args.minutes_dir).glob("*.json")):
            raw.extend(find_paragraphs(json.loads(path.read_text(encoding="utf-8"))))

    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, int, int, str]] = set()
    for paragraph in raw:
        text = paragraph_text(paragraph)
        if not text:
            continue
        start = int(paragraph.get("start_time") or paragraph.get("startTime") or 0)
        end = int(paragraph.get("end_time") or paragraph.get("endTime") or start)
        key = (str(paragraph.get("pid", "")), start, end, text)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(paragraph)

    deduped.sort(key=lambda item: int(item.get("start_time") or item.get("startTime") or 0))
    return deduped


def write_outputs(paragraphs: list[dict[str, Any]], output_prefix: str) -> None:
    prefix = Path(output_prefix)
    prefix.parent.mkdir(parents=True, exist_ok=True)

    (prefix.with_name(prefix.name + "_paragraphs.json")).write_text(
        json.dumps(paragraphs, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    srt_entries: list[str] = []
    index = 1
    md_lines = ["# Tencent Meeting Transcript", ""]
    txt_lines: list[str] = []

    for paragraph in paragraphs:
        speaker_info = paragraph.get("speaker") or {}
        speaker = speaker_info.get("user_name") or speaker_info.get("name") or ""
        p_start = int(paragraph.get("start_time") or paragraph.get("startTime") or 0)
        p_end = int(paragraph.get("end_time") or paragraph.get("endTime") or p_start)
        text = paragraph_text(paragraph)
        label = f"{speaker}: " if speaker else ""
        md_lines.append(f"[{format_hms(p_start)}--{format_hms(p_end)}] {label}{text}")
        md_lines.append("")
        txt_lines.append(f"{label}{text}")

        sentences = paragraph.get("sentences") or []
        if not sentences:
            srt_entries.append(
                f"{index}\n{format_srt_time(p_start)} --> {format_srt_time(p_end)}\n{label}{text}\n"
            )
            index += 1
            continue

        for sentence in sentences:
            words = sentence.get("words") or []
            if words:
                sentence_text = "".join(str(word.get("text", "")) for word in words).strip()
            else:
                sentence_text = str(sentence.get("text", "")).strip()
            if not sentence_text:
                continue
            start = int(sentence.get("start_time") or sentence.get("startTime") or p_start)
            end = int(sentence.get("end_time") or sentence.get("endTime") or start + 1000)
            srt_entries.append(
                f"{index}\n{format_srt_time(start)} --> {format_srt_time(end)}\n{label}{sentence_text}\n"
            )
            index += 1

    prefix.with_suffix(".srt").write_text("\n".join(srt_entries), encoding="utf-8")
    prefix.with_suffix(".md").write_text("\n".join(md_lines), encoding="utf-8")
    prefix.with_suffix(".txt").write_text("\n".join(txt_lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export Tencent Meeting minutes JSON to transcript files.")
    parser.add_argument("--minutes-dir", help="Directory containing minutes page JSON files.")
    parser.add_argument("--paragraphs-json", help="Existing normalized transcript_paragraphs.json or API JSON.")
    parser.add_argument("--output-prefix", default="transcript", help="Output prefix, default: transcript.")
    args = parser.parse_args()

    if not args.minutes_dir and not args.paragraphs_json:
        parser.error("Provide --minutes-dir and/or --paragraphs-json.")

    paragraphs = load_paragraphs(args)
    if not paragraphs:
        raise SystemExit("No Tencent minutes paragraphs found.")

    write_outputs(paragraphs, args.output_prefix)
    first = int(paragraphs[0].get("start_time") or 0)
    last = int(paragraphs[-1].get("end_time") or paragraphs[-1].get("start_time") or 0)
    print(f"exported paragraphs={len(paragraphs)} range={format_hms(first)}--{format_hms(last)}")


if __name__ == "__main__":
    main()
