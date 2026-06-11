# HTML Output Contract

Use this file when creating the final `index.html`.

## Hard Requirements

- Output one complete `index.html`.
- Keep all CSS and JS inside the file unless the user explicitly allows a project structure.
- Declare the detected paper type in HTML, preferably as `data-paper-type="<mode>"` on `<body>` or `<main>`.
- Use KaTeX from CDN:
  - `katex.min.css`
  - `katex.min.js`
  - `auto-render.min.js`
- Render inline math and block math.
- Preserve the original LaTeX source in `data-latex` attributes for formula copy.
- Include a right-click or explicit copy interaction for formulas.
- Use Simplified Chinese for explanations.
- Use arXiv HTML image URLs for paper figures when available.
- Recreate key tables with exact numbers.
- Keep responsive layout usable on mobile and desktop.

## Suggested Page Layout

Use this structure:

1. Sticky minimal navigation with section anchors.
2. Hero with paper identity and thesis.
3. Verdict Board or executive scan band: judgement, strongest evidence, confidence, caveat, action.
4. Deep-dive sections with alternating text/visual rhythm.
5. Fixed-width reading content, full-width visual bands for diagrams and tables.
6. End with reviewer critique and reproducibility checklist.

Avoid:

- Marketing filler.
- Decorative gradient blobs.
- Nested cards.
- Huge text inside dense technical panels.
- Long paragraphs without visual structure.

## Apple-Like Design Rules

- Use generous whitespace, precise typography, subtle borders, and restrained motion.
- Favor black/white/neutral base with one or two purposeful accent colors.
- Use high contrast and clear hierarchy.
- Use large hero type only in the hero.
- Use dense, scan-friendly layouts for experiment tables.
- Use smooth scroll and progressive reveal only if it does not obscure content.

## Figure Handling

For arXiv ID `<id>`, try:

- `https://arxiv.org/html/<id>/x1.png`
- `https://arxiv.org/html/<id>/x2.png`
- Continue in order based on actual arXiv HTML inventory.

Each figure block should include:

- Figure number if known.
- Caption summary in Chinese.
- Original caption excerpt or paraphrase.
- Why the figure matters.
- Link to source image.

If image loading is uncertain, include:

```html
<div class="figure-placeholder">
  <strong>Figure X placeholder</strong>
  <p>Expected arXiv image: https://arxiv.org/html/ID/xN.png</p>
  <p>Caption: ...</p>
</div>
```

## Table Handling

For key result tables:

- Use exact numbers.
- Preserve arrows and metric direction.
- Highlight best and second-best only when the paper does or when you explain your own highlighting.
- Add "what this table proves" and "what it does not prove".

For very large tables:

- Show the important subset.
- Provide a collapsed full table when feasible.
- Explain omitted columns/rows.

## Verdict and Evidence Modules

Every page should include a judgement-bearing module near the top, especially for surveys and benchmarks.

Minimum fields:

- Verdict: a direct answer to the paper's central question.
- Evidence: strongest table, figure, section, appendix, or artifact.
- Confidence: high/medium/low with reason.
- Caveat: the biggest limitation or uncertainty.
- Action: how the reader should use the result.

Use matrices and ledgers rather than plain lists when comparing papers, projects, benchmarks, models, or claims. At minimum, one dense evidence area should be represented as a table, matrix, or claim-evidence ledger.

## Formula Handling

Represent formulas as:

```html
<span class="math-inline" data-latex="x_i">\(x_i\)</span>
<div class="math-block" data-latex="L = ...">\[L = ...\]</div>
```

JS must call:

```js
renderMathInElement(document.body, {
  delimiters: [
    { left: "$$", right: "$$", display: true },
    { left: "\\[", right: "\\]", display: true },
    { left: "\\(", right: "\\)", display: false },
    { left: "$", right: "$", display: false }
  ],
  throwOnError: false
});
```

For inline math, CSS should prevent ugly wrapping:

```css
.katex { white-space: nowrap; }
.math-inline { white-space: nowrap; }
```

Formula contrast is mandatory:

- `.math-block` must explicitly set both `background` and `color`.
- `.math-block .katex` must explicitly set a readable `color`.
- Any dark parent container that can contain math, such as `.band`, `.dark`, `.hero-dark`, `.callout-dark`, or `.overlay`, must include a local override for `.math-block` and `.math-block .katex`.
- Do not rely on inherited color for formulas. A dark section with `color: #fff` and a light `.math-block` without a `color` override will make KaTeX unreadable.

Minimum safe CSS:

```css
.math-block {
  background: #f7f8fa;
  color: #1d1d1f;
}
.math-block .katex { color: #1d1d1f; }
.band .math-block,
.dark .math-block,
.hero-dark .math-block,
.callout-dark .math-block {
  background: #fff;
  color: #111;
}
.band .math-block .katex,
.dark .math-block .katex,
.hero-dark .math-block .katex,
.callout-dark .math-block .katex {
  color: #111;
}
```

## Interaction Ideas

Use interactions only when they clarify:

- Section progress rail.
- Toggle between "paper claim" and "reviewer view".
- Formula explainer tabs: symbol, meaning, role, failure mode.
- Experiment matrix filters by dataset/baseline/metric.
- Algorithm stepper showing state updates.
- Figure zoom modal.
- Copy LaTeX on right-click or copy button.

## Browser QA

Before completion:

- Open the generated file or local server in browser.
- Check console errors.
- Confirm KaTeX rendered visibly.
- Confirm formulas are readable by checking computed styles for at least one `.math-block` and its `.katex` child. In dark sections, the formula block must not inherit white or low-contrast text on a light formula background.
- Confirm images load or placeholders are explicit.
- Check mobile width around 390 px and desktop width around 1440 px.
- Check no text overlap in nav, cards, tables, and hero.
- Check anchor navigation reaches all required sections.
