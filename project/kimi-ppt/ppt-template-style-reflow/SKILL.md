---
name: ppt-template-style-reflow
description: Replicate the visual style of one PowerPoint template deck onto another content deck while preserving the content deck's page count and substantive content. Use for PPT/PPTX tasks such as "replace this deck's template with that deck", "use the first PPT as master/theme for the second PPT", "template style replication", "PPTD reflow", "keep all pages but restyle", or Kimi-style template extraction plus content re-layout workflows.
---

# PPT Template Style Reflow

## Core Contract

Transform a content deck by rebuilding it in the style of a template deck. Preserve the content deck's page count unless the user explicitly allows additions or deletions. Preserve all substantive text, tables, code, diagrams, screenshots, and image content; restyle and reposition them to match the template's visual system.

Use the PPTD workflow when available: convert both decks to `.pptd`, inspect the generated `.pptd`, `pages/*.page`, and `images/` files, create a new result `.pptd`, generate new `.page` files, run the checker, repair issues, then export/render the final PPTX.

Bundled scripts provide a portable baseline:

- `scripts/convert.sh`: convert a PPTX into a PPTD-like project for inspection and reflow. It extracts slide size, text boxes, images, basic shapes, and media resources.
- `scripts/check.sh`: statically validate a generated PPTD project for missing files, missing image sources, out-of-bounds elements, likely text overflow, underfilled text boxes, and likely occlusion.
- `scripts/generate_pages.py`: generate a result PPTD project from a compact JSON page plan using reusable cover, standard, section, process, and final page patterns.
- `scripts/export.sh`: export a generated PPTD project to PPTX through `pptxgenjs` when Node.js and that package are available.
- `scripts/render.sh`: render a generated PPTD project to an HTML preview for visual QA without requiring PowerPoint.

For the detailed Kimi-derived workflow and warning taxonomy, read `references/kimi-pptd-workflow.md`.

## Runtime Requirements

- Python 3 is required for conversion, checking, HTML rendering, and page generation.
- Node.js plus `pptxgenjs` is required only for `scripts/export.sh` PPTX export. In Codex desktop, `export.sh` automatically checks the bundled primary runtime node modules path. If `pptxgenjs` is unavailable, use `scripts/render.sh` for visual QA and an environment-specific presentation exporter for final PPTX.
- PowerPoint, WPS, or LibreOffice are optional for final manual inspection; the bundled checker and HTML renderer do not require them.

## Workflow

1. **Load the PPT toolchain docs.** Use the active presentation/PPTX skill or bundled PPTD tool docs. If no environment-specific PPTD tools are available, use this skill's bundled `scripts/convert.sh`, `scripts/check.sh`, `scripts/export.sh`, and `scripts/render.sh`.

2. **Convert both decks.** Convert the template PPTX and the content PPTX into separate `.pptd` folders:
   - `template_convert/`
   - `content_convert/`
   Keep their `pages/` and `images/` directories separate until result assembly.

3. **Inventory both decks.** Read each main `.pptd` file to confirm slide size, theme colors, and page count. Read every template page and every content page. Generate or inspect screenshots when page roles, diagrams, tables, or visual density are unclear.

4. **Extract template style.** Identify the template's reusable visual system:
   - logo assets and recurring placement
   - background images and decorative shapes
   - theme colors, accent colors, gradients, and line styles
   - title bars, section dividers, ending page patterns
   - typography, text hierarchy, margins, and spacing
   - table, list, card, flow, code, and image treatments

5. **Classify content pages.** Assign each content page a role such as cover, agenda, standard content, section divider, flow/process, table-heavy, image-heavy, code-heavy, or final. Do this from the content, not from page number alone.

6. **Map content pages to template archetypes.** Choose the closest template page style for each content page role. If template and content page counts differ, do not cycle blindly. Match semantics and information density, usually:
   - cover content -> cover template
   - standard explanatory content -> most flexible standard template page
   - chapter transition -> divider template
   - multi-flow/multi-module content -> grid or process template
   - final/thanks -> ending template

7. **Assemble result resources.** Create `result/pages` and `result/images`. Copy template images needed for the visual system. Copy content images, diagrams, screenshots, and other assets that must be preserved. Rename copied content assets when needed to avoid collisions, and update all `src` references.

8. **Generate the result `.pptd`.** Create a main `.pptd` with the content deck's page count and page order. Use the template's theme colors and result page paths. Generate `.page` files with scripts, preferably Python, using helper functions for common template elements such as logos, title bars, decorative backgrounds, footer marks, content boxes, and tables. Use `scripts/generate_pages.py` as a starting scaffold when a compact page plan is useful, then customize generated pages for the actual template and content.

9. **Validate and repair.** Run the PPTD checker. Treat missing images, malformed pages, text overflow, and real occlusion as repair issues. Treat intentional decorative bleed outside the slide, or text layered over a title bar by design, as acceptable only after visual confirmation.

10. **Export and visually verify.** Export to PPTX or use the available PPT renderer. Verify page count, slide dimensions, key content preservation, asset rendering, and representative slides across cover, content, tables, diagrams, code, and final pages.

## Rules

- Do not add or delete pages unless the user explicitly authorizes it.
- Do not preserve the template only as a theme palette. Recreate its visible layout language: recurring bars, logo placement, backgrounds, spacing, typographic hierarchy, and page archetypes.
- Do not simply paste content on top of copied template pages when page counts differ. Generate new pages that combine template style with content-specific layout.
- Prefer structured text, tables, and shapes over page screenshots. Use screenshots only for complex diagrams, images, or content that cannot be safely reconstructed.
- Keep absolute or correctly relative image `src` paths consistent with the result `.pptd` location and checker expectations.
- Run the checker before export. Iterate until there are no errors and only explainable, visually acceptable warnings remain.
- Treat bundled scripts as a baseline implementation. For production-quality fidelity, prefer a richer environment-specific PPTD converter/exporter when available, especially for SmartArt, charts, complex masters, and exact PowerPoint rendering.
