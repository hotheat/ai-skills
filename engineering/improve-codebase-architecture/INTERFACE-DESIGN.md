# Interface Design

When the user wants to explore alternative interfaces for a chosen deepening candidate, use this pattern. The first design is unlikely to be the best.

Use the vocabulary in [LANGUAGE.md](LANGUAGE.md) and dependency categories in [DEEPENING.md](DEEPENING.md).

## Process

### 1. Frame the problem space

Before spawning subagents, write a user-facing explanation of the chosen candidate:

- Constraints any new interface must satisfy
- Dependencies it relies on, and which category they fall into
- A rough illustrative code sketch that grounds the constraints without becoming a proposal

Show this to the user, then proceed to Step 2. The user can read while subagents work.

### 2. Spawn subagents

Spawn at least three subagents in parallel when available. Each must produce a radically different interface for the deepened module.

Prompt each subagent with a separate technical brief: file paths, coupling details, dependency category, what sits behind the seam, domain vocabulary from `CONTEXT.md`, and architecture vocabulary from [LANGUAGE.md](LANGUAGE.md).

Use different design constraints:

- Agent 1: minimize the interface; aim for one to three entry points.
- Agent 2: maximize flexibility; support many use cases and extension.
- Agent 3: optimize for the most common caller; make the default case trivial.
- Agent 4, when relevant: design around ports and adapters for cross-seam dependencies.

Each subagent outputs:

1. Interface: types, methods, params, invariants, ordering, and error modes
2. Usage example showing how callers use it
3. What the implementation hides behind the seam
4. Dependency strategy and adapters
5. Trade-offs: where leverage is high, where it is thin

If subagents are unavailable, produce the same set of alternatives yourself and label each design constraint explicitly.

### 3. Present and compare

Present designs sequentially, then compare them by **depth**, **locality**, and **seam placement**.

Give your recommendation. If elements from different designs combine well, propose a hybrid. Be opinionated.
