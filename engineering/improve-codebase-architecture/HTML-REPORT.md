# HTML Report Format

The architecture review is rendered as a single self-contained HTML file in the OS temp directory. Tailwind and Mermaid both come from CDNs. Mermaid handles graph-shaped diagrams reliably; hand-built divs and inline SVG handle editorial visuals such as mass diagrams and cross-sections. Mix the two.

## Scaffold

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Architecture review - {{repo name}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
      mermaid.initialize({ startOnLoad: true, theme: "neutral", securityLevel: "loose" });
    </script>
    <style>
      /* Small custom layer for things Tailwind does not cover cleanly:
         dashed seam lines, hand-drawn-feeling arrow heads, etc. */
      .seam { stroke-dasharray: 4 4; }
      .leak { stroke: #dc2626; }
      .deep { background: linear-gradient(135deg, #0f172a, #1e293b); }
    </style>
  </head>
  <body class="bg-stone-50 text-slate-900 font-sans">
    <main class="max-w-5xl mx-auto px-6 py-12 space-y-12">
      <header>...</header>
      <section id="candidates" class="space-y-10">...</section>
      <section id="top-recommendation">...</section>
    </main>
  </body>
</html>
```

## Header

Repo name, date, and a compact legend: solid box = module, dashed line = seam, red arrow = leakage, thick dark box = deep module. No introduction paragraph. Go straight into candidates.

## Candidate card

The diagrams carry the weight. Prose is sparse, plain, and uses the glossary terms from [LANGUAGE.md](LANGUAGE.md).

Each candidate is one `<article>`:

- **Title**: short, names the deepening, such as "Collapse the Order intake pipeline".
- **Badge row**: recommendation strength (`Strong` = emerald, `Worth exploring` = amber, `Speculative` = slate), plus dependency category from [DEEPENING.md](DEEPENING.md).
- **Files**: monospaced list, `font-mono text-sm`.
- **Before / After diagram**: the centrepiece. Two columns, side by side. See patterns below.
- **Problem**: one sentence. What hurts.
- **Solution**: one sentence. What changes.
- **Wins**: bullets, six words or fewer where possible, such as "Tests hit one interface" or "Pricing logic stops leaking".
- **ADR callout**: only when applicable, one line in an amber-tinted box.

No paragraphs of explanation. If the diagram needs a paragraph to be understood, redraw the diagram.

## Diagram patterns

Pick the pattern that fits the candidate. Mix them. Do not make every diagram look the same.

### Mermaid graph

Use a Mermaid `flowchart` or `graph` when the point is dependency or call-flow shape. Wrap it in a Tailwind-styled card.

```html
<div class="rounded-lg border border-slate-200 bg-white p-4">
  <pre class="mermaid">
    flowchart LR
      A[OrderHandler] --> B[OrderValidator]
      B --> C[OrderRepo]
      C -.leak.-> D[PricingClient]
      classDef leak stroke:#dc2626,stroke-width:2px;
      class C,D leak
  </pre>
</div>
```

### Hand-built boxes and arrows

Use modules as `<div>`s with borders and labels. Use inline SVG `<line>` or `<path>` elements positioned absolutely over a relative container. Reach for this when the after diagram should feel like one thick-bordered deep module with faded internals.

### Cross-section

Use stacked horizontal bands (`h-12 border-l-4`) to show layers a call passes through. Before: many thin layers each doing little. After: one thick band labelled with the consolidated responsibility.

### Mass diagram

Use two rectangles per module: one for interface surface area, one for implementation. Before: interface rectangle nearly as tall as implementation rectangle. After: interface rectangle short, implementation rectangle tall.

### Call-graph collapse

Before: a tree of function calls rendered as nested boxes. After: the same tree collapsed into one box, with now-internal calls shown faded inside it.

## Style guidance

- Lean editorial, not corporate-dashboard.
- Use generous whitespace.
- Use colour sparingly: one accent, red for leakage, amber for warnings.
- Keep diagrams about 320px tall so before/after sits side by side without scrolling.
- Use `text-xs uppercase tracking-wider` for module labels inside diagrams.
- The only scripts are the Tailwind CDN and the Mermaid ESM import. The report is otherwise static.

## Top recommendation section

One larger card. Candidate name, one sentence on why, anchor link to its card. That is enough.

## Tone

Plain English and concise. Architecture nouns and verbs come from [LANGUAGE.md](LANGUAGE.md).

Use exactly: module, interface, implementation, depth, deep, shallow, seam, adapter, leverage, locality.

Never substitute: component, service, unit for module; API or signature for interface; boundary for seam; layer or wrapper when you mean module.

Phrasings that fit:

- "Order intake module is shallow: interface nearly matches the implementation."
- "Pricing leaks across the seam."
- "Deepen: one interface, one place to test."
- "Two adapters justify the seam: HTTP in prod, in-memory in tests."

Wins bullets name the gain in glossary terms: "locality: bugs concentrate in one module", "leverage: one interface, N call sites", "interface shrinks; implementation absorbs the wrappers". Do not write vague benefits such as "easier to maintain" or "cleaner code".

No hedging. If a sentence could be a bullet, make it a bullet. If a bullet can be cut, cut it.
