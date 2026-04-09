"use client";
import type { Theme } from "@/types/theme";
import { configurationApi } from "@/utils/api";
import { useState } from "react";

type CriterionDraft = {
  id: string;
  value: string;
};

type ThemeDraft = Omit<Theme, "criteria"> & {
  criteria: CriterionDraft[];
};

const createClientId = (prefix: string) => {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }

  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2)}`;
};

const DEFAULT_THEME: ThemeDraft = {
  name: "",
  objective: "",
  description: "",
  criteria: [],
};

const toThemePayload = (theme: ThemeDraft): Theme => ({
  name: theme.name,
  objective: theme.objective,
  description: theme.description,
  criteria: theme.criteria.map((criterion) => criterion.value),
});

const ThemeForm: React.FC = () => {
  const [theme, setTheme] = useState<ThemeDraft>(DEFAULT_THEME);

  const [status, setStatus] = useState<string>("");

  const handleJobSubmission = async () => {
    try {
      setStatus("Sending request...");

      const payload = {
        id: createClientId("theme"),
        ...toThemePayload(theme),
      };
      const response = await configurationApi.post("/themes", payload);

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

  const handleCriteriaChange = (criterionId: string, value: string) => {
    setTheme((currentTheme) => ({
      ...currentTheme,
      criteria: currentTheme.criteria.map((criterion) =>
        criterion.id === criterionId ? { ...criterion, value } : criterion,
      ),
    }));
  };

  const addCriterion = () => {
    setTheme((currentTheme) => ({
      ...currentTheme,
      criteria: [...currentTheme.criteria, { id: createClientId("criterion"), value: "" }],
    }));
  };

  const removeCriterion = (criterionId: string) => {
    setTheme((currentTheme) => ({
      ...currentTheme,
      criteria: currentTheme.criteria.filter((criterion) => criterion.id !== criterionId),
    }));
  };

  return (
    <div className="flex flex-col items-center justify-start w-screen h-screen bg-gray-100 dark:bg-gray-900 p-6">
      <div className="w-full max-w-full bg-white shadow-default dark:bg-boxdark p-6 rounded-lg">
        <h3 className="font-medium text-black dark:text-white mb-6 text-center">Add Theme</h3>
        <div className="flex flex-col gap-4 mb-6">
          <div>
            <label
              htmlFor="theme-name"
              className="font-large text-black dark:text-white mb-2 block"
            >
              Theme Name
            </label>
            <input
              id="theme-name"
              type="text"
              value={theme.name}
              onChange={(e) => setTheme({ ...theme, name: e.target.value })}
              className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
              placeholder="Type the theme name"
            />
          </div>
          <div>
            <label
              htmlFor="theme-objective"
              className="text-sm font-medium text-black dark:text-white mb-2 block"
            >
              Theme Objective
            </label>
            <input
              id="theme-objective"
              type="text"
              value={theme.objective}
              onChange={(e) => setTheme({ ...theme, objective: e.target.value })}
              className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
              placeholder="Type the theme objective"
            />
          </div>
          <div>
            <label
              htmlFor="theme-description"
              className="text-sm font-medium text-black dark:text-white mb-2 block"
            >
              Theme Description
            </label>
            <textarea
              id="theme-description"
              value={theme.description}
              onChange={(e) => setTheme({ ...theme, description: e.target.value })}
              className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
              placeholder="Type the theme description"
            />
          </div>
        </div>

        {/* Criteria Section */}
        <div className="w-full">
          <h4 className="text-lg font-medium text-black dark:text-white mb-2">Criteria</h4>
          {theme.criteria.map((criterion, index) => (
            <div key={criterion.id} className="flex items-center gap-4 mb-2 w-full">
              <input
                aria-label={`Criterion ${index + 1}`}
                type="text"
                value={criterion.value}
                onChange={(e) => handleCriteriaChange(criterion.id, e.target.value)}
                className="w-full rounded-lg border-[1.5px] border-stroke bg-transparent outline-none transition focus:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
                placeholder="Enter criterion"
              />
              <button
                type="button"
                onClick={() => removeCriterion(criterion.id)}
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
          type="button"
          onClick={handleJobSubmission}
          className="mt-6 px-4 py-2 bg-non-photo-blue text-white rounded hover:bg-blue-600 w-full"
        >
          Add Theme
        </button>
        {status && (
          <p className="mt-2 text-center text-sm text-gray-700 dark:text-gray-300">{status}</p>
        )}
      </div>
    </div>
  );
};

export default ThemeForm;
