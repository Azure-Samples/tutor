"use client";
import React, { useState, useEffect } from 'react';
import Modal from 'react-modal';
import { BACK_URL, evaluateApi } from '@/utils/api';
import { useHumanEvaluation } from '@/utils/humanEvalContext';
import { Transcription as TranscriptionType, SummaryData } from '@/types/transcription';

interface TranscriptionFileProps {
  transcription: TranscriptionType;
}

interface EvalApiResponse {
  classification: string;
  summaryData: { [key: string]: SummaryData };
  improvementSuggestion: string;
}

const promptData = [
  {
    label: 'Closing',
    value: 'closing',
    defaultPrompt: `Did the investment advisor properly close the call by asking the client if they needed any additional assistance or had further questions?
If the advisor ended the call informally but courteously and attentively, consider it as if they asked the client. Assign a score of 1 if all recommendations were followed and 0 otherwise.
In the JSON structure, consider the item as "Closing" and the sub-item as "Asked if client needed any further assistance or had questions."`,
  },
];

const Transcription: React.FC<TranscriptionFileProps> = ({ transcription }) => {
  const { filename, successfulCall, classification, content } = transcription;
  const { humanEvaluation, updateHumanEvaluation } = useHumanEvaluation();

  const [isEvaluationModalOpen, setIsEvaluationModalOpen] = useState(false);
  const [isTranscriptionModalOpen, setIsTranscriptionModalOpen] = useState(false);
  const [evalApiResponse, setEvalApiResponse] = useState<EvalApiResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true); // Track loading state
  const [selectedPrompt, setSelectedPrompt] = useState(promptData[0].defaultPrompt);
  const [selectedTopic, setSelectedTopic] = useState(promptData[0].value);
  const [improvedTranscription, setImprovedTranscription] = useState<string>(content);

  useEffect(() => {
    const fetchEvaluationData = async () => {
      setIsLoading(true); // Start loading
      try {
        const response = await evaluateApi.get(`/specialist-evaluation?transcription_id=${transcription.id}`);
        if (response?.data?.result) {
          const responseData = {
            classification: response.data.result[0].classification,
            summaryData: response.data.result[0].summaryData,
            improvementSuggestion: response.data.result[0].improvementSuggestion,
          };
          setEvalApiResponse(responseData);
          console.log('Evaluation data:', responseData);
        }
      } catch (error) {
        console.error('Failed to fetch evaluation data:', error);
      } finally {
        setIsLoading(false); // Stop loading after fetching
      }
    };

    fetchEvaluationData();
  }, [transcription.id]);

  const handlePromptChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selected = promptData.find((item) => item.value === e.target.value);
    if (selected) {
      setSelectedTopic(selected.value);
      setSelectedPrompt(selected.defaultPrompt);
    }
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setSelectedPrompt(e.target.value);
  };

  const handleEvaluationSubmit = async () => {
    // handle evaluation submit logic here
  };

  const handleImprovement = async () => {
    // handle improvement logic here
  };

  const closeEvaluationModal = () => setIsEvaluationModalOpen(false);
  const closeTranscriptionModal = () => {
    setImprovedTranscription(content); // Reset to original content
    setIsTranscriptionModalOpen(false);
  };

  const downloadAudio = async () => {
    // download audio logic here
  };

  const renderEvaluationTable = () => (
    <div className="mt-8">
      <h4 className="text-lg font-bold mb-2 text-black dark:text-white">Evaluation Results</h4>
      <table className="table-auto w-full text-left text-gray-800 dark:text-gray-300 border-collapse">
        <thead>
          <tr>
            <th className="border-b-2 p-2">Item</th>
            <th className="border-b-2 p-2">Sub-Item</th>
            <th className="border-b-2 p-2">Score</th>
            <th className="border-b-2 p-2">Justification</th>
          </tr>
        </thead>
        <tbody>
          {evalApiResponse?.summaryData && Object.keys(evalApiResponse.summaryData).map((key, index) => {
            const data = evalApiResponse.summaryData[key];
            return (
              <tr key={index}>
                <td className="border-b p-2">{key}</td>
                <td className="border-b p-2">{data.sub_criteria}</td>
                <td className="border-b p-2">{data.score}</td>
                <td className="border-b p-2">{data.rationale}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );

  // Render a loading message while data is being fetched
  if (isLoading) {
    return <p className="text-gray-500 dark:text-gray-400">Loading transcription data...</p>;
  }

  return (
    <div className="p-8 bg-white dark:bg-gray-900 w-full mx-auto mt-16">
      <h4 className="text-xl font-bold mb-4 text-black dark:text-white">Transcription Details - {transcription.id}</h4>
      <div className="mb-4 text-gray-800 dark:text-gray-300">
        <p>Successful Call: {successfulCall ? "Yes" : "No"}</p>
        <p>Classification: {classification}</p>
        <p>Filename: {filename}</p>
      </div>
      <div className="mt-8">
      <h4 className="text-lg font-bold mb-2 text-black dark:text-white">Evaluation Results</h4>
      <table className="table-auto w-full text-left text-gray-800 dark:text-gray-300 border-collapse">
        <thead>
          <tr>
            <th className="border-b-2 p-2">Item</th>
            <th className="border-b-2 p-2">Sub-Item</th>
            <th className="border-b-2 p-2">Score</th>
            <th className="border-b-2 p-2">Justification</th>
          </tr>
        </thead>
        <tbody>
          {evalApiResponse?.summaryData && Object.keys(evalApiResponse.summaryData).map((key, index) => {
            const data = evalApiResponse.summaryData[key];
            return (
              <tr key={index}>
                <td className="border-b p-2">{key}</td>
                <td className="border-b p-2">{data.sub_criteria}</td>
                <td className="border-b p-2">{data.score}</td>
                <td className="border-b p-2">{data.rationale}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
      <button onClick={downloadAudio} className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">Download Audio</button>
      <button onClick={() => setIsEvaluationModalOpen(true)} className="mt-4 ml-4 px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600">Prompt Evaluation</button>
      <button onClick={() => setIsTranscriptionModalOpen(true)} className="mt-4 ml-4 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600">Optimize Transcription</button>

      <Modal
        isOpen={isEvaluationModalOpen}
        onRequestClose={closeEvaluationModal}
        ariaHideApp={false}
        className="modal-class"
        overlayClassName="modal-overlay"
      >
        <h4 className="text-xl font-bold">Prompt Evaluation</h4>
        <select value={selectedTopic} onChange={handlePromptChange} className="w-full p-2 mt-4">
          {promptData.map((item) => (
            <option key={item.value} value={item.value}>{item.label}</option>
          ))}
        </select>
        <textarea value={selectedPrompt} onChange={handleTextareaChange} className="w-full h-40 mt-4 p-2" />
        <button onClick={handleEvaluationSubmit} className="mt-4 bg-green-500 px-4 py-2 text-white rounded">Evaluate</button>
        {evalApiResponse && renderEvaluationTable()}
      </Modal>

      <Modal
        isOpen={isTranscriptionModalOpen}
        onRequestClose={closeTranscriptionModal}
        ariaHideApp={false}
        className="modal-class"
        overlayClassName="modal-overlay"
      >
        <h4 className="text-xl font-bold">Optimize Transcription</h4>
        <textarea value={improvedTranscription} readOnly className="w-full h-40 mt-4 p-2" />
        <button onClick={handleImprovement} className="mt-4 bg-green-500 px-4 py-2 text-white rounded">Optimize</button>
      </Modal>
    </div>
  );
};

export default Transcription;
