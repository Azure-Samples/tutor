---
title: "Python: Implement Feature"
description: "Implement a Python feature with type hints, async patterns, and pytest coverage following PEP standards."
mode: "python-specialist"
input: "Describe the feature, module, or function to implement. Include any API contracts or data models."
---

Implement the requested Python feature following these standards:

1. **Type Safety** — Full type annotations (mypy --strict compatible), PEP 604 unions, Protocol-based structural typing where appropriate.
2. **Async-First** — Use asyncio.TaskGroup or anyio for concurrent operations. Sync wrappers only when the caller requires it.
3. **Validation** — Pydantic models at system boundaries. Validate all external input.
4. **Testing** — Write pytest tests with parametrize for edge cases. Target meaningful coverage, not coverage percentage.
5. **Packaging** — Use PEP 621 pyproject.toml. Pin dependencies via uv.
6. **Paradigm** — Prefer data-oriented (plain dataclasses + standalone functions) over OOP unless encapsulated state is genuinely needed.

Deliver the implementation, tests, and any necessary configuration changes.
