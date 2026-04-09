"use client";
import type { Question } from "@/types/question";
import { questionsEngine } from "@/utils/api";
import { useState } from "react";

const QuestionForm: React.FC = () => {
  const [question, setQuestion] = useState<Question>({
    id: "",
    topic: "",
    question: "",
    explanation: "",
  });

  const [status, setStatus] = useState<string>("");

  const handleJobSubmission = async () => {
    try {
      setStatus("Sending request...");

      const payload = {
        ...question,
        id:
          question.id ||
          (typeof crypto !== "undefined" && "randomUUID" in crypto
            ? crypto.randomUUID()
            : `q-${Date.now()}`),
        explanation: question.explanation ?? "",
      };

      const response = await questionsEngine.post("/questions", payload);

      if (response.status === 200 || response.status === 201) {
        setStatus("Question created successfully!");
      } else {
        setStatus("Error occurred while creating the question.");
      }
    } catch (error) {
      console.error("Error initiating the question creation:", error);
      setStatus("Error initiating the question creation.");
    }
  };

  return (
    <div className="flex flex-col items-center justify-start w-screen h-screen bg-gray-100 dark:bg-gray-900 p-6">
      <div className="w-full max-w-full bg-white shadow-default dark:bg-boxdark p-6 rounded-lg">
        <h3 className="font-medium text-black dark:text-white mb-6 text-center">Add Question</h3>
        <div className="flex flex-col gap-4 mb-6">
          <div>
            <label
              htmlFor="question-topic"
              className="font-large text-black dark:text-white mb-2 block"
            >
              Topic
            </label>
            <input
              id="question-topic"
              type="text"
              value={question.topic}
              onChange={(e) => setQuestion({ ...question, topic: e.target.value })}
              className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
              placeholder="Type the topic"
            />
          </div>
          <div>
            <label
              htmlFor="question-body"
              className="text-sm font-medium text-black dark:text-white mb-2 block"
            >
              Question
            </label>
            <textarea
              id="question-body"
              value={question.question}
              onChange={(e) => setQuestion({ ...question, question: e.target.value })}
              className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
              placeholder="Type the question"
            />
          </div>
          <div>
            <label
              htmlFor="question-explanation"
              className="text-sm font-medium text-black dark:text-white mb-2 block"
            >
              Explanation
            </label>
            <textarea
              id="question-explanation"
              value={question.explanation ?? ""}
              onChange={(e) => setQuestion({ ...question, explanation: e.target.value })}
              className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
              placeholder="Type the explanation"
            />
          </div>
        </div>

        <button
          type="button"
          onClick={handleJobSubmission}
          className="mt-6 px-4 py-2 bg-non-photo-blue text-white rounded hover:bg-blue-600 w-full"
        >
          Add Question
        </button>
        {status && (
          <p className="mt-2 text-center text-sm text-gray-700 dark:text-gray-300">{status}</p>
        )}
      </div>
    </div>
  );
};

export default QuestionForm;
