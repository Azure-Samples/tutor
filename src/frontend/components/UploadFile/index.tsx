"use client";
import { useState, useEffect } from "react";
import { webApi, webApp } from "@/utils/api";

const UploadFile: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<string>("");
  const [destinationContainer, setDestinationContainer] = useState<string>("audio-files");
  const [managerName, setManagerName] = useState<string | null>(null);
  const [specialistName, setSpecialistName] = useState<string | null>(null);
  const [managerOptions, setManagerOptions] = useState<{ name: string; specialists: string[] }[]>([]);
  const [specialistOptions, setSpecialistOptions] = useState<string[]>([]);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setSelectedFile(event.target.files[0]);
    }
  };

  useEffect(() => {
    const fetchManagerOptions = async () => {
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

    fetchManagerOptions();
  }, []);

  // Update specialists when manager selection changes
  useEffect(() => {
    const selectedManager = managerOptions.find(manager => manager.name === managerName);
    setSpecialistOptions(selectedManager ? selectedManager.specialists : []);
    setSpecialistName(null); // Reset specialist selection when manager changes
  }, [managerName, managerOptions]);

  const handleFileUpload = async () => {
    if (!selectedFile) {
      setUploadStatus("Please, submit a file.");
      return;
    }

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const params = {
        destination_container: destinationContainer,
        manager_name: managerName,
        specialist_name: specialistName,
      };

      formData.append("params", JSON.stringify(params));

      setUploadStatus("Uploading File...");

      const response = await webApi.post("/audio-upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      if (response.status === 200) {
        setUploadStatus("File sent successfully!");
      } else {
        setUploadStatus(`There was an error processing the file: ${response?.data?.detail}`);
      }
    } catch (error) {
      const errorMessage = (error as any)?.response?.data?.detail || (error as any)?.message || "Unknown error";
      console.error("There was an error processing the file:", error);
      setUploadStatus(`Error processing the file: ${errorMessage}`);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center w-screen bg-gray-100 dark:bg-gray-900 p-6">
      <div className="w-full max-w-2xl rounded-sm border border-stroke bg-white shadow-lg dark:border-strokedark dark:bg-boxdark">
        <div className="border-b border-stroke px-6.5 py-4 dark:border-strokedark flex items-center justify-between">
          <h3 className="font-medium text-black dark:text-white">
            File upload for transcription analysis
          </h3>
          <div className="">
            <svg
              className="w-5 h-5 text-gray-500 cursor-pointer hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
            >
              <path
                d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 20C7.59 20 4 16.41 4 12C4 7.59 7.59 4 12 4C16.41 4 20 7.59 20 12C20 16.41 16.41 20 12 20ZM13 11V16H11V11H8L12 7L16 11H13Z"
                fill="currentColor"
              />
            </svg>
            <div className="absolute hidden group-hover:block w-max bg-black text-white text-xs rounded py-1 px-2 left-1/2 transform -translate-x-1/2 -translate-y-full mt-2">
              files accepted: .zip, .wav, and .mp3
            </div>
          </div>
        </div>
        <div className="flex flex-col gap-5.5 p-6.5">
          <div>
            <label className="block text-sm font-medium text-black dark:text-white mb-2">
              Select the file
            </label>
            <input
              type="file"
              lang="en-US"
              onChange={handleFileChange}
              className="w-full cursor-pointer rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition file:mr-5 file:border-collapse file:cursor-pointer file:border-0 file:border-r file:border-solid file:border-stroke file:bg-whiter file:px-5 file:py-3 file:hover:bg-primary file:hover:bg-opacity-10 focus:border-primary active:border-primary disabled:cursor-default disabled:bg-whiter dark:border-form-strokedark dark:bg-form-input dark:file:border-form-strokedark dark:file:bg-white/30 dark:file:text-white dark:focus:border-primary"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-black dark:text-white mb-2">
              Destination Blob Container:
            </label>
            <input
              type="text"
              value={destinationContainer}
              onChange={(e) => setDestinationContainer(e.target.value)}
              className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-black dark:text-white mb-2">
              Manager Name:
            </label>
            <select
              value={managerName || ""}
              onChange={(e) => setManagerName(e.target.value)}
              className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary"
            >
              <option value="" disabled>Select a manager</option>
              {managerOptions.map((manager) => (
                <option key={manager.name} value={manager.name}>{manager.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-black dark:text-white mb-2">
              Specialist Name:
            </label>
            <select
              value={specialistName || ""}
              onChange={(e) => setSpecialistName(e.target.value)}
              className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary"
              disabled={!specialistOptions.length}
            >
              <option value="" disabled>Select a specialist</option>
              {specialistOptions.map((specialist) => (
                <option key={specialist} value={specialist}>{specialist}</option>
              ))}
            </select>
          </div>
          <button
            onClick={handleFileUpload}
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 w-full"
          >
            Upload File
          </button>
          {uploadStatus && (
            <p className="mt-2 text-center text-sm text-gray-700 dark:text-gray-300">
              {uploadStatus}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default UploadFile;
