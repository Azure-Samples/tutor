import { useState } from "react";
import { questionsEngine } from "@/utils/api";
import { Question } from "@/types/question";
import { FaPen, FaBook, FaPlus, FaQuestionCircle } from "react-icons/fa";

const QuestionForm: React.FC<{ questionData?: Question; onSuccess?: () => void }> = ({ questionData, onSuccess }) => {
  const [form, setForm] = useState<Question>(
    questionData || { topic: "", question: "", answer: "" }
  );
  const [status, setStatus] = useState("");
  const isEdit = !!questionData;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("Saving...");
    try {
      let res;
      if (isEdit) {
        res = await questionsEngine.put(`/questions/${form.topic}`, form);
      } else {
        res = await questionsEngine.post("/questions", form);
      }
      if (res.status === 200 || res.status === 201) {
        setStatus(isEdit ? "Question updated!" : "Question created!");
        if (onSuccess) onSuccess();
      } else {
        setStatus("Error saving question.");
      }
    } catch (e) {
      setStatus("Error saving question.");
    }
  };

  return (
    <form
      className="flex flex-col gap-4 w-full max-w-xl mx-auto p-0 form-dot-scrollbar overflow-y-auto"
      id="modal-form"
      onSubmit={handleSubmit}
    >
      <label className="flex items-center gap-2 text-cyan-700 font-bold">
        <FaQuestionCircle /> Question
      </label>
      <textarea
        value={form.question}
        onChange={e => setForm({ ...form, question: e.target.value })}
        className="w-full rounded-2xl border-2 border-cyan-200 focus:border-green-400 focus:ring-2 focus:ring-green-200 px-4 py-3 text-lg transition-all duration-200 bg-cyan-50 dark:bg-cyan-900 placeholder:text-cyan-400 focus:bg-white dark:focus:bg-boxdark resize-y min-h-[48px] max-h-[240px]"
        placeholder="Type the question"
        rows={2}
      />
      <label className="flex items-center gap-2 text-green-700 font-bold">
        <FaBook /> Topic
      </label>
      <input
        type="text"
        value={form.topic}
        onChange={e => setForm({ ...form, topic: e.target.value })}
        className="w-full rounded-2xl border-2 border-green-200 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-200 px-4 py-3 text-lg transition-all duration-200 bg-green-50 dark:bg-green-900 placeholder:text-green-400 focus:bg-white dark:focus:bg-boxdark"
        placeholder="Topic"
      />
      <label className="flex items-center gap-2 text-blue-700 font-bold">
        <FaPen /> Answer
      </label>
      <textarea
        value={form.answer}
        onChange={e => setForm({ ...form, answer: e.target.value })}
        className="w-full rounded-2xl border-2 border-blue-200 focus:border-yellow-400 focus:ring-2 focus:ring-yellow-200 px-4 py-3 text-lg transition-all duration-200 bg-blue-50 dark:bg-blue-900 placeholder:text-blue-400 focus:bg-white dark:focus:bg-boxdark resize-y min-h-[48px] max-h-[240px]"
        placeholder="Type the answer"
        rows={2}
      />
      {status && <p className="mt-2 text-center text-sm text-gray-700 dark:text-gray-300">{status}</p>}
    </form>
  );
};

export default QuestionForm;
