---
title: "UI: Accessibility Audit"
description: "Audit a UI component or page for WCAG 2.2 AA compliance, keyboard navigation, and screen reader compatibility."
mode: "ui-agent"
input: "Specify the component, page, or URL to audit. Include the target platform (web, CLI, desktop)."
---

Perform a comprehensive accessibility audit:

1. **Semantic Structure** — Validate heading hierarchy (h1→h6, no skips). Landmark elements (nav, main, aside, footer). List structure for list content.
2. **Color & Contrast** — Minimum 4.5:1 for normal text, 3:1 for large text. Non-color indicators for state (icons, patterns).
3. **Keyboard Navigation** — Tab order follows visual order. All interactive elements reachable. No keyboard traps. Visible focus indicators (min 2px).
4. **Screen Readers** — aria-label/aria-describedby on non-text controls. Live regions for dynamic content. Form error announcements.
5. **Motion & Responsiveness** — prefers-reduced-motion respected. Content reflows at 320px. Touch targets ≥44x44px on mobile.
6. **Forms** — Labels programmatically associated. Error messages linked to fields. Required fields marked for assistive tech.

Deliver a compliance report with pass/fail per criterion, remediation steps, and priority ranking.
