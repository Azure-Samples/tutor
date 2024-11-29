"use client";
import { useState } from "react";
import { webApp } from "@/utils/api";
import { Question } from "@/types/question";

const QuestionForm: React.FC = () => {
  const [question, setQuestion] = useState<Question>({
    topic: "",
    question: "",
    answer: "",
  });

  const [status, setStatus] = useState<string>("");

  const handleJobSubmission = async () => {
    try {
      setStatus("Sending request...");

      const response = await webApp.post("/create-question", question);

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
        <h3 className="font-medium text-black dark:text-white mb-6 text-center">
          Add Question
        </h3>
        <div className="flex flex-col gap-4 mb-6">
          <div>
            <label className="font-large text-black dark:text-white mb-2 block">
              Topic
            </label>
            <input
              type="text"
              value={question.topic}
              onChange={(e) => setQuestion({ ...question, topic: e.target.value })}
              className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
              placeholder="Type the topic"
            />
          </div>
          <div>
            <label className="text-sm font-medium text-black dark:text-white mb-2 block">
              Question
            </label>
            <textarea
              value={question.question}
              onChange={(e) => setQuestion({ ...question, question: e.target.value })}
              className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
              placeholder="Type the question"
            />
          </div>
          <div>
            <label className="text-sm font-medium text-black dark:text-white mb-2 block">
              Answer
            </label>
            <textarea
              value={question.answer}
              onChange={(e) => setQuestion({ ...question, answer: e.target.value })}
              className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
              placeholder="Type the answer"
            />
          </div>
        </div>

        <button
          onClick={handleJobSubmission}
          className="mt-6 px-4 py-2 bg-non-photo-blue text-white rounded hover:bg-blue-600 w-full"
        >
          Add Question
        </button>
        {status && (
          <p className="mt-2 text-center text-sm text-gray-700 dark:text-gray-300">
            {status}
          </p>
        )}
      </div>
    </div>
  );
};

export default QuestionForm;
