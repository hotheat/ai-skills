# Browser QA

Run this before claiming the page is complete.

## Required Checks

- Open the generated `index.html` or local server in a browser.
- Check console errors.
- Confirm KaTeX rendered and at least one `.math-block` and `.math-inline` are readable.
- Check computed foreground/background contrast for formulas inside dark bands, cards, heroes, callouts, and overlays.
- Confirm all images load or have explicit placeholders with source/caption.
- Check desktop around 1440px and mobile around 390px.
- Check nav, hero, cards, tables, formulas, and figure captions for overlap.
- Check wide tables scroll inside their containers instead of overflowing the page.
- Check anchors reach all required sections.

## Useful Browser Snippet

```js
() => {
  const imgs = [...document.images].map(img => ({
    src: img.getAttribute("src"),
    complete: img.complete,
    w: img.naturalWidth,
    h: img.naturalHeight
  }));
  const math = [...document.querySelectorAll(".math-block")].map(el => {
    const katex = el.querySelector(".katex");
    return {
      bg: getComputedStyle(el).backgroundColor,
      color: getComputedStyle(el).color,
      katexColor: katex ? getComputedStyle(katex).color : null,
      text: el.textContent.trim().slice(0, 80)
    };
  });
  const overflow = [...document.querySelectorAll("body *")]
    .filter(el => el.scrollWidth > el.clientWidth + 2 && !["auto", "scroll", "hidden"].includes(getComputedStyle(el).overflowX))
    .slice(0, 20)
    .map(el => ({ tag: el.tagName, cls: String(el.className), text: el.textContent.trim().slice(0, 80) }));
  return { imgs, math, overflow };
}
```
