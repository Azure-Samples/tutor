"use client";
import React, { useState, useRef } from "react";
import { FaUpload, FaFileAlt, FaHistory, FaSpinner } from "react-icons/fa";
import { essaysEngine } from "@/utils/api";
import { v4 as uuidv4 } from 'uuid';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

// Backend /assemblies returns Swarm objects: { id, topic_name, agents }
// We adapt to what the UI needs by adding friendly name/description fields.
interface EssayCase {
  id: string;
  topic_name: string; // original backend field used as the display label
  agents: any[];
  name?: string; // derived (topic_name)
  description?: string; // currently not provided by backend
  content?: string; // reference text / prompt body
  explanation?: string; // instructions / rubric
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
  const [essayLookup, setEssayLookup] = useState<Record<string, any>>({});

  // Load available essay cases (assemblies)
  React.useEffect(() => {
    setLoadingCases(true);
    essaysEngine.get("/assemblies")
      .then(res => {
        const raw = Array.isArray(res.data?.content) ? res.data.content : [];
        const mapped: EssayCase[] = raw.map((r: any) => ({
          id: r.id,
          topic_name: r.topic_name,
            // Provide fallbacks so UI never breaks
          agents: r.agents || [],
          name: r.topic_name,
          description: r.description || ""
        }));
        if (mapped.length === 0) {
          // Fallback: try to derive cases from existing essays if assemblies not seeded yet
          return essaysEngine.get('/essays').then(er => {
            const essays = Array.isArray(er.data?.content) ? er.data.content : [];
            const essayCases: EssayCase[] = essays.map((e: any) => ({
              id: e.id,
              topic_name: e.topic || e.theme || e.id,
              agents: [],
              name: e.topic || e.theme || e.id,
              description: e.explanation || '',
              content: e.content,
              explanation: e.explanation
            }));
            setCases(essayCases);
            const lookup: Record<string, any> = {};
            essays.forEach((e: any) => { lookup[e.id] = e; });
            setEssayLookup(lookup);
          }).catch(fallbackErr => {
            console.error('Fallback /essays fetch failed:', fallbackErr);
            setCases([]);
          });
        }
        setCases(mapped);
      })
      .catch(err => {
        console.error('Failed loading /assemblies:', err);
        setCases([]);
      })
      .finally(() => setLoadingCases(false));
  }, []);

  // Load submission history (using /resources now, since submissions are stored as resources)
  React.useEffect(() => {
    setLoadingHistory(true);
    essaysEngine.get("/resources")
      .then(res => {
        const content = Array.isArray(res.data?.content) ? res.data.content : [];
        const mapped: Submission[] = content.map((r: any) => ({
          id: r.id,
          essayText: r.content,
          description: Array.isArray(r.objective) ? r.objective.slice(1).join(' ') : '',
          submittedAt: r.submittedAt || '', // backend currently does not send this
          essayFileName: undefined,
          evaluations: []
        }));
        setHistory(mapped);
      })
      .catch(() => setHistory([]))
      .finally(() => setLoadingHistory(false));
  }, []);

  // Independently load essays to enrich lookup for markdown reference/instructions
  React.useEffect(() => {
    essaysEngine.get('/essays')
      .then(res => {
        const items = Array.isArray(res.data?.content) ? res.data.content : [];
        const lookup: Record<string, any> = {};
        items.forEach((e: any) => { lookup[e.id] = e; });
        setEssayLookup(lookup);
      })
      .catch(err => console.warn('Could not load essays for reference text:', err));
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

    // NOTE: Backend /resources expects: id, objective (List[str]), content?, essay_id, url?.
    // We treat a submission as a Resource referencing the selectedCase (assembly) id.
    const resourcePayload = {
      id: uuidv4(),
      objective: description ? ["student_submission", description] : ["student_submission"],
      content: essayText || (essayFile ? `(uploaded file: ${essayFile.name})` : ''),
      essay_id: selectedCase.id,
      url: undefined
    };

    try {
      const res = await essaysEngine.post("/resources", resourcePayload);
      // We don't receive evaluations from this endpoint; keep empty for now.
      const submission: Submission = {
        id: resourcePayload.id,
        essayText: resourcePayload.content,
        essayFileName: essayFile?.name,
        description: description,
        submittedAt: new Date().toISOString(),
        evaluations: []
      };
      setHistory(h => [submission, ...h]);
      // Clear form
      setEssayText('');
      setEssayFile(null);
      setDescription('');
    } catch (err) {
      console.error('Failed to submit resource', err);
    } finally {
      setSubmitting(false);
    }
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
              <option key={ca.id} value={ca.id}>📝 {ca.name || ca.topic_name || "Untitled"}</option>
            ))}
          </select>
        )}
      </div>
      {selectedCase && (
        <div className="mb-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="rounded-2xl border-2 border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/40 p-4 overflow-y-auto max-h-[360px] prose prose-sm md:prose-base dark:prose-invert">
            <h3 className="text-lg font-bold mb-2">📄 Reference Text</h3>
            <div className="break-words">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                { (essayLookup[selectedCase.id]?.content) || selectedCase.content || 'No reference text available.' }
              </ReactMarkdown>
            </div>
          </div>
          <div className="rounded-2xl border-2 border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/40 p-4 overflow-y-auto max-h-[360px] prose prose-sm md:prose-base dark:prose-invert">
            <h3 className="text-lg font-bold mb-2">🧭 Instructions / Rubric</h3>
            <div className="break-words">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                { (essayLookup[selectedCase.id]?.explanation) || selectedCase.explanation || selectedCase.description || 'No instructions available.' }
              </ReactMarkdown>
            </div>
          </div>
        </div>
      )}
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
