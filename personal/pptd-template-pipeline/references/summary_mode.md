# Summary Mode

Use summary mode when the user provides an existing long document, article, report, transcript, Markdown file, PDF-derived text, or source deck as the content source for a new template-driven PPTD deck.

## Required Reading

After identifying summary mode, read:

1. `summary_mode.md`
2. `outline_mode.md`
3. `pptd.md`
4. `general.md`

Keep `template_mode.md` active when a PPT/PPTX template drives the visual system.

## When to Choose Summary Mode

Choose summary mode when:

- The user says to use an uploaded document, article, manuscript, report, transcript, or Markdown file as the source.
- The content already has meaningful sections that should be preserved.
- The task is to upgrade source material into a slide deck, not invent a deck from sparse notes.
- The user asks for a PPT "based on this document" or "using the first article as content."

Do not collapse summary mode into generic outline mode. Existing documents require source coverage and traceability.

## Create `source_profile.md`

Before writing `outline.md`, create a source profile:

```md
# Source Profile

## Source
- File:
- Title:
- Type:
- Audience:

## Core Thesis

## Section Inventory
- Section:
- Role in the argument:
- Must keep:
- Can compress:

## Key Terms

## Must-Preserve Details
- Names, parameters, APIs, commands, diagrams, data structures, decisions, risks.

## Exclusions
- Details intentionally omitted from slides and why.
```

## Create `source_map.md`

Map source sections to planned slides:

```md
# Source Map

| Slide | Page File | Source Section | Slide Job | Must Keep | Compression |
|---|---|---|---|---|---|
| 1 | cover.page | title/front matter | introduce deck | title, context | brief |
```

Every content slide should cite at least one source section. If a source section is omitted, record the omission in `source_profile.md`.

## Convert Document Content to Slides

Use these transformations:

- Section hierarchy -> chapters and divider pages.
- Dense paragraphs -> one slide claim plus short supporting bullets.
- Lists -> cards, tables, or grouped callouts.
- Architecture descriptions -> layered diagrams.
- Process descriptions -> flow diagrams or lifecycle views.
- Comparisons -> comparison tables.
- Risks or tradeoffs -> matrix or two-column contrast.
- Code/config details -> compact code excerpt or labeled implementation card.

Keep claims faithful to the source. Do not add unsupported claims unless clearly marked as inference.

## Text Budget

Set a text budget before authoring each page:

- Page title: one line when possible.
- Content page: one main message.
- Bullets: 3 to 5 short bullets.
- Cards: one title plus 1 to 2 lines each.
- Table: prefer at most 4 columns and 6 rows.
- Flow: prefer at most 6 nodes on one page.

If a page exceeds these limits, split it before running the checker. Do not rely on aggressive font shrinkage to force dense source text into one slide.

## Outline Integration

Each `outline.md` slide entry should include:

```md
### 8. page08_transcript_tree.page
- Source:
- Archetype:
- Slide job:
- Main message:
- Visual form:
- Must keep:
- Can compress:
- Text budget:
- Checker risk:
```

`Source` links the slide to the original document section. `Checker risk` predicts dense tables, long labels, or flow-node overlap before generation.
