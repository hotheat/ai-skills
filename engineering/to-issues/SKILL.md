---
name: to-issues
description: Use when turning a plan, spec, PRD, or parent issue into independently grabbable tracker issues, especially when the work should be split into tracer-bullet vertical slices across schema, API, UI, tests, or other integration layers.
---

# To Issues

Break a plan into independently grabbable issues using vertical slices, also called tracer bullets.

A tracer-bullet issue is a thin but complete path through the required integration layers. It is not "database issue," "API issue," then "UI issue." Each completed slice should be demoable or verifiable by itself.

## Process

### 1. Gather Context

Work from whatever is already in the conversation context. If the user passes an issue reference, URL, or path, fetch and read the full body and comments when a tracker tool or CLI is available.

If tracker access is unavailable, ask for the missing source text only when the current context is insufficient. Otherwise, draft issues from the available plan.

### 2. Explore the Codebase

If the implementation area is not already clear, inspect the codebase enough to understand the current state.

Issue titles and descriptions should use the project's domain glossary vocabulary and respect ADRs in the area being touched. Look for prefactoring that would make the change easier before slicing the feature.

### 3. Draft Vertical Slices

Break the plan into tracer-bullet issues. Each issue is a thin vertical slice that cuts through all relevant integration layers end-to-end, not a horizontal slice of one layer.

<vertical-slice-rules>

- Each slice delivers a narrow but complete path through the needed layers, such as schema, API, UI, tests, or workflow glue
- A completed slice is demoable or verifiable on its own
- Any required prefactoring should be done first
- Avoid slices that only create infrastructure unless they unblock the first tracer bullet

</vertical-slice-rules>

### 4. Quiz the User

Present the proposed breakdown as a numbered list. For each slice, show:

- **Title**: short descriptive name
- **Blocked by**: which other slices, if any, must complete first
- **User stories covered**: which user stories this addresses, if the source material has them

Ask the user:

- Does the granularity feel right?
- Are the dependency relationships correct?
- Should any slices be merged or split further?

Iterate until the user approves the breakdown.

### 5. Publish or Hand Off

If an issue tracker tool or CLI is available and the user has approved the breakdown, publish new issues in dependency order so blockers get real issue identifiers first. If tracker labels are required but not known, ask for the label vocabulary before publishing.

If tracker access is not available, produce Markdown issue drafts using the template below. Do not claim they were created in the tracker.

<issue-template>

## Parent

A reference to the parent issue on the issue tracker, if the source was an existing issue. Otherwise omit this section.

## What to Build

A concise description of this vertical slice. Describe the end-to-end behavior, not layer-by-layer implementation.

Avoid specific file paths or code snippets because they go stale quickly. Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can, such as a state machine, reducer, schema, or type shape, inline only the decision-rich part and note that it came from a prototype.

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Blocked By

- A reference to the blocking ticket, if any

Or "None - can start immediately" if no blockers.

</issue-template>

Do not close or modify any parent issue.
