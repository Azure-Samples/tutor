"use client";
import { useState } from "react";
import { webApp } from "@/utils/api";
import { Manager } from "@/types/manager";
import { Specialist } from "@/types/specialist";

const ManagerForm: React.FC = () => {
  const [manager, setManager] = useState<Manager>({
    name: "",
    role: "",
    specialists: [],
    performance: 0
  });

  const [status, setStatus] = useState<string>("");

  const handleJobSubmission = async () => {
    try {
      setStatus("Sending request...");

      const response = await webApp.post("/create-manager", manager);

      if (response.status === 200 || response.status === 201) {
        setStatus("Manager created successfully!");
      } else {
        setStatus("Error occurred while creating the job.");
      }
    } catch (error) {
      console.error("Error initiating the job:", error);
      setStatus("Error initiating the job.");
    }
  };

  const handleSpecialistChange = (index: number, field: keyof Specialist, value: any) => {
    const updatedSpecialists = manager.specialists.map((specialist, i) => {
      if (i === index) {
        return { ...specialist, [field]: value };
      }
      return specialist;
    });
    setManager({ ...manager, specialists: updatedSpecialists });
  };

  const addSpecialist = () => {
    setManager({
      ...manager,
      specialists: [
        ...manager.specialists,
        { name: "", role: "", transcriptions: [], performance: 0 },
      ],
    });
  };

  const removeSpecialist = (index: number) => {
    setManager({
      ...manager,
      specialists: manager.specialists.filter((_, i) => i !== index),
    });
  };

  return (
    <div className="flex flex-col items-center justify-start w-screen h-screen bg-gray-100 dark:bg-gray-900 p-6">
      <div className="w-full max-w-full bg-white shadow-default dark:bg-boxdark p-6 rounded-lg">
        <h3 className="font-medium text-black dark:text-white mb-6 text-center">
          Add Manager
        </h3>
        <div className="flex flex-col gap-4 mb-6">
          <div>
            <label className="font-large text-black dark:text-white mb-2 block">
              Manager Name
            </label>
            <input
              type="text"
              value={manager.name}
              onChange={(e) => setManager({ ...manager, name: e.target.value })}
              className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
              placeholder="Type the manager name"
            />
          </div>
          <div>
            <label className="text-sm font-medium text-black dark:text-white mb-2 block">
              Manager Role
            </label>
            <input
              type="text"
              value={manager.role}
              onChange={(e) => setManager({ ...manager, role: e.target.value })}
              className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
              placeholder="Type the manager role"
            />
          </div>
        </div>

        {/* Specialists Section */}
        <div className="w-full">
          <h4 className="text-lg font-medium text-black dark:text-white mb-2">Manager Team</h4>
          <div className="grid grid-cols-3 gap-4 text-sm font-semibold text-gray-600 dark:text-gray-300 mb-2">
            <span>Name</span>
            <span>Role</span>
            <span>Actions</span>
          </div>
          {manager.specialists.map((specialist, index) => (
            <div key={index} className="grid grid-cols-3 gap-4 items-center mb-2">
              <input
                type="text"
                value={specialist.name}
                onChange={(e) => handleSpecialistChange(index, "name", e.target.value)}
                className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
                placeholder="Specialist Name"
              />
              <input
                type="text"
                value={specialist.role}
                onChange={(e) => handleSpecialistChange(index, "role", e.target.value)}
                className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
                placeholder="Specialist Role"
              />
              <button
                type="button"
                onClick={() => removeSpecialist(index)}
                className="text-red-500 hover:text-red-700"
              >
                Remove
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={addSpecialist}
            className="mt-2 px-4 py-2 bg-kelly-green text-white rounded hover:bg-green-600"
          >
            Add Team Member
          </button>
        </div>

        <button
          onClick={handleJobSubmission}
          className="mt-6 px-4 py-2 bg-non-photo-blue text-white rounded hover:bg-blue-600 w-full"
        >
          Add Manager
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

export default ManagerForm;
