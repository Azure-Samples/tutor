"use client"
import React, { useState, useRef } from "react";
import { Message } from "@/types/message";
import api from "@/utils/api";  // Supondo que o controle de API esteja em `utils/api.ts`


const ChatCard = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const chatMessageStreamEnd = useRef<HTMLDivElement | null>(null);

  let messageId = 1;

  const sendMessage = async () => {
    if (input.trim() === '') return;
    const userMessage: Message = { id: messageId, sender: 'user', content: input };
    setMessages([...messages, userMessage]);
    setInput('');
    messageId += 1;

    try {
      const response = await api.post('/chat', { question: input });

      setMessages(prevMessages => [
        ...prevMessages,
        { id: messageId, sender: 'bot', content: response.data }
      ]);
    } catch (error) {
      console.error('Error streaming from API:', error);
      setMessages(prevMessages => [
        ...prevMessages,
        { id: messageId, sender: 'bot', content: 'Ocorreu um erro. Tente novamente mais tarde.' }
      ]);
    } finally {
      messageId += 1;
      chatMessageStreamEnd.current?.scrollIntoView({ behavior: "smooth" });
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  return (
    <div className="h-full w-full">
      <div className="h-full w-full flex flex-col">
        <div className="flex-1 p-4 overflow-y-auto space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`p-2 max-w-xs rounded-lg ${
                  message.sender === 'user' ? 'bg-blue-200 text-black' : 'bg-gray-200 text-gray-800'
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
              className="ml-2 p-2 text-white rounded-lg"
              onClick={sendMessage}
            >
              <svg
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
