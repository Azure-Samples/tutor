---
applyTo: '**/*.py,**/*.ts,**/*.tsx,**/*.rs,**/*.js,**/*.jsx'
---

## Programming Paradigm Selection

Apply paradigms in this priority order:

1. **Aspect / Data-Oriented Programming** (preferred)
   - Use plain data carriers (dataclasses, structs, interfaces) to represent state
   - Separate behaviour into standalone functions that operate on data
   - Leverage structural subtyping (protocols, traits, interfaces) instead of class hierarchies
   - Use decorators / attributes / aspects for cross-cutting concerns (logging, validation, retry, caching)

2. **Object-Oriented Programming** (when data-oriented is insufficient)
   - Composition over inheritance
   - Keep classes small — Single Responsibility Principle
   - ABCs/traits only when polymorphism is essential

3. **Functional Programming** (for serverless / stateless workloads)
   - Pure functions, immutable data structures
   - Higher-order functions and utility combinators
   - Generators and lazy evaluation pipelines
