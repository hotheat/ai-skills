---
name: bilibili-render-pdf
description: Generate a professional, detailed, figure-rich LaTeX course note and final PDF from a Bilibili lecture, tutorial, or technical talk. Use when the user provides a Bilibili URL (BV number) and wants structured Chinese teaching notes that combine the video's title, chapters, diagrams, formulas, code, subtitle explanations, the original video cover on the front page, and a final synthesis chapter, with key frames extracted from the highest usable video resolution and inserted as figures, and where the final deliverable must include a rendered PDF. Prefer CC subtitles, then a remote ASR service from `.env` `ASR_SERVICE_URL` when configured, then local Whisper, and finally visual-only mode when transcription is not usable.
---

# Bilibili Render PDF

Use this skill to turn a Bilibili video into a complete, compileable `.tex` note and a rendered PDF.

This skill extends the `youtube-render-pdf` workflow with Bilibili-specific adaptations for subtitle scarcity, login-gated high resolution, multi-part (分P) videos, and platform-specific non-teaching content.

## Bilibili vs YouTube: Key Differences

| Aspect | Handling |
|--------|----------|
| **Subtitle scarcity** | Try CC subtitles first → fall back to remote ASR from `.env` `ASR_SERVICE_URL` → fall back to local Whisper → visual-only mode |
| **Login-gated HD** | 1080P+ requires cookies; prompt the user to use `yt-dlp --cookies-from-browser chrome` |
| **Multi-part videos** | Detect 分P videos and ask the user which parts to process |
| **URL formats** | Support `bilibili.com/video/BVxxxxxxx` and `b23.tv` short links |
| **Danmaku** | Do not use danmaku as a teaching content source (too noisy); use only CC subtitles or Whisper output |

## Goal

Produce a professional Chinese lecture note from a Bilibili URL.

The output must:

- use the video's actual teaching content rather than subtitle transcription alone
- place the video's original cover image on the front page of the `.tex` and rendered PDF whenever available
- include all necessary high-value key frames as figures, without adding redundant screenshots
- end with a final synthesis section that includes the speaker's substantive closing discussion and your own distilled takeaways
- be structurally organized with `\section{...}` and `\subsection{...}`
- be a complete `.tex` document from `\documentclass` to `\end{document}`
- be compiled successfully to PDF as part of the final delivery

## Pedagogical Standard

The notes must read like a strong human teacher is guiding the reader through the material.

- organize each major section so the reader first understands the motivation, then the main idea, then the mechanism, then the example or evidence, and finally the takeaway
- be patient and explicit about logical transitions; make it clear why the speaker introduces a concept, what problem it solves, and how the next idea follows
- aim for deep-but-accessible explanations: keep the technical depth, but introduce formalism only after giving intuition in plain language
- when a section is dense, break it into smaller subsections that progressively build understanding rather than compressing everything into one long derivation
- do not dump subtitle content in chronological order; rewrite it into a teaching sequence with clear intent, contrast, and buildup

## Source Acquisition

### Per-Video Working Directory (Mandatory First Step)

Before metadata inspection, subtitle acquisition, audio extraction, frame extraction, or LaTeX/PDF generation, create and enter an isolated working directory for the target video ID.
All subsequent commands for that video must run inside this directory so concurrent jobs for different videos cannot overwrite shared artifacts such as `audio.wav`, subtitle files, frames, `notes.tex`, or compiled PDF outputs.

1. Resolve the stable video ID first.
   Use the `BV...` ID from a normal Bilibili URL.
   For `b23.tv` short links, resolve the final URL first, then extract the `BV...` ID.
   For multi-part videos, keep one root directory per `BV...` video and use part-specific filenames or subdirectories only when needed.

2. Create the working directory under the user's current project/output directory, then `cd` into it before running acquisition commands.
   Prefer this layout:

```bash
VIDEO_ID="BVxxxxxxxxxx"
WORKDIR="${VIDEO_ID}"
mkdir -p "$WORKDIR"
cd "$WORKDIR"
```

3. Preserve remote ASR configuration after changing directories.
   If the original invocation directory has a `.env`, copy or symlink it into the per-video working directory before running `transcribe_audio.py`, because the script reads `.env` from the current working directory.

```bash
test -f ../.env && cp ../.env .env
```

4. Keep all generated artifacts for the video inside this directory.
   Do not write reusable filenames such as `audio.wav`, `metadata.json`, `notes.tex`, `frames/`, or `segment_*.tex` in the parent directory or in the skill directory.

### Metadata Inspection

1. Inspect the video metadata first.
   Prefer title, chapters, duration, thumbnail availability, and subtitle availability before writing.

2. Detect multi-part (分P) videos.
   List all parts and ask the user which parts to process before downloading.

### Subtitle Acquisition (Four-Level Fallback)

**Priority 1: CC subtitles (platform-embedded)**

Use manual subtitles over auto-generated subtitles when both are available.
Prefer `zh-Hans`, `zh-CN`, `zh`, or `ai-zh` subtitle tracks.
Preserve the subtitle timestamps; do not flatten subtitles into plain text too early if figures still need to be located.

```
yt-dlp --write-subs --sub-langs "zh-Hans,zh-CN,zh,ai-zh" --convert-subs srt \
  --skip-download -o "%(title)s.%(ext)s" "<URL>"
```

**Priority 2: Remote ASR via `.env` `ASR_SERVICE_URL` (when no CC subtitles are available)**

If the current working directory has a `.env` file with `ASR_SERVICE_URL=http://host:port/asr`, use the bundled script first.
The remote call must mirror the reference service contract from `news-intelligence-analysis`:

- send `multipart/form-data`
- file field name must be `audio_file`
- send query parameters `language` and `output`
- prefer remote timecoded output, not plain text alone
- when `output=json`, parse JSON response and read `text` plus `segments`

Use:

```bash
yt-dlp -x --audio-format wav -o "audio.%(ext)s" "<URL>"
python "${SKILL_DIR}/scripts/transcribe_audio.py" \
  audio.wav \
  --language zh \
  --remote-mode auto \
  --whisper-model medium
```

The script reads `.env` from the current working directory automatically.
Internally it first tries remote `srt`:

```bash
curl --silent --show-error --fail --max-time "${ASR_HTTP_TIMEOUT:-900}" \
  --request POST \
  --form "audio_file=@audio.wav" \
  "$ASR_SERVICE_URL?language=zh&output=srt"
```

If remote `srt` is unavailable, try remote `json` and convert `segments[start/end/text]` into a local `.srt` file.
Only fall back to local Whisper when the remote service still cannot produce usable subtitle timestamps for frame-time alignment.

**Priority 3: Local Whisper speech-to-text (when no remote ASR is configured, remote ASR fails, or timestamped SRT is still needed)**

Extract audio first, then transcribe with Whisper to produce a timestamped SRT file.

```
yt-dlp -x --audio-format wav -o "audio.%(ext)s" "<URL>"
whisper audio.wav --model medium --language zh --output_format srt --output_dir .
```

**Priority 4: Visual-only mode (when audio quality is too poor)**

Skip subtitles entirely and rely on dense frame sampling to extract teaching content from the video frames alone.

### Video and Cover Download

1. Acquire the video's original cover image before writing the `.tex`.
   Prefer the highest-resolution thumbnail exposed by the platform metadata.
   Save the selected cover locally and reference that local asset from the front page.

2. Prefer the best usable video source for figure extraction.
   Probe formats and choose the highest resolution that is actually downloadable in the current environment.
   Note that 1080P+ on Bilibili typically requires login cookies.

3. Keep all source artifacts local when practical.
   Typical working artifacts are metadata, the downloaded cover image, a timestamped subtitle file (CC, remote-ASR-generated, or Whisper-generated), optional remote-ASR transcript text, a local video file, and extracted frames.

## Long Video Strategy

When the video's total duration exceeds 20 minutes, or the video has multiple parts (分P), use the segmented writing workflow below. The single most common failure mode for long videos is loading all subtitles into context and attempting a single-pass write — this causes severe content compression as earlier subtitle content gets evicted from the context window before writing reaches later sections.

### Principle: Write While Reading, Not After Reading

Do not read all subtitle files first and then write the entire document from memory. Instead, write each section while the corresponding subtitle content is fresh in context. For every section or batch of sections, re-read the relevant SRT file(s) immediately before writing that section's LaTeX content.

### Segmented Writing Workflow

**Step 1: Build a global outline.**

Read all subtitle files to understand the full scope, then produce a structural outline that assigns section/subsection titles and maps each section to its source SRT file(s) and time ranges. Save this outline to a working file (e.g., `outline.md`).

**Step 2: Write in batches of 1–2 parts.**

For multi-part (分P) videos, group every 1–2 parts into a batch. For single long videos, split by chapter boundaries or 15–20 minute windows.

For each batch, use a subagent that:

1. Reads the outline (for context on its position in the whole)
2. Reads only this batch's SRT file(s) and inspects this batch's frames
3. Writes the complete LaTeX `\section` / `\subsection` content for its assigned sections, following the pedagogical standard and writing rules
4. Saves its output to a segment file (e.g., `segment_p01_p02.tex`)

Spawn subagents in parallel when possible — each batch is independent.

**Step 3: Integrate into the final document.**

The main agent collects all segment files and:

1. Assembles them in outline order into `notes.tex`
2. Deduplicates any overlapping content between adjacent segments
3. Adds cross-references and transitional paragraphs
4. Writes the front page, `\tableofcontents`, and final `\section{总结与延伸}`
5. Compiles to PDF

## Teaching Content Rules

Build the notes from all of the following when available:

- video title and chapter structure
- the video's original cover image and key metadata
- on-screen diagrams, formulas, tables, plots, and architecture slides
- subtitle explanations, examples, and verbal emphasis
- short high-signal original dialogue segments in interview, panel, podcast, or conversation videos, when the exact wording adds presence, humor, intuition, or unusually compact information
- code snippets shown or described in the talk

Skip content that does not contribute to the actual lesson:

- greetings
- small talk
- routine back-and-forth that does not add information, tension, humor, intuition, or teaching value
- sponsorship
- channel logistics (一键三连, 关注投币, etc.)
- closing pleasantries

Keep the speaker's closing discussion when it carries actual teaching value, such as synthesis, limitations, future work, tradeoffs, advice, or open questions.

## Writing Rules

1. Write the notes in Chinese unless the user explicitly requests another language.

2. Organize the document with `\section{...}` and `\subsection{...}`.
   Reconstruct the teaching flow when needed; do not blindly mirror subtitle order.
   Each section should answer, in order when applicable: what problem is being solved, why simpler views are insufficient, what the core idea is, how it works, and what the reader should retain.

3. Start from `assets/notes-template.tex`.
   Fill in the metadata block, including the local cover image path, and replace the body content block with the generated notes.

4. The front page must include the video's original cover image when available.
   Place it on the first page rather than burying it later in the document.
   Keep it visually distinct from in-body teaching figures.

5. Use figures whenever they materially improve explanation.
   Include as many figures as are necessary for teaching clarity, even if that means many figures across the document.
   Do not optimize for a small figure count; optimize for explanatory coverage and readability.
   Good figures are key formulas, diagrams, tables, plots, visual comparisons, pipeline schedules, architecture views, and stage-by-stage visual progressions.

6. Do not place images inside custom message boxes.

7. When a mathematical formula appears:
   first explain in plain Chinese what the formula is trying to express and why it appears
   show it in display math using `$$...$$`
   then immediately follow with a flat list that explains every symbol

8. When the video shows, discusses, or analyzes source code:
   actively extract key code snippets into `lstlisting` blocks — do not merely describe code in prose when a listing would be clearer.
   Explain the role of the code before the listing and summarize the expected behavior after it when useful.
   When the code is not fully legible in the video frame, reconstruct the essential logic from the speaker's explanation and mark it with a comment like `% 基于视频讲解重建`.
   Wrap all code in `lstlisting` with a descriptive `caption`.
   For source-code-analysis or architecture-walkthrough videos, code listings are a primary content element, not optional decoration.

9. Highlight teaching signals deliberately and repeatedly when the content justifies it:
   use `importantbox` for core concepts the reader must walk away with, including formal definitions, central claims, key mechanism summaries, theorem-like statements, critical algorithm steps, and compact restatements of the main idea after a dense explanation
   use `knowledgebox` for background and side knowledge that improves understanding without being the main thread, including prerequisite reminders, historical lineage, engineering context, design tradeoffs, terminology comparisons, and intuition-building analogies
   use `warningbox` for common misunderstandings and failure points, including notation overload, hidden assumptions, misleading heuristics, easy-to-make implementation mistakes, causal confusions, off-by-one style reasoning errors, and places where the speaker contrasts a wrong intuition with the correct one
   use `dialoguebox` only for conversation-heavy videos when a brief original dialogue segment is high-information, funny, vivid, or especially intuitive, and preserving the speaker's wording gives the reader a stronger sense of being present in the discussion
   a `dialoguebox` may contain either one exchange or several tightly connected turns, such as a question, follow-up, pushback, clarification, and answer sequence
   keep `dialoguebox` snippets short: preserve speaker labels and a concrete timestamp or interval, lightly clean obvious ASR errors only when confident, and follow the box with prose that explains why the dialogue segment matters
   do not use `dialoguebox` for greetings, filler, long transcript dumps, or dialogue that would be clearer as ordinary summarized exposition
   there is no quota of one box per section; add multiple boxes in a section when the material contains multiple distinct teaching signals
   each box should carry a specific pedagogical payload rather than generic emphasis
   prefer placing a box immediately after the paragraph, derivation, or example that motivates it
   routine exposition should stay in normal prose; boxes are for high-signal takeaways, not decoration
   figures must stay outside `importantbox`, `knowledgebox`, `warningbox`, and `dialoguebox`

10. End every major section with `\subsection{本章小结}`.
    Add `\subsection{拓展阅读}` when there are one or two worthwhile external links.

11. End the document with a final top-level section such as `\section{总结与延伸}`.
    That final section must include:
    - the speaker's substantive closing discussion, excluding routine sign-off language
    - your own structured distillation of the core claims, mechanisms, and practical implications
    - your expanded synthesis, including conceptual compression, cross-links between sections, and any careful generalization that stays faithful to the video
    - concrete takeaways, open questions, or next steps when the material supports them

12. Do not emit `[cite]`-style placeholders anywhere in the LaTeX.

## Figure Handling

Select figures by necessity and teaching value, not by an arbitrary quota or a bias toward keeping the document visually sparse.

When locating candidate frames, bias strongly toward recall before precision.
It is better to inspect too many nearby candidates first than to miss the one frame where the slide, formula, table, or diagram is finally fully revealed and readable.

Frame understanding must come from direct visual inspection.

- Use the `view image` tool to inspect candidate frames and crops before deciding what they show, how they should be described, and whether they are complete enough to include.
- Do not use OCR tools such as `tesseract` as a substitute for visual understanding of a frame.
- Do not infer a frame's semantic content only from nearby subtitles, filenames, or timestamps without checking the image itself.
- Contact sheets, montages, and tiled strips are good for recall, but final keep-or-reject decisions and semantic naming must be based on actual image inspection with `view image`.

### Frame Selection Checklist

Before inserting any video frame, first inspect several nearby candidates from the same subtitle-aligned interval and apply this checklist. If any item fails, reject the frame and keep searching nearby rather than forcing an approximate match.

- Relevance: the frame must directly support the exact concept discussed in the surrounding paragraph or subsection, not just the same broad topic.
- Required content visible: every visual element referenced in the text must already be visible in the frame.
- Fully revealed state: when slides, whiteboards, animations, or dashboards build progressively, use the final fully populated readable state rather than an intermediate state.
- Best nearby candidate: compare multiple nearby frames and prefer the one that is both most complete and most readable.
- Readability: text, formulas, labels, and diagram structure must be legible enough to justify inclusion.

### Frame Naming

- Use neutral timestamp-based names for raw candidate frames. Do not assign semantic names before inspecting the actual frame content.
- Rename a frame semantically only after visually confirming what is fully visible in the image.
- The semantic filename must describe the frame's actual visible content, not a guess based on subtitles, nearby narration, or the intended paragraph topic.
- If the frame is partially revealed, transitional, or ambiguous, keep searching and do not lock in a semantic name yet.

- Use the timestamped subtitle file (CC, remote-ASR-generated SRT, or locally generated Whisper SRT) as the primary locator for key-frame search.
- First identify the subtitle span that corresponds to the concept, example, formula, or visual explanation being discussed.
- Then search within that subtitle-aligned time interval, and slightly around its boundaries when needed, to find the best readable frame.
- Do not jump directly from one guessed timestamp to one extracted frame.
  First generate a dense candidate set across the relevant interval, then inspect and down-select.
- Prefer tools that help you inspect many nearby candidates at once, such as `magick montage`, contact sheets, tiled frame strips, or equivalent workflows.
  Use them to maximize recall and avoid missing the frame where the visual content is fully present.
- When the visual is a progressive PPT reveal, animation build, whiteboard accumulation, or dashboard state change, explicitly search for the final fully populated state.
  Do not stop at the first frame that seems approximately correct.
- If several nearby candidates differ only by progressive reveal state, keep checking until you find the frame with the most complete readable information.
- When in doubt between a sparse early frame and a denser later frame from the same explanation window, prefer the later frame if it is materially more complete and still readable.
- Include every figure that is necessary to explain the content well.
- It is acceptable, and often desirable, to include several figures within one section or subsection when the video builds an idea in stages.
- Omit repetitive or low-information frames.
- Extract frames near chapter boundaries and explanation peaks when chapters exist, but still validate them against subtitle timing.
- Search nearby timestamps when the first extracted frame catches an animation transition.
- Crop, enlarge, or isolate the relevant region when the full frame is too loose.
- When a slide reveals content progressively, capture the final readable state and add intermediate frames only when they teach a genuinely different step.
- For dense visual sections, it is acceptable to over-sample first and discard later.
  Do not optimize candidate count so early that key visual states are never inspected.
- Prefer a sequence of necessary figures over one overloaded figure with unreadable labels.
- Preserve readability of formulas and labels.

## Figure Time Provenance

Whenever the `.tex` or PDF references a specific video frame, or a crop derived from a video frame, record its source time interval on the same page as a bottom footnote.

- The footnote must show the concrete time interval, for example `00:12:31--00:12:46`.
- The interval should come from the subtitle-aligned segment used to locate the figure, not from a vague chapter-level estimate.
- If the figure is a crop, the footnote still refers to the original video time interval of the source frame or subtitle span.
- If several nearby frames in one figure all come from the same subtitle interval, one clear footnote is enough.
- Keep the figure and its time footnote anchored to the same page; prefer layouts such as `[H]`, a non-floating block, or another stable placement when ordinary floats would separate them.

## Visualization

For concepts that remain hard to explain with only screenshots and prose, add accurate visualizations.

Two acceptable routes:

- generate LaTeX-native visualizations with TikZ or PGFPlots
- generate figures ahead of time with scripts and include them as images

For script-generated illustrations, prefer Python tools such as `matplotlib` and `seaborn` when they are the clearest way to produce an accurate teaching figure.

When a visualization is generated externally rather than drawn natively in LaTeX:

- export the figure as `pdf` so it can be inserted into the `.tex` without rasterization loss
- prefer vector output for plots, charts, and schematic illustrations
- avoid `png` or `jpg` for script-generated teaching figures unless the content is inherently raster

When the source material contains relationships, results, or equations that would be clearer when redrawn than when shown as a screenshot, prefer rebuilding them with LaTeX-native tools or with `matplotlib` / `seaborn`.

Use visualizations for:

- process flows, pipelines, and architecture overviews
- curves and charts such as scaling laws, training curves, benchmark results, and ablation comparisons
- distributions, correlations, heatmaps, and other plots that explain data relationships
- complex functions, surfaces, contour plots, and geometric intuition figures
- tables or comparisons that become clearer when redrawn as charts
- summary diagrams that compress a section's core mechanism or takeaway into one figure

Do not add decorative graphics that do not teach anything.

## Final Checklist

Before delivery, verify all of the following:

- no important teaching content has been dropped, and no concrete but critical detail has been lost during condensation, restructuring, or summarization
- the text and figures are aligned: each inserted frame supports the surrounding explanation, necessary crops have been applied, and the chosen frame shows the fullest relevant information rather than a transitional or incomplete state
- the document is visually rich enough for teaching: check whether more high-information key frames should be added, and whether additional LaTeX-native or Python-script-generated illustrations would improve clarity
- **segmented writing check**: for long or multi-part videos, each section was written with its source SRT fresh in context (via the segmented writing workflow), not from compressed memory of a prior read
- **per-section check**: every major `\section` has substantive content — motivation, mechanism, and takeaway paragraphs, not one-line summaries; sections covering code or architecture include `lstlisting` blocks

## Delivery

Deliver all of the following:

- the final `.tex` file
- the downloaded cover image referenced on the front page
- any extracted or generated figure assets referenced by the document
- the compiled PDF
- the remote-ASR-generated SRT subtitle file, if remote ASR was used
- the remote-ASR transcript text file, if remote ASR was used
- the Whisper-generated SRT subtitle file, if local Whisper was used for timestamps or speech-to-text

## Asset

- `assets/notes-template.tex`: default LaTeX template to copy and fill
