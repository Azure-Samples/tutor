import { expect, test } from "@playwright/test";

import { mockEvaluationApim } from "./fixtures/evaluation-apim";

test("evaluation dashboard lists datasets, creates a dataset, starts a run, and opens the run", async ({
  page,
}) => {
  const apimState = await mockEvaluationApim(page);

  await page.goto("/evaluation");

  await expect(
    page.getByRole("heading", { name: "Dataset inventory and run launch" }),
  ).toBeVisible();
  await expect(page.getByText("Loaded 1 evaluation dataset.")).toBeVisible();
  await expect(page.getByRole("cell", { name: "Foundation Evaluation Dataset" })).toBeVisible();

  await page.getByLabel("Dataset ID").fill("e2e-dataset");
  await page.getByLabel("Dataset name").fill("E2E Evaluation Dataset");
  await page.getByLabel("Prompt").fill("Summarize momentum in one sentence.");
  await page.getByLabel("Expected answer").fill("Momentum is mass multiplied by velocity.");
  await page.getByRole("button", { name: "Create dataset" }).click();

  await expect(page.getByText("Dataset e2e-dataset is ready for evaluation runs.")).toBeVisible();
  await expect(page.getByRole("cell", { name: "E2E Evaluation Dataset" })).toBeVisible();
  await expect(page.getByLabel("Dataset", { exact: true })).toHaveValue("e2e-dataset");

  await page.getByLabel("Agent ID").fill("agent-e2e");
  await page.getByRole("button", { name: "Start run" }).click();

  await expect(page.getByText("Evaluation run run-e2e-001 is queued.")).toBeVisible();
  const viewRunLink = page.getByRole("link", { name: "View run run-e2e-001" });
  await expect(viewRunLink).toBeVisible();
  await expect(viewRunLink).toHaveAttribute("href", "/evaluation/run-e2e-001");
  await Promise.all([
    page.waitForURL(/\/evaluation\/run-e2e-001$/, { waitUntil: "commit" }),
    viewRunLink.click(),
  ]);

  await expect(page).toHaveURL(/\/evaluation\/run-e2e-001$/);
  await expect(page.getByRole("heading", { name: "run-e2e-001" })).toBeVisible();
  await expect(page.getByText("Run run-e2e-001 loaded with status queued.")).toBeVisible();
  await expect(page.getByText("agent-e2e")).toBeVisible();
  await expect(page.getByText("e2e-dataset")).toBeVisible();

  expect(apimState.requests.map((request) => `${request.method} ${request.path}`)).toEqual(
    expect.arrayContaining([
      "GET /api/evaluation/datasets",
      "POST /api/evaluation/datasets",
      "POST /api/evaluation/evaluation/run",
      "GET /api/evaluation/evaluation/run/run-e2e-001",
    ]),
  );
});
