"use client";
import { useState } from "react";
import { webApp } from "@/utils/api";
import { Criteria, SubCriteria } from "@/types/rules";

const RuleForm: React.FC = () => {
  const [criteria, setCriteria] = useState<Criteria>({
    topic: "",
    description: "",
    businessRules: [],
    subCriteria: [],
  });

  const [status, setStatus] = useState<string>("");

  const handleJobSubmission = async () => {
    try {
      setStatus("Sending request...");

      const response = await webApp.post("/create-rule", criteria);

      if (response.status === 200 || response.status === 201) {
        setStatus("Rule created successfully!");
      } else {
        setStatus("Error occurred while creating the criteria.");
      }
    } catch (error) {
      console.error("Error initiating the job:", error);
      setStatus("Error initiating the job.");
    }
  };

  const handleSubCriteriaChange = (index: number, field: keyof SubCriteria, value: any) => {
    const updatedSubCriteria = criteria.subCriteria.map((subCriteria, i) => {
      if (i === index) {
        return { ...subCriteria, [field]: value };
      }
      return subCriteria;
    });
    setCriteria({ ...criteria, subCriteria: updatedSubCriteria });
  };

  const addSubCriteria = () => {
    setCriteria({
      ...criteria,
      subCriteria: [
        ...criteria.subCriteria,
        { topic: "", description: "" },
      ],
    });
  };

  const removeSubCriteria = (index: number) => {
    setCriteria({
      ...criteria,
      subCriteria: criteria.subCriteria.filter((_, i) => i !== index),
    });
  };

  return (
    <div className="flex flex-col items-center justify-start w-screen h-screen bg-gray-100 dark:bg-gray-900 p-6">
      <div className="w-full max-w-full bg-white shadow-default dark:bg-boxdark p-6 rounded-lg">
        <h3 className="font-medium text-black dark:text-white mb-6 text-center">
          Add Rule
        </h3>
        <div className="flex flex-col gap-4 mb-6">
          <div>
            <label className="font-large text-black dark:text-white mb-2 block">
              Criteria Topic
            </label>
            <input
              type="text"
              value={criteria.topic}
              onChange={(e) => setCriteria({ ...criteria, topic: e.target.value })}
              className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
              placeholder="Type the criteria topic"
            />
          </div>
          <div>
            <label className="text-sm font-medium text-black dark:text-white mb-2 block">
              Criteria Description
            </label>
            <input
              type="text"
              value={criteria.description}
              onChange={(e) => setCriteria({ ...criteria, description: e.target.value })}
              className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
              placeholder="Type the criteria description"
            />
          </div>
          <div>
            <label className="text-sm font-medium text-black dark:text-white mb-2 block">
              Business Rules (Comma Separated)
            </label>
            <input
              type="text"
              value={criteria.businessRules.join(", ")}
              onChange={(e) => setCriteria({ ...criteria, businessRules: e.target.value.split(",").map(rule => rule.trim()) })}
              className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
              placeholder="Type business rules, separated by commas"
            />
          </div>
        </div>

        <div className="w-full">
          <h4 className="text-lg font-medium text-black dark:text-white mb-2">Sub-Criteria</h4>
          <div className="grid grid-cols-3 gap-4 text-sm font-semibold text-gray-600 dark:text-gray-300 mb-2">
            <span>Topic</span>
            <span>Description</span>
            <span>Actions</span>
          </div>
          {criteria.subCriteria.map((subCriteria, index) => (
            <div key={index} className="grid grid-cols-3 gap-4 items-center mb-2">
              <input
                type="text"
                value={subCriteria.topic}
                onChange={(e) => handleSubCriteriaChange(index, "topic", e.target.value)}
                className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
                placeholder="Sub-Criteria Topic"
              />
              <input
                type="text"
                value={subCriteria.description}
                onChange={(e) => handleSubCriteriaChange(index, "description", e.target.value)}
                className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
                placeholder="Sub-Criteria Description"
              />
              <button
                type="button"
                onClick={() => removeSubCriteria(index)}
                className="text-red-500 hover:text-red-700"
              >
                Remove
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={addSubCriteria}
            className="mt-2 px-4 py-2 bg-kelly-green text-white rounded hover:bg-green-600"
          >
            Add Sub-Criteria
          </button>
        </div>

        <button
          onClick={handleJobSubmission}
          className="mt-6 px-4 py-2 bg-non-photo-blue text-white rounded hover:bg-blue-600 w-full"
        >
          Add Criteria
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

export default RuleForm;
