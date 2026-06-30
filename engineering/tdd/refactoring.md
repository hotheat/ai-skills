# Refactor Candidates

After the TDD cycle, look for:

- **Duplication**: extract function or class
- **Long methods**: break into private helpers while keeping tests on the public interface
- **Shallow modules**: combine or deepen
- **Feature envy**: move logic to where data lives
- **Primitive obsession**: introduce value objects
- **Existing code**: fix code the new implementation reveals as problematic
