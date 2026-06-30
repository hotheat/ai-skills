---
name: tdd
description: Use when building features or fixing bugs test-first, planning red-green-refactor cycles, writing integration-style behavior tests, mentions tracer bullets or vertical slices, or needs to avoid all-tests-then-all-code horizontal TDD.
---

# Test-Driven Development

## Core Idea

A tracer bullet is one thin end-to-end behavior that proves the whole path works. In this skill, each TDD cycle is one tracer bullet:

```
one behavior test -> minimal implementation across real layers -> passing test -> next behavior
```

The test should verify observable behavior through a public interface. The implementation should do only enough to make that tracer bullet pass.

## Philosophy

**Core principle**: Tests should verify behavior through public interfaces, not implementation details. Code can change entirely; tests should not.

**Good tests** are integration-style: they exercise real code paths through public APIs. They describe _what_ the system does, not _how_ it does it. A good test reads like a specification: "user can checkout with valid cart" tells you exactly what capability exists. These tests survive refactors because they do not care about internal structure.

**Bad tests** are coupled to implementation. They mock internal collaborators, test private methods, or verify through external means like querying a database directly instead of using the interface. Warning sign: the test breaks when you refactor, but behavior has not changed.

Read [tests.md](tests.md) when choosing test shape and [mocking.md](mocking.md) before adding mocks.

## Anti-Pattern: Horizontal Slices

Do not write all tests first, then all implementation. This is horizontal slicing: treating RED as "write all tests" and GREEN as "write all code."

This produces weak tests:

- Tests written in bulk test imagined behavior, not actual behavior
- Tests check data shapes or function signatures instead of user-facing behavior
- Tests become insensitive to real changes: they pass when behavior breaks, fail when behavior is fine
- Test structure outruns what the implementation has taught you

Correct approach: vertical slices via tracer bullets. One test, one implementation, repeat. Each test responds to what you learned from the previous cycle.

```
WRONG (horizontal):
  RED:   test1, test2, test3, test4, test5
  GREEN: impl1, impl2, impl3, impl4, impl5

RIGHT (vertical):
  RED->GREEN: test1->impl1
  RED->GREEN: test2->impl2
  RED->GREEN: test3->impl3
```

## Workflow

### 1. Planning

When exploring the codebase, read `CONTEXT.md` if it exists so test names and interface vocabulary match the project's domain language. Respect ADRs in the area you are touching.

Before writing code:

- Confirm the public interface shape with the user when it is not already clear from the task
- Confirm the most important behaviors to test
- List behaviors, not implementation steps
- If architecture or testability is unclear, use the `improve-codebase-architecture` vocabulary: module, interface, seam, adapter, leverage, locality

Ask: "What should the public interface look like? Which behaviors matter most?"

Do not try to test everything. Focus on critical paths and complex logic.

### 2. Tracer Bullet

Write one test that confirms one behavior about the system:

```
RED:   Write test for first behavior -> test fails
GREEN: Write minimal code to pass -> test passes
```

This is the tracer bullet. It proves the path works end-to-end.

### 3. Incremental Loop

For each remaining behavior:

```
RED:   Write next test -> fails
GREEN: Minimal code to pass -> passes
```

Rules:

- One test at a time
- Only enough code to pass the current test
- Do not anticipate future tests
- Keep tests focused on observable behavior

### 4. Refactor

After all tests pass, read [refactoring.md](refactoring.md) and look for refactor candidates:

- Extract duplication
- Deepen modules by moving complexity behind simple interfaces
- Apply SOLID principles where natural
- Consider what new code reveals about existing code
- Run tests after each refactor step

Never refactor while RED. Get to GREEN first.

## Checklist Per Cycle

```
[ ] Test describes behavior, not implementation
[ ] Test uses public interface only
[ ] Test would survive internal refactor
[ ] Code is minimal for this test
[ ] No speculative features added
```
