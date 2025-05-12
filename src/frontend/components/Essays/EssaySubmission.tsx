"use client";
import React, { useState, useRef } from "react";
import { FaUpload, FaFileAlt, FaHistory, FaSpinner } from "react-icons/fa";
import { essaysEngine } from "@/utils/api";

interface EssayCase {
  id: string;
  name: string;
  description: string;
}

interface Evaluation {
  agent: string;
  feedback: string;
  score?: number;
}

interface Submission {
  id: string;
  essayText?: string;
  essayFileName?: string;
  description: string;
  submittedAt: string;
  evaluations: Evaluation[];
}

const EssaySubmission: React.FC = () => {
  const [cases, setCases] = useState<EssayCase[]>([]);
  const [selectedCase, setSelectedCase] = useState<EssayCase | null>(null);
  const [essayText, setEssayText] = useState("");
  const [essayFile, setEssayFile] = useState<File | null>(null);
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
  const [history, setHistory] = useState<Submission[]>([]);
  const [loadingCases, setLoadingCases] = useState(true);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load available essay cases
  React.useEffect(() => {
    setLoadingCases(true);
    essaysEngine.get("/assemblies")
      .then(res => {
        // Failsafe: ensure data is an array
        const content = Array.isArray(res.data?.content) ? res.data.content : [];
        setCases(content);
      })
      .catch(() => setCases([]))
      .finally(() => setLoadingCases(false));
  }, []);

  // Load submission history
  React.useEffect(() => {
    setLoadingHistory(true);
    essaysEngine.get("/essays")
      .then(res => {
        // Failsafe: ensure data is an array
        const content = Array.isArray(res.data?.content) ? res.data.content : [];
        setHistory(content);
      })
      .catch(() => setHistory([]))
      .finally(() => setLoadingHistory(false));
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setEssayFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCase || (!essayText && !essayFile)) return;
    setSubmitting(true);
    setEvaluations([]);
    const formData = new FormData();
    formData.append("caseId", selectedCase.id);
    formData.append("description", description);
    if (essayText) formData.append("essayText", essayText);
    if (essayFile) formData.append("essayFile", essayFile);
    const res = await essaysEngine.post("/essays", formData);
    const data = res.data;
    setEvaluations(data.evaluations || []);
    setHistory(h => [data.content, ...h]);
    setSubmitting(false);
  };

  if (loadingCases) {
    return (
      <div className="w-full h-[60vh] flex flex-col justify-center items-center">
        <FaSpinner className="animate-spin text-4xl text-cyan-500 mb-4" />
        <span className="text-xl text-cyan-700 font-bold">Loading essay themes...</span>
      </div>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto p-4">
      <h2 className="text-3xl font-extrabold mb-4 flex items-center gap-2">
        ✍️ Submit Your Essay Adventure!
      </h2>
      {/* Loader for essay case selection */}
      <div className="mb-6">
        <label className="block font-semibold mb-2 text-lg flex items-center gap-2">
          🎯 Pick Your Mission (Essay Case)
        </label>
        {loadingCases ? (
          <div className="flex items-center gap-2 text-cyan-600"><FaSpinner className="animate-spin" /> Loading cases...</div>
        ) : cases.length === 0 ? (
          <div className="text-red-600 font-bold">No essay cases available. Please try again later.</div>
        ) : (
          <select
            className="w-full rounded-2xl border-2 border-cyan-300 px-3 py-2 text-lg bg-cyan-50 dark:bg-cyan-900 focus:border-green-400 focus:ring-2 focus:ring-green-200"
            value={selectedCase?.id || ""}
            onChange={e => {
              const c = cases.find(ca => ca.id === e.target.value);
              setSelectedCase(c || null);
            }}
          >
            <option value="">-- 🚀 Choose your challenge --</option>
            {cases.map(ca => (
              <option key={ca.id} value={ca.id}>📝 {ca.name || "Untitled"}</option>
            ))}
          </select>
        )}
        {selectedCase && <div className="mt-2 text-cyan-700 text-base italic">{selectedCase.description || "No description."}</div>}
      </div>
      {/* Essay submission form */}
      <form onSubmit={handleSubmit} className="bg-white dark:bg-boxdark rounded-2xl shadow-lg p-8 mb-8 flex flex-col gap-6 border-2 border-cyan-100 dark:border-cyan-800">
        <label className="font-semibold flex items-center gap-2 text-green-700">
          🏷️ Give your essay a catchy description!
        </label>
        <input
          type="text"
          className="rounded-2xl border-2 border-green-200 px-3 py-2 text-lg bg-green-50 dark:bg-green-900 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-200"
          value={description}
          onChange={e => setDescription(e.target.value)}
          placeholder="e.g. My Epic Argument for Pizza Fridays"
        />
        <label className="font-semibold flex items-center gap-2 text-blue-700">
          ✏️ Write your essay masterpiece below!
        </label>
        <textarea
          className="rounded-2xl border-2 border-blue-200 px-3 py-2 text-lg min-h-[120px] bg-blue-50 dark:bg-blue-900 focus:border-yellow-400 focus:ring-2 focus:ring-yellow-200"
          value={essayText}
          onChange={e => setEssayText(e.target.value)}
          placeholder="Once upon a time... (or paste your essay here!)"
        />
        <div className="flex items-center gap-4">
          <label className="font-semibold flex items-center gap-2 text-pink-700">
            📎 Or upload your essay file
          </label>
          <input
            type="file"
            accept=".pdf,.doc,.docx,.txt"
            ref={fileInputRef}
            onChange={handleFileChange}
            className="rounded border-2 border-pink-200 px-2 py-1 bg-pink-50 dark:bg-pink-900 focus:border-cyan-400"
          />
          {essayFile && <span className="text-green-700 flex items-center gap-1"><FaFileAlt /> {essayFile.name}</span>}
        </div>
        <button
          type="submit"
          className="mt-4 bg-gradient-to-br from-green-400 to-cyan-400 text-white font-bold px-8 py-4 rounded-full shadow-lg hover:scale-105 transition-all duration-200 flex items-center gap-3 justify-center text-xl"
          disabled={submitting || !selectedCase || (!essayText && !essayFile)}
        >
          {submitting ? <FaSpinner className="animate-spin" /> : <FaUpload />} {submitting ? "Sending to the wizards..." : "Submit Essay!"}
        </button>
      </form>
      {/* Real-time evaluation area */}
      <div className="mb-8">
        <h3 className="text-2xl font-bold mb-2 flex items-center gap-2">🔍 Evaluation Results</h3>
        {submitting && <div className="text-cyan-600 flex items-center gap-2"><FaSpinner className="animate-spin" /> Evaluating essay...</div>}
        {!submitting && evaluations.length === 0 && <div className="text-gray-500">No evaluation yet. Submit your essay to get magical feedback! ✨</div>}
        <div className="grid gap-4">
          {evaluations.map(ev => (
            <div key={ev.agent} className="border-2 border-cyan-200 rounded-2xl p-4 bg-cyan-50 dark:bg-cyan-900 shadow">
              <div className="font-bold text-cyan-700 flex items-center gap-2">🤖 Agent: {ev.agent}</div>
              <div className="text-gray-800 dark:text-gray-100 whitespace-pre-line mt-2">{ev.feedback}</div>
              {ev.score !== undefined && <div className="text-green-700 font-semibold mt-2">🏅 Score: {ev.score}</div>}
            </div>
          ))}
        </div>
      </div>
      {/* Submission history */}
      <div>
        <h3 className="text-2xl font-bold mb-2 flex items-center gap-2"><FaHistory /> Submission History</h3>
        {loadingHistory ? (
          <div className="text-cyan-600 flex items-center gap-2"><FaSpinner className="animate-spin" /> Loading history...</div>
        ) : !Array.isArray(history) || history.length === 0 ? (
          <div className="text-gray-500">No submissions yet. Be the first to submit your essay adventure! 🚀</div>
        ) : (
          <ul className="divide-y">
            {history.map(sub => (
              <li key={sub.id} className="py-4">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-2">
                  <div>
                    <span className="font-semibold">{sub.submittedAt ? new Date(sub.submittedAt).toLocaleString() : "Unknown date"}</span> - {sub.essayFileName ? <span className="text-green-700 flex items-center gap-1"><FaFileAlt />{sub.essayFileName}</span> : <span className="text-blue-700">📝 Written Essay</span>}
                    <div className="text-gray-600 text-sm italic">{sub.description || "No description."}</div>
                  </div>
                  <div className="flex flex-col gap-1">
                    {Array.isArray(sub.evaluations) && sub.evaluations.length > 0 ? sub.evaluations.map(ev => (
                      <div key={ev.agent} className="text-xs text-cyan-700">🤖 {ev.agent}: <span className="text-gray-800 dark:text-gray-100">{ev.feedback}</span></div>
                    )) : <div className="text-xs text-gray-400">No evaluations.</div>}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default EssaySubmission;
