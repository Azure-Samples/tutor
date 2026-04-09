import type { Case } from "@/types/cases";
import type { Profile } from "@/types/profile";
import type { CaseStep } from "@/types/steps";
import { avatarEngine } from "@/utils/api";
import { useState } from "react";
import { FaInfoCircle, FaListOl, FaPen, FaPlus, FaTrash, FaUser } from "react-icons/fa";

type CaseStepDraft = CaseStep & {
  draftId: string;
};

type CaseDraft = Omit<Case, "steps" | "profile"> & {
  profile: Profile;
  steps: CaseStepDraft[];
};

const DEFAULT_PROFILE: Profile = {
  name: "",
  gender: "",
  age: undefined,
  role: "",
  level: "",
  details: "",
};

const createDraftId = (prefix: string) => {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }

  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2)}`;
};

const toCaseStepDraft = (step: CaseStep): CaseStepDraft => ({
  ...step,
  draftId: createDraftId("step"),
});

const toCaseDraft = (caseData?: Case): CaseDraft => ({
  id: caseData?.id,
  name: caseData?.name ?? "",
  role: caseData?.role ?? "",
  steps: (caseData?.steps ?? []).map(toCaseStepDraft),
  profile: { ...DEFAULT_PROFILE, ...(caseData?.profile ?? {}) },
  history: caseData?.history,
});

const toCasePayload = (draft: CaseDraft): Case => ({
  id: draft.id,
  name: draft.name,
  role: draft.role,
  steps: draft.steps.map(({ draftId, ...step }) => step),
  profile: draft.profile,
  history: draft.history,
});

const createObjectiveIds = (steps: CaseStepDraft[]) =>
  Object.fromEntries(
    steps.map((step) => [step.draftId, step.objectives.map(() => createDraftId("objective"))]),
  );

const CaseForm: React.FC<{ caseData?: Case; onSuccess?: () => void }> = ({
  caseData,
  onSuccess,
}) => {
  const initialCase = toCaseDraft(caseData);
  const [useCase, setCase] = useState<CaseDraft>(initialCase);
  const [status, setStatus] = useState<string>("");
  const [newObjectives, setNewObjectives] = useState<Record<string, string>>({});
  const [objectiveIdsByStep, setObjectiveIdsByStep] = useState<Record<string, string[]>>(() =>
    createObjectiveIds(initialCase.steps),
  );
  const isEdit = !!caseData?.id;

  const handleJobSubmission = async () => {
    try {
      setStatus("Sending request...");
      const payload = toCasePayload(useCase);

      if (isEdit && !payload.id) {
        throw new Error("Missing case id for update.");
      }

      const response = isEdit
        ? await avatarEngine.put(`/cases/${payload.id}`, payload)
        : await avatarEngine.post("/create-case", payload);

      if (response.status === 200 || response.status === 201) {
        setStatus(isEdit ? "Case updated successfully!" : "Case created successfully!");
        if (onSuccess) onSuccess();
      } else {
        setStatus("Error occurred while saving the case.");
      }
    } catch (error) {
      console.error("Error saving the case:", error);
      setStatus("Error saving the case.");
    }
  };

  const handleStepChange = <K extends keyof CaseStep>(
    draftId: string,
    field: K,
    value: CaseStep[K],
  ) => {
    setCase((currentCase) => ({
      ...currentCase,
      steps: currentCase.steps.map((step) =>
        step.draftId === draftId ? { ...step, [field]: value } : step,
      ),
    }));
  };

  const handleProfileChange = (field: keyof Profile, value: Profile[keyof Profile]) => {
    setCase((currentCase) => ({
      ...currentCase,
      profile: {
        ...currentCase.profile,
        [field]: value,
      },
    }));
  };

  const addStep = () => {
    const newStep = toCaseStepDraft({
      order: useCase.steps.length + 1,
      name: "",
      objectives: [],
      files: [],
    });

    setCase((currentCase) => ({
      ...currentCase,
      steps: [...currentCase.steps, newStep],
    }));
    setObjectiveIdsByStep((currentIds) => ({ ...currentIds, [newStep.draftId]: [] }));
  };

  const removeStep = (draftId: string) => {
    setCase((currentCase) => ({
      ...currentCase,
      steps: currentCase.steps.filter((step) => step.draftId !== draftId),
    }));
    setObjectiveIdsByStep((currentIds) => {
      const updatedIds = { ...currentIds };
      delete updatedIds[draftId];
      return updatedIds;
    });
    setNewObjectives((currentObjectives) => {
      const updatedObjectives = { ...currentObjectives };
      delete updatedObjectives[draftId];
      return updatedObjectives;
    });
  };

  const removeObjective = (stepDraftId: string, objectiveIndex: number) => {
    setCase((currentCase) => ({
      ...currentCase,
      steps: currentCase.steps.map((step) =>
        step.draftId === stepDraftId
          ? {
              ...step,
              objectives: step.objectives.filter((_, index) => index !== objectiveIndex),
            }
          : step,
      ),
    }));
    setObjectiveIdsByStep((currentIds) => ({
      ...currentIds,
      [stepDraftId]: (currentIds[stepDraftId] ?? []).filter((_, index) => index !== objectiveIndex),
    }));
  };

  const addObjective = (stepDraftId: string) => {
    const objectiveText = newObjectives[stepDraftId]?.trim();
    if (!objectiveText) {
      return;
    }

    setCase((currentCase) => ({
      ...currentCase,
      steps: currentCase.steps.map((step) =>
        step.draftId === stepDraftId
          ? { ...step, objectives: [...step.objectives, objectiveText] }
          : step,
      ),
    }));
    setObjectiveIdsByStep((currentIds) => ({
      ...currentIds,
      [stepDraftId]: [...(currentIds[stepDraftId] ?? []), createDraftId("objective")],
    }));
    setNewObjectives((currentObjectives) => ({ ...currentObjectives, [stepDraftId]: "" }));
  };

  return (
    <form className="flex flex-col items-center justify-start w-full mx-auto p-0">
      <div className="w-full flex flex-col gap-4 mb-6">
        <label htmlFor="case-name" className="flex items-center gap-2 text-cyan-700 font-bold">
          <FaPen /> Case Name
        </label>
        <input
          id="case-name"
          type="text"
          value={useCase.name}
          onChange={(e) => setCase({ ...useCase, name: e.target.value })}
          className="w-full rounded-2xl border-2 border-cyan-200 focus:border-green-400 focus:ring-2 focus:ring-green-200 px-4 py-3 text-lg transition-all duration-200 bg-cyan-50 dark:bg-cyan-900 placeholder:text-cyan-400 focus:bg-white dark:focus:bg-boxdark"
          placeholder="Case name, used to identify the case"
        />
      </div>
      <div className="w-full flex flex-col gap-4 mb-6">
        <label htmlFor="case-role" className="flex items-center gap-2 text-green-700 font-bold">
          <FaUser /> Case Role
        </label>
        <input
          id="case-role"
          type="text"
          value={useCase.role}
          onChange={(e) => setCase({ ...useCase, role: e.target.value })}
          className="w-full rounded-2xl border-2 border-green-200 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-200 px-4 py-3 text-lg transition-all duration-200 bg-green-50 dark:bg-green-900 placeholder:text-green-400 focus:bg-white dark:focus:bg-boxdark"
          placeholder="Case Role, used to define the type of case the Avatar will interpret"
        />
      </div>
      <div className="w-full flex flex-col gap-4 mb-6">
        <p className="flex items-center gap-2 text-blue-700 font-bold">
          <FaInfoCircle /> Profile
        </p>
        <div className="flex flex-col gap-2">
          <div className="flex gap-2">
            <input
              type="text"
              value={useCase.profile.name}
              onChange={(e) => handleProfileChange("name", e.target.value)}
              className="w-full rounded-2xl border-2 border-blue-200 focus:border-yellow-400 focus:ring-2 focus:ring-yellow-200 px-4 py-3 text-lg transition-all duration-200 bg-blue-50 dark:bg-blue-900 placeholder:text-blue-400 focus:bg-white dark:focus:bg-boxdark"
              placeholder="Avatar Name"
            />
            <input
              type="text"
              value={useCase.profile.gender || ""}
              onChange={(e) => handleProfileChange("gender", e.target.value)}
              className="w-full rounded-2xl border-2 border-pink-200 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-200 px-4 py-3 text-lg transition-all duration-200 bg-pink-50 dark:bg-pink-900 placeholder:text-pink-400 focus:bg-white dark:focus:bg-boxdark"
              placeholder="Gender"
            />
            <input
              type="number"
              value={useCase.profile.age || ""}
              onChange={(e) => handleProfileChange("age", Number.parseInt(e.target.value))}
              className="w-full rounded-2xl border-2 border-yellow-200 focus:border-green-400 focus:ring-2 focus:ring-green-200 px-4 py-3 text-lg transition-all duration-200 bg-yellow-50 dark:bg-yellow-900 placeholder:text-yellow-400 focus:bg-white dark:focus:bg-boxdark"
              placeholder="Age"
            />
          </div>
          <input
            type="text"
            value={useCase.profile.role}
            onChange={(e) => handleProfileChange("role", e.target.value)}
            className="w-full rounded-2xl border-2 border-green-200 focus:border-blue-400 focus:ring-2 focus:ring-blue-200 px-4 py-3 text-lg transition-all duration-200 bg-green-50 dark:bg-green-900 placeholder:text-green-400 focus:bg-white dark:focus:bg-boxdark"
            placeholder="Avatar Role"
          />
          <input
            type="text"
            value={useCase.profile.level || ""}
            onChange={(e) => handleProfileChange("level", e.target.value)}
            className="w-full rounded-2xl border-2 border-cyan-200 focus:border-yellow-400 focus:ring-2 focus:ring-yellow-200 px-4 py-3 text-lg transition-all duration-200 bg-cyan-50 dark:bg-cyan-900 placeholder:text-cyan-400 focus:bg-white dark:focus:bg-boxdark"
            placeholder="Level"
          />
          <textarea
            value={useCase.profile.details}
            onChange={(e) => handleProfileChange("details", e.target.value)}
            className="w-full rounded-2xl border-2 border-gray-200 focus:border-blue-400 focus:ring-2 focus:ring-blue-200 px-4 py-3 text-lg transition-all duration-200 bg-gray-50 dark:bg-gray-900 placeholder:text-gray-400 focus:bg-white dark:focus:bg-boxdark resize-y min-h-[48px] max-h-[320px]"
            placeholder="Any other important detail"
            rows={2}
          />
        </div>
      </div>
      <div className="w-full mb-6">
        <p className="flex items-center gap-2 text-yellow-700 font-bold mb-2">
          <FaListOl /> Case Steps
        </p>
        {useCase.steps.map((step, index) => (
          <div
            key={step.draftId}
            className="mb-4 rounded-2xl shadow bg-yellow-50 dark:bg-yellow-900 border border-yellow-200 dark:border-yellow-800"
          >
            <div className="flex items-center justify-between px-4 py-2 bg-yellow-100 dark:bg-yellow-800 rounded-t-2xl">
              <span className="font-bold text-yellow-800 dark:text-yellow-200 flex items-center gap-2">
                <FaListOl /> Step {index + 1}: {step.name || "(No name)"}
              </span>
              <button
                type="button"
                onClick={() => removeStep(step.draftId)}
                className="text-red-500 hover:text-red-700 flex items-center gap-1 px-2 py-1 rounded-full bg-red-100 dark:bg-red-900"
                title="Remove Step"
              >
                <FaTrash />
              </button>
            </div>
            <div className="flex flex-col gap-2 px-4 py-3">
              <div className="flex flex-row gap-4 items-center">
                <label
                  htmlFor={`case-step-order-${step.draftId}`}
                  className="w-24 font-semibold text-yellow-700"
                >
                  Number
                </label>
                <input
                  id={`case-step-order-${step.draftId}`}
                  type="number"
                  value={step.order}
                  onChange={(e) =>
                    handleStepChange(step.draftId, "order", Number.parseInt(e.target.value))
                  }
                  className="w-24 rounded-2xl border-2 border-yellow-200 focus:border-green-400 focus:ring-2 focus:ring-green-200 px-3 py-2 text-lg transition-all duration-200 bg-yellow-50 dark:bg-yellow-900 placeholder:text-yellow-400 focus:bg-white dark:focus:bg-boxdark"
                  placeholder="Order"
                />
              </div>
              <div className="flex flex-row gap-4 items-center">
                <label
                  htmlFor={`case-step-name-${step.draftId}`}
                  className="w-24 font-semibold text-blue-700"
                >
                  Name
                </label>
                <input
                  id={`case-step-name-${step.draftId}`}
                  type="text"
                  value={step.name}
                  onChange={(e) => handleStepChange(step.draftId, "name", e.target.value)}
                  className="flex-1 rounded-2xl border-2 border-blue-200 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-200 px-3 py-2 text-lg transition-all duration-200 bg-blue-50 dark:bg-blue-900 placeholder:text-blue-400 focus:bg-white dark:focus:bg-boxdark"
                  placeholder="Specialist Name"
                />
              </div>
              <div className="flex flex-col gap-2">
                <p className="font-semibold text-green-700">Objectives</p>
                <div className="flex flex-wrap gap-2 mb-2">
                  {step.objectives.map((obj, objIdx) => (
                    <span
                      key={objectiveIdsByStep[step.draftId]?.[objIdx]}
                      className="flex items-center gap-1 bg-green-200 dark:bg-green-800 text-green-900 dark:text-green-100 px-3 py-1 rounded-full"
                    >
                      {obj}
                      <button
                        type="button"
                        className="ml-1 text-red-500 hover:text-red-700"
                        onClick={() => removeObjective(step.draftId, objIdx)}
                        title="Remove objective"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={newObjectives[step.draftId] || ""}
                    onChange={(e) => {
                      setNewObjectives((currentObjectives) => ({
                        ...currentObjectives,
                        [step.draftId]: e.target.value,
                      }));
                    }}
                    className="flex-1 rounded-2xl border-2 border-green-200 focus:border-yellow-400 focus:ring-2 focus:ring-yellow-200 px-3 py-2 text-lg transition-all duration-200 bg-green-50 dark:bg-green-900 placeholder:text-green-400 focus:bg-white dark:focus:bg-boxdark"
                    placeholder="Add objective"
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && (newObjectives[step.draftId] || "").trim()) {
                        e.preventDefault();
                        addObjective(step.draftId);
                      }
                    }}
                  />
                  <button
                    type="button"
                    className="px-4 py-2 rounded-2xl bg-green-400 text-white font-bold hover:bg-green-500 transition-all"
                    onClick={() => addObjective(step.draftId)}
                  >
                    Add
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
        <button
          type="button"
          onClick={addStep}
          className="mt-2 px-4 py-2 bg-kelly-green text-white rounded-2xl hover:bg-green-600 flex items-center gap-2"
        >
          <FaPlus /> Add Step
        </button>
      </div>
      <button
        type="button"
        onClick={handleJobSubmission}
        className="mt-6 px-4 py-3 bg-gradient-to-br from-green-400 to-cyan-400 hover:from-cyan-400 hover:to-yellow-300 text-white font-bold rounded-2xl shadow-lg w-full flex items-center justify-center gap-2 text-lg transition-all duration-200"
      >
        {isEdit ? <FaPen /> : <FaPlus />} {isEdit ? "Update Case" : "Add Case"}
      </button>
      {status && (
        <p className="mt-2 text-center text-sm text-gray-700 dark:text-gray-300">{status}</p>
      )}
    </form>
  );
};

export default CaseForm;
