import { expect, test } from "@playwright/test";

interface RouteSmokeCase {
  heading: RegExp;
  path: string;
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
    heading: /Configuration operations hub/i,
    path: "/configuration",
  },
] as const satisfies readonly RouteSmokeCase[];

test.describe("modern route shells", () => {
  for (const smokeCase of ROUTE_SMOKE_CASES) {
    test(`${smokeCase.path} renders without live backend services`, async ({ page }) => {
      await page.goto(smokeCase.path);

      await expect(page.locator("#main-content")).toBeVisible();
      await expect(page.getByRole("heading", { name: smokeCase.heading })).toBeVisible();
    });
  }
});
