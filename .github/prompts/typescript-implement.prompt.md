---
title: "TypeScript: Implement Feature"
description: "Implement a TypeScript/React feature with strict types, React Server Components, and accessibility compliance."
mode: "typescript-specialist"
input: "Describe the feature or component to implement. Include API contracts, UI wireframe description, or data requirements."
---

Implement the requested TypeScript feature following these standards:

1. **Strict Types** — TypeScript strict mode. No `any` without written justification. Use discriminated unions over inheritance.
2. **React Patterns** — Server Components by default. Client Components only for interactivity. Suspense boundaries for async data.
3. **State Management** — React Query for server state. Local state with useState/useReducer. No prop drilling beyond 2 levels.
4. **Accessibility** — WCAG 2.2 AA minimum. Semantic HTML. Keyboard navigation. aria-* attributes where needed.
5. **Styling** — Tailwind with design tokens. Responsive mobile-first. Logical properties for RTL support.
6. **Testing** — Vitest/Jest with React Testing Library. Test behavior, not implementation. MSW for API mocking.

Deliver the implementation, tests, and any route/config changes.
