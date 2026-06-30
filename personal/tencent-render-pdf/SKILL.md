---
name: tencent-render-pdf
description: Generate a professional Chinese LaTeX course note and compiled PDF from Tencent Meeting cloud recordings such as `https://meeting.tencent.com/cw/...`. Use when the user provides a Tencent Meeting recording link and wants metadata extraction, login/session handling, Tencent minutes transcript export, platform summary/timeline use, signed media download, key-frame extraction, figure-rich notes, and final PDF delivery. Prefer Tencent Meeting built-in minutes before ASR; use remote ASR or Whisper only when platform minutes are unavailable or incomplete.
---

# Tencent Render PDF

Use this skill to turn an accessible Tencent Meeting cloud recording into a complete `.tex` note and rendered PDF.

This skill adapts the YouTube/Bilibili render workflow to Tencent Meeting's logged-in web app, platform transcript APIs, signed COS media URLs, and browser-bound playback sessions.

## Tencent vs YouTube/Bilibili

| Aspect | Tencent Meeting handling |
|--------|--------------------------|
| Trigger input | Tencent Meeting cloud recording URL, usually `https://meeting.tencent.com/cw/<id>` |
| Login/session | Prefer the user's existing logged-in Chrome tab. If Codex-to-Chrome extension communication times out while Chrome, the extension, and native host are healthy, retry the same-profile connection up to 3 times before asking the user to open a Chrome window. If QR login, password, or permission approval blocks access, stop and ask the user to complete it. |
| Transcript | Prefer Tencent Meeting `minutes/detail` platform transcript. Paginate by `pid`. Use ASR only when minutes are missing or unusable. |
| Summary/timeline | Use Tencent `summary_note`, `query_timeline`, and visible page summary as outline hints, then verify against transcript and frames. |
| Video source | Extract signed media URL from `video_sign` or the actual browser `media` request after pressing play. Signed URLs may require cookies and `Range: bytes=0-`. |
| Download mode | Download with current Chrome cookies and playback-like headers; verify with `ffprobe`. Do not print signed URLs or cookies. |
| Noise filtering | Remove screen checks, login prompts, meeting controls, participant UI, idle desktop, and routine greetings unless educationally relevant. |

## Working Directory

Before metadata inspection, transcript export, video download, frame extraction, or LaTeX generation, create one isolated directory per recording under the user's current output directory:

```bash
REC_ID="Kex1Rowzc5"
WORKDIR="tencent_${REC_ID}"
mkdir -p "$WORKDIR"
cd "$WORKDIR"
```

Keep all generated artifacts inside that directory: `metadata.json`, `summary.md`, `timeline.md`, `transcript.srt`, `recording.mp4`, `cover.png`, `figures/`, `segments/`, `notes.tex`, and `notes.pdf`.

## Acquisition Workflow

1. Open or select the Tencent Meeting recording in the user's logged-in Chrome session.
   - Prefer an existing tab when the user says the page is already open.
   - If Chrome is running, the Codex extension is enabled, and the native host is healthy but Codex-to-extension communication times out, do not stop after the first timeout. Retry the connection up to 3 times against the same Chrome profile and existing logged-in state.
   - If the 3 retries still time out, then ask the user for confirmation before opening or focusing a same-profile Chrome window for a fresh handshake.
   - Do not bypass password, membership, or permission gates. Ask the user to complete access when blocked.
   - If a Chrome automation layer is unavailable, use another available browser inspection path and state the limitation.

2. Inspect network traffic and save only the needed JSON bodies.
   - Capture `common_record_info`, `multi_record_file`, `uni_record_id`, `minutes/detail`, `summary_note`, `query_timeline`, `critical_node`, `video_sign`, and the first `media` request if playback is needed.
   - Read `references/tencent-cloud-recording.md` when extracting API fields, paginating minutes, or downloading signed media.
   - Redact or delete raw request headers, cookies, signed URLs, and `.network-request` files before final delivery.

3. Extract metadata first.
   - Decode base64 `meeting_info.subject` when needed.
   - Record meeting ID, recording ID, duration, file size, title, cover availability, minutes availability, sharing/download permissions, and transcript source.
   - Download the cover image when `cover_url` is available.

4. Export transcript.
   - Use Tencent Meeting `minutes/detail` pages first. Pagination uses `pid`, not `start_pid`.
   - Convert pages to `transcript.srt`, `transcript.md`, `transcript.txt`, and `transcript_paragraphs.json`:

```bash
python "${SKILL_DIR}/scripts/extract_minutes.py" \
  --minutes-dir minutes_pages \
  --output-prefix transcript
```

5. Export summary and timeline.
   - Convert `official_template_summary.summary_infos` to `summary.md`.
   - Convert `timeline_info.timeline_infos` to `timeline.md`.
   - Treat them as outline hints, not as a substitute for reading transcript chunks.

6. Download the recording.
   - If `video_sign` `signurl` works, use it with cookies and playback-like headers.
   - If it returns 403, press play in the browser and use the actual `media` request URL.
   - Use `scripts/download_signed_media.py` without printing the signed URL:

```bash
python "${SKILL_DIR}/scripts/download_signed_media.py" \
  --url-file media_url.txt \
  --cookies tencent_cookies.txt \
  --output recording.mp4
ffprobe -v error -show_entries format=duration,size,bit_rate -show_streams -of json recording.mp4
```

7. Clean sensitive acquisition artifacts.
   - Remove exported cookie files, raw network request/response dumps, and files containing signed URLs once `recording.mp4`, transcript files, and metadata are verified.
   - Keep only redacted `metadata.json` fields in final output.

## PDF Writing Workflow

Start from `assets/notes-template.tex`. Preserve the Bilibili render standard unless Tencent-specific evidence requires a change:

- use the actual meeting content, not transcript dumps
- put the cover or best title frame on the front page
- include high-value frames as figures with same-page time footnotes
- end every major `\section` with `\subsection{本章小结}`
- end with a final top-level `\section{总结与延伸}` covering the speaker's substantive closing and your synthesis
- do not emit `[cite]` placeholders

For recordings longer than 20 minutes, use segmented writing:

1. Build `outline.md` from transcript, timeline, summary, and inspected frames.
2. Split transcript by timeline or 15-20 minute windows into `chunks/*.md`.
3. Write each section immediately after reading its source chunk and inspecting its relevant frames.
4. Assemble `segments/segment_*.tex` into `notes.tex`, deduplicate overlap, add transitions, then compile twice with XeLaTeX.

## Frame Handling

Use the timestamped transcript as the locator and the video frames as visual evidence.

- Generate broad contact sheets first for recall.
- Densely sample around transcript-aligned intervals.
- Use the image viewing tool to inspect candidate frames and crops before naming or inserting them.
- Reject login screens, desktop wallpaper, participant tiles, Tencent controls, blank slides, and transition frames unless they directly teach something.
- Prefer final fully revealed slide states over partial animation states.

## Verification

Before final delivery:

- `ffprobe` confirms local `recording.mp4` duration and size match Tencent metadata within reasonable tolerance.
- `transcript.srt` has timestamps covering the recording or the available transcript range.
- `notes.tex` has no `[cite]`, no signed URLs, and no cookie/token strings.
- `xelatex -interaction=nonstopmode -halt-on-error notes.tex` succeeds twice.
- `pdfinfo notes.pdf` reports a valid PDF.
- Render and inspect representative pages, including title page, a figure-heavy page, and the final page.
- Delete sensitive raw artifacts before final response.

## Delivery

Deliver:

- `notes.pdf`
- `notes.tex`
- `cover.png` or selected front-page image
- referenced `figures/`
- `metadata.json` with redacted provenance and hashes
- `transcript.srt`, `transcript.md`, and `transcript.txt` when Tencent minutes or ASR were used
- `recording.mp4` when downloaded for frame extraction
