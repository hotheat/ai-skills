# General Rules

## Operating Principles

This workflow is for producing a presentation from research content and a PPT/PPTX template. The model should behave like a deck author plus layout QA reviewer:

- Read the generation specs before writing pages.
- Use the uploaded template as the visual source of truth.
- Convert vague topic briefs into a structured slide outline before authoring `.page` files.
- Use the PPTD checker as the hard quality gate.
- Fix real layout errors until they reach zero.
- Preserve intentional template decorations even if the checker warns about them, but document that decision.

## Required Source Documents

When available, read these files in this order:

1. `SKILL.md`: global constraints and trigger rules for the presentation/PPTD environment.
2. `generate_slides.md`: the main generation workflow.
3. `template_mode.md`: rules for uploaded template-driven work.
4. `summary_mode.md`: rules for existing long documents as source material.
5. `outline_mode.md`: rules for topic/key-point inputs without a detailed page outline.
6. `pptd.md`: PPTD syntax, page file structure, and checker usage.
7. `general.md`: broad writing, design, and validation guidance.

If these files exist in a packaged PPTD or presentation skill, treat those files as implementation references. This local skill records the workflow pattern and should complement, not override, environment-specific syntax rules.

## Quality Gates

The final deck must pass these gates:

- `0 errors`
- `0 TextOverflow`
- `0 TextOcclusion`
- `0 TextUnderfill`
- Every `.page` mentioned by checker output has been opened and reviewed.
- Remaining warnings have a clear rationale, usually inherited template art or intentional decoration intersections.
- Existing source documents have a `source_profile.md` and `source_map.md`.
- Generated-deck accepted warnings have been compared against the template warning baseline when available.

Do not accept unresolved overflow, occlusion, or underfill as "probably fine." These issues usually become visible in exported slides.

## Repair Toolkit

Use the smallest repair that preserves the template style:

- Shorten text before shrinking it aggressively.
- Reduce font size only within the template's visual hierarchy.
- Expand text bounds when the surrounding layout allows it.
- Move elements when checker output identifies true overlap.
- Increase gaps between cards, columns, and flow nodes.
- Split dense content into an adjacent page when a page is overloaded.
- Keep logos, title lines, wave backgrounds, road graphics, and other template motifs unless the user asks to redesign.

## Final Response

Report the result in practical terms:

- Deck entry file and important generated pages.
- Checker command or validation method used.
- Final checker status.
- Any accepted warnings and why they are template intent.
- Any limitations, such as missing template assets or an unavailable checker.
For existing documents, also report whether every major source section was represented or intentionally omitted.
