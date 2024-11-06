"use client";
import { useState, useEffect } from "react";
import { webApp, transcriptionApi, evaluateApi } from "@/utils/api";

const EvaluationJob: React.FC = () => {
  const [managers, setManagers] = useState<{ id: string; name: string; assistants: { id: string; name: string; transcriptions: { id: string; filename: string; transcription: string; is_valid_call: string; metadata: Record<string, any> }[] }[] }[]>([]);
  const [managerName, setManagerName] = useState<string>("");
  const [specialistName, setSpecialistName] = useState<string>("");
  const [specialists, setSpecialists] = useState<string[]>([]);
  const [transcriptions, setTranscriptions] = useState<{ id: string; filename: string; transcription: string; is_valid_call: string; metadata: Record<string, any> }[]>([]);
  const [criteriaOptions, setCriteriaOptions] = useState<{ topic: string; business_rules: string[]; sub_criteria: any[] }[]>([]);
  const [selectedCriteria, setSelectedCriteria] = useState<string[]>([]);
  const [status, setStatus] = useState<string>("");
  const [theme, setTheme] = useState<string>("");

  useEffect(() => {
    const fetchCriteria = async () => {
      try {
        const response = await webApp.get("/rules");
        if (response.status === 200) {
          const transformedCriteria = response.data.detail.rules.map((criteria: any) => ({
            ...criteria,
            sub_criteria: criteria.subCriteria || [],
            business_rules: criteria.businessRules || [],
          }));
          setCriteriaOptions(transformedCriteria);
        } else {
          console.error("Failed to fetch criteria:", response.statusText);
        }
      } catch (error) {
        console.error("Error fetching criteria:", error);
      }
    };

    fetchCriteria();
  }, []);

  // Fetch managers and set options
  useEffect(() => {
    const fetchManagers = async () => {
      try {
        const response = await transcriptionApi.get("/transcriptions");
        if (response.status === 200) {
          setManagers(response.data.result);
        } else {
          console.error("Failed to fetch managers:", response.statusText);
        }
      } catch (error) {
        console.error("Error fetching managers:", error);
      }
    };

    fetchManagers();
  }, []);

  // Fetch specialists based on selected manager
  useEffect(() => {
    if (managerName) {
      const selectedManager = managers.find((manager) => manager.name === managerName);
      if (selectedManager) {
        setSpecialists(selectedManager.assistants.map((specialist) => specialist.name));
      }
    }
  }, [managerName, managers]);

  // Load all transcriptions for the selected specialist under the manager
  useEffect(() => {
    if (managerName && specialistName) {
      const selectedManager = managers.find((manager) => manager.name === managerName);
      const selectedSpecialist = selectedManager?.assistants.find((specialist) => specialist.name === specialistName);
      if (selectedSpecialist) {
        setTranscriptions(selectedSpecialist.transcriptions);
      }
    }
  }, [managerName, specialistName, managers]);

  // Handle form submission to start an evaluation job
  const handleJobSubmission = async () => {
    try {
      const payload = {
        theme,
        transcriptions,
        criteria: criteriaOptions.filter((criteria) => selectedCriteria.includes(criteria.topic)),
      };

      setStatus("Starting Evaluation...");

      const response = await evaluateApi.post("/evaluate", payload);

      if (response.status === 200) {
        setStatus("Evaluation job started!");
      } else {
        setStatus("There was an error processing your request.");
      }
    } catch (error) {
      console.error("Error on evaluation job:", error);
      setStatus("There was an error processing your request.");
    }
  };

  console.log(managers)

  return (
    <div className="flex flex-col items-center justify-start w-screen h-screen bg-gray-100 dark:bg-gray-900 p-6">
      <div className="w-full max-w-full bg-white shadow-default dark:bg-boxdark p-6 rounded-lg">
        <h3 className="font-medium text-black dark:text-white mb-6 text-center">
          Evaluation Job
        </h3>
        <div className="flex flex-col gap-4 mb-6">
          <div>
            <label className="text-sm font-medium text-black dark:text-white mb-2 block">
              Call Center Theme
            </label>
            <input
              type="text"
              value={theme}
              onChange={(e) => setTheme(e.target.value)}
              className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
              placeholder="Enter the type of callcenter that the AI should represent"
            />
          </div>
          
          {/* Manager Selection */}
          <div>
            <label className="text-sm font-medium text-black dark:text-white mb-2 block">
              Select Manager
            </label>
            <select
              value={managerName}
              onChange={(e) => setManagerName(e.target.value)}
              className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
            >
              <option value="">Select a manager</option>
              {managers.map((manager) => (
                <option key={manager.id} value={manager.name}>
                  {manager.name}
                </option>
              ))}
            </select>
          </div>

          {/* Specialist Selection */}
          <div>
            <label className="text-sm font-medium text-black dark:text-white mb-2 block">
              Select Specialist
            </label>
            <select
              value={specialistName}
              onChange={(e) => setSpecialistName(e.target.value)}
              className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
            >
              <option value="">Select a specialist</option>
              {specialists.map((specialist) => (
                <option key={specialist} value={specialist}>
                  {specialist}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-sm font-medium text-black dark:text-white mb-2 block">
              Select Criteria
            </label>
            <select
              multiple
              value={selectedCriteria}
              onChange={(e) => setSelectedCriteria(Array.from(e.target.selectedOptions, option => option.value))}
              className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
            >
              {criteriaOptions.map((criteria) => (
                <option key={criteria.topic} value={criteria.topic}>
                  {criteria.topic}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Submit Button */}
        <button
          onClick={handleJobSubmission}
          className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 w-full"
        >
          Start Evaluation
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

export default EvaluationJob;
