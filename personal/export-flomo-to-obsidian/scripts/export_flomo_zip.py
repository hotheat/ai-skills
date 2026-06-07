#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import shutil
import sys
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Callable, Iterable

import yaml


RELATED_START = "<!-- flomo-related:start -->"
RELATED_END = "<!-- flomo-related:end -->"
OBSIDIAN_FILE_PATTERN = re.compile(r"ObsidianFile[：:]\s*([^\n\r]+)")
TAG_LINE_PATTERN = re.compile(r"^(?:#[^\s#]+)(?:\s+#[^\s#]+)*$")


@dataclass
class ParsedMemo:
    created_at: str
    raw_blocks: list[str]
    file_sources: list[str]


@dataclass
class ManagedNote:
    key: str
    title: str
    path: pathlib.Path
    created_at: str
    created_date: str
    tags: list[str]
    body: str
    tokens: set[str] = field(default_factory=set)
    english_terms: set[str] = field(default_factory=set)
    cjk_phrases: set[str] = field(default_factory=set)


@dataclass
class LinkEvidence:
    score: float
    shared_tags: list[str]
    shared_terms: list[str]
    shared_phrases: list[str]

    def rationale(self) -> str:
        reasons: list[str] = []
        if self.shared_tags:
            rendered_tags = "、".join(f"`{tag}`" for tag in self.shared_tags[:2])
            reasons.append(f"共享标签 {rendered_tags}")
        if self.shared_terms:
            rendered_terms = "、".join(f"`{term}`" for term in self.shared_terms[:2])
            reasons.append(f"共同关键词 {rendered_terms}")
        if self.shared_phrases:
            rendered_phrases = "、".join(f"`{phrase}`" for phrase in self.shared_phrases[:2])
            reasons.append(f"共同短语 {rendered_phrases}")
        return "；".join(reasons)


class FlomoHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.memos: list[ParsedMemo] = []
        self._memo_stack_depth = 0
        self._div_class_stack: list[list[str]] = []
        self._current_section: str | None = None
        self._current_memo: dict[str, object] | None = None
        self._current_block_parts: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {name: value or "" for name, value in attrs}
        if tag == "div":
            classes = attr_map.get("class", "").split()
            self._div_class_stack.append(classes)

            if "memo" in classes and self._current_memo is None:
                self._current_memo = {
                    "time_parts": [],
                    "blocks": [],
                    "files": [],
                }
                self._memo_stack_depth = 1
                return

            if self._current_memo is not None:
                self._memo_stack_depth += 1
                if "time" in classes:
                    self._current_section = "time"
                elif "content" in classes:
                    self._current_section = "content"
                elif "files" in classes:
                    self._current_section = "files"
                return

        if self._current_memo is None:
            return

        if self._current_section == "content":
            if tag in {"p", "li"}:
                self._current_block_parts = []
            elif tag == "br" and self._current_block_parts is not None:
                self._current_block_parts.append("\n")

        if self._current_section == "files" and tag in {"img", "audio", "source"}:
            source = attr_map.get("src", "").strip()
            if source:
                files = self._current_memo["files"]
                assert isinstance(files, list)
                files.append(source)

    def handle_endtag(self, tag: str) -> None:
        if self._current_memo is None:
            if tag == "div" and self._div_class_stack:
                self._div_class_stack.pop()
            return

        if tag in {"p", "li"} and self._current_block_parts is not None:
            block = normalize_block("".join(self._current_block_parts))
            blocks = self._current_memo["blocks"]
            assert isinstance(blocks, list)
            blocks.append(block)
            self._current_block_parts = None

        if tag == "div":
            classes = self._div_class_stack.pop() if self._div_class_stack else []
            if any(name in classes for name in ("time", "content", "files")):
                self._current_section = None

            self._memo_stack_depth -= 1
            if self._memo_stack_depth == 0:
                time_parts = self._current_memo["time_parts"]
                blocks = self._current_memo["blocks"]
                files = self._current_memo["files"]
                assert isinstance(time_parts, list)
                assert isinstance(blocks, list)
                assert isinstance(files, list)
                created_at = normalize_block("".join(time_parts))
                self.memos.append(
                    ParsedMemo(created_at=created_at, raw_blocks=blocks, file_sources=files)
                )
                self._current_memo = None

    def handle_data(self, data: str) -> None:
        if self._current_memo is None:
            return
        if self._current_section == "time":
            time_parts = self._current_memo["time_parts"]
            assert isinstance(time_parts, list)
            time_parts.append(data)
        elif self._current_section == "content" and self._current_block_parts is not None:
            self._current_block_parts.append(data)


def normalize_block(value: str) -> str:
    value = value.replace("\r\n", "\n").replace("\r", "\n").replace("\xa0", " ")
    value = re.sub(r"[ \t]+\n", "\n", value)
    value = re.sub(r"\n[ \t]+", "\n", value)
    value = re.sub(r"[ \t]{2,}", " ", value)
    return value.strip()


def parse_zip(zip_path: pathlib.Path) -> list[ParsedMemo]:
    with zipfile.ZipFile(zip_path) as archive:
        html_files = [name for name in archive.namelist() if name.lower().endswith(".html")]
        if len(html_files) != 1:
            raise ValueError(f"Expected exactly one html file in {zip_path}, found {len(html_files)}")
        html_text = archive.read(html_files[0]).decode("utf-8", errors="replace")

    parser = FlomoHTMLParser()
    parser.feed(html_text)
    parser.close()
    return [memo for memo in parser.memos if memo.created_at]


def extract_tags_and_body(raw_blocks: Iterable[str]) -> tuple[list[str], list[str]]:
    tags: list[str] = []
    body_blocks: list[str] = []
    seen_tags: set[str] = set()

    for raw_block in raw_blocks:
        block = normalize_block(raw_block)
        if not block:
            continue
        body_lines: list[str] = []
        for line in block.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if TAG_LINE_PATTERN.fullmatch(stripped):
                for match in re.finditer(r"(?<!\S)#([^\s#]+)", stripped):
                    tag = match.group(1)
                    if tag not in seen_tags:
                        seen_tags.add(tag)
                        tags.append(tag)
                continue
            body_lines.append(stripped)
        cleaned_block = normalize_block("\n".join(body_lines))
        if cleaned_block:
            body_blocks.append(cleaned_block)

    return tags, body_blocks


def memo_key(created_at: str, raw_blocks: Iterable[str]) -> str:
    payload = created_at + "\n" + "\n".join(block for block in raw_blocks)
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()


def summarize_title(body_blocks: Iterable[str]) -> str:
    candidates = [
        re.sub(r"https?://\S+", "", block).strip()
        for block in body_blocks
        if block and not re.fullmatch(r"https?://\S+", block)
    ]
    if not candidates:
        summary = "Flomo 笔记"
    else:
        summary = candidates[0]
        summary = re.split(r"[。！？!?；;\n]", summary, maxsplit=1)[0].strip()
        if len(summary) > 28 and "，" in summary:
            summary = summary.split("，", 1)[0].strip()
        summary = summary[:28].strip()
        if not summary:
            summary = "Flomo 笔记"
    return summary


def title_source_text(body_blocks: Iterable[str]) -> str:
    return normalize_block("\n".join(block for block in body_blocks if block))


def should_use_llm_title(body_blocks: Iterable[str]) -> bool:
    source_text = title_source_text(body_blocks)
    cjk_chars = len(re.findall(r"[\u4e00-\u9fff]", source_text))
    english_words = len(re.findall(r"[A-Za-z][A-Za-z0-9._/-]{1,}", source_text))
    return cjk_chars >= 12 or english_words >= 6


def heuristic_title_needs_llm(fallback_title: str, body_blocks: Iterable[str]) -> bool:
    title = normalize_block(fallback_title)
    if not title or title == "Flomo 笔记":
        return True

    cjk_chars = len(re.findall(r"[\u4e00-\u9fff]", title))
    english_words = len(re.findall(r"[A-Za-z][A-Za-z0-9._/-]{1,}", title))
    compact_length = len(re.sub(r"[^A-Za-z0-9\u4e00-\u9fff]+", "", title))

    if cjk_chars >= 6 or english_words >= 2 or compact_length >= 12:
        return False

    return should_use_llm_title(body_blocks)


def normalize_generated_title(title: str, fallback_title: str) -> str:
    cleaned = normalize_block(title).strip().strip("'\"`")
    cleaned = re.sub(r"\.(?:md|markdown|txt)$", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.split(r"[\r\n]", cleaned, maxsplit=1)[0].strip()
    cleaned = re.split(r"[。！？!?；;]", cleaned, maxsplit=1)[0].strip()
    cleaned = cleaned[:28].strip()
    cleaned = safe_stem(cleaned)
    return cleaned or fallback_title


def request_llm_title(
    source_text: str,
    model: str,
    api_key: str,
    base_url: str,
    timeout_seconds: float = 30.0,
) -> str:
    endpoint = base_url.rstrip("/")
    if not endpoint.endswith("/chat/completions"):
        endpoint = f"{endpoint}/chat/completions"

    payload = {
        "model": model,
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You generate concise Obsidian note titles from Flomo memos. "
                    "Return exactly one title and nothing else."
                ),
            },
            {
                "role": "user",
                "content": (
                    "为下面的 Flomo 笔记生成一个适合作为 Obsidian 文件名的标题。\n"
                    "要求：\n"
                    "1. 只输出标题本身，不要解释，不要引号，不要序号。\n"
                    "2. 优先概括核心主题，不要机械照抄第一句。\n"
                    "3. 最长 28 个字符。\n"
                    "4. 不要带日期、时间、扩展名、Markdown 标记。\n"
                    "5. 若原文主要是中文，就输出中文标题；否则保留原语言。\n\n"
                    f"笔记内容：\n{source_text}"
                ),
            },
        ],
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        result = json.loads(response.read().decode("utf-8"))
    choices = result.get("choices") or []
    if not choices:
        raise RuntimeError("No choices returned from title generation API")
    message = choices[0].get("message") or {}
    content = message.get("content", "")
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(str(item.get("text", "")))
        content = "\n".join(part for part in parts if part)
    content = str(content).strip()
    if not content:
        raise RuntimeError("Empty title returned from title generation API")
    return content


def build_title_generator(
    title_mode: str,
    title_model: str | None = None,
    title_api_key: str | None = None,
    title_base_url: str | None = None,
    timeout_seconds: float = 30.0,
) -> Callable[[list[str], str], str]:
    if title_mode == "heuristic":
        return lambda body_blocks, fallback_title: fallback_title

    model = (
        title_model
        or os.environ.get("FLOMO_TITLE_MODEL")
        or os.environ.get("OPENAI_MODEL")
        or "deepseek-chat"
    ).strip()
    api_key = (title_api_key or os.environ.get("FLOMO_TITLE_API_KEY") or os.environ.get("OPENAI_API_KEY") or "").strip()
    base_url = (
        title_base_url
        or os.environ.get("FLOMO_TITLE_BASE_URL")
        or os.environ.get("OPENAI_BASE_URL")
        or "https://api.deepseek.com"
    ).strip()
    warned = {"value": False}

    def generator(body_blocks: list[str], fallback_title: str) -> str:
        if not heuristic_title_needs_llm(fallback_title, body_blocks):
            return fallback_title
        if not model or not api_key:
            if not warned["value"]:
                print(
                    "LLM title fallback is enabled, but model or API key is missing. Keeping heuristic titles.",
                    file=sys.stderr,
                )
                warned["value"] = True
            return fallback_title
        source_text = title_source_text(body_blocks)
        try:
            generated = request_llm_title(
                source_text=source_text,
                model=model,
                api_key=api_key,
                base_url=base_url,
                timeout_seconds=timeout_seconds,
            )
        except (OSError, RuntimeError, urllib.error.URLError, json.JSONDecodeError) as exc:
            if not warned["value"]:
                print(
                    f"LLM title fallback failed ({exc}). Keeping heuristic titles.",
                    file=sys.stderr,
                )
                warned["value"] = True
            return fallback_title
        return normalize_generated_title(generated, fallback_title)

    return generator


def safe_stem(value: str) -> str:
    value = value.replace("/", "·").replace("\\", "·")
    value = re.sub(r'[<>:"|?*]', "", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value or "Flomo 笔记"


def unique_note_path(
    output_dir: pathlib.Path,
    created_date: str,
    desired_title: str,
    reserved: set[str],
    key: str,
) -> pathlib.Path:
    base = safe_stem(desired_title)
    candidate = base
    suffix = key[:6]
    index = 2
    while candidate in reserved:
        candidate = f"{base}-{suffix}" if index == 2 else f"{base}-{suffix}-{index}"
        index += 1
    reserved.add(candidate)
    note_dir = output_dir / created_date
    note_dir.mkdir(parents=True, exist_ok=True)
    return note_dir / f"{candidate}.md"


def find_obsidian_vault_root(start: pathlib.Path) -> pathlib.Path | None:
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".obsidian").is_dir():
            return candidate
    return None


def require_obsidian_vault_root(start: pathlib.Path | None = None) -> pathlib.Path:
    root = find_obsidian_vault_root(start or pathlib.Path.cwd())
    if root is None:
        raise RuntimeError(
            "Current directory is not inside an Obsidian vault. Switch to the target Obsidian repository and rerun."
        )
    return root


def build_vault_file_index(vault_root: pathlib.Path) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    hidden_root = (vault_root / ".obsidian").resolve()
    for path in vault_root.rglob("*"):
        if not path.is_file():
            continue
        try:
            path.resolve().relative_to(hidden_root)
            continue
        except ValueError:
            pass
        relative = path.relative_to(vault_root).as_posix()
        index.setdefault(path.name.lower(), []).append(relative)
    return index


def resolve_obsidian_embed_target(file_name: str, vault_index: dict[str, list[str]]) -> str | None:
    requested = normalize_block(file_name)
    if not requested:
        return None
    normalized = requested.lstrip("./")
    if "/" in normalized:
        direct = normalized
        candidates = vault_index.get(pathlib.PurePosixPath(direct).name.lower(), [])
        if direct in candidates:
            return direct
    candidates = vault_index.get(pathlib.PurePosixPath(normalized).name.lower(), [])
    if not candidates:
        return None
    if len(candidates) == 1:
        candidate = candidates[0]
        return pathlib.PurePosixPath(candidate).name
    if normalized in candidates:
        return normalized
    return sorted(candidates, key=lambda value: (value.count("/"), value.casefold()))[0]


def extract_obsidian_file_embeds(
    body_blocks: Iterable[str],
    vault_index: dict[str, list[str]],
) -> tuple[list[str], list[str]]:
    cleaned_blocks: list[str] = []
    embed_targets: list[str] = []
    seen_targets: set[str] = set()

    for raw_block in body_blocks:
        block = raw_block
        matches = OBSIDIAN_FILE_PATTERN.findall(block)
        for match in matches:
            target = resolve_obsidian_embed_target(match, vault_index)
            if target and target not in seen_targets:
                seen_targets.add(target)
                embed_targets.append(target)
        block = OBSIDIAN_FILE_PATTERN.sub("", block)
        block = normalize_block(block)
        if block:
            cleaned_blocks.append(block)

    return cleaned_blocks, embed_targets


def copy_attachments(
    archive: zipfile.ZipFile,
    output_dir: pathlib.Path,
    key: str,
    file_sources: Iterable[str],
) -> list[str]:
    attachments_dir = output_dir / "attachments"
    attachments_dir.mkdir(parents=True, exist_ok=True)
    written_paths: list[str] = []

    for index, source in enumerate(file_sources, start=1):
        normalized_source = source.lstrip("./")
        source_name = pathlib.PurePosixPath(normalized_source).name
        suffix = pathlib.Path(source_name).suffix or ".bin"
        target_name = f"{key[:12]}-{index:02d}{suffix.lower()}"
        target_path = attachments_dir / target_name
        if not target_path.exists():
            with archive.open(resolve_archive_path(archive, normalized_source)) as source_handle:
                with target_path.open("wb") as target_handle:
                    shutil.copyfileobj(source_handle, target_handle)
        written_paths.append(target_name)

    return written_paths


def resolve_archive_path(archive: zipfile.ZipFile, source: str) -> str:
    candidates = [source]
    if archive.namelist():
        root = archive.namelist()[0].split("/", 1)[0]
        candidates.append(f"{root}/{source}")
    for candidate in candidates:
        if candidate in archive.namelist():
            return candidate
    raise FileNotFoundError(f"Attachment not found in archive: {source}")


def render_note_body(
    body_blocks: Iterable[str],
    attachment_names: Iterable[str],
    obsidian_embed_targets: Iterable[str] = (),
) -> str:
    sections = [block for block in body_blocks if block]
    for target in obsidian_embed_targets:
        sections.append(f"![[{target}]]")
    for attachment_name in attachment_names:
        sections.append(f"![[attachments/{attachment_name}]]")
    return "\n\n".join(sections).strip()


def quote_yaml(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def render_frontmatter(tags: Iterable[str], created_at: str, key: str, zip_name: str) -> str:
    created_date = created_at.split(" ", 1)[0]
    lines = ["---"]
    tag_list = list(tags)
    if tag_list:
        lines.append("tags:")
        for tag in tag_list:
            lines.append(f"  - {tag}")
    else:
        lines.append("tags: []")
    lines.extend(
        [
            f"created: {created_date}",
            'source: "flomo"',
            f"flomo_created_at: {quote_yaml(created_at)}",
            f"flomo_source_zip: {quote_yaml(zip_name)}",
            f"flomo_idempotency_key: {quote_yaml(key)}",
            "---",
        ]
    )
    return "\n".join(lines)


def render_related_block(related_items: Iterable[tuple[str, str]]) -> str:
    items = list(related_items)
    if not items:
        return ""
    lines = [
        RELATED_START,
        "## Related",
        "",
    ]
    for title, rationale in items:
        if rationale:
            lines.append(f"- [[{title}]]: {rationale}")
        else:
            lines.append(f"- [[{title}]]")
    lines.append(RELATED_END)
    return "\n".join(lines).strip()


def strip_related_block(body: str) -> str:
    pattern = re.compile(
        rf"\n*{re.escape(RELATED_START)}.*?{re.escape(RELATED_END)}\n*",
        re.DOTALL,
    )
    return pattern.sub("\n\n", body).strip()


def split_frontmatter(content: str) -> tuple[dict[str, object], str]:
    match = re.match(r"^---\n(.*?)\n---\n?(.*)$", content, flags=re.DOTALL)
    if not match:
        return {}, content
    frontmatter = yaml.safe_load(match.group(1)) or {}
    body = match.group(2)
    if not isinstance(frontmatter, dict):
        return {}, body
    return frontmatter, body


def iter_note_paths(output_dir: pathlib.Path) -> Iterable[pathlib.Path]:
    attachments_dir = (output_dir / "attachments").resolve()
    for path in sorted(output_dir.rglob("*.md")):
        try:
            path.resolve().relative_to(attachments_dir)
        except ValueError:
            yield path


def scan_existing_notes(output_dir: pathlib.Path) -> dict[str, ManagedNote]:
    managed: dict[str, ManagedNote] = {}
    for note_path in iter_note_paths(output_dir):
        content = note_path.read_text(encoding="utf-8")
        frontmatter, body = split_frontmatter(content)
        key = str(frontmatter.get("flomo_idempotency_key", "")).strip()
        if not key:
            continue
        title = note_path.stem
        created_at = str(frontmatter.get("flomo_created_at", "")).strip()
        created_date = str(frontmatter.get("created", "")).strip() or created_at.split(" ", 1)[0]
        tags = [str(tag) for tag in frontmatter.get("tags", []) or []]
        clean_body = strip_related_block(body)
        managed[key] = ManagedNote(
            key=key,
            title=title,
            path=note_path,
            created_at=created_at,
            created_date=created_date,
            tags=tags,
            body=clean_body,
        )
    return managed


def tokenize(text: str, tags: Iterable[str]) -> set[str]:
    text = re.sub(r"!\[\[[^\]]+\]\]", " ", text)
    text = re.sub(r"\[\[[^\]]+\]\]", " ", text)
    lowered = text.lower()
    tokens = {
        token
        for token in re.findall(r"[a-z0-9][a-z0-9._/-]{1,}", lowered)
        if len(token) >= 2
    }
    for tag in tags:
        tokens.add(f"tag:{tag.lower()}")
        for part in tag.split("/"):
            normalized = part.strip().lower()
            if normalized:
                tokens.add(f"tagleaf:{normalized}")
    for chunk in re.findall(r"[\u4e00-\u9fff]{2,}", text):
        if len(chunk) <= 4:
            tokens.add(chunk)
            continue
        for size in (2, 3):
            for index in range(0, len(chunk) - size + 1):
                tokens.add(chunk[index : index + size])
    return tokens


def extract_english_terms(text: str) -> set[str]:
    text = re.sub(r"!\[\[[^\]]+\]\]", " ", text)
    text = re.sub(r"\[\[[^\]]+\]\]", " ", text)
    text = re.sub(r"https?://\S+", " ", text)
    stop_words = {
        "about",
        "after",
        "also",
        "being",
        "could",
        "during",
        "from",
        "have",
        "into",
        "just",
        "more",
        "not",
        "that",
        "then",
        "this",
        "through",
        "very",
        "with",
    }
    return {
        token.lower()
        for token in re.findall(r"[A-Za-z][A-Za-z0-9._/-]{2,}", text)
        if token.lower() not in stop_words
    }


def extract_cjk_substrings(text: str, min_len: int = 4, max_len: int = 6) -> set[str]:
    phrases: set[str] = set()
    for span in re.findall(r"[\u4e00-\u9fff]{4,24}", text):
        for size in range(min(max_len, len(span)), min_len - 1, -1):
            for index in range(0, len(span) - size + 1):
                phrases.add(span[index : index + size])
    return phrases


def select_phrases(shared: set[str], limit: int = 2) -> list[str]:
    chosen: list[str] = []
    for phrase in sorted(shared, key=lambda item: (-len(item), item)):
        if any(phrase in existing for existing in chosen):
            continue
        chosen.append(phrase)
        if len(chosen) >= limit:
            break
    return chosen


def tag_roots(tags: Iterable[str]) -> set[str]:
    return {tag.split("/", 1)[0] for tag in tags if tag}


def collect_link_evidence(left: ManagedNote, right: ManagedNote) -> LinkEvidence | None:
    left_tags = set(left.tags)
    right_tags = set(right.tags)
    shared_tags = sorted(left_tags & right_tags)
    shared_terms = sorted(left.english_terms & right.english_terms)
    shared_phrases = select_phrases(left.cjk_phrases & right.cjk_phrases)

    if not shared_tags:
        return None

    has_supporting_evidence = (
        len(shared_tags) >= 2
        or len(shared_terms) >= 2
        or len(shared_phrases) >= 1
    )
    if not has_supporting_evidence:
        return None

    score = 5.0 * min(len(shared_tags), 2)
    score += 2.0 * min(len(shared_terms), 2)
    score += 1.5 * min(len(shared_phrases), 1)

    return LinkEvidence(
        score=score,
        shared_tags=shared_tags,
        shared_terms=shared_terms[:2],
        shared_phrases=shared_phrases[:1],
    )


def update_related_links(notes: dict[str, ManagedNote], related_limit: int) -> int:
    note_list = list(notes.values())
    for note in note_list:
        note.tokens = tokenize(note.body, note.tags)
        note.english_terms = extract_english_terms(note.body)
        note.cjk_phrases = extract_cjk_substrings(note.body)

    pair_evidence: dict[tuple[str, str], LinkEvidence] = {}
    for index, left in enumerate(note_list):
        for right in note_list[index + 1 :]:
            evidence = collect_link_evidence(left, right)
            if evidence is not None:
                pair_evidence[(left.key, right.key)] = evidence

    candidates: dict[str, list[tuple[float, str, str]]] = {note.key: [] for note in note_list}
    for (left_key, right_key), evidence in pair_evidence.items():
        rationale = evidence.rationale()
        candidates[left_key].append((evidence.score, right_key, rationale))
        candidates[right_key].append((evidence.score, left_key, rationale))

    selected: dict[str, dict[str, str]] = {note.key: {} for note in note_list}
    for note in note_list:
        ranked = sorted(
            candidates[note.key],
            key=lambda item: (-item[0], notes[item[1]].title),
        )
        for _, other_key, rationale in ranked[:related_limit]:
            selected[note.key][other_key] = rationale
            selected[other_key][note.key] = rationale

    updated = 0
    for note in note_list:
        related_items = sorted(
            ((notes[key].title, rationale) for key, rationale in selected[note.key].items()),
            key=lambda item: item[0].casefold(),
        )
        base_body = strip_related_block(note.path.read_text(encoding="utf-8"))
        frontmatter, raw_body = split_frontmatter(base_body)
        clean_body = strip_related_block(raw_body)
        related_block = render_related_block(related_items)
        final_body = clean_body if not related_block else f"{clean_body}\n\n{related_block}".strip()
        new_content = render_frontmatter(
            [str(tag) for tag in frontmatter.get("tags", []) or []],
            str(frontmatter.get("flomo_created_at", note.created_at)),
            str(frontmatter.get("flomo_idempotency_key", note.key)),
            str(frontmatter.get("flomo_source_zip", "")),
        )
        new_content = f"{new_content}\n{final_body}\n"
        current_content = note.path.read_text(encoding="utf-8")
        if current_content != new_content:
            note.path.write_text(new_content, encoding="utf-8")
            updated += 1
        note.body = clean_body
    return updated


def export_zip(
    zip_path: pathlib.Path | str,
    output_dir: pathlib.Path | str,
    related_limit: int = 4,
    title_mode: str = "llm",
    title_generator: Callable[[list[str], str], str] | None = None,
    title_model: str | None = None,
    title_api_key: str | None = None,
    title_base_url: str | None = None,
) -> dict[str, int]:
    zip_path = pathlib.Path(zip_path)
    output_dir = pathlib.Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    vault_root = require_obsidian_vault_root(pathlib.Path.cwd())
    vault_index = build_vault_file_index(vault_root)
    resolved_title_generator = title_generator or build_title_generator(
        title_mode=title_mode,
        title_model=title_model,
        title_api_key=title_api_key,
        title_base_url=title_base_url,
    )

    existing_notes = scan_existing_notes(output_dir)
    reserved_titles = {note.path.stem for note in existing_notes.values()}

    # Build reverse index: flomo_created_at -> ManagedNote for detecting edits
    notes_by_created_at: dict[str, ManagedNote] = {}
    for note in existing_notes.values():
        if note.created_at:
            notes_by_created_at[note.created_at] = note

    created = 0
    skipped = 0
    replaced = 0

    with zipfile.ZipFile(zip_path) as archive:
        for memo in parse_zip(zip_path):
            key = memo_key(memo.created_at, memo.raw_blocks)
            if key in existing_notes:
                skipped += 1
                continue

            # Check if an older version of the same memo exists (same
            # created_at but different content hash).  If so, remove it
            # so the new version takes its place.
            old_note = notes_by_created_at.get(memo.created_at)
            if old_note is not None and old_note.key != key:
                old_path = old_note.path
                if old_path.exists():
                    old_path.unlink()
                # Remove stale entries from both indexes
                existing_notes.pop(old_note.key, None)
                reserved_titles.discard(old_note.title)
                replaced += 1

            tags, body_blocks = extract_tags_and_body(memo.raw_blocks)
            body_blocks, obsidian_embed_targets = extract_obsidian_file_embeds(body_blocks, vault_index)
            created_date = memo.created_at.split(" ", 1)[0]
            fallback_title = summarize_title(body_blocks)
            title = resolved_title_generator(body_blocks, fallback_title)
            note_path = unique_note_path(output_dir, created_date, title, reserved_titles, key)
            attachment_names = copy_attachments(archive, output_dir, key, memo.file_sources)
            body = render_note_body(body_blocks, attachment_names, obsidian_embed_targets)
            content = (
                f"{render_frontmatter(tags, memo.created_at, key, zip_path.name)}\n"
                f"{body}\n"
            )
            note_path.write_text(content, encoding="utf-8")
            new_note = ManagedNote(
                key=key,
                title=note_path.stem,
                path=note_path,
                created_at=memo.created_at,
                created_date=created_date,
                tags=tags,
                body=body,
            )
            existing_notes[key] = new_note
            notes_by_created_at[memo.created_at] = new_note
            created += 1

    linked = update_related_links(existing_notes, related_limit=related_limit)
    return {"created": created, "skipped": skipped, "replaced": replaced, "linked": linked}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert a Flomo export zip into Obsidian markdown notes.",
    )
    parser.add_argument("--zip", required=True, help="Path to the Flomo export zip file")
    parser.add_argument(
        "--out",
        default=".",
        help="Output root directory. Notes are written under ./YYYY-MM-DD/ and attachments go to ./attachments/",
    )
    parser.add_argument(
        "--related-limit",
        type=int,
        default=4,
        help="Maximum number of related note wikilinks to keep per note",
    )
    parser.add_argument(
        "--title-mode",
        choices=("llm", "heuristic"),
        default="llm",
        help="How to generate filenames. 'llm' is default: start with heuristic titles and only ask the model when the heuristic result is generic or too short.",
    )
    parser.add_argument(
        "--title-model",
        help="Model name for LLM title generation. Defaults to FLOMO_TITLE_MODEL, OPENAI_MODEL, or deepseek-chat.",
    )
    parser.add_argument(
        "--title-base-url",
        help="Base URL for an OpenAI-compatible API. Defaults to FLOMO_TITLE_BASE_URL, OPENAI_BASE_URL, or https://api.deepseek.com.",
    )
    parser.add_argument(
        "--title-api-key",
        help="API key for filename generation. Defaults to FLOMO_TITLE_API_KEY or OPENAI_API_KEY.",
    )
    args = parser.parse_args()

    try:
        stats = export_zip(
            args.zip,
            args.out,
            related_limit=max(args.related_limit, 0),
            title_mode=args.title_mode,
            title_model=args.title_model,
            title_api_key=args.title_api_key,
            title_base_url=args.title_base_url,
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    print(
        "created={created} skipped={skipped} replaced={replaced} linked={linked}".format(
            **stats,
        )
    )


if __name__ == "__main__":
    main()
