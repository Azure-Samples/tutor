"use client";

import { useState } from "react";

import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { lmsGatewayApi } from "@/utils/api";

const LmsGatewayPage = () => {
  const [adapter, setAdapter] = useState("moodle");
  const [intervalMinutes, setIntervalMinutes] = useState(60);
  const [jobId, setJobId] = useState("");
  const [status, setStatus] = useState("");
  const [result, setResult] = useState<any>(null);

  const syncNow = async () => {
    try {
      setStatus("Starting sync...");
      const { data } = await lmsGatewayApi.post("/lms/sync", { adapter });
      setResult(data);
      setStatus("Sync completed.");
    } catch (err: any) {
      setStatus(err?.message || "Failed to run LMS sync.");
    }
  };

  const schedule = async () => {
    try {
      setStatus("Scheduling sync...");
      const { data } = await lmsGatewayApi.post("/lms/sync/schedule", { adapter, interval_minutes: intervalMinutes });
      setJobId(data?.job_id || "");
      setResult(data);
      setStatus("Sync scheduled.");
    } catch (err: any) {
      setStatus(err?.message || "Failed to schedule LMS sync.");
    }
  };

  const getJob = async () => {
    if (!jobId) {
      setStatus("job_id is required.");
      return;
    }
    try {
      setStatus("Loading job...");
      const { data } = await lmsGatewayApi.get(`/lms/sync/jobs/${jobId}`);
      setResult(data);
      setStatus("Job loaded.");
    } catch (err: any) {
      setStatus(err?.message || "Failed to load job.");
    }
  };

  return (
    <DefaultLayout>
      <Breadcrumb pageName="LMS Gateway" subtitle="Trigger and inspect LMS synchronization jobs through APIM." />
      <div className="mx-auto max-w-4xl space-y-4 rounded-2xl bg-white p-6 shadow dark:bg-boxdark">
        <div className="grid gap-4 md:grid-cols-3">
          <select className="rounded border px-3 py-2" value={adapter} onChange={(e) => setAdapter(e.target.value)}>
            <option value="moodle">moodle</option>
            <option value="canvas">canvas</option>
          </select>
          <input
            type="number"
            className="rounded border px-3 py-2"
            value={intervalMinutes}
            onChange={(e) => setIntervalMinutes(Number(e.target.value || 60))}
            placeholder="interval minutes"
          />
          <input className="rounded border px-3 py-2" value={jobId} onChange={(e) => setJobId(e.target.value)} placeholder="job_id" />
        </div>

        <div className="flex flex-wrap gap-2">
          <button className="rounded bg-cyan-600 px-4 py-2 text-white hover:bg-cyan-700" onClick={syncNow}>Sync Now</button>
          <button className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700" onClick={schedule}>Schedule Sync</button>
          <button className="rounded bg-emerald-600 px-4 py-2 text-white hover:bg-emerald-700" onClick={getJob}>Get Job</button>
        </div>

        {status && <p className="text-sm text-gray-700 dark:text-gray-200">{status}</p>}

        {result && (
          <div className="rounded border p-4">
            <pre className="overflow-auto whitespace-pre-wrap text-sm">{JSON.stringify(result, null, 2)}</pre>
          </div>
        )}
      </div>
    </DefaultLayout>
  );
};

export default LmsGatewayPage;
