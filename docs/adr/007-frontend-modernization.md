# ADR-007: Frontend Modernization (Next.js 15 + React 19)

**Status:** Accepted  
**Date:** 2026-02-24  
**Deciders:** Platform Team

---

## Context

The frontend currently uses:

| Package | Current Version | Latest Stable | Gap |
|---------|----------------|---------------|-----|
| Next.js | 14.2.5 | 15.x | Major version behind |
| React | 18.3.1 | 19.x | Major version behind |
| TypeScript | 5.6.3 | 5.7+ | Minor version behind |
| Tailwind CSS | 3.4.14 | 4.x | Major version behind |
| ESLint | 8.57.0 | 9.x | Major version behind |
| Node.js | 18+ (README) | 22 LTS | Major version behind |

Additional issues:

1. **Dead imports** — Components import `webApp` from `@/utils/api` which doesn't exist.
2. **Empty components** — `Transcriptions/index.tsx`, `Configuration/Cases.tsx` are empty stubs.
3. **No authentication** — No MSAL, no protected routes, no session management.
4. **No avatar parameter UI** — Backend supports avatar configuration but frontend has no UI for it.
5. **Package manager** — Uses Yarn 1.x (classic); modern projects use Yarn 4.x or pnpm.
6. **No evaluation page** — No UI for agent evaluation results.

## Decision

**Upgrade the frontend to Next.js 15 with React 19**, modernize the tooling, and add missing capabilities.

### 1. Dependency Upgrades

```json
{
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "axios": "^1.7.0",
    "zustand": "^5.0.0",
    "microsoft-cognitiveservices-speech-sdk": "^1.40.0",
    "@azure/msal-browser": "^4.0.0",
    "@azure/msal-react": "^3.0.0",
    "react-markdown": "^9.0.0",
    "remark-gfm": "^4.0.0",
    "clsx": "^2.1.0",
    "uuid": "^10.0.0",
    "recharts": "^2.13.0"
  },
  "devDependencies": {
    "@types/node": "^22.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "typescript": "^5.7.0",
    "tailwindcss": "^4.0.0",
    "eslint": "^9.0.0",
    "eslint-config-next": "^15.0.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  },
  "packageManager": "pnpm@9.0.0"
}
```

### 2. New Pages

| Route | Component | Purpose |
|-------|-----------|---------|
| `/evaluation` | `EvalDashboard` | Agent evaluation results, run history, quality trends |
| `/evaluation/[runId]` | `EvalRunViewer` | Detailed evaluation run with per-test-case scores |
| `/avatar/settings` | `AvatarSettings` | Avatar parameter selection (voice, style, language) |

### 3. Authentication with MSAL

```typescript
// app/providers.tsx
import { MsalProvider } from "@azure/msal-react";
import { PublicClientApplication } from "@azure/msal-browser";

const msalConfig = {
  auth: {
    clientId: process.env.NEXT_PUBLIC_AZURE_CLIENT_ID!,
    authority: `https://login.microsoftonline.com/${process.env.NEXT_PUBLIC_AZURE_TENANT_ID}`,
    redirectUri: process.env.NEXT_PUBLIC_REDIRECT_URI || "http://localhost:3000",
  },
};

const msalInstance = new PublicClientApplication(msalConfig);

export function Providers({ children }: { children: React.ReactNode }) {
  return <MsalProvider instance={msalInstance}>{children}</MsalProvider>;
}
```

### 4. React 19 Features to Adopt

| Feature | Usage |
|---------|-------|
| **Server Components** | Default for pages; client components opt-in with `"use client"` |
| **Server Actions** | Form submissions for configuration CRUD |
| **`use()` hook** | Async data fetching in components |
| **Suspense streaming** | Progressive loading for evaluation dashboards |
| **Improved hydration** | Better error reporting during SSR/CSR mismatch |

### 5. Avatar Parameter Selector Component

```typescript
// components/Avatar/AvatarParameterSelector.tsx
interface AvatarParams {
  voiceName: "en-US-JennyNeural" | "en-US-GuyNeural" | "en-US-AriaNeural";
  speakingStyle: "friendly" | "professional" | "empathetic";
  language: "en-US" | "pt-BR" | "es-ES";
  avatarStyle: "casual" | "formal" | "technical";
  responseLength: "concise" | "detailed" | "comprehensive";
  expertiseLevel: "beginner" | "intermediate" | "advanced";
}
```

Selected parameters are saved via `PUT /api/avatar/config` and reflected in the Avatar Service's agent initialization.

## Consequences

### Positive

- **Latest framework features** — Server Components, Server Actions, streaming SSR.
- **Smaller bundle** — React 19 compiler optimizations reduce client JS.
- **Authentication** — MSAL integration for Entra ID SSO.
- **Evaluation visibility** — Professors can monitor agent quality from the UI.
- **Avatar customization** — Students/professors can tune avatar behavior.

### Negative

- **Breaking changes** — React 19 drops some deprecated APIs; components may need updates.
- **Tailwind 4 migration** — Config format changes from `tailwind.config.ts` to CSS-based config.
- **Testing updates** — React Testing Library needs updates for React 19 concurrent features.

## References

- [Next.js 15 release notes](https://nextjs.org/blog/next-15)
- [React 19 migration guide](https://react.dev/blog/2024/04/25/react-19-upgrade-guide)
- [MSAL React docs](https://learn.microsoft.com/entra/identity-platform/tutorial-v2-react)
- [Tailwind CSS v4](https://tailwindcss.com/blog/tailwindcss-v4)
