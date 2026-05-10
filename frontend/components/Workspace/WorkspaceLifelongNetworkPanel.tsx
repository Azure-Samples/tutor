"use client";

import { useWorkspace } from "@/components/Workspace/WorkspaceProvider";
import {
  getLifelongNetwork,
  humanizeIdentifier,
  type AccessContextPayload,
  type LifelongLearnerNetworkPayload,
} from "@/utils/workspace-api";
import { useCallback, useEffect, useMemo, useState } from "react";
import { FiAward, FiBriefcase, FiDatabase, FiRefreshCw, FiShield } from "react-icons/fi";

const PILOT_LEARNER_ID = "paulo-nogueira";
const PILOT_TENANT_ID = "tutor-pilot-tenant";

interface LifelongNetworkContext {
  contextId: string;
  learnerId: string;
  tenantId: string;
}

const getAlumniAccessContext = (accessContext: AccessContextPayload | null, contextId: string) => {
  const roleContext = accessContext?.roles.find((item) => item.role === "alumni");
  const selectedContext = roleContext?.contexts.find((context) => context.context_id === contextId);
  return selectedContext ?? roleContext?.contexts[0] ?? null;
};

const getScopedValue = (
  accessContext: AccessContextPayload | null,
  contextId: string,
  fieldName: "institution_ids" | "learner_ids",
): string | null => {
  const roleContext = accessContext?.roles.find((item) => item.role === "alumni");
  const selectedContext = roleContext?.contexts.find((context) => context.context_id === contextId);
  return (
    selectedContext?.scope[fieldName][0] ??
    roleContext?.contexts[0]?.scope[fieldName][0] ??
    roleContext?.grants[0]?.scope[fieldName][0] ??
    null
  );
};

const CountCard = ({
  label,
  value,
  detail,
}: {
  label: string;
  value: string | number;
  detail: string;
}) => (
  <div className="rounded-[1.25rem] border border-stone-200 bg-stone-50/80 p-4 dark:border-slate-700 dark:bg-slate-950/60">
    <dt className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">
      {label}
    </dt>
    <dd className="mt-2 text-2xl font-semibold text-slate-900 dark:text-slate-50">{value}</dd>
    <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">{detail}</p>
  </div>
);

const StatusPill = ({ label }: { label: string }) => (
  <span className="inline-flex rounded-full border border-stone-200 bg-white px-3 py-1 text-xs font-semibold text-slate-700 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-200">
    {label}
  </span>
);

const reviewLabel = (status: string | null | undefined) => {
  if (!status) {
    return "Unavailable";
  }

  const normalizedStatus = status.toLowerCase().replace(/[\s:-]+/g, "_");

  if (normalizedStatus === "not_final" || normalizedStatus === "non_final") {
    return "Review draft";
  }

  if (normalizedStatus.includes("final")) {
    return "Review recorded";
  }

  if (normalizedStatus.includes("operational")) {
    return "Review required";
  }

  return humanizeIdentifier(status);
};

// No GoF pattern applies -- this route panel presents one learner-scoped read model.
const WorkspaceLifelongNetworkPanel = () => {
  const { accessContext, actor, currentContext, isMockMode } = useWorkspace();
  const [network, setNetwork] = useState<LifelongLearnerNetworkPayload | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [loadError, setLoadError] = useState("");

  const lifelongContext = useMemo<LifelongNetworkContext>(() => {
    const alumniContext = getAlumniAccessContext(accessContext, currentContext.id);
    const learnerId =
      getScopedValue(accessContext, currentContext.id, "learner_ids") ??
      currentContext.learnerIds?.[0] ??
      PILOT_LEARNER_ID;
    const tenantId =
      actor?.tenant_id ??
      getScopedValue(accessContext, currentContext.id, "institution_ids") ??
      PILOT_TENANT_ID;
    const contextId = alumniContext?.context_id.includes(":")
      ? alumniContext.context_id
      : `alumni:learner:${learnerId}`;

    return { contextId, learnerId, tenantId };
  }, [accessContext, actor?.tenant_id, currentContext]);

  const loadNetwork = useCallback(async () => {
    setIsLoading(true);
    setLoadError("");

    try {
      const payload = await getLifelongNetwork(lifelongContext.learnerId, {
        contextId: lifelongContext.contextId,
        tenantId: lifelongContext.tenantId,
      });
      setNetwork(payload);
    } catch (caughtError: unknown) {
      setNetwork(null);
      setLoadError(
        caughtError instanceof Error
          ? caughtError.message
          : "Lifelong network API is unavailable. Current record links remain active.",
      );
    } finally {
      setIsLoading(false);
    }
  }, [lifelongContext]);

  useEffect(() => {
    void loadNetwork();
  }, [loadNetwork]);

  const primaryCredential = network?.credentials[0] ?? null;
  const primaryPathway = network?.re_entry_pathways[0] ?? null;
  const publicationStatus = network?.publication_approvals[0]?.status ?? "review_required";

  return (
    <section className="rounded-[1.75rem] border border-stone-200 bg-white/90 p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900/75">
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-teal-700 dark:text-teal-300">
            P3 lifelong network
          </p>
          <h2 className="mt-3 text-2xl font-semibold text-slate-900 dark:text-slate-50">
            Credentials, portfolio, re-entry, and research governance
          </h2>
          <p className="mt-2 text-sm leading-7 text-slate-600 dark:text-slate-300">
            {humanizeIdentifier(lifelongContext.learnerId)} · {humanizeIdentifier(lifelongContext.tenantId)}
          </p>
        </div>
        <button
          type="button"
          onClick={() => void loadNetwork()}
          disabled={isLoading}
          className="inline-flex items-center justify-center gap-2 rounded-full border border-stone-200 bg-white px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-stone-50 disabled:opacity-60 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-50 dark:hover:bg-slate-900"
        >
          <FiRefreshCw aria-hidden="true" className={isLoading ? "animate-spin" : ""} />
          Refresh network
        </button>
      </div>

      {(loadError || isMockMode) && (
        <div className="mt-5 rounded-[1.25rem] border border-amber-200 bg-amber-50/80 p-4 text-sm leading-7 text-amber-950 dark:border-amber-900/60 dark:bg-amber-950/20 dark:text-amber-100">
          {loadError || "Workspace access context is unavailable. Local pilot defaults are shown."}
        </div>
      )}

      <dl className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <CountCard
          label="Credentials"
          value={network?.credentials.length ?? 0}
          detail={primaryCredential ? humanizeIdentifier(primaryCredential.status) : "No credential payload loaded"}
        />
        <CountCard
          label="Portfolio"
          value={network?.portfolio_artifacts.length ?? 0}
          detail={network?.portfolio_artifacts[0]?.title ?? "Evidence references unavailable"}
        />
        <CountCard
          label="Re-entry"
          value={network?.re_entry_pathways.length ?? 0}
          detail={primaryPathway ? humanizeIdentifier(primaryPathway.readiness) : "Pathway payload unavailable"}
        />
        <CountCard
          label="Research"
          value={network?.research_datasets.length ?? 0}
          detail={humanizeIdentifier(publicationStatus)}
        />
      </dl>

      <div className="mt-5 grid gap-4 lg:grid-cols-3">
        <article className="rounded-[1.25rem] border border-stone-200 bg-stone-50/80 p-5 dark:border-slate-700 dark:bg-slate-950/60">
          <div className="flex items-center gap-3">
            <FiAward aria-hidden="true" className="text-xl text-teal-700 dark:text-teal-300" />
            <h3 className="text-base font-semibold text-slate-900 dark:text-slate-50">
              Credential summary
            </h3>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            <StatusPill label={primaryCredential ? humanizeIdentifier(primaryCredential.status) : "Unavailable"} />
            <StatusPill label={`${network?.credential_definitions.length ?? 0} definitions`} />
            <StatusPill label={`${network?.verification_requests.length ?? 0} verifications`} />
          </div>
        </article>

        <article className="rounded-[1.25rem] border border-stone-200 bg-stone-50/80 p-5 dark:border-slate-700 dark:bg-slate-950/60">
          <div className="flex items-center gap-3">
            <FiBriefcase aria-hidden="true" className="text-xl text-teal-700 dark:text-teal-300" />
            <h3 className="text-base font-semibold text-slate-900 dark:text-slate-50">
              Re-entry network
            </h3>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            <StatusPill label={`${network?.mentor_relationships.length ?? 0} mentor links`} />
            <StatusPill label={`${network?.community_events.length ?? 0} events`} />
            <StatusPill label={primaryPathway?.status ? humanizeIdentifier(primaryPathway.status) : "Unavailable"} />
          </div>
        </article>

        <article className="rounded-[1.25rem] border border-stone-200 bg-stone-50/80 p-5 dark:border-slate-700 dark:bg-slate-950/60">
          <div className="flex items-center gap-3">
            <FiShield aria-hidden="true" className="text-xl text-teal-700 dark:text-teal-300" />
            <h3 className="text-base font-semibold text-slate-900 dark:text-slate-50">
              Governance
            </h3>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            <StatusPill label={reviewLabel(network?.governance.review.status)} />
            <StatusPill label={network?.governance.final_decision ? "Review recorded" : "Advisory only"} />
            <StatusPill label={network?.data_minimization.direct_identifiers ?? "not_returned"} />
          </div>
        </article>
      </div>

      <div className="mt-5 rounded-[1.25rem] border border-stone-200 bg-stone-50/80 p-4 dark:border-slate-700 dark:bg-slate-950/60">
        <div className="flex items-center gap-3">
          <FiDatabase aria-hidden="true" className="text-xl text-teal-700 dark:text-teal-300" />
          <p className="text-sm font-semibold text-slate-900 dark:text-slate-50">
            Research governance summary
          </p>
        </div>
        <dl className="mt-4 grid gap-3 text-sm text-slate-600 md:grid-cols-3 dark:text-slate-300">
          <div>
            <dt className="font-medium text-slate-900 dark:text-slate-50">Data-use agreements</dt>
            <dd>{network?.data_use_agreements.length ?? 0}</dd>
          </div>
          <div>
            <dt className="font-medium text-slate-900 dark:text-slate-50">De-identification runs</dt>
            <dd>{network?.de_identification_runs.length ?? 0}</dd>
          </div>
          <div>
            <dt className="font-medium text-slate-900 dark:text-slate-50">Publication approvals</dt>
            <dd>{humanizeIdentifier(publicationStatus)}</dd>
          </div>
        </dl>
      </div>
    </section>
  );
};

export default WorkspaceLifelongNetworkPanel;