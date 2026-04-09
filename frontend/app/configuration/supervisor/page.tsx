"use client";

import Link from "next/link";
import { type FormEvent, useCallback, useEffect, useState } from "react";

import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { humanizeIdentifier } from "@/utils/workspace-api";

import { type InsightReport, createInsightBriefing, listInsightReports } from "./api";

const freshnessStyles = {
  fresh: "border-emerald-200 bg-emerald-50 text-emerald-900",
  derived: "border-sky-200 bg-sky-50 text-sky-900",
  stale: "border-amber-200 bg-amber-50 text-amber-900",
  degraded: "border-rose-200 bg-rose-50 text-rose-900",
} as const;

const formatDate = (value: string) => {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }
  return parsed.toLocaleString();
};

const renderFreshnessBadge = (report: InsightReport) => {
  if (!report.freshness) {
    return <span className="text-gray-500 dark:text-gray-400">-</span>;
  }

  return (
    <span
      className={`inline-flex rounded-full border px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] ${freshnessStyles[report.freshness.status]}`}
    >
      {humanizeIdentifier(report.freshness.status)}
    </span>
  );
};

const SupervisorConfigurationPage = () => {
  const [schoolId, setSchoolId] = useState("");
  const [weekOf, setWeekOf] = useState("");
  const [filterSchoolId, setFilterSchoolId] = useState("");
  const [reports, setReports] = useState<InsightReport[]>([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  const loadReports = useCallback(async (schoolFilter?: string) => {
    setLoading(true);
    setError("");
    try {
      const data = await listInsightReports(schoolFilter);
      setReports(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load supervisor reports.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadReports();
  }, [loadReports]);

  const handleGenerate = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const normalizedSchoolId = schoolId.trim();
    if (!normalizedSchoolId) {
      setError("School ID is required to generate a briefing report.");
      return;
    }

    setSubmitting(true);
    setError("");
    setStatus("");
    try {
      await createInsightBriefing({
        schoolId: normalizedSchoolId,
        weekOf: weekOf.trim() || undefined,
        onDemand: true,
      });
      setStatus("Briefing generated successfully.");
      await loadReports(filterSchoolId.trim() || undefined);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to generate briefing report.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleFilter = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const normalizedFilter = filterSchoolId.trim();
    setStatus("");
    await loadReports(normalizedFilter || undefined);
  };

  return (
    <DefaultLayout>
      <Breadcrumb
        pageName="Supervisor Insights"
        subtitle="Generate school briefings and review available reports before supervisor visits."
      />

      <div className="space-y-6">
        <section
          className="rounded-2xl bg-white p-6 shadow dark:bg-boxdark"
          aria-labelledby="supervisor-generate-title"
        >
          <h3
            id="supervisor-generate-title"
            className="mb-4 text-lg font-semibold text-black dark:text-white"
          >
            Generate Briefing
          </h3>
          <form className="grid gap-4 md:grid-cols-4" onSubmit={handleGenerate}>
            <div className="md:col-span-2">
              <label
                htmlFor="supervisor-school-id"
                className="mb-1 block text-sm font-medium text-black dark:text-white"
              >
                School ID
              </label>
              <input
                id="supervisor-school-id"
                type="text"
                value={schoolId}
                onChange={(event) => setSchoolId(event.target.value)}
                className="w-full rounded border border-stroke bg-transparent px-3 py-2 text-black outline-none focus:border-cyan-600 dark:border-form-strokedark dark:bg-form-input dark:text-white"
                placeholder="school-123"
              />
            </div>
            <div>
              <label
                htmlFor="supervisor-week-of"
                className="mb-1 block text-sm font-medium text-black dark:text-white"
              >
                Week Of
              </label>
              <input
                id="supervisor-week-of"
                type="date"
                value={weekOf}
                onChange={(event) => setWeekOf(event.target.value)}
                className="w-full rounded border border-stroke bg-transparent px-3 py-2 text-black outline-none focus:border-cyan-600 dark:border-form-strokedark dark:bg-form-input dark:text-white"
              />
            </div>
            <div className="flex items-end">
              <button
                type="submit"
                disabled={submitting}
                className="w-full rounded bg-cyan-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-cyan-700 disabled:cursor-not-allowed disabled:bg-cyan-400"
              >
                {submitting ? "Generating..." : "Generate Briefing"}
              </button>
            </div>
          </form>
        </section>

        <section
          className="rounded-2xl bg-white p-6 shadow dark:bg-boxdark"
          aria-labelledby="supervisor-reports-title"
        >
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <h3
              id="supervisor-reports-title"
              className="text-lg font-semibold text-black dark:text-white"
            >
              Available Reports
            </h3>
            <form className="flex flex-wrap gap-2" onSubmit={handleFilter}>
              <input
                type="text"
                value={filterSchoolId}
                onChange={(event) => setFilterSchoolId(event.target.value)}
                className="rounded border border-stroke bg-transparent px-3 py-2 text-sm text-black outline-none focus:border-cyan-600 dark:border-form-strokedark dark:bg-form-input dark:text-white"
                placeholder="Filter by school ID"
                aria-label="Filter reports by school ID"
              />
              <button
                type="submit"
                className="rounded bg-blue-600 px-3 py-2 text-sm font-semibold text-white transition-colors hover:bg-blue-700"
              >
                Apply Filter
              </button>
              <button
                type="button"
                className="rounded border border-stroke px-3 py-2 text-sm font-semibold text-black hover:bg-gray-100 dark:border-strokedark dark:text-white dark:hover:bg-white/10"
                onClick={() => {
                  setFilterSchoolId("");
                  void loadReports();
                }}
              >
                Clear
              </button>
            </form>
          </div>

          {status && (
            <output
              aria-live="polite"
              className="mb-4 block rounded bg-emerald-50 p-3 text-sm text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-200"
            >
              {status}
            </output>
          )}

          {error && (
            <p
              role="alert"
              className="mb-4 rounded bg-red-50 p-3 text-sm text-red-700 dark:bg-red-900/30 dark:text-red-200"
            >
              {error}
            </p>
          )}

          {loading && (
            <output aria-live="polite" className="block text-sm text-gray-600 dark:text-gray-300">
              Loading reports...
            </output>
          )}

          {!loading && reports.length === 0 && !error && (
            <output aria-live="polite" className="block text-sm text-gray-600 dark:text-gray-300">
              No reports found for the selected scope.
            </output>
          )}

          {!loading && reports.length > 0 && (
            <div className="overflow-x-auto">
              <table className="w-full table-auto text-sm">
                <thead>
                  <tr className="border-b border-stroke text-left dark:border-strokedark">
                    <th className="px-4 py-3 font-medium text-black dark:text-white">School</th>
                    <th className="px-4 py-3 font-medium text-black dark:text-white">Week Of</th>
                    <th className="px-4 py-3 font-medium text-black dark:text-white">Generated</th>
                    <th className="px-4 py-3 font-medium text-black dark:text-white">Source</th>
                    <th className="px-4 py-3 font-medium text-black dark:text-white">Freshness</th>
                    <th className="px-4 py-3 font-medium text-black dark:text-white">Trust</th>
                    <th className="px-4 py-3 font-medium text-black dark:text-white">Feedback</th>
                    <th className="px-4 py-3 font-medium text-black dark:text-white">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {reports.map((report) => (
                    <tr
                      key={report.report_id}
                      className="border-b border-stroke last:border-b-0 dark:border-strokedark"
                    >
                      <td className="px-4 py-3 text-black dark:text-white">{report.school_id}</td>
                      <td className="px-4 py-3 text-gray-600 dark:text-gray-300">
                        {report.week_of || "-"}
                      </td>
                      <td className="px-4 py-3 text-gray-600 dark:text-gray-300">
                        {formatDate(report.generated_at)}
                      </td>
                      <td className="px-4 py-3 text-gray-600 dark:text-gray-300">
                        {report.source}
                      </td>
                      <td className="px-4 py-3">{renderFreshnessBadge(report)}</td>
                      <td className="px-4 py-3 text-gray-600 dark:text-gray-300">
                        {report.trust ? humanizeIdentifier(report.trust.human_review.status) : "-"}
                      </td>
                      <td className="px-4 py-3 text-gray-600 dark:text-gray-300">
                        {report.feedback_count}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex flex-col gap-2">
                          <Link
                            href={`/configuration/supervisor/${encodeURIComponent(report.school_id)}`}
                            className="rounded bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white transition-colors hover:bg-indigo-700"
                          >
                            Open School View
                          </Link>
                          {report.deep_links?.map((link) => (
                            <Link
                              key={`${report.report_id}-${link.href}`}
                              href={link.href}
                              className="text-xs font-medium text-cyan-700 hover:text-cyan-800 dark:text-cyan-300 dark:hover:text-cyan-200"
                            >
                              {link.label}
                            </Link>
                          ))}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </DefaultLayout>
  );
};

export default SupervisorConfigurationPage;
