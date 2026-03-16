---
title: "UI: Design Component"
description: "Design and implement a responsive, accessible UI component with proper semantic HTML and design tokens."
mode: "ui-agent"
input: "Describe the component (purpose, content, interactions). Specify platform: web (Tailwind), CLI (Ink), or desktop (Tauri)."
---

Design and implement the requested UI component:

1. **Semantic HTML** — Use the most specific element (button, not div[role=button]). Proper heading hierarchy in context.
2. **Responsive Layout** — Mobile-first with Container Queries where scoped. CSS Grid for 2D layouts, Flexbox for 1D. Fluid typography via clamp().
3. **Design Tokens** — Use project design tokens for colors, spacing, typography. No magic numbers.
4. **Accessibility** — WCAG 2.2 AA. Keyboard operable. Focus indicators visible. Screen reader announcements for state changes.
5. **Performance** — Minimize layout shifts (provide width/height on media). Lazy-load below-fold content. Target LCP < 2.5s, INP < 200ms.
6. **Cross-Platform** — If web: Tailwind + logical properties. If CLI: Ink components. If desktop: Tauri + web stack.

Deliver the component code, usage example, and accessibility notes.
