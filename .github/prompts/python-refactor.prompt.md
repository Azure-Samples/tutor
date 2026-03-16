---
title: "Python: Refactor Module"
description: "Refactor Python code to reduce complexity, eliminate code smells, and improve maintainability."
mode: "python-specialist"
input: "Specify the module or file to refactor. Optionally describe the target improvement (performance, readability, testability)."
---

Refactor the specified Python module:

1. **Identify Smells** — Scan for long methods (>20 lines), god classes, feature envy, primitive obsession, and shotgun surgery.
2. **Select Techniques** — Choose from Extract Method, Replace Conditional with Polymorphism, Introduce Parameter Object, Replace Temp with Query, or other applicable techniques from the refactoring catalog.
3. **Preserve Behavior** — Every refactoring step must maintain existing test pass/fail state. If tests are missing, write them first.
4. **Apply Paradigm Priority** — Migrate toward data-oriented patterns where the current code uses unnecessary OOP ceremony.
5. **Verify** — Run existing tests after each step. Report any behavioral changes.

Deliver the refactored code with a summary of changes made and rationale for each.
