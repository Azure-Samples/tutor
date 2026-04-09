"use client";

import { useState } from "react";

import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { lmsGatewayApi } from "@/utils/api";

const ADAPTER_INPUT_ID = "lms-gateway-adapter";
const INTERVAL_INPUT_ID = "lms-gateway-interval";
const JOB_ID_INPUT_ID = "lms-gateway-job-id";

const getErrorMessage = (error: unknown, fallback: string) =>
  error instanceof Error ? error.message : fallback;

const LmsGatewayConfigPage = () => {
  const [adapter, setAdapter] = useState("moodle");
  const [intervalMinutes, setIntervalMinutes] = useState(60);
  const [jobId, setJobId] = useState("");
  const [status, setStatus] = useState("");
  const [result, setResult] = useState<unknown | null>(null);

  const syncNow = async () => {
    try {
      setStatus("Starting sync...");
      const { data } = await lmsGatewayApi.post("/lms/sync", { adapter });
      setResult(data);
      setStatus("Sync completed.");
    } catch (error: unknown) {
      setStatus(getErrorMessage(error, "Failed to run LMS sync."));
    }
  };

  const schedule = async () => {
    try {
      setStatus("Scheduling sync...");
      const { data } = await lmsGatewayApi.post("/lms/sync/schedule", {
        adapter,
        interval_minutes: intervalMinutes,
      });
      setJobId(data?.job_id || "");
      setResult(data);
      setStatus("Sync scheduled.");
    } catch (error: unknown) {
      setStatus(getErrorMessage(error, "Failed to schedule LMS sync."));
    }
  };

  const getJob = async () => {
    if (!jobId) {
      setStatus("job_id is required.");
      return;
    }
    try {
      setStatus("Loading job...");
      const { data } = await lmsGatewayApi.get(`/lms/sync/jobs/${encodeURIComponent(jobId)}`);
      setResult(data);
      setStatus("Job loaded.");
    } catch (error: unknown) {
      setStatus(getErrorMessage(error, "Failed to load job."));
    }
  };

  return (
    <DefaultLayout>
      <Breadcrumb
        pageName="LMS Gateway Configuration"
        subtitle="Trigger and inspect LMS synchronization jobs through APIM."
      />
      <div className="mx-auto max-w-4xl space-y-4 rounded-2xl bg-white p-6 shadow dark:bg-boxdark">
        <div className="grid gap-4 md:grid-cols-3">
          <div>
            <label
              className="mb-1 block text-sm font-medium text-black dark:text-white"
              htmlFor={ADAPTER_INPUT_ID}
            >
              Adapter
            </label>
            <select
              id={ADAPTER_INPUT_ID}
              className="w-full rounded border px-3 py-2"
              value={adapter}
              onChange={(e) => setAdapter(e.target.value)}
            >
              <option value="moodle">moodle</option>
              <option value="canvas">canvas</option>
            </select>
          </div>
          <div>
            <label
              className="mb-1 block text-sm font-medium text-black dark:text-white"
              htmlFor={INTERVAL_INPUT_ID}
            >
              Interval minutes
            </label>
            <input
              id={INTERVAL_INPUT_ID}
              type="number"
              className="w-full rounded border px-3 py-2"
              value={intervalMinutes}
              onChange={(e) => setIntervalMinutes(Number(e.target.value || 60))}
              placeholder="interval minutes"
            />
          </div>
          <div>
            <label
              className="mb-1 block text-sm font-medium text-black dark:text-white"
              htmlFor={JOB_ID_INPUT_ID}
            >
              Job ID
            </label>
            <input
              id={JOB_ID_INPUT_ID}
              className="w-full rounded border px-3 py-2"
              value={jobId}
              onChange={(e) => setJobId(e.target.value)}
              placeholder="job_id"
            />
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            className="rounded bg-cyan-600 px-4 py-2 text-white hover:bg-cyan-700"
            onClick={syncNow}
          >
            Sync Now
          </button>
          <button
            type="button"
            className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
            onClick={schedule}
          >
            Schedule Sync
          </button>
          <button
            type="button"
            className="rounded bg-emerald-600 px-4 py-2 text-white hover:bg-emerald-700"
            onClick={getJob}
          >
            Get Job
          </button>
        </div>

        {status && <p className="text-sm text-gray-700 dark:text-gray-200">{status}</p>}

        {result !== null && (
          <div className="rounded border p-4">
            <pre className="overflow-auto whitespace-pre-wrap text-sm">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </DefaultLayout>
  );
};

export default LmsGatewayConfigPage;
