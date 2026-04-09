"use client";
import type { Message } from "@/types/message";
import { chatApi } from "@/utils/api";
import type React from "react";
import { useRef, useState } from "react";

const ChatCard = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [studentId, setStudentId] = useState("showcase-student");
  const [courseId, setCourseId] = useState("showcase-course");
  const chatMessageStreamEnd = useRef<HTMLDivElement | null>(null);
  const nextMessageId = useRef(1);

  const sendMessage = async () => {
    if (input.trim() === "") return;
    const userMessage: Message = { id: nextMessageId.current, sender: "user", content: input };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInput("");
    nextMessageId.current += 1;

    try {
      const response = await chatApi.post("/guide", {
        student_id: studentId,
        course_id: courseId,
        prompt: input,
      });
      const guidance =
        typeof response.data?.guidance === "string"
          ? response.data.guidance
          : "No guidance was returned.";

      setMessages((prevMessages) => [
        ...prevMessages,
        { id: nextMessageId.current, sender: "bot", content: guidance },
      ]);
    } catch (error) {
      console.error("Error streaming from API:", error);
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          id: nextMessageId.current,
          sender: "bot",
          content: "Ocorreu um erro. Tente novamente mais tarde.",
        },
      ]);
    } finally {
      nextMessageId.current += 1;
      chatMessageStreamEnd.current?.scrollIntoView({ behavior: "smooth" });
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      sendMessage();
    }
  };

  return (
    <div className="h-full w-full">
      <div className="h-full w-full flex flex-col">
        <div className="flex-1 p-4 overflow-y-auto space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`p-2 max-w-xs rounded-lg ${
                  message.sender === "user" ? "bg-blue-200 text-black" : "bg-gray-200 text-gray-800"
                }`}
              >
                {message.content}
              </div>
            </div>
          ))}
          <div ref={chatMessageStreamEnd} />
        </div>
      </div>
      <div className="flex flex-col mt-10 bg-white w-full">
        <div className="fixed bottom-0 right-0 w-203 mb-2 mr-4 p-2 border rounded-full border-gray-100 bg-white">
          <div className="mb-2 flex gap-2 px-2">
            <input
              type="text"
              className="w-1/2 rounded-lg border border-gray-200 px-2 py-1 text-xs"
              value={studentId}
              onChange={(e) => setStudentId(e.target.value)}
              placeholder="student_id"
            />
            <input
              type="text"
              className="w-1/2 rounded-lg border border-gray-200 px-2 py-1 text-xs"
              value={courseId}
              onChange={(e) => setCourseId(e.target.value)}
              placeholder="course_id"
            />
          </div>
          <div className="flex items-center">
            <input
              type="text"
              className="flex-1 p-2 rounded-lg focus:outline-none border-none"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Pergunte sobre os dados..."
            />
            <button
              type="button"
              aria-label="Send message"
              className="ml-2 rounded-lg p-2 text-white"
              onClick={sendMessage}
            >
              <svg
                aria-hidden="true"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="red"
                width="24px"
                height="24px"
              >
                <path d="M2 21l21-9L2 3v7l15 2-15 2v7z" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatCard;
