"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import {
  type EvaluationRun,
  getEvaluationErrorMessage,
  getEvaluationRun,
} from "@/utils/evaluation";

interface EvaluationRunViewerProps {
  runId: string;
}

const EvaluationRunViewer = ({ runId }: EvaluationRunViewerProps) => {
  const [run, setRun] = useState<EvaluationRun | null>(null);
  const [statusMessage, setStatusMessage] = useState(`Loading run ${runId}...`);
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  const loadRun = useCallback(async () => {
    try {
      setIsLoading(true);
      setErrorMessage("");
      setStatusMessage(`Loading run ${runId}...`);
      const nextRun = await getEvaluationRun(runId);
      setRun(nextRun);
      setStatusMessage(`Run ${nextRun.run_id} loaded with status ${nextRun.status}.`);
    } catch (error: unknown) {
      setRun(null);
      setErrorMessage(getEvaluationErrorMessage(error, "Failed to load evaluation run."));
      setStatusMessage(`Run ${runId} could not be loaded.`);
    } finally {
      setIsLoading(false);
    }
  }, [runId]);

  useEffect(() => {
    loadRun();
  }, [loadRun]);

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-stone-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-teal-700 dark:text-teal-300">
              Evaluation run
            </p>
            <h1 className="mt-3 break-words text-3xl font-semibold text-slate-900 dark:text-slate-50">
              {runId}
            </h1>
            <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-600 dark:text-slate-300">
              This page is backed by GET /api/evaluation/evaluation/run/{"{run_id}"} through the
              shared APIM evaluation facade.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={loadRun}
              disabled={isLoading}
              className="rounded-md border border-teal-700 bg-teal-700 px-4 py-2 text-sm font-semibold text-white transition hover:bg-teal-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isLoading ? "Refreshing..." : "Refresh run"}
            </button>
            <Link
              href="/evaluation"
              className="rounded-md border border-stone-200 bg-white px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-stone-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-50 dark:hover:bg-slate-800"
            >
              Back to evaluation
            </Link>
          </div>
        </div>

        <output
          aria-live="polite"
          className="mt-5 block rounded-md border border-teal-100 bg-teal-50 p-4 text-sm leading-7 text-teal-950 dark:border-teal-900 dark:bg-teal-950/40 dark:text-teal-100"
        >
          {statusMessage}
        </output>
        {errorMessage && (
          <div
            role="alert"
            className="mt-3 rounded-md border border-amber-200 bg-amber-50 p-4 text-sm leading-7 text-amber-950 dark:border-amber-900 dark:bg-amber-950/40 dark:text-amber-100"
          >
            {errorMessage}
          </div>
        )}
      </section>

      {run && (
        <section className="rounded-lg border border-stone-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
          <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-50">Run details</h2>
          <dl className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <div className="rounded-md border border-stone-200 bg-stone-50 p-4 dark:border-slate-700 dark:bg-slate-950/60">
              <dt className="text-xs font-medium uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">
                Status
              </dt>
              <dd className="mt-2 text-lg font-semibold text-slate-900 dark:text-slate-50">
                {run.status}
              </dd>
            </div>
            <div className="rounded-md border border-stone-200 bg-stone-50 p-4 dark:border-slate-700 dark:bg-slate-950/60">
              <dt className="text-xs font-medium uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">
                Agent ID
              </dt>
              <dd className="mt-2 break-words font-mono text-sm text-slate-900 dark:text-slate-50">
                {run.agent_id}
              </dd>
            </div>
            <div className="rounded-md border border-stone-200 bg-stone-50 p-4 dark:border-slate-700 dark:bg-slate-950/60">
              <dt className="text-xs font-medium uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">
                Dataset ID
              </dt>
              <dd className="mt-2 break-words font-mono text-sm text-slate-900 dark:text-slate-50">
                {run.dataset_id}
              </dd>
            </div>
            <div className="rounded-md border border-stone-200 bg-stone-50 p-4 dark:border-slate-700 dark:bg-slate-950/60">
              <dt className="text-xs font-medium uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">
                Total cases
              </dt>
              <dd className="mt-2 text-lg font-semibold text-slate-900 dark:text-slate-50">
                {run.total_cases}
              </dd>
            </div>
          </dl>
        </section>
      )}
    </div>
  );
};

export default EvaluationRunViewer;
