import { defineConfig, devices } from "@playwright/test";

const e2ePort = Number(process.env.E2E_PORT ?? 3100);
const e2eBaseUrl = process.env.E2E_BASE_URL ?? `http://127.0.0.1:${e2ePort}`;
const reuseExistingServer = Boolean(process.env.PLAYWRIGHT_REUSE_SERVER) && !process.env.CI;

const createWebServerEnvironment = (): Record<string, string> => {
  const environment: Record<string, string> = {};

  for (const [name, value] of Object.entries(process.env)) {
    if (typeof value === "string") {
      environment[name] = value;
    }
  }

  environment.NEXT_PUBLIC_APIM_BASE_URL = e2eBaseUrl;

  return environment;
};

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: process.env.CI ? "github" : "list",
  timeout: 30000,
  expect: {
    timeout: 5000,
  },
  use: {
    baseURL: e2eBaseUrl,
    serviceWorkers: "block",
    trace: "retain-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: {
    command: `pnpm exec next dev --hostname 127.0.0.1 --port ${e2ePort}`,
    env: createWebServerEnvironment(),
    reuseExistingServer,
    timeout: 120000,
    url: e2eBaseUrl,
  },
});
