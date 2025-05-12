"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import type { Essay } from "@/types/essays";
import { essaysEngine } from "@/utils/api";

const EssayDetailPage: React.FC = () => {
  const { id } = useParams();
  const [essay, setEssay] = useState<Essay | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    essaysEngine.get(`/essays/${id}`)
      .then(res => {
        setEssay(res.data.content || null);
        setLoading(false);
      })
      .catch(() => {
        setError("Could not load essay.");
        setLoading(false);
      });
  }, [id]);

  return (
    <DefaultLayout>
      <Breadcrumb pageName="Essay Details" subtitle="Review the essay theme, content, and explanation." />
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <span className="text-lg text-cyan-500 animate-pulse">Loading essay...</span>
        </div>
      ) : error ? (
        <div className="text-center text-red-600 font-bold py-8">{error}</div>
      ) : essay ? (
        <div className="max-w-2xl mx-auto bg-white dark:bg-boxdark rounded-2xl shadow-lg p-8 mt-8">
          <h2 className="text-3xl font-bold text-cyan-700 mb-4">{essay.topic}</h2>
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-blue-700 mb-2">Content</h3>
            <p className="text-base text-gray-800 dark:text-gray-200 whitespace-pre-line">{essay.content}</p>
          </div>
          {essay.explanation && (
            <div>
              <h3 className="text-lg font-semibold text-green-700 mb-2">Explanation</h3>
              <p className="text-base text-gray-700 dark:text-gray-300 whitespace-pre-line">{essay.explanation}</p>
            </div>
          )}
        </div>
      ) : (
        <div className="text-center text-gray-600 py-8">No essay found.</div>
      )}
    </DefaultLayout>
  );
};

export default EssayDetailPage;
