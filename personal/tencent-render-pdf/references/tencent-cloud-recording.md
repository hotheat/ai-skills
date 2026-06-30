# Tencent Meeting Cloud Recording Reference

Read this reference when working with Tencent Meeting cloud recording APIs, transcript pagination, signed media URLs, or sensitive acquisition artifacts.

## Access and Session

- Use the user's real Chrome login session for `meeting.tencent.com`.
- Prefer selecting an already open recording tab over opening a duplicate tab.
- If the page shows QR login, password entry, permission request, expired share, or inaccessible recording, stop and ask the user to resolve access.
- Do not claim the recording is unavailable until checking the visible page and the relevant network responses.

## Common Network Requests

The exact request IDs vary. Search by URL substring or response keys.

| Request | Purpose | Useful fields |
|---------|---------|---------------|
| `common_record_info` | primary metadata | `data.meeting_info`, `data.recordings`, `allow_download`, `minutes_exportable` |
| `uni_record_id` | COS path component | `data.uni_record_id` |
| `multi_record_file` | file size and resource types | `data.files`, `data.total_size` |
| `minutes/detail` | transcript paragraphs | `data.minutes.paragraphs` |
| `summary_note` | platform summary | `data.official_template_summary.summary_infos` |
| `query_timeline` | chapter-like timeline | `data.timeline_info.timeline_infos` |
| `critical_node` | screen share and important events | `data.critical_nodes` |
| `video_sign` | signed media hint | top-level or nested `signurl` |
| media `*.mp4` | actual playback request | status `206`, `content-range`, `content-length` |

## Metadata Parsing

- `meeting_info.subject` may be base64 encoded; decode before using it as the note title.
- `recordings[0].duration` is usually milliseconds.
- `recordings[0].cover_url` can be signed; download it early with `Referer: https://meeting.tencent.com/`.
- `allow_download=false` means the web UI may hide download. It does not mean the browser has no playback request. Process only recordings the user is authorized to view.
- Preserve `meeting_id`, `recording_id`, `uni_record_id`, `duration`, `size`, `title`, and `source_url` in `metadata.json`.
- Never persist signed URLs or cookies in `metadata.json`.

## Minutes Transcript

Prefer Tencent minutes over ASR when present.

The endpoint is commonly:

```text
https://meeting.tencent.com/wemeet-cloudrecording-webapi/v1/minutes/detail
```

Observed behavior:

- Pagination uses `pid`.
- `start_pid` may be ignored.
- Fetch page `pid=0`, then set the next `pid` to the last returned paragraph `pid + 1`.
- Stop on an empty page, duplicate `pid`, duplicate first paragraph, or unchanged last paragraph.
- Preserve paragraph and sentence timestamps; do not flatten before frame search.

Export shape:

- `transcript_paragraphs.json`: normalized paragraph list
- `transcript.srt`: sentence-level timestamped subtitles
- `transcript.md`: paragraph-level transcript with speaker names and time ranges
- `transcript.txt`: plain paragraph text

If minutes are unavailable or incomplete, extract audio from the downloaded media and use the same fallback order as Bilibili: remote ASR via `.env` `ASR_SERVICE_URL`, then local Whisper, then visual-only mode.

## Summary and Timeline

`summary_note` often contains `official_template_summary.summary_infos` with Markdown-like content. Export it to `summary.md`.

`query_timeline` often contains `timeline_info.timeline_infos`, each with:

- `start_time`: seconds from recording start
- `content`: chapter summary

Export it to `timeline.md` and use it to split transcript chunks. Treat it as an outline hint; verify important claims against transcript and frames.

## Signed Video and Download

Tencent cloud recordings commonly use COS signed URLs. There are two useful sources:

1. `video_sign` response `signurl`
2. actual browser `media` request after pressing play

Pitfalls:

- `signurl` can return 403 when requested without the same Chrome cookies.
- The browser media request may be `206 Partial Content` with `Range: bytes=0-` but still returns the whole file.
- `Content-Length` and `Content-Range` are the best indicators of expected file size.
- Download with Chrome cookies and playback-like headers:

```text
Referer: https://meeting.tencent.com/
Accept: */*
Accept-Encoding: identity;q=1, *;q=0
Range: bytes=0-
Sec-Fetch-Dest: video
Sec-Fetch-Mode: no-cors
Sec-Fetch-Site: same-site
```

Use `yt-dlp --cookies-from-browser chrome --cookies tencent_cookies.txt --skip-download --simulate <url>` only to export cookies when needed. The Tencent URL may be unsupported by yt-dlp; a non-zero exit can still leave a valid Netscape cookie jar.

Delete `tencent_cookies.txt`, raw `.network-request`, raw `.network-response`, and files containing `token=` before final delivery.

## Safe Logging

When printing diagnostics:

- print host and path, not query string
- print token length, not token value
- print cookie count, not cookie content
- print file sizes and hashes
- call a URL "signed media URL" instead of pasting it

Sensitive regexes to check before final response:

```bash
rg -n 'we_meet_token|hy_anon_token|ACTIVITY_TICKET|token=|Set-Cookie|Cookie:' .
```

## Frame and Meeting UI Noise

Reject these as teaching figures unless directly relevant:

- QR login, permission, password, expired share screens
- participant grid, mute prompt, "can you see my screen" screens
- Tencent Meeting controls, chat panel, transcript side panel
- desktop wallpaper or idle app switching
- blank title slides when a nearby content slide is better

Prefer slide states that are fully revealed, annotated, and readable.
