# Template Mode

Use template mode when the user uploads or names a PPT/PPTX template and expects the new deck to follow that template's visual system.

## Required Reading

Start by reading:

1. `SKILL.md`
2. `generate_slides.md`
3. `template_mode.md`

Then inspect the template itself.

## Template Inspection

Use both visual and structural inspection:

- Render or screenshot representative template pages.
- Convert the template PPT/PPTX into PPTD/page form when the environment supports it.
- Read the generated `page1.page` through `pageN.page` files.
- Compare screenshots against `.page` structure so visual motifs become reproducible page rules.
- Run the checker on the converted template when possible before generating new slides.

For example, Kimi inspected `OTR-PPT-Template-simple.pptx` by rendering screenshots, converting it to `.pptd`, then reading template screenshots and `page1.page` to `page5.page`.

## Extract the Design System

Record findings in `design.md`. At minimum capture:

- Canvas size and safe area.
- Page archetypes: cover, table of contents, chapter divider, content page, final page.
- Brand colors: primary, secondary, neutrals, gradients.
- Typography: family, title sizes, body sizes, weight, alignment.
- Brand marks: logo placement, size, margins.
- Title treatment: lines, rules, underlines, prefixes, section labels.
- Background motifs: waves, road shapes, bands, textures, ornaments.
- Layout grid: margins, columns, card sizes, safe zones.
- Warning policy: which overlaps or out-of-bounds elements are template intent.

Use this structure:

```md
# Design System

## Canvas
- Size:
- Safe area:

## Theme Tokens
- Primary:
- Secondary:
- Neutral:
- Background:
- Text:

## Typography
- Cover title:
- Page title:
- Body:
- Table:
- Caption:

## Page Archetypes
### cover
- Source page:
- Reusable elements:
- Editable zones:

### toc
### chapter
### content
### final

## Layout Rules
- Margins:
- Columns:
- Title bar:
- Logo:
- Decoration:

## Warning Baseline
- Accepted:
- Never accept:
```

## OTR Template Example

The OpenClaw run extracted this template system:

- Five page types: cover, contents, chapter page, content page, ending page.
- Deep blue `#244EB1` as the primary brand color.
- Orange `#E68337` as accent color.
- Arial as the main typeface.
- OTR logo in the upper-right corner.
- Blue gradient title line.
- Orange short horizontal rule.
- Wave and road decorative backgrounds.

These details should be reused consistently when generating new pages. Do not invent a new visual language unless the user asks for redesign.

## Template Warnings

Some checker warnings can come from intentional template art:

- Road graphics extending outside the canvas.
- Decorative waves beyond the slide edge.
- Text crossing a designed title line.
- Chapter labels interacting with template ornamentation.

Only accept these warnings after confirming they appear in the source template. Real content collisions remain errors to fix.

## Template Baseline

When conversion produces a template `.pptd`, run the checker on it and save the result in `template_warning_baseline.md`.

Use the baseline during generated-deck validation:

- Warning present in the template baseline and reproduced unchanged: may be accepted as template intent.
- New `TextOverflow`, `TextOcclusion`, or `TextUnderfill`: always repair.
- New `TextDrift` or `BoundsOutside`: accept only when caused by inherited decorative template elements.
- Any warning involving generated content text: inspect the named `.page` before accepting.
