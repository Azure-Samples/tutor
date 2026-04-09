import { useState } from "react";
import { FaCommentDots, FaHashtag, FaPen, FaPlus, FaUser } from "react-icons/fa";

import type { Answer } from "@/types/answer";
import { questionsEngine } from "@/utils/api";

const AnswerForm: React.FC<{ answerData?: Answer; onSuccess?: () => void }> = ({
  answerData,
  onSuccess,
}) => {
  const [form, setForm] = useState<Answer>(
    answerData || {
      id: "",
      text: "",
      question_id: "",
      respondent: "student",
    },
  );
  const [status, setStatus] = useState("");
  const isEdit = !!answerData;

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setStatus("Saving...");

    try {
      const answerId =
        (answerData?.id || form.id || "").trim() ||
        (typeof crypto !== "undefined" && "randomUUID" in crypto
          ? crypto.randomUUID()
          : `ans-${Date.now()}`);
      const payload: Answer = {
        id: answerId,
        text: form.text,
        question_id: form.question_id,
        respondent: form.respondent || "student",
      };

      const response = isEdit
        ? await questionsEngine.put(`/answers/${encodeURIComponent(answerId)}`, payload)
        : await questionsEngine.post("/answers", payload);

      if (response.status === 200 || response.status === 201) {
        setStatus(isEdit ? "Answer updated!" : "Answer created!");
        if (onSuccess) {
          onSuccess();
        }
        if (!isEdit) {
          setForm({ id: "", text: "", question_id: "", respondent: "student" });
        }
      } else {
        setStatus("Error saving answer.");
      }
    } catch {
      setStatus("Error saving answer.");
    }
  };

  return (
    <form
      className="flex flex-col gap-4 w-full max-w-xl mx-auto p-0 form-dot-scrollbar overflow-y-auto"
      id="modal-form"
      onSubmit={handleSubmit}
    >
      <label htmlFor="answer-id" className="flex items-center gap-2 text-cyan-700 font-bold">
        <FaHashtag /> Answer ID
      </label>
      <input
        id="answer-id"
        type="text"
        value={form.id}
        onChange={(e) => setForm({ ...form, id: e.target.value })}
        disabled={isEdit}
        className="w-full rounded-2xl border-2 border-cyan-200 focus:border-green-400 focus:ring-2 focus:ring-green-200 px-4 py-3 text-lg transition-all duration-200 bg-cyan-50 dark:bg-cyan-900 placeholder:text-cyan-400 focus:bg-white dark:focus:bg-boxdark"
        placeholder="Leave blank to auto-generate"
      />

      <label htmlFor="answer-text" className="flex items-center gap-2 text-green-700 font-bold">
        <FaCommentDots /> Answer Text
      </label>
      <textarea
        id="answer-text"
        value={form.text}
        onChange={(e) => setForm({ ...form, text: e.target.value })}
        className="w-full rounded-2xl border-2 border-green-200 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-200 px-4 py-3 text-lg transition-all duration-200 bg-green-50 dark:bg-green-900 placeholder:text-green-400 focus:bg-white dark:focus:bg-boxdark resize-y min-h-[48px] max-h-[240px]"
        placeholder="Student answer"
        rows={3}
      />

      <label
        htmlFor="answer-question-id"
        className="flex items-center gap-2 text-blue-700 font-bold"
      >
        <FaHashtag /> Question ID
      </label>
      <input
        id="answer-question-id"
        type="text"
        value={form.question_id}
        onChange={(e) => setForm({ ...form, question_id: e.target.value })}
        className="w-full rounded-2xl border-2 border-blue-200 focus:border-yellow-400 focus:ring-2 focus:ring-yellow-200 px-4 py-3 text-lg transition-all duration-200 bg-blue-50 dark:bg-blue-900 placeholder:text-blue-400 focus:bg-white dark:focus:bg-boxdark"
        placeholder="Question ID reference"
      />

      <label
        htmlFor="answer-respondent"
        className="flex items-center gap-2 text-purple-700 font-bold"
      >
        <FaUser /> Respondent
      </label>
      <input
        id="answer-respondent"
        type="text"
        value={form.respondent}
        onChange={(e) => setForm({ ...form, respondent: e.target.value })}
        className="w-full rounded-2xl border-2 border-purple-200 focus:border-blue-400 focus:ring-2 focus:ring-blue-200 px-4 py-3 text-lg transition-all duration-200 bg-purple-50 dark:bg-purple-900 placeholder:text-purple-400 focus:bg-white dark:focus:bg-boxdark"
        placeholder="student"
      />

      <button
        type="submit"
        className="mt-4 px-4 py-3 bg-gradient-to-br from-green-400 to-cyan-400 hover:from-cyan-400 hover:to-yellow-300 text-white font-bold rounded-2xl shadow-lg w-full flex items-center justify-center gap-2 text-lg transition-all duration-200"
      >
        {isEdit ? <FaPen /> : <FaPlus />} {isEdit ? "Update Answer" : "Create Answer"}
      </button>

      {status && (
        <p className="mt-2 text-center text-sm text-gray-700 dark:text-gray-300">{status}</p>
      )}
    </form>
  );
};

export default AnswerForm;
