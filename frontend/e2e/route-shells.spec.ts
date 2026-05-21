import { expect, test, type Page } from "@playwright/test";

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

const ADMIN_NAV_ACTIVE_CASES = [
  {
    activeLabel: "Configuration",
    path: "/configuration",
  },
  {
    activeLabel: "Avatar cases",
    path: "/configuration/cases",
  },
  {
    activeLabel: "Policies",
    path: "/configuration/questions",
  },
  {
    activeLabel: "Integrations",
    path: "/lms-gateway",
  },
  {
    activeLabel: "AI governance",
    path: "/workspace/admin/ai-governance",
  },
] as const;

const WORKSPACE_REFLOW_CASES = [
  {
    path: "/configuration/cases",
    role: "admin",
  },
  {
    path: "/workspace/supervisor/briefings",
  },
  {
    path: "/workspace/alumni/record",
  },
] as const;

const WORKSPACE_REFLOW_VIEWPORTS = [
  {
    height: 844,
    name: "mobile",
    width: 390,
  },
  {
    height: 1024,
    name: "tablet",
    width: 768,
  },
] as const;

const expectNoHorizontalOverflow = async (page: Page) => {
  await expect
    .poll(async () =>
      page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth),
    )
    .toBeLessThanOrEqual(1);
};

const expectSidebarOffCanvas = async (page: Page) => {
  await expect
    .poll(async () =>
      page.locator("#sidebar").evaluate((sidebar) => Math.round(sidebar.getBoundingClientRect().right)),
    )
    .toBeLessThanOrEqual(1);
};

const expectSidebarOnCanvas = async (page: Page) => {
  await expect
    .poll(async () =>
      page.locator("#sidebar").evaluate((sidebar) => Math.round(sidebar.getBoundingClientRect().right)),
    )
    .toBeGreaterThan(200);
};

const expectSidebarFixed = async (page: Page) => {
  await expect
    .poll(async () => page.locator("#sidebar").evaluate((sidebar) => window.getComputedStyle(sidebar).position))
    .toBe("fixed");
};

const expectWorkspaceShellBelowHeader = async (page: Page) => {
  await expect
    .poll(async () =>
      page.evaluate(() => {
        const header = document.querySelector("#workspace-header");
        const sidebar = document.querySelector("#sidebar");
        const mainPanel = document.querySelector("[data-workspace-main-panel]");

        if (!header || !sidebar || !mainPanel) {
          return Number.NEGATIVE_INFINITY;
        }

        const headerBottom = Math.ceil(header.getBoundingClientRect().bottom);
        const sidebarTop = Math.floor(sidebar.getBoundingClientRect().top);
        const mainPanelTop = Math.floor(mainPanel.getBoundingClientRect().top);

        return Math.min(sidebarTop - headerBottom, mainPanelTop - headerBottom);
      }),
    )
    .toBeGreaterThanOrEqual(-1);
};

const setWorkspaceRole = async (page: Page, role: string) => {
  await page.addInitScript((workspaceRole) => {
    window.localStorage.setItem("tutor.workspace.role", JSON.stringify(workspaceRole));
  }, role);
};

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

test.describe("admin sidebar navigation", () => {
  test.beforeEach(async ({ page }) => {
    await setWorkspaceRole(page, "admin");
  });

  for (const navCase of ADMIN_NAV_ACTIVE_CASES) {
    test(`${navCase.path} marks exactly one admin sidebar item active`, async ({ page }) => {
      await page.goto(navCase.path);

      await expect(page.locator("#main-content")).toBeVisible();

      const activeSidebarLinks = page.locator('#sidebar nav a[aria-current="page"]');
      await expect(activeSidebarLinks).toHaveCount(1);
      await expect(activeSidebarLinks).toContainText(navCase.activeLabel);
    });
  }
});

test.describe("workspace shell reflow", () => {
  for (const viewport of WORKSPACE_REFLOW_VIEWPORTS) {
    for (const reflowCase of WORKSPACE_REFLOW_CASES) {
      test(`${reflowCase.path} has no horizontal overflow on ${viewport.name}`, async ({ page }) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        if ("role" in reflowCase) {
          await setWorkspaceRole(page, reflowCase.role);
        }

        await page.goto(reflowCase.path);

        await expect(page.locator("#main-content")).toBeVisible();
        await expectWorkspaceShellBelowHeader(page);
        await expectNoHorizontalOverflow(page);
      });
    }
  }

  for (const viewport of WORKSPACE_REFLOW_VIEWPORTS) {
    test(`workspace sidebar starts closed and toggles on ${viewport.name}`, async ({ page }) => {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await setWorkspaceRole(page, "admin");

      await page.goto("/configuration/cases");

      await expect(page.locator("#main-content")).toBeVisible();
      await expect(page.locator('button[aria-label="Close sidebar"]')).toHaveCount(0);
      await expect(page.locator('button[aria-controls="sidebar"]')).toHaveAttribute(
        "aria-expanded",
        "false",
      );
      await expectWorkspaceShellBelowHeader(page);
      await expectSidebarOffCanvas(page);
      await expectNoHorizontalOverflow(page);

      await page.locator('button[aria-controls="sidebar"]').click();
      await expect(page.locator('button[aria-label="Close sidebar"]')).toBeVisible();
      await expect(page.locator('button[aria-controls="sidebar"]')).toHaveAttribute(
        "aria-expanded",
        "true",
      );
      await expectWorkspaceShellBelowHeader(page);
      await expectSidebarOnCanvas(page);

      await page.mouse.click(viewport.width - 16, Math.min(320, viewport.height - 16));
      await expect(page.locator('button[aria-label="Close sidebar"]')).toHaveCount(0);
      await expect(page.locator('button[aria-controls="sidebar"]')).toHaveAttribute(
        "aria-expanded",
        "false",
      );
      await expectWorkspaceShellBelowHeader(page);
      await expectSidebarOffCanvas(page);
      await expectNoHorizontalOverflow(page);
    });
  }

  test("workspace sidebar is visible by default on desktop and still toggles", async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await setWorkspaceRole(page, "admin");

    await page.goto("/configuration/cases");

    await expect(page.locator("#main-content")).toBeVisible();
    await expect(page.locator('button[aria-controls="sidebar"]')).toHaveAttribute("aria-expanded", "true");
    await expectWorkspaceShellBelowHeader(page);
    await expectSidebarOnCanvas(page);
    await expectSidebarFixed(page);
    await expectNoHorizontalOverflow(page);

    await page.locator('button[aria-controls="sidebar"]').click();
    await expect(page.locator('button[aria-controls="sidebar"]')).toHaveAttribute("aria-expanded", "false");
    await expectWorkspaceShellBelowHeader(page);
    await expectSidebarOffCanvas(page);
    await expectNoHorizontalOverflow(page);

    await page.locator('button[aria-controls="sidebar"]').click();
    await expect(page.locator('button[aria-controls="sidebar"]')).toHaveAttribute("aria-expanded", "true");
    await expectWorkspaceShellBelowHeader(page);
    await expectSidebarOnCanvas(page);
    await expectNoHorizontalOverflow(page);
  });
});
