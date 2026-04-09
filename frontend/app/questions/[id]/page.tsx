"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { unwrapContent } from "@/types/api";
import type { Question } from "@/types/question";
import { questionsEngine } from "@/utils/api";

const QuestionDetailPage: React.FC = () => {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const questionId = Array.isArray(params?.id) ? params.id[0] : params?.id;

  const [question, setQuestion] = useState<Question | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!questionId) {
      setLoading(false);
      return;
    }

    setLoading(true);
    questionsEngine
      .get(`/questions/${questionId}`)
      .then((res) => {
        const data = unwrapContent<Question | null>(res.data);
        setQuestion(data ?? null);
      })
      .catch(() => {
        setError("Could not load question details.");
      })
      .finally(() => {
        setLoading(false);
      });
  }, [questionId]);

  return (
    <DefaultLayout>
      <Breadcrumb
        pageName="Question Details"
        subtitle="Inspect question metadata and grading context."
      />
      <button
        type="button"
        onClick={() => router.back()}
        className="mb-4 rounded bg-blue-500 px-4 py-2 text-white hover:bg-blue-600"
      >
        Back
      </button>

      {loading ? (
        <div className="p-6">Loading question...</div>
      ) : error ? (
        <div className="p-6 text-red-600">{error}</div>
      ) : question ? (
        <div className="mt-4 max-w-3xl rounded-2xl bg-white p-6 shadow dark:bg-boxdark">
          <h2 className="text-2xl font-bold text-cyan-700">{question.topic}</h2>
          <p className="mt-4 whitespace-pre-line text-base text-gray-800 dark:text-gray-200">
            {question.question}
          </p>
          {question.explanation && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold text-green-700">Explanation</h3>
              <p className="mt-2 whitespace-pre-line text-gray-700 dark:text-gray-300">
                {question.explanation}
              </p>
            </div>
          )}
        </div>
      ) : (
        <div className="p-6">Question not found.</div>
      )}
    </DefaultLayout>
  );
};

export default QuestionDetailPage;
