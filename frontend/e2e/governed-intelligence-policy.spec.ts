import { expect, test, type Page, type Route } from "@playwright/test";

import type {
  AccessContextPayload,
  AccessScope,
  CausalStudyReport,
  ConformalRiskReport,
  IntelligenceGovernanceMetadata,
  SchoolUnitIntelligencePayload,
} from "@/utils/workspace-api";

type GovernedWorkspaceRole = "principal" | "supervisor";

interface SuccessEnvelope<T> {
  success: true;
  content: T;
}

interface ApimRequestRecord {
  method: string;
  path: string;
}

interface GovernedPolicyApimState {
  requests: ApimRequestRecord[];
}

const GENERATED_AT = "2026-05-09T12:00:00.000Z";
const LEARNER_ID = "learner-policy-001";
const SCHOOL_ID = "aurora-campus-north";
const TENANT_ID = "tutor-pilot-tenant";

const createScope = (overrides: Partial<AccessScope> = {}): AccessScope => ({
  class_ids: [],
  course_ids: [],
  institution_ids: [TENANT_ID],
  learner_ids: [],
  program_ids: [],
  school_ids: [SCHOOL_ID],
  staff_ids: ["policy-reviewer"],
  ...overrides,
});

const createAccessContext = (
  role: GovernedWorkspaceRole,
  learnerIds: string[],
): AccessContextPayload => {
  const workspacePath =
    role === "principal" ? "/workspace/principal/school-health" : "/workspace/supervisor/briefings";
  const context = {
    context_id: `${role}:school:${SCHOOL_ID}`,
    context_type: "school",
    label: role === "principal" ? "Aurora Campus North" : "Aurora Network Briefing",
    relationship: role === "principal" ? "principal_of_school" : "network_supervisor",
    role,
    scope: createScope({ learner_ids: learnerIds }),
    workspace_path: workspacePath,
  };

  return {
    actor: {
      display_name: "Policy Reviewer",
      email: "policy-reviewer@local.test",
      object_id: `${role}-object-id`,
      subject: `${role}-subject`,
      tenant_id: TENANT_ID,
    },
    available_roles: [role],
    default_context: context,
    default_role: role,
    feature_flags: ["workspace-shell"],
    roles: [
      {
        contexts: [context],
        default_context_id: context.context_id,
        grants: [
          {
            relationship: context.relationship,
            role,
            scope: createScope({ learner_ids: learnerIds }),
          },
        ],
        role,
      },
    ],
  };
};

const createSuppression = (
  suppressed: boolean,
): IntelligenceGovernanceMetadata["suppression"] => ({
  minimum_count: suppressed ? 10 : null,
  observed_count: suppressed ? 4 : null,
  rationale: suppressed
    ? "Small cell suppressed in the advisory fixture."
    : "No suppression in the advisory fixture.",
  reason: suppressed ? "small_cell" : "none",
  suppressed,
  suppressed_fields: suppressed ? ["value"] : [],
});

const createUncertainty = (): IntelligenceGovernanceMetadata["uncertainty"] => ({
  confidence_level: 0.9,
  interval_width: null,
  lower_bound: null,
  method: "policy-e2e-fixture",
  point_estimate: null,
  rationale: "Fixture output is advisory and non-final.",
  upper_bound: null,
  wide: false,
});

const createCalibration = (): IntelligenceGovernanceMetadata["calibration"] => ({
  calibrated_at: GENERATED_AT,
  calibration_set_id: "policy-e2e-calibration",
  expected_coverage: 0.8,
  method: "split_conformal",
  observed_coverage: 0.82,
  sample_count: 24,
});

const createCoverage = (): IntelligenceGovernanceMetadata["coverage"] => ({
  covered_count: 20,
  coverage_rate: 0.83,
  eligible_count: 24,
  minimum_required: 10,
  population: "Aurora Campus North learners",
});

const createDrift = (metricName: string): IntelligenceGovernanceMetadata["drift"][number] => ({
  current_window: "2026-W18",
  measured_at: GENERATED_AT,
  metric_name: metricName,
  reference_window: "2026-W17",
  score: 0.03,
  status: "stable",
  threshold: 0.2,
});

const createAbstention = (): IntelligenceGovernanceMetadata["abstention"] => ({
  abstained: false,
  degraded: false,
  fallback_behavior: "show_advisory",
  reason: null,
});

const createAdvisoryGovernance = (): IntelligenceGovernanceMetadata => ({
  abstention: createAbstention(),
  advisory_only: true,
  appeal: {
    available: true,
    status: "available",
  },
  assumptions: [
    {
      assumption_id: "advisory-only",
      category: "policy",
      evidence_refs: ["policy-e2e"],
      required_for_use: true,
      statement: "P2/P3 outputs are advisory and cannot become final decisions in this fixture.",
    },
  ],
  calibration: createCalibration(),
  coverage: createCoverage(),
  drift: [createDrift("attendance_consistency")],
  final_decision: false,
  provenance: {
    generator: "playwright-policy-fixture",
    model: null,
    source_ids: ["policy-e2e"],
    source_type: "synthetic_e2e_fixture",
    workflow_version: "p2-p3-policy-e2e",
  },
  review: {
    required: true,
    status: "required",
    summary: "Advisory only; not a final decision.",
  },
  suppression: createSuppression(false),
  uncertainty: createUncertainty(),
});

const createSchoolUnitIntelligence = (requestUrl: URL): SchoolUnitIntelligencePayload => ({
  generated_at: GENERATED_AT,
  governance: createAdvisoryGovernance(),
  metrics: [
    {
      label: "Attendance consistency",
      metric_id: "attendance_consistency",
      sample_count: 24,
      status: "visible",
      suppression: createSuppression(false),
      value: 0.82,
    },
  ],
  school_id: requestUrl.searchParams.get("school_id") ?? SCHOOL_ID,
  tenant_id: requestUrl.searchParams.get("tenant_id") ?? TENANT_ID,
  unit_id: requestUrl.searchParams.get("unit_id") ?? `principal:school:${SCHOOL_ID}`,
});

const createConformalRisk = (learnerId: string, requestUrl: URL): ConformalRiskReport => ({
  abstention: createAbstention(),
  calibration: createCalibration(),
  context_id: requestUrl.searchParams.get("context_id") ?? `supervisor:school:${SCHOOL_ID}`,
  coverage: createCoverage(),
  drift: createDrift("risk_score"),
  generated_at: GENERATED_AT,
  governance: createAdvisoryGovernance(),
  learner_id: learnerId,
  risks: [
    {
      risk_id: "engagement-watch",
      risk_label: "Advisory engagement watch",
      risk_type: "engagement",
      sample_count: 24,
      score: 0.27,
      suppression: createSuppression(false),
      uncertainty: createUncertainty(),
    },
  ],
  tenant_id: requestUrl.searchParams.get("tenant_id") ?? TENANT_ID,
});

const readJsonPayload = (route: Route): Record<string, unknown> => {
  try {
    const payload: unknown = route.request().postDataJSON();

    return typeof payload === "object" && payload !== null
      ? (payload as Record<string, unknown>)
      : {};
  } catch {
    return {};
  }
};

const getStringPayloadValue = (payload: Record<string, unknown>, fieldName: string): string | null => {
  const value = payload[fieldName];

  return typeof value === "string" && value.trim().length > 0 ? value : null;
};

const createCausalStudy = (payload: Record<string, unknown>): CausalStudyReport => ({
  adjustment_set: ["prior mastery", "attendance consistency"],
  dag:
    getStringPayloadValue(payload, "dag") ??
    "weekly tutoring -> mastery growth; prior mastery -> mastery growth",
  dag_edges: [],
  effect_estimate: 0.12,
  estimand:
    getStringPayloadValue(payload, "estimand") ??
    "average treatment effect of weekly tutoring on mastery growth",
  generated_at: GENERATED_AT,
  governance: createAdvisoryGovernance(),
  outcome: getStringPayloadValue(payload, "outcome") ?? "mastery growth",
  population: getStringPayloadValue(payload, "population") ?? "Aurora Campus North learners",
  refutation_checks: ["placebo outcome"],
  refutation_results: [
    {
      check: "placebo outcome",
      result: "Planned for reviewer validation; no final decision made.",
      status: "needs_review",
    },
  ],
  school_id: getStringPayloadValue(payload, "school_id") ?? SCHOOL_ID,
  sensitivity_checks: [
    {
      check_id: "negative-control",
      method: "negative control exposure",
      status: "planned",
      summary: "Advisory fixture keeps the study in draft posture.",
      target: "mastery growth",
    },
  ],
  study_id: "causal-study-policy-e2e",
  tenant_id: getStringPayloadValue(payload, "tenant_id") ?? TENANT_ID,
  treatment: getStringPayloadValue(payload, "treatment") ?? "weekly tutoring",
  uncertainty: createUncertainty(),
});

const fulfillEnvelope = async <T>(route: Route, content: T, status = 200) => {
  const envelope: SuccessEnvelope<T> = { content, success: true };

  await route.fulfill({
    body: JSON.stringify(envelope),
    contentType: "application/json",
    status,
  });
};

const fulfillError = async (route: Route, status: number, detail: string) => {
  await route.fulfill({
    body: JSON.stringify({ detail, success: false }),
    contentType: "application/json",
    status,
  });
};

const recordRequest = (state: GovernedPolicyApimState, route: Route): URL => {
  const request = route.request();
  const requestUrl = new URL(request.url());

  state.requests.push({ method: request.method(), path: requestUrl.pathname });

  return requestUrl;
};

// Adapter between Playwright route interception and the governed intelligence APIM contract.
const mockGovernedPolicyApim = async (
  page: Page,
  accessContext: AccessContextPayload,
): Promise<GovernedPolicyApimState> => {
  const state: GovernedPolicyApimState = { requests: [] };

  await page.route("**/api/configuration/access-context", async (route) => {
    recordRequest(state, route);
    await fulfillEnvelope(route, accessContext);
  });

  await page.route("**/api/insights/**", async (route) => {
    const requestUrl = recordRequest(state, route);
    const method = route.request().method();
    const path = requestUrl.pathname;

    if (method === "GET" && path === "/api/insights/school-unit-intelligence") {
      await fulfillEnvelope(route, createSchoolUnitIntelligence(requestUrl));
      return;
    }

    if (method === "GET" && path.startsWith("/api/insights/conformal-risk/")) {
      const learnerId = decodeURIComponent(path.slice("/api/insights/conformal-risk/".length));
      await fulfillEnvelope(route, createConformalRisk(learnerId, requestUrl));
      return;
    }

    if (method === "POST" && path === "/api/insights/causal-studies") {
      await fulfillEnvelope(route, createCausalStudy(readJsonPayload(route)), 201);
      return;
    }

    await fulfillError(route, 404, `Unhandled governed policy route: ${method} ${path}`);
  });

  return state;
};

const requestKeys = (requests: ApimRequestRecord[]) =>
  requests.map((request) => `${request.method} ${request.path}`);

test.describe("P2/P3 governed intelligence policy", () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => window.localStorage.clear());
  });

  test("principal school health does not request learner-only or causal capabilities", async ({
    page,
  }) => {
    const apimState = await mockGovernedPolicyApim(
      page,
      createAccessContext("principal", []),
    );

    await page.goto("/workspace/principal/school-health");

    await expect(page.getByText("P2/P3 governed status").first()).toBeVisible();
    await expect(
      page.getByRole("heading", { name: "School-unit intelligence and risk governance" }),
    ).toBeVisible();
    await expect(page.getByText("Attendance consistency")).toBeVisible();
    await expect(page.getByText("Learner scope required for risk").first()).toBeVisible();
    await expect(
      page.getByText(
        "Conformal risk was not requested because this leader context has no explicit learner membership.",
      ),
    ).toBeVisible();
    await expect(page.getByRole("button", { name: "Draft causal study" })).toBeHidden();

    expect(
      apimState.requests.some((request) =>
        request.path.startsWith("/api/insights/conformal-risk/"),
      ),
    ).toBe(false);
    expect(
      apimState.requests.some((request) => request.path === "/api/insights/causal-studies"),
    ).toBe(false);
  });

  test("supervisor briefings can load learner risk and draft a causal study", async ({ page }) => {
    const apimState = await mockGovernedPolicyApim(
      page,
      createAccessContext("supervisor", [LEARNER_ID]),
    );
    const conformalRiskRequest = page.waitForRequest((request) => {
      const requestUrl = new URL(request.url());

      return (
        request.method() === "GET" &&
        requestUrl.pathname === `/api/insights/conformal-risk/${LEARNER_ID}`
      );
    });

    await page.goto("/workspace/supervisor/briefings");

    await expect(page.getByText("P2/P3 governed status").first()).toBeVisible();
    await expect(page.getByRole("button", { name: "Draft causal study" })).toBeVisible();
    await conformalRiskRequest;
    await expect(page.getByText("Advisory engagement watch")).toBeVisible();

    const causalStudyRequest = page.waitForRequest((request) => {
      const requestUrl = new URL(request.url());

      return request.method() === "POST" && requestUrl.pathname === "/api/insights/causal-studies";
    });

    await page.getByRole("button", { name: "Draft causal study" }).click();
    await causalStudyRequest;
    await expect(page.getByText("0.120")).toBeVisible();

    expect(requestKeys(apimState.requests)).toEqual(
      expect.arrayContaining([
        `GET /api/insights/conformal-risk/${LEARNER_ID}`,
        "POST /api/insights/causal-studies",
      ]),
    );
  });
});