---
name: plan-interviewer
description: Interview the user in Chinese to deepen a plan, spec, PRD, or design document, then write the refined specification back to the target file. Use when the user asks to interview them, flesh out a plan/spec, ask non-obvious questions, clarify implementation or UX tradeoffs, or convert an existing plan file into a more complete spec using Codex or Claude Code question tools.
---

# Plan Interviewer

Use this skill to turn a rough plan file into a clearer implementation spec through focused Chinese interview questions.

## Workflow

1. Read the target file before asking anything.
2. Identify the largest unresolved decisions across implementation, UX, risks, tradeoffs, data flow, dependencies, rollout, and validation.
3. Ask up to 9 high-leverage questions in Chinese. Avoid obvious questions already answered by the file.
4. Continue only while answers materially change the spec. Stop when the remaining uncertainty is minor or speculative.
5. Write the updated spec back to the same file unless the user asks for a different destination.

## Question Tool Compatibility

- In Claude Code, use `AskUserQuestion` when available.
- In Codex Plan mode, use `request_user_input` when available.
- In Codex non-Plan mode, or when no user-question tool is available, ask concise Chinese questions in normal chat, provide 2-3 options for each question, and wait for the user's answer.
- Ask one focused batch at a time. Prefer 3-5 questions per batch unless the user explicitly asks for all 9 at once.

## Interview Rules

- Ask about hidden constraints, failure modes, acceptance criteria, boundaries, and sequencing.
- Make each question answerable. Offer options only when the choice space is clear.
- Track answers as decisions. Do not re-ask resolved points.
- If the file contains contradictions, ask about the contradiction before rewriting.
- If a decision is blocked by missing external facts, mark it as an assumption or open question in the spec.

## Rewrite Rules

- Preserve useful existing structure.
- Add concise sections for decisions, requirements, non-goals, open questions, implementation outline, and validation when they are missing.
- Mark inferred content as assumptions.
- Remove stale TODOs only when the interview answer resolves them.
- Keep the final spec practical enough for another agent or engineer to execute.
