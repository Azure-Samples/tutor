"use client";

import { useState } from "react";

import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { upskillingApi } from "@/utils/api";
import { unwrapContent } from "@/types/api";

const UpskillingPage = () => {
  const [timeframe, setTimeframe] = useState("week");
  const [topic, setTopic] = useState("Physics");
  const [classId, setClassId] = useState("class-3A");
  const [title, setTitle] = useState("Introduction");
  const [content, setContent] = useState("Start with the core concept and include one applied example.");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<any>(null);

  const runEvaluation = async () => {
    setLoading(true);
    setError("");
    try {
      const payload = {
        timeframe,
        topic,
        class_id: classId,
        paragraphs: [{ title, content }],
        performance_history: [],
      };
      const response = await upskillingApi.post("/plan/evaluate", payload);
      setResult(unwrapContent<any>(response.data));
    } catch (err: any) {
      setError(err?.message || "Failed to evaluate upskilling plan.");
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <DefaultLayout>
      <Breadcrumb
        pageName="Upskilling"
        subtitle="Evaluate teaching plans with agentic coaching feedback."
      />

      <div className="mx-auto max-w-4xl space-y-4 rounded-2xl bg-white p-6 shadow dark:bg-boxdark">
        <div className="grid gap-4 md:grid-cols-3">
          <input className="rounded border px-3 py-2" value={timeframe} onChange={(e) => setTimeframe(e.target.value)} placeholder="timeframe" />
          <input className="rounded border px-3 py-2" value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="topic" />
          <input className="rounded border px-3 py-2" value={classId} onChange={(e) => setClassId(e.target.value)} placeholder="class_id" />
        </div>
        <input className="w-full rounded border px-3 py-2" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="paragraph title" />
        <textarea className="min-h-[140px] w-full rounded border px-3 py-2" value={content} onChange={(e) => setContent(e.target.value)} placeholder="paragraph content" />

        <button onClick={runEvaluation} className="rounded bg-cyan-600 px-4 py-2 font-semibold text-white hover:bg-cyan-700" disabled={loading}>
          {loading ? "Evaluating..." : "Evaluate Plan"}
        </button>

        {error && <p className="text-red-600">{error}</p>}

        {result && (
          <div className="rounded border p-4">
            <h3 className="font-semibold">Result</h3>
            <pre className="mt-2 overflow-auto whitespace-pre-wrap text-sm">{JSON.stringify(result, null, 2)}</pre>
          </div>
        )}
      </div>
    </DefaultLayout>
  );
};

export default UpskillingPage;
