import { expect, test, type Page } from "@playwright/test";

const LOCALIZED_PUBLIC_HEADER_CASES = [
  { htmlLang: "es", locale: "es" },
  { htmlLang: "pt-BR", locale: "pt" },
] as const;

const PUBLIC_HEADER_REFLOW_VIEWPORTS = [
  { height: 844, name: "mobile", width: 390 },
  { height: 1024, name: "tablet", width: 768 },
] as const;

const getPublicHeaderLanguageSwitcher = (page: Page) =>
  page.locator("header").getByLabel(/^(Language|Idioma)$/).filter({ visible: true }).first();

const expectNoHorizontalOverflow = async (page: Page) => {
  await expect
    .poll(async () =>
      page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth),
    )
    .toBeLessThanOrEqual(1);
};

test("public header language switcher updates translated home copy and html lang", async ({ page }) => {
  await page.goto("/");

  const languageSwitcher = getPublicHeaderLanguageSwitcher(page);
  await expect(languageSwitcher).toBeVisible();

  await languageSwitcher.selectOption("es");

  await expect(page.locator("html")).toHaveAttribute("lang", "es");
  await expect(
    page.getByRole("heading", {
      name: /Una entrada acad.mica profesional para registros de estudiantes, trabajo guiado, briefings de liderazgo y reingreso curado\./i,
    }),
  ).toBeVisible();
  await expect(page.getByRole("link", { name: "Entrar a un espacio piloto" })).toBeVisible();

  await languageSwitcher.selectOption("pt");

  await expect(page.locator("html")).toHaveAttribute("lang", "pt-BR");
  await expect(
    page.getByRole("heading", {
      name: /Uma entrada acad.mica profissional para registros de estudantes, trabalho guiado, briefings de lideran.a e reentrada curada\./i,
    }),
  ).toBeVisible();
  await expect(page.getByRole("link", { name: "Entrar em um espaço piloto" })).toBeVisible();
});

test.describe("localized public header reflow", () => {
  for (const viewport of PUBLIC_HEADER_REFLOW_VIEWPORTS) {
    for (const localizedCase of LOCALIZED_PUBLIC_HEADER_CASES) {
      test(`public header has no horizontal overflow for ${localizedCase.locale} on ${viewport.name}`, async ({
        page,
      }) => {
        await page.setViewportSize({ height: viewport.height, width: viewport.width });
        await page.goto("/");

        const languageSwitcher = getPublicHeaderLanguageSwitcher(page);
        await expect(languageSwitcher).toBeVisible();
        await languageSwitcher.selectOption(localizedCase.locale);

        await expect(page.locator("html")).toHaveAttribute("lang", localizedCase.htmlLang);
        await expect(getPublicHeaderLanguageSwitcher(page)).toBeVisible();
        await expectNoHorizontalOverflow(page);
      });
    }
  }
});