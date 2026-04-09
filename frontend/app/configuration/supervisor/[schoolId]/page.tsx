"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";

import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { humanizeIdentifier } from "@/utils/workspace-api";

import {
  type InsightIndicator,
  type InsightReport,
  getInsightReport,
  listInsightReports,
} from "../api";

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

const renderStringList = (items: string[], emptyText: string) => {
  if (items.length === 0) {
    return <p className="text-sm text-gray-500 dark:text-gray-400">{emptyText}</p>;
  }

  return (
    <ul className="list-disc space-y-1 pl-5 text-sm text-gray-700 dark:text-gray-200">
      {items.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  );
};

const SupervisorSchoolDetailPage = () => {
  const params = useParams<{ schoolId: string }>();
  const schoolId = useMemo(() => decodeURIComponent(params.schoolId), [params.schoolId]);

  const [reports, setReports] = useState<InsightReport[]>([]);
  const [selectedReportId, setSelectedReportId] = useState("");
  const [selectedReport, setSelectedReport] = useState<InsightReport | null>(null);
  const [listLoading, setListLoading] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);
  const [listError, setListError] = useState("");
  const [detailError, setDetailError] = useState("");

  const loadSelectedReport = useCallback(async (reportId: string) => {
    setDetailLoading(true);
    setDetailError("");
    try {
      const report = await getInsightReport(reportId);
      setSelectedReport(report);
    } catch (err: unknown) {
      setDetailError(err instanceof Error ? err.message : "Failed to load report details.");
      setSelectedReport(null);
    } finally {
      setDetailLoading(false);
    }
  }, []);

  useEffect(() => {
    const loadReports = async () => {
      setListLoading(true);
      setListError("");
      try {
        const data = await listInsightReports(schoolId);
        setReports(data);
        if (data.length > 0) {
          const firstReportId = data[0].report_id;
          setSelectedReportId(firstReportId);
          await loadSelectedReport(firstReportId);
        } else {
          setSelectedReportId("");
          setSelectedReport(null);
        }
      } catch (err: unknown) {
        setListError(err instanceof Error ? err.message : "Failed to load school reports.");
      } finally {
        setListLoading(false);
      }
    };

    void loadReports();
  }, [loadSelectedReport, schoolId]);

  const handleSelectReport = async (reportId: string) => {
    setSelectedReportId(reportId);
    await loadSelectedReport(reportId);
  };

  return (
    <DefaultLayout>
      <Breadcrumb
        pageName={`Supervisor - ${schoolId}`}
        subtitle="Inspect generated report sections for a specific school before on-site visits."
      />

      <div className="mb-4">
        <Link
          href="/configuration/supervisor"
          className="inline-flex items-center rounded border border-stroke px-3 py-2 text-sm font-semibold text-black hover:bg-gray-100 dark:border-strokedark dark:text-white dark:hover:bg-white/10"
        >
          Back to Supervisor Overview
        </Link>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <section
          className="rounded-2xl bg-white p-5 shadow dark:bg-boxdark lg:col-span-1"
          aria-labelledby="school-reports-list-title"
        >
          <h3
            id="school-reports-list-title"
            className="mb-4 text-base font-semibold text-black dark:text-white"
          >
            School Reports
          </h3>

          {listError && (
            <p
              role="alert"
              className="rounded bg-red-50 p-3 text-sm text-red-700 dark:bg-red-900/30 dark:text-red-200"
            >
              {listError}
            </p>
          )}

          {listLoading && (
            <output aria-live="polite" className="block text-sm text-gray-600 dark:text-gray-300">
              Loading reports...
            </output>
          )}

          {!listLoading && reports.length === 0 && !listError && (
            <output aria-live="polite" className="block text-sm text-gray-600 dark:text-gray-300">
              No reports available for this school.
            </output>
          )}

          {!listLoading && reports.length > 0 && (
            <ul className="space-y-2">
              {reports.map((report) => {
                const active = report.report_id === selectedReportId;
                return (
                  <li key={report.report_id}>
                    <button
                      type="button"
                      onClick={() => {
                        void handleSelectReport(report.report_id);
                      }}
                      className={`w-full rounded border px-3 py-2 text-left text-sm transition-colors ${
                        active
                          ? "border-indigo-400 bg-indigo-50 text-indigo-700 dark:border-indigo-500 dark:bg-indigo-900/30 dark:text-indigo-200"
                          : "border-stroke text-black hover:bg-gray-100 dark:border-strokedark dark:text-white dark:hover:bg-white/10"
                      }`}
                      aria-pressed={active}
                    >
                      <p className="font-semibold">{formatDate(report.generated_at)}</p>
                      <p className="text-xs opacity-80">
                        {report.source} • feedback {report.feedback_count}
                      </p>
                      {report.freshness && (
                        <span
                          className={`mt-2 inline-flex rounded-full border px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.18em] ${freshnessStyles[report.freshness.status]}`}
                        >
                          {humanizeIdentifier(report.freshness.status)}
                        </span>
                      )}
                    </button>
                  </li>
                );
              })}
            </ul>
          )}
        </section>

        <section
          className="rounded-2xl bg-white p-5 shadow dark:bg-boxdark lg:col-span-2"
          aria-labelledby="school-report-detail-title"
        >
          <h3
            id="school-report-detail-title"
            className="mb-4 text-base font-semibold text-black dark:text-white"
          >
            Report Sections
          </h3>

          {detailError && (
            <p
              role="alert"
              className="mb-4 rounded bg-red-50 p-3 text-sm text-red-700 dark:bg-red-900/30 dark:text-red-200"
            >
              {detailError}
            </p>
          )}

          {detailLoading && (
            <output aria-live="polite" className="block text-sm text-gray-600 dark:text-gray-300">
              Loading report details...
            </output>
          )}

          {!detailLoading && !selectedReport && !detailError && (
            <output aria-live="polite" className="block text-sm text-gray-600 dark:text-gray-300">
              Select a report to inspect sections.
            </output>
          )}

          {!detailLoading && selectedReport && (
            <div className="space-y-5">
              <div className="grid gap-3 rounded border border-stroke p-4 text-sm dark:border-strokedark md:grid-cols-2">
                <p className="text-black dark:text-white">
                  <span className="font-semibold">Generated:</span>{" "}
                  {formatDate(selectedReport.generated_at)}
                </p>
                <p className="text-black dark:text-white">
                  <span className="font-semibold">Week Of:</span> {selectedReport.week_of || "-"}
                </p>
                <p className="text-black dark:text-white">
                  <span className="font-semibold">Source:</span> {selectedReport.source}
                </p>
                <p className="text-black dark:text-white">
                  <span className="font-semibold">Feedback Count:</span>{" "}
                  {selectedReport.feedback_count}
                </p>
                <p className="text-black dark:text-white">
                  <span className="font-semibold">Freshness:</span>{" "}
                  {selectedReport.freshness
                    ? humanizeIdentifier(selectedReport.freshness.status)
                    : "-"}
                </p>
                <p className="text-black dark:text-white">
                  <span className="font-semibold">Review:</span>{" "}
                  {selectedReport.trust
                    ? humanizeIdentifier(selectedReport.trust.human_review.status)
                    : "-"}
                </p>
              </div>

              {(selectedReport.freshness || selectedReport.trust) && (
                <div className="grid gap-4 lg:grid-cols-2">
                  {selectedReport.freshness && (
                    <div className="rounded border border-stroke p-4 text-sm dark:border-strokedark">
                      <p className="font-semibold text-black dark:text-white">Freshness metadata</p>
                      <span
                        className={`mt-3 inline-flex rounded-full border px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] ${freshnessStyles[selectedReport.freshness.status]}`}
                      >
                        {humanizeIdentifier(selectedReport.freshness.status)}
                      </span>
                      <p className="mt-3 text-gray-700 dark:text-gray-200">
                        {selectedReport.freshness.note}
                      </p>
                      <p className="mt-3 text-xs text-gray-500 dark:text-gray-400">
                        Generated {formatDate(selectedReport.freshness.generated_at)}
                      </p>
                      {selectedReport.freshness.source_updated_at && (
                        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                          Source updated {formatDate(selectedReport.freshness.source_updated_at)}
                        </p>
                      )}
                    </div>
                  )}

                  {selectedReport.trust && (
                    <div className="rounded border border-stroke p-4 text-sm dark:border-strokedark">
                      <p className="font-semibold text-black dark:text-white">Trust metadata</p>
                      <p className="mt-3 text-gray-700 dark:text-gray-200">
                        {selectedReport.trust.note}
                      </p>
                      <p className="mt-3 text-gray-700 dark:text-gray-200">
                        Evaluation: {humanizeIdentifier(selectedReport.trust.evaluation_state)}
                      </p>
                      <p className="mt-1 text-gray-700 dark:text-gray-200">
                        Human review: {selectedReport.trust.human_review.summary}
                      </p>
                      <p className="mt-3 text-xs text-gray-500 dark:text-gray-400">
                        {selectedReport.trust.provenance.generator} ·{" "}
                        {selectedReport.trust.provenance.workflow_version}
                      </p>
                    </div>
                  )}
                </div>
              )}

              {selectedReport.deep_links?.length ? (
                <div>
                  <h4 className="mb-2 text-sm font-semibold text-black dark:text-white">
                    Deep Links
                  </h4>
                  <div className="flex flex-wrap gap-3">
                    {selectedReport.deep_links.map((link) => (
                      <Link
                        key={`${selectedReport.report_id}-${link.href}`}
                        href={link.href}
                        className="rounded border border-stroke px-3 py-2 text-xs font-semibold text-cyan-700 transition-colors hover:bg-cyan-50 dark:border-strokedark dark:text-cyan-300 dark:hover:bg-cyan-900/20"
                      >
                        {link.label}
                      </Link>
                    ))}
                  </div>
                </div>
              ) : null}

              <div>
                <h4 className="mb-2 text-sm font-semibold text-black dark:text-white">
                  Indicators
                </h4>
                {selectedReport.indicators.length === 0 ? (
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    No indicators were returned for this report.
                  </p>
                ) : (
                  <div className="space-y-2">
                    {selectedReport.indicators.map((indicator: InsightIndicator) => (
                      <div
                        key={indicator.indicator}
                        className="rounded border border-stroke p-3 text-sm dark:border-strokedark"
                      >
                        <p className="font-semibold text-black dark:text-white">
                          {indicator.indicator}
                        </p>
                        <p className="text-gray-700 dark:text-gray-200">
                          Score: {Math.round(indicator.score * 100)}%
                        </p>
                        <p className="text-gray-700 dark:text-gray-200">Trend: {indicator.trend}</p>
                        <p className="text-gray-600 dark:text-gray-300">{indicator.summary}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div>
                <h4 className="mb-2 text-sm font-semibold text-black dark:text-white">Trends</h4>
                {renderStringList(selectedReport.trends, "No trends were reported.")}
              </div>

              <div>
                <h4 className="mb-2 text-sm font-semibold text-black dark:text-white">Alerts</h4>
                {renderStringList(selectedReport.alerts, "No alerts for this report.")}
              </div>

              <div>
                <h4 className="mb-2 text-sm font-semibold text-black dark:text-white">
                  Focus Points
                </h4>
                {renderStringList(selectedReport.focus_points, "No focus points were generated.")}
              </div>

              <div>
                <h4 className="mb-2 text-sm font-semibold text-black dark:text-white">
                  Improvements
                </h4>
                {renderStringList(
                  selectedReport.improvements,
                  "No improvement recommendations were generated.",
                )}
              </div>
            </div>
          )}
        </section>
      </div>
    </DefaultLayout>
  );
};

export default SupervisorSchoolDetailPage;
