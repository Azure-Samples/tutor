---
applyTo: '**/*.py,**/*.ts,**/*.tsx,**/*.rs,**/*.js,**/*.jsx'
---

## Design Pattern Reasoning (MANDATORY)

For **every component** you create or modify:

1. **Reason about the problem** — what responsibility does this component have?
2. **Consult the pattern catalog** at <https://refactoring.guru/design-patterns/catalog> — identify candidate patterns with language-specific examples
3. **If a pattern matches**, implement it following the catalog's sample as a structural reference, adapted to the project's conventions
4. **If no pattern matches**, document why in a brief comment (e.g., `# No GoF pattern applies — simple data transform`)

Commonly applicable patterns:
- **Strategy** for interchangeable algorithms
- **Template Method** for pipeline steps with varying implementation
- **Observer / Mediator** for event-driven decoupling
- **Builder** for complex object construction
- **Repository** for data access abstraction
- **Decorator** (structural) for wrapping behaviour transparently
