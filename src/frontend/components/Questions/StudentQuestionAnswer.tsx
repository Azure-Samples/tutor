"use client";
import React, { useState, useEffect } from "react";
import { questionsEngine } from "@/utils/api";
import type { Question } from "@/types/question";
import type { Assembly } from "@/types/assembly";
import type { Grader } from "@/types/grader";
import type { Answer } from "@/types/answer";
import type { ChatResponse } from "@/types/chatResponse";

interface Evaluation {
  agent: string;
  feedback: string;
  score?: number;
}

interface Submission {
  id: string;
  answer: string;
  evaluations: Evaluation[];
  submittedAt: string;
}

const StudentQuestionAnswer: React.FC = () => {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [assemblies, setAssemblies] = useState<Assembly[]>([]);
  const [selectedQuestionIdx, setSelectedQuestionIdx] = useState(0);
  const [loadingQuestion, setLoadingQuestion] = useState(true);
  const [loadingAssemblies, setLoadingAssemblies] = useState(true);
  const [answer, setAnswer] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
  const [history, setHistory] = useState<Submission[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load all questions
  useEffect(() => {
    setLoadingQuestion(true);
    questionsEngine.get("/questions")
      .then(res => {
        const content = Array.isArray(res.data?.content) ? res.data.content : [];
        setQuestions(content);
        setSelectedQuestionIdx(0);
      })
      .catch(() => setQuestions([]))
      .finally(() => setLoadingQuestion(false));
  }, []);

  // Load assemblies (evaluators)
  useEffect(() => {
    setLoadingAssemblies(true);
    questionsEngine.get("/assemblies")
      .then(res => {
        const content = Array.isArray(res.data?.content) ? res.data.content : [];
        setAssemblies(content);
      })
      .catch(() => setAssemblies([]))
      .finally(() => setLoadingAssemblies(false));
  }, []);

  // Load submission history
  useEffect(() => {
    setLoadingHistory(true);
    questionsEngine.get("/answers")
      .then(res => {
        const content = Array.isArray(res.data?.content) ? res.data.content : [];
        setHistory(content);
      })
      .catch(() => setHistory([]))
      .finally(() => setLoadingHistory(false));
  }, []);

  // Handle answer submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!answer.trim() || questions.length === 0 || assemblies.length === 0) return;
    setSubmitting(true);
    setError(null);
    setEvaluations([]);
    try {
      const selectedQuestion = questions[selectedQuestionIdx];
      const selectedAssembly = assemblies[0]; // Use the first assembly for now
      // Build the answer object
      const answerObj: Answer = {
        id: `${selectedQuestion.topic}_${Date.now()}`,
        text: answer,
        question_id: selectedQuestion.topic,
        respondent: "student", // Replace with actual user if available
      };
      // Build the ChatResponse payload
      const chatPayload: ChatResponse = {
        case_id: selectedAssembly.id,
        question: selectedQuestion,
        answer: answerObj,
      };
      // Call grader/interaction
      const res = await questionsEngine.post("/grader/interaction", chatPayload);
      // The backend may return a string or an object; handle both
      console.log(res);
      let evals: any[] = [];
      if (Array.isArray(res.data?.text)) {
        evals = res.data.text;
        console.log("Evaluations:", evals);
      } else if (typeof res.data?.text === "string") {
        try { evals = JSON.parse(res.data.text); } catch { evals = [{ agent: "AI", feedback: res.data.text }]; }
      }
      setEvaluations(evals);
      // Save answer
      await questionsEngine.post("/answers", answerObj);
      // Reload history
      questionsEngine.get("/answers").then(res => {
        const content = Array.isArray(res.data?.content) ? res.data.content : [];
        setHistory(content);
      });
    } catch (err) {
      setError("Failed to submit answer. Please try again!");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md mt-8">
      <h2 className="text-2xl font-bold mb-4">📝 Answer the Question!</h2>
      {loadingQuestion || loadingAssemblies ? (
        <div className="text-gray-500">Loading question...</div>
      ) : questions.length > 0 ? (
        <div className="mb-6">
          <div className="text-lg font-semibold mb-2">{questions[selectedQuestionIdx].question}</div>
          {questions.length > 1 && (
            <div className="mb-4">
              <label className="font-semibold">Select Question:</label>
              <select
                className="border rounded p-2 ml-2"
                value={selectedQuestionIdx}
                onChange={e => setSelectedQuestionIdx(Number(e.target.value))}
              >
                {questions.map((q, idx) => (
                  <option key={q.topic} value={idx}>
                    {q.topic}: {q.question}
                  </option>
                ))}
              </select>
            </div>
          )}
          <form onSubmit={handleSubmit} className="space-y-4">
            <textarea
              className="w-full border rounded p-2 min-h-[100px] focus:outline-none focus:ring-2 focus:ring-blue-300"
              placeholder="Type your answer here..."
              value={answer}
              onChange={e => setAnswer(e.target.value)}
              disabled={submitting}
              required
            />
            <button
              type="submit"
              className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded transition"
              disabled={submitting || !answer.trim()}
            >
              {submitting ? "Submitting..." : "Submit Answer"}
            </button>
          </form>
          {error && <div className="text-red-500 mt-2">{error}</div>}
          <div className="mt-4">
            <h3 className="font-semibold mb-2">🔍 Evaluation:</h3>
            {evaluations.length === 0 ? (
              <div className="text-gray-400">No evaluation yet. Submit your answer to see feedback!</div>
            ) : Array.isArray(evaluations) && typeof evaluations[0] === "string" ? (
              <ul className="space-y-2">
                {(evaluations as unknown as string[]).map((part, idx) => (
                  <li key={idx} className="bg-blue-50 p-2 rounded">
                    <span className="font-bold">Part {idx + 1}:</span> {part}
                  </li>
                ))}
              </ul>
            ) : (
              <ul className="space-y-2">
                {(evaluations as Evaluation[]).map((ev, idx) => (
                  <li key={idx} className="bg-blue-50 p-2 rounded">
                    {ev.agent && <span className="font-bold">{ev.agent}:</span>}
                    {Array.isArray(ev.feedback) ? (
                      <ul className="ml-4 list-disc">
                        {ev.feedback.map((part: any, i: number) => (
                          typeof part === "string" ? (
                            <li key={i}>{part}</li>
                          ) : part && typeof part === "object" ? (
                            <li key={i}>
                              {Object.entries(part).map(([k, v], j) => (
                                <div key={j}><span className="font-semibold">{k}:</span> {String(v)}</div>
                              ))}
                            </li>
                          ) : null
                        ))}
                      </ul>
                    ) : typeof ev.feedback === "object" && ev.feedback !== null ? (
                      <ul className="ml-4 list-disc">
                        {Object.entries(ev.feedback).map(([k, v], i) => (
                          <li key={i}><span className="font-semibold">{k}:</span> {String(v)}</li>
                        ))}
                      </ul>
                    ) : (
                      <span>{ev.feedback}</span>
                    )}
                    {ev.score !== undefined && <span className="ml-2 text-green-600">(Score: {ev.score})</span>}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      ) : (
        <div className="text-gray-500">No question available at the moment. 🎉</div>
      )}
      <div className="mt-8">
        <h3 className="text-xl font-bold mb-2">📜 Submission History</h3>
        {loadingHistory ? (
          <div className="text-gray-400">Loading history...</div>
        ) : history.length === 0 ? (
          <div className="text-gray-400">No submissions yet. Try answering a question!</div>
        ) : (
          <ul className="space-y-4">
            {history.map((sub, idx) => (
              <li key={sub.id || idx} className="border rounded p-3 bg-gray-50">
                <div className="mb-1">
                  <span className="font-semibold">Answer:</span> {sub.answer}
                </div>
                <div className="mb-1 text-sm text-gray-500">Submitted: {sub.submittedAt ? new Date(sub.submittedAt).toLocaleString() : "Unknown date"}</div>
                <div>
                  <span className="font-semibold">Evaluations:</span>
                  <ul className="ml-4 list-disc">
                    {(sub.evaluations || []).map((ev, i) => (
                      <li key={i}>
                        <span className="font-bold">{ev.agent}:</span>{" "}
                        {Array.isArray(ev.feedback) ? (
                          <ul className="ml-4 list-disc">
                            {ev.feedback.map((part: any, j) => (
                              typeof part === "string" ? (
                                <li key={j}>{part}</li>
                              ) : part && typeof part === "object" ? (
                                <li key={j}>
                                  {Object.entries(part).map(([k, v], kidx) => (
                                    <div key={kidx}><span className="font-semibold">{k}:</span> {String(v)}</div>
                                  ))}
                                </li>
                              ) : null
                            ))}
                          </ul>
                        ) : typeof ev.feedback === "object" && ev.feedback !== null ? (
                          <ul className="ml-4 list-disc">
                            {Object.entries(ev.feedback).map(([k, v], j) => (
                              <li key={j}><span className="font-semibold">{k}:</span> {String(v)}</li>
                            ))}
                          </ul>
                        ) : (
                          <span>{ev.feedback}</span>
                        )}
                        {ev.score !== undefined && <span className="ml-2 text-green-600">(Score: {ev.score})</span>}
                      </li>
                    ))}
                  </ul>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default StudentQuestionAnswer;
