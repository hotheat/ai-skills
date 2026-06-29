---
name: improve-codebase-architecture
description: Find deepening opportunities in a codebase, informed by domain language in CONTEXT.md and decisions in docs/adr/. Use when the user wants to improve architecture, find refactoring opportunities, consolidate tightly-coupled modules, produce an architecture review report, or make a codebase more testable and AI-navigable.
---

# Improve Codebase Architecture

Surface architectural friction and propose **deepening opportunities**: refactors that turn shallow modules into deep ones. The aim is testability and AI-navigability.

Use the vocabulary in [LANGUAGE.md](LANGUAGE.md) exactly. Do not drift into "component," "service," "API," or "boundary" when the architecture terms are **module**, **interface**, **seam**, **adapter**, **leverage**, and **locality**.

This skill is informed by the project's domain model. `CONTEXT.md` gives names to good seams; ADRs in `docs/adr/` record decisions this skill should not re-litigate.

## Process

### 1. Explore

Read existing documentation first:

- `CONTEXT.md`, or `CONTEXT-MAP.md` plus each referenced `CONTEXT.md` in a multi-context repo
- Relevant ADRs in `docs/adr/`, including context-scoped ADR directories

If these files do not exist, proceed silently. Do not flag their absence or suggest creating them upfront.

Then inspect the codebase. Use subagents for broad exploration when available; otherwise explore directly. Do not follow rigid heuristics. Note where you experience friction:

- Where does understanding one concept require bouncing between many small modules?
- Where are modules **shallow**, with an interface nearly as complex as the implementation?
- Where have pure functions been extracted for testability, while the real bugs hide in how they are called?
- Where do tightly-coupled modules leak across their seams?
- Which parts of the codebase are untested, or hard to test through their current interface?

Apply the **deletion test** from [LANGUAGE.md](LANGUAGE.md) to anything that looks shallow. If deleting it concentrates complexity, it was earning its keep. If deleting it makes complexity vanish, it was pass-through structure.

### 2. Present candidates as an HTML report

Write a self-contained HTML file to the OS temp directory so nothing lands in the repo. Resolve the temp dir from `$TMPDIR`, falling back to `/tmp` on Unix-like systems or `%TEMP%` on Windows. Write to `<tmpdir>/architecture-review-<timestamp>.html` so each run gets a fresh file.

Open the report for the user:

- macOS: `open <path>`
- Linux: `xdg-open <path>`
- Windows: `start <path>`

Tell the user the absolute path.

Use [HTML-REPORT.md](HTML-REPORT.md) for the full scaffold, diagram patterns, and style guidance. Each candidate must include:

- **Files**: files and modules involved
- **Problem**: why the current architecture causes friction
- **Solution**: what would change
- **Benefits**: locality, leverage, and test improvement
- **Before / After diagram**: side-by-side visualisation
- **Recommendation strength**: `Strong`, `Worth exploring`, or `Speculative`

Classify each candidate's dependency shape using [DEEPENING.md](DEEPENING.md). Use `CONTEXT.md` vocabulary for the domain and [LANGUAGE.md](LANGUAGE.md) vocabulary for architecture. If `CONTEXT.md` defines "Order," talk about "the Order intake module," not implementation class names unless the file list needs them.

If a candidate contradicts an existing ADR, only surface it when the friction is real enough to warrant revisiting the ADR. Mark the conflict clearly. Do not list every theoretical refactor an ADR forbids.

End the report with a **Top recommendation** section: which candidate to tackle first and why.

Do not propose interfaces yet. After opening the file, ask the user: "Which of these would you like to explore?"

### 3. Grilling loop

Once the user picks a candidate, walk the design tree with them: constraints, dependencies, the shape of the deepened module, what sits behind the seam, what tests survive.

Side effects happen inline as decisions crystallize:

- **Naming a deepened module after a concept not in `CONTEXT.md`?** Add the term to `CONTEXT.md`. Create the file lazily if it does not exist.
- **Sharpening a fuzzy term during the conversation?** Update `CONTEXT.md` right there.
- **User rejects the candidate with a load-bearing reason?** Offer an ADR only when future architecture reviews need that reason to avoid re-suggesting the same thing. Skip ephemeral reasons such as "not worth it right now."
- **User wants alternative interfaces for the deepened module?** Use [INTERFACE-DESIGN.md](INTERFACE-DESIGN.md).

Keep the conversation grounded in code paths and observable friction. Do not turn the candidate into a full refactor plan until the user chooses an interface direction.
