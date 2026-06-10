---
name: frontend-design
description: Use when designing agent-facing experiences, agent tools, workflows, interfaces, or deliverables that need distinctive, production-grade design quality and should avoid generic AI aesthetics.
license: Complete terms in LICENSE.txt
---

This skill guides creation of distinctive, production-grade agent design work that avoids generic "AI slop" aesthetics. Apply it to agent-facing products, agent workflows, tool surfaces, documentation experiences, visual artifacts, and interaction surfaces.

The user provides agent design requirements: an agent product, workflow, tool UI, component, page, application, visual artifact, or documentation experience to design or build. They may include context about the agent's role, audience, operating environment, output format, or technical constraints.

## Design Thinking

Before coding, understand the context and commit to a BOLD aesthetic direction:
- **Purpose**: What problem does this agent experience solve? Who uses it, maintains it, or consumes its output?
- **Agent Role**: What decisions does the agent make, what inputs does it need, what state does it expose, and where does human judgment enter?
- **Tone**: Pick an extreme: brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, etc. There are so many flavors to choose from. Use these for inspiration but design one that is true to the aesthetic direction.
- **Constraints**: Technical requirements (framework, performance, accessibility).
- **Trust Surface**: What evidence, status, uncertainty, approvals, logs, or reversibility does the design need to make the agent understandable?
- **Differentiation**: What makes this UNFORGETTABLE? What's the one thing someone will remember?

**CRITICAL**: Choose a clear conceptual direction and execute it with precision. Bold maximalism and refined minimalism both work - the key is intentionality, not intensity.

Then produce the requested artifact or implementation (HTML/CSS/JS, React, Vue, design spec, workflow map, promptable UI contract, document, or visual system) that is:
- Production-grade and functional
- Visually striking and memorable
- Cohesive with a clear aesthetic point-of-view
- Explicit about agent state, inputs, outputs, and human control points when relevant
- Meticulously refined in every detail

## Agent Design Guidelines

Focus on:
- **Typography**: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the artifact's aesthetics; unexpected, characterful font choices. Pair a distinctive display font with a refined body font.
- **Color & Theme**: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes.
- **Motion**: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available. Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions. Use scroll-triggering and hover states that surprise.
- **Spatial Composition**: Unexpected layouts. Asymmetry. Overlap. Diagonal flow. Grid-breaking elements. Generous negative space OR controlled density.
- **Backgrounds & Visual Details**: Create atmosphere and depth rather than defaulting to solid colors. Add contextual effects and textures that match the overall aesthetic. Apply creative forms like gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, custom cursors, and grain overlays.
- **Agent State Model**: Show what the agent knows, what it is doing now, what is queued, what failed, and what needs human input. Avoid decorative status that does not map to real state.
- **Control & Recovery**: Design clear approval, undo, pause, retry, escalation, and audit paths when the agent can change external state or spend user time/money.
- **Output Legibility**: Make the agent's result easy to scan, compare, verify, and reuse. Surface sources, assumptions, diffs, confidence, or validation evidence when they affect trust.

NEVER use generic AI-generated aesthetics like overused font families (Inter, Roboto, Arial, system fonts), cliched color schemes (particularly purple gradients on white backgrounds), predictable layouts and component patterns, vague agent magic, ornamental dashboards, and cookie-cutter design that lacks context-specific character.

Interpret creatively and make unexpected choices that feel genuinely designed for the context. No design should be the same. Vary between light and dark themes, different fonts, different aesthetics. NEVER converge on common choices (Space Grotesk, for example) across generations.

**IMPORTANT**: Match implementation complexity to the aesthetic vision. Maximalist designs need elaborate code with extensive animations and effects. Minimalist or refined designs need restraint, precision, and careful attention to spacing, typography, and subtle details. Elegance comes from executing the vision well.

Remember: the agent is capable of extraordinary creative work. Don't hold back, show what can truly be created when thinking outside the box and committing fully to a distinctive vision.
