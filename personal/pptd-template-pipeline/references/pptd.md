# PPTD and Page Authoring

## Deck Manifest

Generate one main `.pptd` file as the deck entry point. It should reference every slide page in order. Treat it like the table of contents for the generated deck.

Example deck entry:

- `openclaw_pi.pptd`: main manifest for the OpenClaw deck.
- Referenced pages: `cover.page`, `toc.page`, chapter pages, content pages, and `final.page`.

Follow the active PPTD environment's exact syntax. If an upstream `pptd.md` exists, read it before authoring.

## Page Files

Each `.page` file should represent one slide and should:

- Match one extracted template archetype.
- Use stable bounds for title, body, cards, diagrams, and decorations.
- Keep live text inside safe areas.
- Use the template's colors, fonts, logo, and decorative motifs.
- Avoid hidden assumptions that cannot be checked by the PPTD checker.

## Checker Command

Use the environment's real checker path when available. The OpenClaw/Kimi run used a command shaped like:

```bash
cd /app/.agents/skills/pptx && bash scripts/check.sh /mnt/agents/output/openclaw_pi/openclaw_pi.pptd
```

Adapt the path to the current workspace and deck name.

## Terminal and Python Usage

Use the terminal for:

- Listing generated files.
- Running template conversion tools.
- Running screenshot/render helpers.
- Running the PPTD checker.
- Inspecting checker logs.

Use Python only when it is the provided or most reliable way to inspect PPTX structure, automate conversion, parse checker output, or perform safe mechanical calculations. Keep the reasoning in `outline.md`, `design.md`, and the final response so the workflow remains auditable.

## Checker Triage

Treat these as real issues to eliminate:

- `TextOverflow`: text does not fit its bounds.
- `TextOcclusion`: text overlaps with another element or live text area.
- `TextUnderfill`: text box is poorly sized or content does not occupy expected bounds.

Common fixes:

- Shorten labels and bullets.
- Lower font size modestly.
- Increase width or height of the text bounds.
- Move a conflicting element.
- Increase spacing between repeated blocks.
- Split a dense slide into two pages.

Treat these as possible warnings only after visual/template confirmation:

- Decorative background extends outside the canvas.
- Template road or wave art crosses a boundary.
- Template title text intersects a decorative rule by design.

Compare generated-deck warnings against `template_warning_baseline.md` when available. Baseline matching is evidence for template intent; it is not permission to ignore warnings involving newly generated text.

## Repair Loop

For every checker pass:

1. Re-run checker.
2. Copy the named issue list into a repair checklist.
3. Open each affected `.page`.
4. Apply the smallest layout repair.
5. Re-run checker.
6. Continue until real errors are zero.

Do not repair from memory. Re-open the `.page` files after each checker report because earlier fixes can create new overlaps.

## Page Reading and Editing Checklist

When checker output names a page:

1. Open the page file, for example `checkpoint_flow.page`.
2. Locate the reported element ids or nearby text.
3. Compare the issue against the intended template layout.
4. Decide whether it is a real content problem or inherited template decoration.
5. Edit the `.page` file directly: text, font size, bounds, x/y position, width, height, or spacing.
6. Re-run the checker immediately.

For OpenClaw, Kimi repeatedly opened and edited pages such as `page08_transcript_tree.page`, `page11_message_store.page`, `page12_agent_loop.page`, `page13_event_streaming.page`, `page15_tool_arch.page`, `page16_sandbox_audit.page`, and `page17_request_lifecycle.page`.

## Typical Repair Style

In generated `.page` files, repair measured checker problems with exact bounds:

- If a text box overflows vertically, increase height, shorten text, or split the slide.
- If two elements overlap, move the later element or adjust z-order only after checking geometry.
- If a flow arrow touches the edge of a text box, move the arrow or shrink the text bounds by an exact amount.
- If a title bar overlaps a title, move the bar down or reorder layers while preserving the template style.

This is the intended repair style: read the measured checker issue, adjust exact bounds, and validate again.
