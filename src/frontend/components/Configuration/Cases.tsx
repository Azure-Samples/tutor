"use client";
import { useState } from "react";
import { webApp } from "@/utils/api";
import { Case } from "@/types/cases";
import { CaseStep } from "@/types/steps";
import { Profile } from "@/types/profile";


const CaseForm: React.FC = () => {
  const [useCase, setCase] = useState<Case>({
    name: "",
    role: "",
    steps: [],
    profile: {
      name: "",
      gender: "",
      age: undefined,
      role: "",
      level: "",
      details: "",
    },
  });

  const [status, setStatus] = useState<string>("");

  const handleJobSubmission = async () => {
    try {
      setStatus("Sending request...");

      const response = await webApp.post("/create-case", useCase);

      if (response.status === 200 || response.status === 201) {
        setStatus("Case created successfully!");
      } else {
        setStatus("Error occurred while creating the job.");
      }
    } catch (error) {
      console.error("Error initiating the job:", error);
      setStatus("Error initiating the job.");
    }
  };

  const handleStepChange = (index: number, field: keyof CaseStep, value: any) => {
    const updatedSteps = useCase.steps.map((step, i) => {
      if (i === index) {
        return { ...step, [field]: value };
      }
      return step;
    });
    setCase({ ...useCase, steps: updatedSteps });
  };

  const handleProfileChange = (field: keyof Profile, value: any) => {
    setCase({
      ...useCase,
      profile: {
        ...useCase.profile,
        [field]: value,
      } as Profile,
    });
  };

  const addStep = () => {
    setCase({
      ...useCase,
      steps: [
        ...useCase.steps,
        { order: useCase.steps.length + 1, name: "", objectives: [], files: [] },
      ],
    });
  };

  const removeStep = (index: number) => {
    setCase({
      ...useCase,
      steps: useCase.steps.filter((_, i) => i !== index),
    });
  };

  return (
    <div className="flex flex-col items-center justify-start w-screen h-screen bg-gray-100 dark:bg-gray-900 p-6">
      <div className="w-full max-w-full bg-white shadow-default dark:bg-boxdark p-6 rounded-lg">
        <h3 className="font-medium text-black dark:text-white mb-6 text-center">Add Case</h3>
        <div className="flex flex-col gap-4 mb-6">
          <div>
            <label className="font-large text-black dark:text-white mb-2 block">Case Name</label>
            <input
              type="text"
              value={useCase.name}
              onChange={(e) => setCase({ ...useCase, name: e.target.value })}
              className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
              placeholder="Case name, used to identify the case"
            />
          </div>
          <div>
            <label className="text-sm font-medium text-black dark:text-white mb-2 block">
              Case Role
            </label>
            <input
              type="text"
              value={useCase.role}
              onChange={(e) => setCase({ ...useCase, role: e.target.value })}
              className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
              placeholder="Case Role, used to define the type of case the Avatar will interpret"
            />
          </div>
        </div>

        {/* Profile Section */}
        <div className="flex flex-col gap-4 mb-6">
          <h4 className="text-lg font-medium text-black dark:text-white mb-2">Profile</h4>
          <input
            type="text"
            value={useCase.profile?.name || ""}
            onChange={(e) => handleProfileChange("name", e.target.value)}
            className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
            placeholder="Avatar Name"
          />
          <input
            type="text"
            value={useCase.profile?.gender || ""}
            onChange={(e) => handleProfileChange("gender", e.target.value)}
            className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
            placeholder="Avatar Gender. Must be 'masculino' or 'feminino'"
          />
          <input
            type="number"
            value={useCase.profile?.age || ""}
            onChange={(e) => handleProfileChange("age", parseInt(e.target.value))}
            className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
            placeholder="Age"
          />
          <input
            type="text"
            value={useCase.profile?.role || ""}
            onChange={(e) => handleProfileChange("role", e.target.value)}
            className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
            placeholder="Avatar Role. Used to define the Avatar's role in the case"
          />
          <input
            type="text"
            value={useCase.profile?.level || ""}
            onChange={(e) => handleProfileChange("level", e.target.value)}
            className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
            placeholder="The dificulty level of the avatar"
          />
          <textarea
            value={useCase.profile?.details || ""}
            onChange={(e) => handleProfileChange("details", e.target.value)}
            className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
            placeholder="Any other important detail"
          ></textarea>
        </div>

        <div className="w-full">
          <h4 className="text-lg font-medium text-black dark:text-white mb-2">Case Steps</h4>
          <div className="grid grid-cols-4 gap-4 text-sm font-semibold text-gray-600 dark:text-gray-300 mb-2">
            <span>Order</span>
            <span>Name</span>
            <span>Objectives</span>
            <span>Actions</span>
          </div>
          {useCase.steps.map((step, index) => (
            <div key={index} className="grid grid-cols-4 gap-4 items-center mb-2">
              <input
                type="number"
                value={step.order}
                onChange={(e) => handleStepChange(index, "order", parseInt(e.target.value))}
                className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
                placeholder="Order"
              />
              <input
                type="text"
                value={step.name}
                onChange={(e) => handleStepChange(index, "name", e.target.value)}
                className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
                placeholder="Specialist Name"
              />
              <input
                type="text"
                value={step.objectives.join(", ")}
                onChange={(e) =>
                  handleStepChange(index, "objectives", e.target.value.split(",").map((obj) => obj.trim()))
                }
                className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
                placeholder="Objectives (comma-separated)"
              />
              <button
                type="button"
                onClick={() => removeStep(index)}
                className="text-red-500 hover:text-red-700"
              >
                Remove
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={addStep}
            className="mt-2 px-4 py-2 bg-kelly-green text-white rounded hover:bg-green-600"
          >
            Add Step
          </button>
        </div>

        <button
          onClick={handleJobSubmission}
          className="mt-6 px-4 py-2 bg-non-photo-blue text-white rounded hover:bg-blue-600 w-full"
        >
          Add Case
        </button>
        {status && (
          <p className="mt-2 text-center text-sm text-gray-700 dark:text-gray-300">{status}</p>
        )}
      </div>
    </div>
  );
};

export default CaseForm;
