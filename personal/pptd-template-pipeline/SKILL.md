---
name: pptd-template-pipeline
description: Use when turning an existing long document, research notes, a topic brief, or key points plus an uploaded PPT/PPTX template into a PPTD deck. Covers document summarization mode, template design-system extraction, outline planning, generating .pptd and .page files, running the PPTD checker, and repairing TextOverflow, TextOcclusion, and TextUnderfill until final validation passes.
---

# PPTD Template Pipeline

## Purpose

Use this skill to reproduce the Kimi-style workflow for generating a presentation from research content and a PowerPoint template. The expected output is a checked PPTD deck: one `.pptd` manifest plus one `.page` file per slide, with real checker errors resolved and any remaining warnings explained as template design intent.

## Read First

Before creating slides, read the relevant generation instructions in this order:

1. `references/general.md`: baseline operating rules, quality gates, and final reporting.
2. `references/generate_slides.md`: end-to-end slide-generation workflow.
3. `references/template_mode.md`: template-driven PPT/PPTX ingestion and design-system extraction.
4. `references/summary_mode.md`: use when the user provides an existing long document or article as the content source.
5. `references/outline_mode.md`: use when the user provides only a topic, research notes, or key points rather than a page-by-page slide outline.
6. `references/pptd.md`: `.pptd` and `.page` authoring, checker commands, and repair loops.

If the active presentation/PPTD environment also contains upstream docs named `SKILL.md`, `generate_slides.md`, `template_mode.md`, `summary_mode.md`, `outline_mode.md`, `pptd.md`, or `general.md`, read those as source-of-truth implementation references too. Search for them with `rg --files | rg '(SKILL|generate_slides|template_mode|summary_mode|outline_mode|pptd|general)\.md$'` when their location is not obvious.

## Workflow

1. Confirm the task type.
   If an uploaded PPT/PPTX is intended as the visual driver, treat the task as template mode. If the content source is an existing article, report, transcript, or long Markdown document, use summary mode before outline planning. If the user gave only a topic and key points, treat the content plan as outline mode.

2. Read and inspect the template.
   Render or screenshot the template, convert it to PPTD/page form when possible, then inspect both visual screenshots and the generated `page1.page` through `pageN.page` files.

3. Extract the design system.
   Identify page archetypes, brand colors, typography, logo placement, title treatments, recurring decorations, layout grids, and which checker warnings come from intentional template art. Run the checker on the converted template when possible and record the inherited warning baseline.

4. Build the content plan.
   For existing documents, first create `source_profile.md` and `source_map.md`. Then create `outline.md` for the slide sequence and `design.md` for template rules. Transform source material into slide-ready claims, section structure, diagrams, flows, and concise text while preserving source coverage.

5. Generate the PPTD deck.
   Create the main `.pptd` manifest as the deck entry point, then create `.page` files in manageable batches. Keep page names stable and descriptive.

6. Run the PPTD checker and repair iteratively.
   Re-read every `.page` mentioned by checker output. Fix real `TextOverflow`, `TextOcclusion`, and `TextUnderfill` issues by shortening text, reducing font size, expanding bounds, moving elements, or adjusting spacing. Re-run the checker after each repair pass.

7. Final acceptance.
   Finish only when there are `0 errors`, `0 TextOverflow`, `0 TextOcclusion`, and `0 TextUnderfill`. Remaining warnings are acceptable only when they are inherited from the template's intentional decorations or known design intersections, and the final response must say so.

## OpenClaw Reference Pattern

The OpenClaw/Kimi example followed this shape:

- Read `SKILL.md`, `generate_slides.md`, and `template_mode.md`, then inspect `OTR-PPT-Template-simple.pptx` by screenshots and PPTD conversion.
- Extract five page types: cover, table of contents, chapter divider, content page, and final page.
- Capture the OTR template system: deep blue `#244EB1`, orange `#E68337`, Arial typography, top-right OTR logo, blue gradient title line, orange short rule, and wave/road background decorations.
- Because the user supplied a long Markdown article rather than a detailed page plan, use summary mode to profile the source, then outline mode to create a page plan.
- Create `source_profile.md`, `source_map.md`, `outline.md`, `design.md`, `openclaw_pi.pptd`, then numbered page files such as `page07_compaction_design.page`, `page08_transcript_tree.page`, `page09_compaction_conflict.page`, `page13_event_streaming.page`, and `page17_request_lifecycle.page`.
- Semantic names such as `checkpoint_flow.page` are acceptable, but they are examples, not required names.
- Iterate with the PPTD checker until all real text errors are cleared. Preserve inherited template warnings only after confirming they match the template baseline.
