# Kimi PPTD Workflow Reference

## Purpose

Use this reference when a deck must be rebuilt in the visual style of a template deck while preserving the content deck's page count and content. The workflow mirrors the Kimi approach observed in a two-deck task: one 5-page template deck was used to restyle a 20-page content deck.

## PPTD Structure

A converted `.pptd` project typically contains:

```text
deck.pptd
pages/
  page1.page
  page2.page
images/
  image_1.png
  image_2.png
```

The main `.pptd` file stores slide size, theme colors, and page paths:

```yaml
size: [1280, 720]
theme:
  colors:
    primary: "#244EB1"
pages:
  - pages/page1.page
  - pages/page2.page
```

Each `.page` file stores page elements. Common fields:

- `pageType`: page role, such as `cover`, `content`, `section`, `process`, `final`.
- `elements`: ordered list of shapes, text, images, and tables.
- `elementId`: stable element name for diagnosis and repair.
- `elementType`: `text`, `image`, `shape`, `table`, or related supported type.
- `bounds: [x, y, width, height]`: slide coordinates, usually in a 1280 by 720 coordinate space.
- `src`: image path. Use paths that the checker/exporter can resolve.
- `fit`: image fitting mode such as `fill` or `contain`.
- `opacity`, `flip`, `fill`, `stroke`, `content`: visual and content properties.

Example final page pattern:

```yaml
pageType: final
elements:
- elementId: bg_image
  elementType: image
  bounds: [0, 0, 1280, 720]
  opacity: 0.5
  src: /mnt/agents/output/result/images/image_4.png
  fit:
    mode: fill
- elementId: otr_logo
  elementType: image
  bounds: [1118, 13, 148, 80]
  src: /mnt/agents/output/result/images/image_1.png
- elementId: blue_bar
  elementType: shape
  bounds: [69, 349, 1141, 30]
  shapeName: rect
  fill:
    type: solid
    color: "#244EB1"
- elementId: thankyou_text
  elementType: text
  bounds: [69, 349, 1141, 30]
  content:
    align: [center, middle]
    fontSize: 32
    fontFamily: Arial, Microsoft YaHei
    color: "#FFFFFF"
    text: |
      <p><strong>Thank You!</strong></p>
```

## Command Pattern

Use the active PPTX/PPTD skill directory when it exists. In the Kimi sandbox, the directory was `/app/.agents/skills/pptx`. This skill also bundles a baseline converter and checker under `scripts/`; prefer a production PPTD converter if available, otherwise use the bundled scripts.

Convert template:

```bash
cd /path/to/ppt-template-style-reflow
bash scripts/convert.sh /mnt/agents/upload/template.pptx -o /mnt/agents/output/template_convert/
```

Convert content:

```bash
cd /path/to/ppt-template-style-reflow
bash scripts/convert.sh /mnt/agents/upload/content.pptx -o /mnt/agents/output/content_convert/
```

Check result:

```bash
cd /path/to/ppt-template-style-reflow
bash scripts/check.sh /mnt/agents/output/result/result.pptd
```

Export result to PPTX:

```bash
cd /path/to/ppt-template-style-reflow
bash scripts/export.sh /mnt/agents/output/result/result.pptd -o /mnt/agents/output/result/result.pptx
```

Render an HTML preview:

```bash
cd /path/to/ppt-template-style-reflow
bash scripts/render.sh /mnt/agents/output/result/result.pptd -o /mnt/agents/output/result/preview
```

Generate a starter result from a compact JSON plan:

```bash
cd /path/to/ppt-template-style-reflow
python3 scripts/generate_pages.py --plan plan.json -o /mnt/agents/output/result --name result
```

The bundled converter is for inspection and reflow scaffolding. It extracts common text, pictures, and basic shapes from PPTX files, but complex SmartArt, charts, animations, theme masters, and precise PowerPoint layout semantics may need the environment's production converter or visual extraction. The bundled checker is static validation; it does not replace final rendering. The bundled exporter uses Node.js plus `pptxgenjs`; if `pptxgenjs` is unavailable, use the HTML renderer for visual QA or install/use the active presentation runtime.

Runtime summary:

- `convert.sh`: Python 3 only, standard library.
- `check.sh`: Python 3 only, standard library.
- `generate_pages.py`: Python 3 only, standard library.
- `render.sh`: Python 3 only, standard library; writes an HTML preview.
- `export.sh`: Node.js plus `pptxgenjs`; writes an editable PPTX approximation of the PPTD.

## Style Extraction Checklist

Read all template pages and screenshots. Extract these into working notes before generating result pages:

- slide size and aspect ratio
- primary, secondary, and accent colors
- logo image filename, bounds, and recurring placement
- cover background, final background, section decoration, and any deliberate bleed outside slide bounds
- title bar style, gradient, height, x/y, text alignment, and margins
- standard content frame and usable content area
- typography: title font size, body font size, table font size, code font size, font family, color
- repeated visual treatments for tables, lists, numbered steps, diagrams, screenshots, and code
- page archetypes available in the template deck

The extracted style does not need to be saved as a separate file. Persist it by writing the result `.pptd`, copied `images/`, and generated `.page` files.

## Content Deck Splitting

Convert the content deck too. The converter should split it into a main `.pptd`, `pages/*.page`, and `images/`.

Use content `.page` files to preserve structured content:

- keep text and list hierarchy when possible
- rebuild editable tables when possible
- keep code blocks as text unless screenshots are required
- preserve diagrams, screenshots, and complex visuals as images when reconstruction is risky

Use content `images/` for original visuals. When copying into `result/images`:

- copy every referenced content image that appears in the generated result
- rename content images if their names collide with template images
- update all `src` references in generated `.page` files
- run the checker to catch missing resources

## Mapping Logic

Map by semantic role and layout need, not by simple page number.

1. Build a table of template archetypes:
   - template page id
   - visual role
   - available content area
   - supported content types
   - required style assets

2. Build a table of content page roles:
   - page number
   - title
   - content density
   - main content type
   - required images/tables/code

3. Match each content page to the closest template archetype:
   - cover -> cover
   - agenda/overview -> summary or standard content
   - dense explanatory pages -> flexible standard content
   - section transition -> section divider
   - process or multi-path flow -> grid/process layout
   - table-heavy pages -> standard content with table-specific typography
   - final -> final/thank-you

Observed example mapping:

| Content pages | Template layout | Rationale |
| --- | --- | --- |
| 1 | template page 1 | Cover title page |
| 2-8, 11-17 | template page 4 | Standard content with blue gradient title bar and logo |
| 9 | template page 3 | Section transition with large title |
| 10 | template page 2 | Multi-flow or four-block process content |
| 18-19 | template page 4 | Standard content |
| 20 | template page 5 | Thank-you final page |

## Generation Pattern

Create result folders:

```bash
mkdir -p /mnt/agents/output/result/pages /mnt/agents/output/result/images
```

Copy template style resources first:

```bash
cp /mnt/agents/output/template_convert/images/*.png /mnt/agents/output/result/images/
```

Copy content resources as needed, renaming to avoid collisions:

```bash
cp /mnt/agents/output/content_convert/images/image_3.png /mnt/agents/output/result/images/content_image_3.png
```

Generate page files with a script instead of manually editing 20 pages. Prefer helper functions:

- `add_logo()`
- `add_cover_background()`
- `add_title_bar()`
- `add_section_decoration()`
- `add_footer_or_accent()`
- `text_box()`
- `table_block()`
- `image_block()`
- `write_page(index, content)`

For a quick scaffold, write a JSON plan and run `scripts/generate_pages.py`. Supported page roles include:

- `cover`: `title`, `subtitle`
- `standard`: `title`, `body` or `bullets`
- `section`: `number`, `title`, `subtitle`
- `process`: `title`, `items` with `title` and `text`
- `final`: `title`

Generate in batches when the deck is large:

- pages 1-5
- pages 6-10
- pages 11-15
- pages 16-20

After each batch, record which pages were written. After all batches, run the checker.

## Validation And Repair

The checker is a static layout and integrity check. It cannot fully replace visual review.

Common issue types:

- `SrcNotFoundWarning`: image `src` does not point to an existing file. Always fix.
- `TextOverflowWarning`: text likely does not fit in bounds. Fix by reducing font, increasing bounds, shortening line breaks, using columns, or converting to a table layout.
- `TextOcclusionWarning`: one text element is blocked by another element. Fix by moving, resizing, reordering layers, or changing content layout.
- `BoundsOutsideWarning`: element extends beyond slide bounds. Fix unless it is intentional decorative bleed from the template and visually acceptable.
- `TextUnderfillWarning`: text frame is much larger than content. Fix when it makes layout visibly loose.
- `TextDriftWarning`: text differs from inferred underlying shape alignment. Often acceptable when title text intentionally sits on a bar, but confirm visually.

Repair loop:

1. Run checker.
2. Group issues by page.
3. Read only the affected `.page` files.
4. Fix missing resources, overflow, occlusion, and excessive bounds.
5. Rerun checker.
6. Export/render when there are no errors and only explainable warnings remain.

## Final Verification

Before delivery:

- Confirm final page count equals the content deck page count.
- Confirm main `.pptd` page list references every generated page in order.
- Confirm all images referenced by result `.page` files exist.
- Render or preview representative pages: cover, standard content, dense text, table, process/flow, image/code, and final.
- Confirm no critical content was dropped during reflow.
- State any remaining acceptable warnings and why they are acceptable.
