"use client";
import { useState, useEffect } from "react";
import { transcriptionApi, webApp } from "@/utils/api";

const TranscriptionJob: React.FC = () => {
  const [originContainer, setOriginContainer] = useState<string>("audio-files");
  const [destinationContainer, setDestinationContainer] = useState<string>("transcripts");
  const [managerName, setManagerName] = useState<string>("");
  const [specialistName, setSpecialistName] = useState<string>("");
  const [limit, setLimit] = useState<number>(-1);
  const [onlyFailed, setOnlyFailed] = useState<boolean>(true);
  const [useCache, setUseCache] = useState<boolean>(false);
  const [status, setStatus] = useState<string>("");

  const [managerOptions, setManagerOptions] = useState<{ name: string; specialists: string[] }[]>([]);
  const [specialistOptions, setSpecialistOptions] = useState<string[]>([]);

  useEffect(() => {
    const fetchManagers = async () => {
      try {
        const response = await webApp.get("/managers-names");
        if (response.status === 200) {
          setManagerOptions(response?.data?.detail?.managers);
        } else {
          console.error("Failed to fetch manager names:", response.statusText);
        }
      } catch (error) {
        console.error("Error fetching manager names:", error);
      }
    };

    fetchManagers();
  }, []);

  useEffect(() => {
    const selectedManager = managerOptions.find((manager) => manager.name === managerName);
    setSpecialistOptions(selectedManager ? selectedManager.specialists : []);
    setSpecialistName("");
  }, [managerName, managerOptions
]);

const handleJobSubmission = async () => {
  try {
    const payload = {
      origin_container: originContainer,
      destination_container: destinationContainer,
      manager_name: managerName,
      specialist_name: specialistName,
      limit: limit,
      only_failed: onlyFailed,
      use_cache: useCache
    };

    setStatus("Starting Transcriptions...");

    const response = await transcriptionApi.post("/transcription", payload);

    if (response.status === 200) {
      setStatus("Transcription job started!");
    } else {
      setStatus("There was an error processing your request.");
    }
  } catch (error) {
    console.error("Error on transcription job:", error);
    setStatus("There was an error processing your request.");
  }
};

return (
  <div className="flex flex-col items-center justify-start w-screen h-screen bg-gray-100 dark:bg-gray-900 p-6">
    <div className="w-full max-w-full bg-white shadow-default dark:bg-boxdark p-6 rounded-lg">
      <h3 className="font-medium text-black dark:text-white mb-6 text-center">
        Transcription Job
      </h3>
      <div className="flex flex-col gap-4 mb-6">
        <div>
          <label className="text-sm font-medium text-black dark:text-white mb-2 block">
            Origin Blob Container
          </label>
          <input
            type="text"
            value={originContainer}
            onChange={(e) => setOriginContainer(e.target.value)}
            className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
            placeholder="Enter origin container name"
          />
        </div>
        <div>
          <label className="text-sm font-medium text-black dark:text-white mb-2 block">
            Destination Blob Container
          </label>
          <input
            type="text"
            value={destinationContainer}
            onChange={(e) => setDestinationContainer(e.target.value)}
            className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
            placeholder="Enter destination container name"
          />
        </div>
        <div>
          <label className="text-sm font-medium text-black dark:text-white mb-2 block">
            Manager Name
          </label>
          <select
            value={managerName}
            onChange={(e) => setManagerName(e.target.value)}
            className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary"
          >
            <option value="">Select a manager</option>
            {managerOptions.map((manager) => (
              <option key={manager.name} value={manager.name}>
                {manager.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-sm font-medium text-black dark:text-white mb-2 block">
            Specialist Name
          </label>
          <select
            value={specialistName}
            onChange={(e) => setSpecialistName(e.target.value)}
            className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary"
            disabled={!specialistOptions.length}
          >
            <option value="">Select a specialist</option>
            {specialistOptions.map((specialist) => (
              <option key={specialist} value={specialist}>
                {specialist}
              </option>
            ))}
          </select>
        </div>
      </div>
      
      {/* Additional Options */}
      <div className="flex flex-col gap-4 mb-6">
        <div>
          <label className="text-sm font-medium text-black dark:text-white mb-2 block">
            Files to Process
          </label>
          <input
            type="number"
            value={limit}
            onChange={(e) => setLimit(parseInt(e.target.value))}
            className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
            placeholder="-1 to process all files"
          />
        </div>
        <div className="flex items-center">
          <input
            type="checkbox"
            checked={onlyFailed}
            onChange={(e) => setOnlyFailed(e.target.checked)}
            className="mr-2 cursor-pointer"
          />
          <label className="text-sm font-medium text-black dark:text-white">
            Process only failed files
          </label>
        </div>
        <div className="flex items-center">
          <input
            type="checkbox"
            checked={useCache}
            onChange={(e) => setUseCache(e.target.checked)}
            className="mr-2 cursor-pointer"
          />
          <label className="text-sm font-medium text-black dark:text-white">
            Use Cached (already transcribed) files
          </label>
        </div>
      </div>

      <button
        onClick={handleJobSubmission}
        className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 w-full"
      >
        Execute Transcription
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

export default TranscriptionJob;