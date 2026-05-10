"use client";

import { useWorkspace } from "@/components/Workspace/WorkspaceProvider";
import {
  createCausalStudy,
  getConformalRisk,
  getSchoolUnitIntelligence,
  humanizeIdentifier,
  type AccessContextPayload,
  type CausalStudyCommand,
  type CausalStudyReport,
  type ConformalRiskReport,
  type SchoolUnitIntelligencePayload,
} from "@/utils/workspace-api";
import type { WorkspaceRole } from "@/utils/workspace";
import { useCallback, useEffect, useMemo, useState } from "react";
import { FiActivity, FiRefreshCw, FiShield, FiZap } from "react-icons/fi";

const PILOT_SCHOOL_ID = "aurora-campus-north";
const PILOT_TENANT_ID = "tutor-pilot-tenant";

interface WorkspaceGovernedIntelligencePanelProps {
  workspaceRole: Extract<WorkspaceRole, "principal" | "supervisor">;
}

interface ScopedIntelligenceContext {
  contextId: string;
  learnerId: string | null;
  schoolId: string;
  tenantId: string;
}

const getRoleAccessContext = (
  accessContext: AccessContextPayload | null,
  role: WorkspaceRole,
  contextId: string,
) => {
  const roleContext = accessContext?.roles.find((item) => item.role === role);
  const selectedContext = roleContext?.contexts.find((context) => context.context_id === contextId);
  return selectedContext ?? roleContext?.contexts[0] ?? null;
};

const getScopedValue = (
  accessContext: AccessContextPayload | null,
  role: WorkspaceRole,
  contextId: string,
  fieldName: "institution_ids" | "school_ids" | "learner_ids",
): string | null => {
  const roleContext = accessContext?.roles.find((item) => item.role === role);
  const selectedContext = roleContext?.contexts.find((context) => context.context_id === contextId);
  const contextValue = selectedContext?.scope[fieldName][0] ?? roleContext?.contexts[0]?.scope[fieldName][0];
  return contextValue ?? roleContext?.grants[0]?.scope[fieldName][0] ?? null;
};

const getExplicitLearnerId = (
  accessContext: AccessContextPayload | null,
  role: WorkspaceRole,
  contextId: string,
): string | null => {
  const roleContext = accessContext?.roles.find((item) => item.role === role);
  const selectedContext = roleContext?.contexts.find((context) => context.context_id === contextId);
  const grantedLearnerId = roleContext?.grants.find((grant) => grant.scope.learner_ids.length > 0)
    ?.scope.learner_ids[0];

  return selectedContext?.scope.learner_ids[0] ?? grantedLearnerId ?? null;
};

const formatPercent = (value: number | null | undefined) =>
  typeof value === "number" ? `${Math.round(value * 100)}%` : "Suppressed";

const governanceLabel = (report: { governance: { review: { status: string }; final_decision: boolean } } | null) => {
  if (!report) {
    return "Unavailable";
  }

  if (report.governance.final_decision) {
    return "Review recorded";
  }

  const normalizedStatus = report.governance.review.status.toLowerCase().replace(/[\s:-]+/g, "_");

  if (normalizedStatus === "not_final" || normalizedStatus === "non_final") {
    return "Review draft";
  }

  if (normalizedStatus.includes("final")) {
    return "Review recorded";
  }

  if (normalizedStatus.includes("operational")) {
    return "Review required";
  }

  return humanizeIdentifier(report.governance.review.status);
};

const buildCausalCommand = (schoolId: string, tenantId: string): CausalStudyCommand => ({
  school_id: schoolId,
  tenant_id: tenantId,
  dag: "weekly tutoring -> mastery growth; prior mastery -> weekly tutoring; prior mastery -> mastery growth",
  treatment: "weekly tutoring",
  outcome: "mastery growth",
  estimand: "average treatment effect of weekly tutoring on mastery growth",
  population: `${humanizeIdentifier(schoolId)} learners`,
  confounders: ["prior mastery", "attendance consistency"],
  refutation_checks: ["placebo outcome", "negative control exposure"],
});

const metricToneClass = (status: "visible" | "suppressed") =>
  status === "suppressed"
    ? "border-amber-200 bg-amber-50 text-amber-950 dark:border-amber-900/60 dark:bg-amber-950/20 dark:text-amber-100"
    : "border-emerald-200 bg-emerald-50 text-emerald-950 dark:border-emerald-900/60 dark:bg-emerald-950/20 dark:text-emerald-100";

const StatusPill = ({ label }: { label: string }) => (
  <span className="inline-flex rounded-full border border-stone-200 bg-white px-3 py-1 text-xs font-semibold text-slate-700 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-200">
    {label}
  </span>
);

// No GoF pattern applies -- this route panel composes typed read models into workspace UI.
const WorkspaceGovernedIntelligencePanel = ({
  workspaceRole,
}: WorkspaceGovernedIntelligencePanelProps) => {
  const { accessContext, actor, currentContext, isMockMode } = useWorkspace();
  const [schoolUnit, setSchoolUnit] = useState<SchoolUnitIntelligencePayload | null>(null);
  const [conformalRisk, setConformalRisk] = useState<ConformalRiskReport | null>(null);
  const [causalReport, setCausalReport] = useState<CausalStudyReport | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isCausalLoading, setIsCausalLoading] = useState(false);
  const [loadError, setLoadError] = useState("");
  const [causalError, setCausalError] = useState("");
  const canDraftCausalStudy = workspaceRole === "supervisor";

  const scopedContext = useMemo<ScopedIntelligenceContext>(() => {
    const roleAccessContext = getRoleAccessContext(accessContext, workspaceRole, currentContext.id);
    const schoolId =
      getScopedValue(accessContext, workspaceRole, currentContext.id, "school_ids") ?? PILOT_SCHOOL_ID;
    const learnerId = getExplicitLearnerId(accessContext, workspaceRole, currentContext.id);
    const tenantId =
      actor?.tenant_id ??
      getScopedValue(accessContext, workspaceRole, currentContext.id, "institution_ids") ??
      PILOT_TENANT_ID;
    const contextId = roleAccessContext?.context_id.includes(":")
      ? roleAccessContext.context_id
      : `${workspaceRole}:school:${schoolId}`;

    return {
      contextId,
      learnerId,
      schoolId,
      tenantId,
    };
  }, [accessContext, actor?.tenant_id, currentContext.id, workspaceRole]);

  const loadGovernedStatus = useCallback(async () => {
    setIsLoading(true);
    setLoadError("");

    const riskRequest = scopedContext.learnerId
      ? getConformalRisk(scopedContext.learnerId, {
          contextId: scopedContext.contextId,
          schoolId: scopedContext.schoolId,
          tenantId: scopedContext.tenantId,
        })
      : Promise.resolve<ConformalRiskReport | null>(null);

    const [schoolResult, riskResult] = await Promise.allSettled([
      getSchoolUnitIntelligence({
        schoolId: scopedContext.schoolId,
        tenantId: scopedContext.tenantId,
        unitId: currentContext.id,
      }),
      riskRequest,
    ]);

    setSchoolUnit(schoolResult.status === "fulfilled" ? schoolResult.value : null);
    setConformalRisk(riskResult.status === "fulfilled" ? riskResult.value : null);

    if (schoolResult.status === "rejected" || (scopedContext.learnerId && riskResult.status === "rejected")) {
      setLoadError("Governed intelligence APIs are unavailable. Current briefing links remain active.");
    }

    setIsLoading(false);
  }, [currentContext.id, scopedContext]);

  useEffect(() => {
    void loadGovernedStatus();
  }, [loadGovernedStatus]);

  const draftCausalStudy = async () => {
    if (!canDraftCausalStudy) {
      return;
    }

    setIsCausalLoading(true);
    setCausalError("");

    try {
      const report = await createCausalStudy(
        buildCausalCommand(scopedContext.schoolId, scopedContext.tenantId),
      );
      setCausalReport(report);
    } catch (caughtError: unknown) {
      setCausalReport(null);
      setCausalError(
        caughtError instanceof Error
          ? caughtError.message
          : "Causal study API is unavailable. Existing briefing links remain active.",
      );
    } finally {
      setIsCausalLoading(false);
    }
  };

  const suppressedMetrics = schoolUnit?.metrics.filter((metric) => metric.status === "suppressed") ?? [];
  const primaryRisk = conformalRisk?.risks[0] ?? null;
  const learnerScopeLabel = scopedContext.learnerId
    ? humanizeIdentifier(scopedContext.learnerId)
    : "Learner scope required for risk";

  return (
    <section className="rounded-[1.75rem] border border-stone-200 bg-white/90 p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900/75">
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-teal-700 dark:text-teal-300">
            P2/P3 governed status
          </p>
          <h2 className="mt-3 text-2xl font-semibold text-slate-900 dark:text-slate-50">
            School-unit intelligence and risk governance
          </h2>
          <p className="mt-2 text-sm leading-7 text-slate-600 dark:text-slate-300">
            {humanizeIdentifier(scopedContext.schoolId)} · {learnerScopeLabel}
          </p>
        </div>
        <button
          type="button"
          onClick={() => void loadGovernedStatus()}
          disabled={isLoading}
          className="inline-flex items-center justify-center gap-2 rounded-full border border-stone-200 bg-white px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-stone-50 disabled:opacity-60 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-50 dark:hover:bg-slate-900"
        >
          <FiRefreshCw aria-hidden="true" className={isLoading ? "animate-spin" : ""} />
          Refresh status
        </button>
      </div>

      {(loadError || isMockMode) && (
        <div className="mt-5 rounded-[1.25rem] border border-amber-200 bg-amber-50/80 p-4 text-sm leading-7 text-amber-950 dark:border-amber-900/60 dark:bg-amber-950/20 dark:text-amber-100">
          {loadError || "Workspace access context is unavailable. Local pilot defaults are shown."}
        </div>
      )}

      <div className={`mt-5 grid gap-4 ${canDraftCausalStudy ? "xl:grid-cols-3" : "xl:grid-cols-2"}`}>
        <article className="rounded-[1.25rem] border border-stone-200 bg-stone-50/80 p-5 dark:border-slate-700 dark:bg-slate-950/60">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <FiActivity aria-hidden="true" className="text-xl text-teal-700 dark:text-teal-300" />
              <h3 className="text-base font-semibold text-slate-900 dark:text-slate-50">
                School-unit intelligence
              </h3>
            </div>
            <StatusPill label={governanceLabel(schoolUnit)} />
          </div>
          <dl className="mt-4 grid gap-3 text-sm text-slate-600 dark:text-slate-300">
            <div className="flex items-center justify-between gap-4">
              <dt>Metrics</dt>
              <dd className="font-semibold text-slate-900 dark:text-slate-50">
                {schoolUnit?.metrics.length ?? 0}
              </dd>
            </div>
            <div className="flex items-center justify-between gap-4">
              <dt>Suppressed cells</dt>
              <dd className="font-semibold text-slate-900 dark:text-slate-50">
                {suppressedMetrics.length}
              </dd>
            </div>
            <div className="flex items-center justify-between gap-4">
              <dt>Coverage</dt>
              <dd className="font-semibold text-slate-900 dark:text-slate-50">
                {formatPercent(schoolUnit?.governance.coverage.coverage_rate)}
              </dd>
            </div>
          </dl>
          <div className="mt-4 space-y-2">
            {(schoolUnit?.metrics ?? []).slice(0, 3).map((metric) => (
              <div
                key={metric.metric_id}
                className={`rounded-[1rem] border px-3 py-2 text-xs font-medium ${metricToneClass(metric.status)}`}
              >
                {metric.label ?? humanizeIdentifier(metric.metric_id)} · {formatPercent(metric.value)} · n=
                {metric.sample_count}
              </div>
            ))}
          </div>
        </article>

        {canDraftCausalStudy && (
          <article className="rounded-[1.25rem] border border-stone-200 bg-stone-50/80 p-5 dark:border-slate-700 dark:bg-slate-950/60">
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <FiZap aria-hidden="true" className="text-xl text-teal-700 dark:text-teal-300" />
                <h3 className="text-base font-semibold text-slate-900 dark:text-slate-50">
                  Causal study
                </h3>
              </div>
              <StatusPill label={causalReport ? governanceLabel(causalReport) : "Draft ready"} />
            </div>
            <dl className="mt-4 grid gap-3 text-sm text-slate-600 dark:text-slate-300">
              <div className="flex items-center justify-between gap-4">
                <dt>Effect estimate</dt>
                <dd className="font-semibold text-slate-900 dark:text-slate-50">
                  {causalReport ? causalReport.effect_estimate.toFixed(3) : "Pending"}
                </dd>
              </div>
              <div className="flex items-center justify-between gap-4">
                <dt>Sensitivity checks</dt>
                <dd className="font-semibold text-slate-900 dark:text-slate-50">
                  {causalReport?.sensitivity_checks.length ?? 0}
                </dd>
              </div>
              <div className="flex items-center justify-between gap-4">
                <dt>Review posture</dt>
                <dd className="font-semibold text-slate-900 dark:text-slate-50">
                  {causalReport?.governance.final_decision ? "Review recorded" : "Review pending"}
                </dd>
              </div>
            </dl>
            <button
              type="button"
              onClick={() => void draftCausalStudy()}
              disabled={isCausalLoading}
              className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-full border border-teal-700 bg-teal-700 px-4 py-2 text-sm font-semibold text-white transition hover:bg-teal-800 disabled:opacity-60"
            >
              <FiZap aria-hidden="true" />
              {isCausalLoading ? "Drafting study" : "Draft causal study"}
            </button>
            {causalError && (
              <p className="mt-3 rounded-[1rem] border border-amber-200 bg-amber-50 px-3 py-2 text-xs leading-6 text-amber-950 dark:border-amber-900/60 dark:bg-amber-950/20 dark:text-amber-100">
                {causalError}
              </p>
            )}
          </article>
        )}

        <article className="rounded-[1.25rem] border border-stone-200 bg-stone-50/80 p-5 dark:border-slate-700 dark:bg-slate-950/60">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <FiShield aria-hidden="true" className="text-xl text-teal-700 dark:text-teal-300" />
              <h3 className="text-base font-semibold text-slate-900 dark:text-slate-50">
                Conformal risk
              </h3>
            </div>
            <StatusPill label={scopedContext.learnerId ? governanceLabel(conformalRisk) : "Learner scope required"} />
          </div>
          {!scopedContext.learnerId && (
            <p className="mt-4 rounded-[1rem] border border-amber-200 bg-amber-50 px-3 py-2 text-xs leading-6 text-amber-950 dark:border-amber-900/60 dark:bg-amber-950/20 dark:text-amber-100">
              Conformal risk was not requested because this leader context has no explicit learner membership.
            </p>
          )}
          <dl className="mt-4 grid gap-3 text-sm text-slate-600 dark:text-slate-300">
            <div className="flex items-center justify-between gap-4">
              <dt>Risk label</dt>
              <dd className="font-semibold text-slate-900 dark:text-slate-50">
                {scopedContext.learnerId ? primaryRisk?.risk_label ?? "Suppressed" : "Awaiting learner scope"}
              </dd>
            </div>
            <div className="flex items-center justify-between gap-4">
              <dt>Score</dt>
              <dd className="font-semibold text-slate-900 dark:text-slate-50">
                {scopedContext.learnerId ? formatPercent(primaryRisk?.score) : "Not requested"}
              </dd>
            </div>
            <div className="flex items-center justify-between gap-4">
              <dt>Abstention</dt>
              <dd className="font-semibold text-slate-900 dark:text-slate-50">
                {scopedContext.learnerId
                  ? conformalRisk?.abstention.abstained
                    ? "Active"
                    : "Clear"
                  : "Not assessed"}
              </dd>
            </div>
          </dl>
          <div className="mt-4 flex flex-wrap gap-2">
            <StatusPill label={`Coverage ${formatPercent(conformalRisk?.coverage.coverage_rate)}`} />
            <StatusPill label={`Calibration n=${conformalRisk?.calibration.sample_count ?? 0}`} />
          </div>
        </article>
      </div>
    </section>
  );
};

export default WorkspaceGovernedIntelligencePanel;