import { expect, test } from "@playwright/test";

interface RouteSmokeCase {
  heading: RegExp;
  path: string;
  visibleText?: RegExp;
}

const ROUTE_SMOKE_CASES = [
  {
    heading: /A professional academic front door/i,
    path: "/",
  },
  {
    heading: /Programs and re-entry offers/i,
    path: "/programs",
  },
  {
    heading: /Tutor does not pretend AI output is institutional truth/i,
    path: "/evidence-trust",
  },
  {
    heading: /Guided learning and coaching/i,
    path: "/workspace/student/learning",
  },
  {
    heading: /AI governance, evaluation, and degraded-state review/i,
    path: "/workspace/admin/ai-governance",
  },
  {
    heading: /Network briefings and school visits/i,
    path: "/workspace/supervisor/briefings",
    visibleText: /P2\/P3 governed status/i,
  },
  {
    heading: /School health and intervention readiness/i,
    path: "/workspace/principal/school-health",
    visibleText: /P2\/P3 governed status/i,
  },
  {
    heading: /Durable record and re-entry pathways/i,
    path: "/workspace/alumni/record",
    visibleText: /P3 lifelong network/i,
  },
  {
    heading: /Configuration operations hub/i,
    path: "/configuration",
  },
  {
    heading: /Upskilling Configuration/i,
    path: "/configuration/upskilling",
    visibleText: /Teaching Plans/i,
  },
] as const satisfies readonly RouteSmokeCase[];

test.describe("modern route shells", () => {
  for (const smokeCase of ROUTE_SMOKE_CASES) {
    test(`${smokeCase.path} renders without live backend services`, async ({ page }) => {
      await page.goto(smokeCase.path);

      await expect(page.locator("#main-content")).toBeVisible();
      await expect(page.getByRole("heading", { name: smokeCase.heading })).toBeVisible();
      if ("visibleText" in smokeCase && smokeCase.visibleText) {
        await expect(page.getByText(smokeCase.visibleText).first()).toBeVisible();
      }
    });
  }
});
