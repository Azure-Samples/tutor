---
title: "TypeScript: Review Code"
description: "Review TypeScript/React code for type safety, accessibility, performance, and React best practices."
mode: "typescript-specialist"
input: "Provide the file(s) or component tree to review. Optionally specify focus (types, a11y, performance)."
---

Review the specified TypeScript code checking for:

1. **Type Safety** — Escaped `any` types. Missing return types on exported functions. Loose union handling without exhaustive checks.
2. **React Correctness** — Client vs Server Component boundary violations. Missing Suspense boundaries. Stale closure bugs in effects.
3. **Accessibility** — Missing alt text, form labels, focus management. Color contrast violations. Keyboard trap risks.
4. **Performance** — Unnecessary re-renders. Missing memoization on expensive computations. Bundle size impact of imports.
5. **Security** — XSS via dangerouslySetInnerHTML. Unvalidated user input. Missing CSRF protection on mutations.
6. **Code Quality** — ESLint warnings. Duplicated components. Missing error boundaries.

Deliver findings as a prioritized list with severity, location, and fix recommendations.
