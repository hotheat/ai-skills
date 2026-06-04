# Outline Mode

Use outline mode when the user gives a topic, research notes, or key points but does not provide a detailed page-by-page outline.

## Required Reading

After identifying outline mode, read:

1. `outline_mode.md`
2. `pptd.md`
3. `general.md`

Also keep `template_mode.md` active when a PPT/PPTX template is driving the design.

## When to Choose Outline Mode

Choose outline mode when:

- The user gives a theme such as "OpenClaw architecture" plus several key points.
- The user asks for a deck but does not specify each slide.
- The input is research material that needs synthesis into chapters.
- The template defines visual style but not content structure.

Do not wait for a perfect slide outline if the request clearly expects the model to structure the deck.

## Create `outline.md`

`outline.md` should contain:

- Deck title and audience.
- Narrative goal.
- Chapter list.
- Slide list with page names.
- For each slide: source, purpose, main message, content bullets, diagram or visual idea, intended page archetype, text budget, and checker risk.

A useful structure:

```md
# Outline

## Deck Goal

## Slide Plan

### 1. cover.page
- Archetype: cover
- Source:
- Message:
- Content:
- Visual form:
- Text budget:
- Checker risk:

### 2. toc.page
- Archetype: table of contents
- Source:
- Message:
- Content:
- Visual form:
- Text budget:
- Checker risk:
```

## Create `design.md`

`design.md` should contain the template rules extracted in template mode:

- Page types and when to use them.
- Colors and typography.
- Logo and recurring decoration placement.
- Content density rules.
- Accepted template warnings.
- Per-page layout notes for unusual slides.

## Research to Slides

Turn research into a deck narrative:

- Group facts into 4 to 6 chapters when possible.
- Convert paragraphs into concise slide statements.
- Prefer architecture diagrams, flow diagrams, data lifecycle views, and comparison tables for technical material.
- Keep each slide's message narrow enough to fit the template.
- Put implementation detail in diagrams and labels rather than long prose blocks.

For existing long documents, also follow `summary_mode.md` and require `source_profile.md` plus `source_map.md` before generating pages.

## Split Rules

Split a slide before authoring when:

- It needs more than one main message.
- A table would exceed 4 columns or 6 rows.
- A flow would exceed 6 nodes.
- Any card would need more than 2 lines of body text.
- The page would likely need font sizes below the template hierarchy.

## OpenClaw Pattern

In the OpenClaw case, the user supplied a long Markdown article and a template, not a detailed slide plan. Kimi therefore created a working directory, wrote planning files, then generated the deck manifest and numbered page files from that plan.
