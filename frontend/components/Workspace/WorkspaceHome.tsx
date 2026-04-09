"use client";

import { useWorkspace } from "@/components/Workspace/WorkspaceProvider";
import {
  type LearnerRecordTimelinePayload,
  type SnapshotItem,
  type WorkspaceSnapshotPayload,
  getLearnerRecordTimeline,
  getWorkspaceSnapshot,
  humanizeIdentifier,
} from "@/utils/workspace-api";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

type AsyncState<T> = {
  data: T | null;
  error: string | null;
  loading: boolean;
};

type KeyedLink<T> = T & {
  key: string;
};

// No GoF pattern applies here; this is a simple list-key stabilization transform.
function withStableLinkKeys<T extends { label: string }>(
  links: readonly T[],
  getHref: (link: T) => string,
): KeyedLink<T>[] {
  const occurrenceCounts = new Map<string, number>();

  return links.map((link) => {
    const baseKey = `${getHref(link)}-${link.label}`;
    const occurrence = (occurrenceCounts.get(baseKey) ?? 0) + 1;
    occurrenceCounts.set(baseKey, occurrence);

    return {
      ...link,
      key: `${baseKey}-${occurrence}`,
    };
  });
}

const toneStyles = {
  deterministic: "border-stone-200 bg-white/95 text-slate-700",
  advisory: "border-teal-200 bg-teal-50/80 text-teal-950",
  attention: "border-amber-200 bg-amber-50/85 text-amber-950",
} as const;

const freshnessStyles = {
  fresh: "border-emerald-200 bg-emerald-50 text-emerald-900",
  derived: "border-sky-200 bg-sky-50 text-sky-900",
  stale: "border-amber-200 bg-amber-50 text-amber-900",
  degraded: "border-rose-200 bg-rose-50 text-rose-900",
} as const;

const timelineStatusStyles = {
  confirmed: "border-stone-200 bg-white text-slate-700",
  advisory: "border-teal-200 bg-teal-50 text-teal-950",
  degraded: "border-amber-200 bg-amber-50 text-amber-950",
  needs_review: "border-rose-200 bg-rose-50 text-rose-950",
} as const;

function formatDateTime(value: string | null | undefined): string | null {
  if (!value) {
    return null;
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return parsed.toLocaleString();
}

function SnapshotSection({
  description,
  emptyText,
  items,
  loading,
  title,
}: {
  description: string;
  emptyText: string;
  items: SnapshotItem[];
  loading: boolean;
  title: string;
}) {
  return (
    <article className="rounded-[1.75rem] border border-stone-200 bg-white/90 p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900/75">
      <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-50">{title}</h2>
      <p className="mt-3 text-sm leading-7 text-slate-600 dark:text-slate-300">{description}</p>

      {loading && (
        <div className="mt-5 rounded-[1.25rem] border border-dashed border-stone-200 bg-stone-50/80 p-4 text-sm text-slate-500 dark:border-slate-700 dark:bg-slate-900/60 dark:text-slate-400">
          Loading the latest section projection...
        </div>
      )}

      {!loading && items.length === 0 && (
        <div className="mt-5 rounded-[1.25rem] border border-dashed border-stone-200 bg-stone-50/80 p-4 text-sm text-slate-500 dark:border-slate-700 dark:bg-slate-900/60 dark:text-slate-400">
          {emptyText}
        </div>
      )}

      {items.length > 0 && (
        <div className="mt-5 space-y-4">
          {items.map((item) => (
            <Link
              key={item.item_id}
              href={item.deep_link.href}
              className="block rounded-[1.25rem] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2"
            >
              <div className={`rounded-[1.25rem] border p-4 ${toneStyles[item.tone]}`}>
                <div className="flex flex-wrap items-center gap-3">
                  <p className="text-[11px] font-semibold uppercase tracking-[0.22em] opacity-75">
                    {item.deep_link.label}
                  </p>
                  {item.metric && (
                    <span className="text-sm font-semibold opacity-90">{item.metric}</span>
                  )}
                </div>
                <p className="mt-2 text-lg font-semibold">{item.title}</p>
                <p className="mt-2 text-sm leading-7 opacity-90">{item.summary}</p>
              </div>
            </Link>
          ))}
        </div>
      )}
    </article>
  );
}

const WorkspaceHome = () => {
  const { actor, currentContext, currentRole, error, isLoading, isMockMode, roleConfig } =
    useWorkspace();
  const [snapshotState, setSnapshotState] = useState<AsyncState<WorkspaceSnapshotPayload>>({
    data: null,
    error: null,
    loading: false,
  });
  const [timelineState, setTimelineState] = useState<AsyncState<LearnerRecordTimelinePayload>>({
    data: null,
    error: null,
    loading: false,
  });

  const timelineLearnerId = useMemo(() => {
    if (!["student", "professor", "alumni"].includes(currentRole)) {
      return null;
    }

    return (
      currentContext.learnerIds?.[0] ??
      (currentRole === "student" || currentRole === "alumni" ? (actor?.subject ?? null) : null)
    );
  }, [actor?.subject, currentContext.learnerIds, currentRole]);

  const recommendedLinks = useMemo(
    () =>
      withStableLinkKeys(
        roleConfig.navigation
          .filter((item) => item.route !== `/workspace/${currentRole}`)
          .slice(0, 3),
        (item) => item.route,
      ),
    [currentRole, roleConfig.navigation],
  );
  const heroLinks = useMemo(() => {
    const links = snapshotState.data?.deep_links.length
      ? snapshotState.data.deep_links
      : recommendedLinks.map((item) => ({ label: item.label, href: item.route }));

    return withStableLinkKeys(links, (link) => link.href);
  }, [recommendedLinks, snapshotState.data?.deep_links]);

  useEffect(() => {
    if (isLoading || isMockMode) {
      return;
    }

    let isActive = true;
    setSnapshotState({ data: null, error: null, loading: true });

    const loadSnapshot = async () => {
      try {
        const snapshot = await getWorkspaceSnapshot(currentRole, currentContext.id);
        if (!isActive) {
          return;
        }

        setSnapshotState({ data: snapshot, error: null, loading: false });
      } catch (caughtError: unknown) {
        if (!isActive) {
          return;
        }

        setSnapshotState({
          data: null,
          error:
            caughtError instanceof Error
              ? caughtError.message
              : "Failed to load workspace snapshot.",
          loading: false,
        });
      }
    };

    void loadSnapshot();

    return () => {
      isActive = false;
    };
  }, [currentContext.id, currentRole, isLoading, isMockMode]);

  useEffect(() => {
    if (isLoading || isMockMode || !timelineLearnerId) {
      setTimelineState({ data: null, error: null, loading: false });
      return;
    }

    let isActive = true;
    setTimelineState({ data: null, error: null, loading: true });

    const loadTimeline = async () => {
      try {
        const timeline = await getLearnerRecordTimeline(timelineLearnerId, {
          contextId: currentContext.id,
          limit: 4,
        });

        if (!isActive) {
          return;
        }

        setTimelineState({ data: timeline, error: null, loading: false });
      } catch (caughtError: unknown) {
        if (!isActive) {
          return;
        }

        setTimelineState({
          data: null,
          error:
            caughtError instanceof Error
              ? caughtError.message
              : "Failed to load learner record preview.",
          loading: false,
        });
      }
    };

    void loadTimeline();

    return () => {
      isActive = false;
    };
  }, [currentContext.id, isLoading, isMockMode, timelineLearnerId]);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <section className="rounded-[2rem] border border-stone-200 bg-white/90 p-6 shadow-sm md:p-8">
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-teal-700">
            {roleConfig.workspaceTitle}
          </p>
          <h1 className="mt-4 text-4xl font-semibold text-slate-900 md:text-5xl dark:text-slate-50">
            Resolving your workspace access
          </h1>
          <p className="mt-4 text-lg leading-8 text-slate-600 dark:text-slate-300">
            Tutor is loading the backend access context for this role before it requests the latest
            snapshot.
          </p>
        </section>
      </div>
    );
  }

  if (isMockMode) {
    return (
      <div className="space-y-8">
        <section className="rounded-[2rem] border border-amber-200 bg-amber-50/80 p-6 shadow-sm md:p-8 dark:border-amber-900/60 dark:bg-amber-950/20">
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-amber-900 dark:text-amber-200">
            Fallback workspace shell
          </p>
          <h1 className="mt-4 text-4xl font-semibold leading-tight text-slate-900 md:text-5xl dark:text-slate-50">
            Backend access context is unavailable right now.
          </h1>
          <p className="mt-4 text-lg leading-8 text-slate-700 dark:text-slate-200">
            The shell is preserving navigation and current routes, but role and context data are
            temporarily using the local fallback configuration.
          </p>
          {error && (
            <p className="mt-4 rounded-[1.25rem] border border-amber-300 bg-white/80 p-4 text-sm leading-7 text-amber-950 dark:border-amber-900/60 dark:bg-slate-950/70 dark:text-amber-100">
              {error}
            </p>
          )}
        </section>

        <section className="grid gap-4 md:grid-cols-3">
          {recommendedLinks.map((item) => (
            <Link
              key={item.key}
              href={item.route}
              className="rounded-[1.5rem] border border-stone-200 bg-white/90 p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:border-slate-700 dark:bg-slate-900/75"
            >
              <p className="text-lg font-semibold text-slate-900 dark:text-slate-50">
                {item.label}
              </p>
              <p className="mt-3 text-sm leading-7 text-slate-600 dark:text-slate-300">
                {item.description}
              </p>
            </Link>
          ))}
        </section>
      </div>
    );
  }

  const snapshot = snapshotState.data;
  const timeline = timelineState.data;

  return (
    <div className="space-y-8">
      <section className="rounded-[2rem] border border-stone-200 bg-white/90 p-6 shadow-sm md:p-8">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
          <div className="max-w-3xl">
            <p className="text-xs font-semibold uppercase tracking-[0.3em] text-teal-700">
              {roleConfig.workspaceTitle}
            </p>
            <h1 className="mt-4 text-4xl font-semibold leading-tight text-slate-900 md:text-5xl dark:text-slate-50">
              {snapshot?.summary || roleConfig.publicPitch}
            </h1>
            <p className="mt-4 text-lg leading-8 text-slate-600 dark:text-slate-300">
              {snapshot
                ? `Current context: ${snapshot.context_label}. Deterministic highlights, advisory items, and attention states below are coming from the backend snapshot contract.`
                : `Tutor is preparing the latest ${roleConfig.label.toLowerCase()} snapshot for this context.`}
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              {heroLinks.map((link) => (
                <Link
                  key={link.key}
                  href={link.href}
                  className="rounded-full border border-stone-200 bg-white px-4 py-2 text-sm font-medium text-slate-900 transition hover:bg-stone-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-50"
                >
                  {link.label}
                </Link>
              ))}
            </div>
          </div>

          <aside className="w-full max-w-md rounded-[1.5rem] border border-stone-200 bg-stone-50/90 p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900/70">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">
              Current context
            </p>
            <h2 className="mt-3 text-2xl font-semibold text-slate-900 dark:text-slate-50">
              {snapshot?.context_label || currentContext.label}
            </h2>
            <p className="mt-1 text-sm font-medium text-slate-600 dark:text-slate-300">
              {currentContext.scope}
            </p>
            <p className="mt-4 text-sm leading-7 text-slate-600 dark:text-slate-300">
              {currentContext.note}
            </p>
            {actor && (
              <div className="mt-4 rounded-[1.25rem] border border-stone-200 bg-white/90 p-4 dark:border-slate-700 dark:bg-slate-950/70">
                <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">
                  Active actor
                </p>
                <p className="mt-2 text-sm font-semibold text-slate-900 dark:text-slate-50">
                  {actor.display_name || actor.email || humanizeIdentifier(actor.subject)}
                </p>
                <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                  {actor.email || actor.subject}
                </p>
              </div>
            )}
          </aside>
        </div>

        {snapshotState.error && (
          <div className="mt-6 rounded-[1.25rem] border border-rose-200 bg-rose-50/80 p-4 text-sm leading-7 text-rose-900 dark:border-rose-900/60 dark:bg-rose-950/20 dark:text-rose-100">
            {snapshotState.error}
          </div>
        )}
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <article className="rounded-[1.5rem] border border-stone-200 bg-white/85 p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900/75">
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Freshness</p>
          {snapshot?.freshness ? (
            <>
              <span
                className={`mt-3 inline-flex rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] ${freshnessStyles[snapshot.freshness.status]}`}
              >
                {snapshot.freshness.status}
              </span>
              <p className="mt-3 text-sm leading-7 text-slate-600 dark:text-slate-300">
                {snapshot.freshness.note}
              </p>
              <p className="mt-3 text-xs text-slate-500 dark:text-slate-400">
                Generated{" "}
                {formatDateTime(snapshot.freshness.generated_at) || snapshot.freshness.generated_at}
              </p>
              {snapshot.freshness.source_updated_at && (
                <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                  Source updated{" "}
                  {formatDateTime(snapshot.freshness.source_updated_at) ||
                    snapshot.freshness.source_updated_at}
                </p>
              )}
            </>
          ) : (
            <p className="mt-3 text-sm leading-7 text-slate-600 dark:text-slate-300">
              Waiting for freshness metadata.
            </p>
          )}
        </article>

        <article className="rounded-[1.5rem] border border-stone-200 bg-white/85 p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900/75">
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Human review</p>
          {snapshot?.trust ? (
            <>
              <p className="mt-3 text-3xl font-semibold text-slate-900 dark:text-slate-50">
                {humanizeIdentifier(snapshot.trust.human_review.status)}
              </p>
              <p className="mt-3 text-sm leading-7 text-slate-600 dark:text-slate-300">
                {snapshot.trust.human_review.summary}
              </p>
            </>
          ) : (
            <p className="mt-3 text-sm leading-7 text-slate-600 dark:text-slate-300">
              Waiting for trust metadata.
            </p>
          )}
        </article>

        <article className="rounded-[1.5rem] border border-stone-200 bg-white/85 p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900/75">
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Provenance</p>
          {snapshot?.trust ? (
            <>
              <p className="mt-3 text-lg font-semibold text-slate-900 dark:text-slate-50">
                {snapshot.trust.provenance.generator}
              </p>
              <p className="mt-2 text-sm leading-7 text-slate-600 dark:text-slate-300">
                {snapshot.trust.note}
              </p>
              <p className="mt-3 text-xs text-slate-500 dark:text-slate-400">
                Workflow {snapshot.trust.provenance.workflow_version}
                {snapshot.trust.provenance.model
                  ? ` · Model ${snapshot.trust.provenance.model}`
                  : ""}
              </p>
            </>
          ) : (
            <p className="mt-3 text-sm leading-7 text-slate-600 dark:text-slate-300">
              Waiting for provenance metadata.
            </p>
          )}
        </article>
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,1.5fr)_minmax(18rem,22rem)]">
        <div className="space-y-6">
          <SnapshotSection
            title="Deterministic highlights"
            description="These items come directly from the backend workspace snapshot and should remain inspectable even when advisory layers change."
            items={snapshot?.deterministic_highlights ?? []}
            loading={snapshotState.loading}
            emptyText="No deterministic highlights were returned for this context."
          />
          <SnapshotSection
            title="Advisory items"
            description="Advisory content is visible, labelled, and kept separate from deterministic status and evidence."
            items={snapshot?.advisory_items ?? []}
            loading={snapshotState.loading}
            emptyText="No advisory items were returned for this context."
          />
          <SnapshotSection
            title="Attention items"
            description="These cards surface degraded states, delays, or operational conditions that need review."
            items={snapshot?.attention_items ?? []}
            loading={snapshotState.loading}
            emptyText="No attention items are active for this context."
          />
        </div>

        <aside className="space-y-4">
          <section className="rounded-[1.75rem] border border-stone-200 bg-white/90 p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900/75">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">
              Trust and governance
            </p>
            {snapshot?.trust ? (
              <div className="mt-4 space-y-4 text-sm leading-7 text-slate-600 dark:text-slate-300">
                <div>
                  <p className="font-semibold text-slate-900 dark:text-slate-50">
                    Evaluation state
                  </p>
                  <p>{humanizeIdentifier(snapshot.trust.evaluation_state)}</p>
                </div>
                <div>
                  <p className="font-semibold text-slate-900 dark:text-slate-50">Source lineage</p>
                  <p>{snapshot.trust.provenance.source_type}</p>
                  {snapshot.trust.provenance.source_ids.length > 0 && (
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      {snapshot.trust.provenance.source_ids.join(" · ")}
                    </p>
                  )}
                </div>
                <div>
                  <p className="font-semibold text-slate-900 dark:text-slate-50">
                    Advisory boundary
                  </p>
                  <p>
                    {snapshot.trust.advisory_only
                      ? "The snapshot includes advisory-only guidance that must be reviewed alongside deterministic evidence."
                      : "The snapshot includes deterministic actions that may be executed directly."}
                  </p>
                </div>
                {snapshot.trust.degraded && (
                  <div className="rounded-[1.25rem] border border-amber-200 bg-amber-50/80 p-4 text-amber-950 dark:border-amber-900/60 dark:bg-amber-950/30 dark:text-amber-100">
                    This snapshot includes degraded output. Tutor is surfacing the condition
                    explicitly instead of masking it.
                  </div>
                )}
              </div>
            ) : (
              <p className="mt-4 text-sm leading-7 text-slate-600 dark:text-slate-300">
                Trust metadata will appear once the snapshot finishes loading.
              </p>
            )}
          </section>

          {timelineLearnerId && (
            <section className="rounded-[1.75rem] border border-stone-200 bg-stone-50/90 p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900/80">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">
                Learner record preview
              </p>
              <p className="mt-2 text-sm leading-7 text-slate-600 dark:text-slate-300">
                Previewing {humanizeIdentifier(timelineLearnerId)} through the learner-record
                timeline contract.
              </p>

              {timelineState.loading && (
                <p className="mt-4 text-sm text-slate-500 dark:text-slate-400">
                  Loading learner record entries...
                </p>
              )}

              {timelineState.error && (
                <p className="mt-4 rounded-[1.25rem] border border-rose-200 bg-rose-50/80 p-4 text-sm leading-7 text-rose-900 dark:border-rose-900/60 dark:bg-rose-950/20 dark:text-rose-100">
                  {timelineState.error}
                </p>
              )}

              {!timelineState.loading && !timelineState.error && timeline?.entries.length === 0 && (
                <p className="mt-4 text-sm text-slate-500 dark:text-slate-400">
                  No learner-record entries were returned for this context.
                </p>
              )}

              {timeline?.entries.length ? (
                <div className="mt-4 space-y-3">
                  {timeline.entries.map((entry) => (
                    <Link
                      key={entry.record_id}
                      href={entry.deep_link.href}
                      className="block rounded-[1.25rem] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2"
                    >
                      <div
                        className={`rounded-[1.25rem] border p-4 ${timelineStatusStyles[entry.status]}`}
                      >
                        <div className="flex flex-wrap items-center gap-3">
                          <p className="text-sm font-semibold">{entry.title}</p>
                          <span className="text-[11px] font-semibold uppercase tracking-[0.2em] opacity-70">
                            {humanizeIdentifier(entry.status)}
                          </span>
                        </div>
                        <p className="mt-2 text-sm leading-7 opacity-90">{entry.summary}</p>
                        <p className="mt-3 text-xs opacity-70">
                          {formatDateTime(entry.occurred_at) || entry.occurred_at} ·{" "}
                          {humanizeIdentifier(entry.event_type)}
                        </p>
                      </div>
                    </Link>
                  ))}
                </div>
              ) : null}
            </section>
          )}

          <section className="rounded-[1.75rem] border border-stone-200 bg-white/90 p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900/75">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">
              Continue exploring
            </p>
            <div className="mt-4 flex flex-col gap-3">
              {recommendedLinks.map((item) => (
                <Link
                  key={item.key}
                  href={item.route}
                  className="rounded-xl border border-stone-200 bg-white px-4 py-3 text-sm font-medium text-slate-900 transition hover:bg-stone-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-50"
                >
                  {item.label}
                </Link>
              ))}
              <Link
                href="/evidence-trust"
                className="rounded-xl border border-stone-200 bg-white px-4 py-3 text-sm font-medium text-slate-900 transition hover:bg-stone-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-50"
              >
                Evidence and Trust
              </Link>
            </div>
          </section>
        </aside>
      </section>
    </div>
  );
};

export default WorkspaceHome;
