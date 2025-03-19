"use client";
import { useState } from "react";
import { webApp } from "@/utils/api";
import { Theme } from "@/types/theme";

const ThemeForm: React.FC = () => {
  const [theme, setTheme] = useState<Theme>({
    name: "",
    objective: "",
    description: "",
    criteria: [],
  });

  const [status, setStatus] = useState<string>("");

  const handleJobSubmission = async () => {
    try {
      setStatus("Sending request...");

      const response = await webApp.post("/create-theme", theme);

      if (response.status === 200 || response.status === 201) {
        setStatus("Theme created successfully!");
      } else {
        setStatus("Error occurred while creating the theme.");
      }
    } catch (error) {
      console.error("Error initiating the theme creation:", error);
      setStatus("Error initiating the theme creation.");
    }
  };

  const handleCriteriaChange = (index: number, value: string) => {
    const updatedCriteria = theme.criteria.map((criterion, i) =>
      i === index ? value : criterion
    );
    setTheme({ ...theme, criteria: updatedCriteria });
  };

  const addCriterion = () => {
    setTheme({
      ...theme,
      criteria: [...theme.criteria, ""],
    });
  };

  const removeCriterion = (index: number) => {
    setTheme({
      ...theme,
      criteria: theme.criteria.filter((_, i) => i !== index),
    });
  };

  return (
    <div className="flex flex-col items-center justify-start w-screen h-screen bg-gray-100 dark:bg-gray-900 p-6">
      <div className="w-full max-w-full bg-white shadow-default dark:bg-boxdark p-6 rounded-lg">
        <h3 className="font-medium text-black dark:text-white mb-6 text-center">
          Add Theme
        </h3>
        <div className="flex flex-col gap-4 mb-6">
          <div>
            <label className="font-large text-black dark:text-white mb-2 block">
              Theme Name
            </label>
            <input
              type="text"
              value={theme.name}
              onChange={(e) => setTheme({ ...theme, name: e.target.value })}
              className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
              placeholder="Type the theme name"
            />
          </div>
          <div>
            <label className="text-sm font-medium text-black dark:text-white mb-2 block">
              Theme Objective
            </label>
            <input
              type="text"
              value={theme.objective}
              onChange={(e) =>
                setTheme({ ...theme, objective: e.target.value })
              }
              className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
              placeholder="Type the theme objective"
            />
          </div>
          <div>
            <label className="text-sm font-medium text-black dark:text-white mb-2 block">
              Theme Description
            </label>
            <textarea
              value={theme.description}
              onChange={(e) =>
                setTheme({ ...theme, description: e.target.value })
              }
              className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
              placeholder="Type the theme description"
            />
          </div>
        </div>

        {/* Criteria Section */}
        <div className="w-full">
          <h4 className="text-lg font-medium text-black dark:text-white mb-2">
            Criteria
          </h4>
          {theme.criteria.map((criterion, index) => (
            <div
              key={index}
              className="flex items-center gap-4 mb-2 w-full"
            >
              <input
                type="text"
                value={criterion}
                onChange={(e) => handleCriteriaChange(index, e.target.value)}
                className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
                placeholder="Enter criterion"
              />
              <button
                type="button"
                onClick={() => removeCriterion(index)}
                className="text-red-500 hover:text-red-700"
              >
                Remove
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={addCriterion}
            className="mt-2 px-4 py-2 bg-kelly-green text-white rounded hover:bg-green-600"
          >
            Add Criterion
          </button>
        </div>

        <button
          onClick={handleJobSubmission}
          className="mt-6 px-4 py-2 bg-non-photo-blue text-white rounded hover:bg-blue-600 w-full"
        >
          Add Theme
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

export default ThemeForm;
