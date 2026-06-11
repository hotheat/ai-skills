---
name: export-flomo-to-obsidian
description: Export Flomo zip archives into Obsidian notes with preserved frontmatter, tags, attachments, date-based output folders, idempotent re-runs, and related-note wikilinks that include explicit evidence. Use when the user provides a Flomo export zip that contains one root HTML file plus a `file/` attachment tree and wants one Obsidian note per memo grouped under `YYYY-MM-DD/` directories inside an Obsidian vault, with attachments copied into a local `attachments/` directory.
---

# Export Flomo To Obsidian

Convert a Flomo export package into Obsidian-friendly Markdown with deterministic frontmatter and stable idempotency keys. The bundled script handles the mechanical work; use Obsidian-aware review only after the import succeeds.

## Quick Start

Before running the exporter, make sure the current working directory is inside the target Obsidian vault. The script checks for a `.obsidian/` directory in the current directory or its parents. If that check fails, stop and switch into the target Obsidian repository first.

Run the exporter from inside the vault:

```bash
cd /path/to/obsidian-vault
python3 scripts/export_flomo_zip.py \
  --zip /path/to/flomo-export.zip \
  --out /path/to/obsidian/folder
```

By default, the exporter uses `--title-mode llm`, but the actual priority is heuristic-first: it generates a filename from the memo text locally, then asks an OpenAI-compatible model only when that heuristic result is generic or too short. This skill defaults to `deepseek-chat` at `https://api.deepseek.com`. If `FLOMO_TITLE_API_KEY` is already exported in your shell, that is enough to enable the fallback model path without passing extra CLI flags. If the API call fails, it keeps the heuristic title. Use `--title-mode heuristic` to disable model fallback entirely.

This writes:

- One `.md` file per memo into `YYYY-MM-DD/` subdirectories under the target folder
- Attachments into `./attachments/`
- Obsidian wikilinks for related notes inside a managed `## Related` block

Example:

```text
Flomo/
  2026-04-13/手绘风信息图提示词.md
  2026-04-13/另一个标题.md
  2026-04-14/后一天的笔记.md
  attachments/<hash>-01.png
```

## Workflow

1. Confirm the input is a Flomo export zip with exactly one `.html` file and a `file/` subtree.
2. Confirm the current working directory is already inside the destination Obsidian vault. If not, change directories before continuing.
3. Run `scripts/export_flomo_zip.py`.
4. Spot-check a few generated notes:
   - Frontmatter contains `tags`, `created`, `flomo_created_at`, and `flomo_idempotency_key`
   - `tags` only come from explicit Flomo hashtag lines that start with `#`; never infer tags from prose
   - Images render as `![[attachments/...]]`
   - Any `ObsidianFile：filename.ext` directive has been converted into an embed such as `![[filename.ext]]`
   - Re-running the script skips already imported memos
5. If the user wants the result inside an active vault, use `obsidian-cli` to inspect imported notes, backlinks, or tags after the filesystem export is done.
6. If the user wants a visual map, derive a `.canvas` from the generated related-note links only after the notes are stable.

## Output Rules

- Preserve memo body text as Markdown paragraphs.
- Convert only explicit Flomo hashtag lines such as `#deepresearch/案例` into frontmatter `tags`.
- Treat `#...` inside ordinary prose as body text, not as a tag.
- Copy note images into the current export folder's `attachments/` directory.
- Write note files into `<输出目录>/<created-date>/标题.md`.
- Use one note per memo.
- Generate note filenames from the memo content summary without duplicating the date in the filename, then keep them stable once written.
- Treat idempotency as `created_at + original text content`. The bundled script stores the resulting hash in `flomo_idempotency_key`.
- On repeat exports, do not duplicate notes. Only refresh the managed related-note block when links need to change.
- Every generated related link must carry a short rationale based on evidence from the two notes, not a naked `[[Note]]` guess.
- Related links must be conservative: require at least one exact shared Flomo tag plus additional supporting evidence from the note bodies. Do not create keyword-only or phrase-only related links.
- If a memo contains `ObsidianFile：<文件名>`, search the current Obsidian vault for that file and convert the directive into an Obsidian embed such as `![[llm_wiki_summary.pdf]]`.
- Remove the raw `ObsidianFile：...` directive from the exported body once the embed has been inserted.

## Bundled Script

Use `scripts/export_flomo_zip.py` for the actual conversion.

Arguments:

- `--zip`: required Flomo export zip
- `--out`: output root folder; defaults to the current directory. Notes go under `YYYY-MM-DD/` subdirectories.
- `--related-limit`: max related-note links per note; defaults to `4`
- `--title-mode`: `llm` or `heuristic`; defaults to `llm` and means heuristic-first with optional LLM fallback for weak titles
- `--title-model`: optional model name; otherwise uses `FLOMO_TITLE_MODEL`, `OPENAI_MODEL`, or the built-in default `deepseek-chat`
- `--title-base-url`: optional OpenAI-compatible base URL; otherwise uses `FLOMO_TITLE_BASE_URL`, `OPENAI_BASE_URL`, or the built-in default `https://api.deepseek.com`
- `--title-api-key`: optional API key; otherwise uses `FLOMO_TITLE_API_KEY` or `OPENAI_API_KEY`

The script aborts early with a clear message if the current working directory is not inside an Obsidian vault.

Typical output:

```text
created=12 skipped=188 linked=27
```

Interpretation:

- `created`: new memo notes written in this run
- `skipped`: memos already imported earlier
- `linked`: note files whose related-link block changed

The managed related block uses this pattern:

```markdown
## Related

- [[Other Note]]: 共享标签 `topic/subtopic`；共同短语 `技能文件`
```

Only write a link when both notes share at least one exact Flomo tag and there is additional supporting evidence from shared English keywords or shared Chinese phrases. Shared roots, loose topical similarity, or keyword-only overlap are not enough.

## Obsidian Conventions

- Keep internal note references as wikilinks: `[[Note Name]]`.
- Keep image embeds as Obsidian embeds: `![[attachments/file.png]]`.
- Do not replace the generated `flomo_idempotency_key` unless you intentionally want to break idempotency detection.
- If you manually improve a note title or body, preserve the frontmatter keys so future runs still recognize the note.

## Working With Other Obsidian Skills

- Use `obsidian-markdown` when you need to hand-edit the exported note format, frontmatter, or wikilinks.
- Use `obsidian-cli` when the notes need to be inspected inside a running vault, or when the user asks for vault search, tag counts, or backlink verification.
- Use `json-canvas` only if the user explicitly asks for a canvas view of the imported note graph.

## Validation

Before claiming the skill works:

```bash
python3 scripts/test_export_flomo_zip.py
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" .
```

For a real export, also run the exporter on an actual Flomo zip and inspect the produced notes.
