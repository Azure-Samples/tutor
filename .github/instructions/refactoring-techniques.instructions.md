---
applyTo: '**/*.py,**/*.ts,**/*.tsx,**/*.rs,**/*.js,**/*.jsx'
---

## Refactoring Techniques

When updating existing code, apply techniques from <https://refactoring.guru/refactoring/techniques>:

- **Extract Method** — break long functions into named steps
- **Replace Conditional with Polymorphism** — when `if/elif` chains map to types
- **Introduce Parameter Object** — when functions take >3 related parameters
- **Move Method** — relocate logic to the class that owns the data
- **Replace Magic Number with Named Constant**
- **Decompose Conditional** — extract complex boolean expressions

Always run the full test suite before and after refactoring to confirm behavioural equivalence.
