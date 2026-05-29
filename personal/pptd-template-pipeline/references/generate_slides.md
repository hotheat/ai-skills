# Generate Slides Workflow

## 1. Classify Inputs

Identify the available inputs:

- Template: uploaded PPT/PPTX, screenshots, or existing PPTD/page files.
- Content: existing long document, article, report, research notes, topic brief, key points, user outline, or existing source deck.
- Output target: PPTD deck, PPTX export, `.page` edits, or checker repair.

For a research-plus-template task, assume the deck must be newly generated in PPTD format unless the user asks only for analysis.
For an existing long document plus template task, use summary mode before outline mode.

## 2. Follow the Operation Trace

For Kimi-style template generation, preserve this concrete action sequence:

1. Read production rules: `SKILL.md`, `generate_slides.md`, `template_mode.md`, then later `summary_mode.md`, `outline_mode.md`, `pptd.md`, and `general.md` when a long source document is detected.
2. Run terminal commands or Python helpers to inspect the uploaded PPT/PPTX, render screenshots, convert the template into PPTD/page files, and list the produced artifacts.
3. Run the checker on the converted template when possible and record inherited template warnings.
4. Read the template screenshots and generated `page1.page` through `pageN.page` files to understand both appearance and structure.
5. For existing documents, record source understanding in `source_profile.md` and source-to-slide coverage in `source_map.md`.
6. Think through the deck plan and record it in `outline.md` and `design.md`.
7. Generate the main `.pptd` file as the manifest.
8. Generate `.page` slide files in batches.
9. Run the PPTD checker from the terminal.
10. Read every `.page` named by checker output.
11. Edit the affected `.page` files with precise text, bounds, and position changes.
12. Re-run the checker and repeat until real errors are zero.

Python is appropriate for mechanical inspection or conversion helpers provided by the active PPTD environment. Manual `.page` content and layout edits should remain reviewable and should be tied to checker output.

## 3. Set Up Working Files

Create a focused work directory for the deck. Standard planning files:

- `outline.md`: slide order, section names, slide goals, and main messages.
- `design.md`: extracted template rules, tokens, page types, and accepted warning rationale.
- `source_profile.md`: source document thesis, section inventory, must-keep details, and intentional omissions.
- `source_map.md`: source-section to slide-page mapping for traceable coverage.
- `<deck_name>.pptd`: manifest or entry point referencing every `.page`.
- `*.page`: one page file per slide.

Use stable, semantic file names. For example:

- `cover.page`
- `toc.page`
- `ch01.page`
- `arch_overview.page`
- `checkpoint_flow.page`
- `streaming_flow.page`
- `final.page`

Numbered names are also valid when they improve order clarity:

- `page07_compaction_design.page`
- `page08_transcript_tree.page`
- `page09_compaction_conflict.page`

## 4. Plan the Deck

Build the slide sequence from the user's goal and research content:

- Cover: title, subtitle, date/context.
- TOC: chapter list.
- Chapter divider pages: one per major section.
- Content pages: architecture, process, data flow, comparison, risks, implementation details.
- Final page: conclusion, summary, or thanks.

Keep each content page focused on one job. Prefer several clean pages over one dense page that will fail checker validation.
For existing documents, every content slide should map back to a source section in `source_map.md`.

## 5. Generate in Batches

Generate page files in batches so errors are easier to isolate.

One semantic-name batch could be:

- `cover.page`
- `toc.page`
- `ch01.page`
- `arch_overview.page`
- `ch02.page`
- `checkpoint_design.page`
- `checkpoint_flow.page`
- `ch03.page`

Second semantic-name batch:

- `message_store.page`
- `message_flow.page`
- `ch04.page`
- `streaming_exec.page`
- `streaming_flow.page`
- `ch05.page`
- `tool_arch.page`
- `tool_patterns.page`
- `final.page`

After each batch, run or prepare to run the checker before adding more complexity.
When using numbered names, keep the same batch strategy and preserve stable page order in the manifest.

In the OpenClaw/Kimi run, the actual generated pages used numbered names such as `page07_compaction_design.page`, `page08_transcript_tree.page`, and `page13_event_streaming.page`.

## 6. Author for the Checker

While writing pages:

- Keep text concise and slide-native.
- Use the template's existing title styles and page archetypes.
- Give text boxes enough bounds for the longest expected line.
- Avoid placing live text over decorative lines unless the template intentionally does so.
- Use consistent spacing for repeated cards or flow nodes.
- Prefer explicit x/y/width/height adjustments over vague visual intent.

## 7. Validate and Iterate

Run the PPTD checker. Then:

1. Read the checker output.
2. Open every named `.page`.
3. Make targeted edits.
4. Re-run the checker.
5. Repeat until real errors are zero.

The checker loop is part of generation, not a final optional polish step.
