import type { CaseStep } from "@/types/steps";
import { avatarEngine } from "@/utils/api";
import { useState } from "react";

interface StepsFormProps {
  steps: CaseStep[];
  onChange: (steps: CaseStep[]) => void;
  readOnly?: boolean;
  caseId?: string;
}

type StepDraft = CaseStep & {
  draftId: string;
};

const createDraftId = (prefix: string) => {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }

  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2)}`;
};

const toStepDraft = (step: CaseStep): StepDraft => ({
  ...step,
  draftId: createDraftId("step"),
});

const toCaseSteps = (steps: StepDraft[]): CaseStep[] => steps.map(({ draftId, ...step }) => step);

const StepsForm: React.FC<StepsFormProps> = ({ steps, onChange, readOnly, caseId }) => {
  const [localSteps, setLocalSteps] = useState<StepDraft[]>(() => steps.map(toStepDraft));
  const [status, setStatus] = useState<string>("");

  const handleStepChange = async <K extends keyof CaseStep>(
    draftId: string,
    field: K,
    value: CaseStep[K],
  ) => {
    const updated = localSteps.map((step) =>
      step.draftId === draftId ? { ...step, [field]: value } : step,
    );
    const serializedSteps = toCaseSteps(updated);
    setLocalSteps(updated);
    onChange(serializedSteps);
    // Inline PATCH on blur/enter
    if (caseId) {
      try {
        setStatus("Saving...");
        await avatarEngine.patch(`/cases/${caseId}/steps`, serializedSteps);
        setStatus("Saved");
      } catch {
        setStatus("Error saving");
      }
    }
  };

  const addStep = () => {
    const newStep = toStepDraft({
      order: localSteps.length + 1,
      name: "",
      objectives: [],
      files: [],
    });
    const updated = [...localSteps, newStep];
    setLocalSteps(updated);
    onChange(toCaseSteps(updated));
  };

  const removeStep = (draftId: string) => {
    const updated = localSteps.filter((step) => step.draftId !== draftId);
    setLocalSteps(updated);
    onChange(toCaseSteps(updated));
  };

  return (
    <div className="flex flex-col items-center justify-start w-full max-w-2xl mx-auto bg-gray-100 dark:bg-gray-900 p-6">
      <div className="w-full bg-white shadow-default dark:bg-boxdark p-6 rounded-lg">
        {status && <div className="text-xs text-gray-500">{status}</div>}
        {localSteps.map((step) => (
          <div key={step.draftId} className="flex gap-2 items-center">
            <input
              type="number"
              value={step.order}
              onBlur={(e) =>
                handleStepChange(step.draftId, "order", Number.parseInt(e.target.value))
              }
              onChange={(e) =>
                handleStepChange(step.draftId, "order", Number.parseInt(e.target.value))
              }
              className="input w-16"
              placeholder="Order"
              disabled={readOnly}
            />
            <input
              type="text"
              value={step.name}
              onBlur={(e) => handleStepChange(step.draftId, "name", e.target.value)}
              onChange={(e) => handleStepChange(step.draftId, "name", e.target.value)}
              className="input"
              placeholder="Name"
              disabled={readOnly}
            />
            <input
              type="text"
              value={step.objectives.join(", ")}
              onBlur={(e) =>
                handleStepChange(
                  step.draftId,
                  "objectives",
                  e.target.value.split(",").map((obj: string) => obj.trim()),
                )
              }
              onChange={(e) =>
                handleStepChange(
                  step.draftId,
                  "objectives",
                  e.target.value.split(",").map((obj: string) => obj.trim()),
                )
              }
              className="input"
              placeholder="Objectives (comma-separated)"
              disabled={readOnly}
            />
            <button
              type="button"
              onClick={() => removeStep(step.draftId)}
              disabled={readOnly}
              className="text-red-500"
            >
              Remove
            </button>
          </div>
        ))}
        {!readOnly && (
          <button
            type="button"
            onClick={addStep}
            className="bg-green-600 text-white px-2 py-1 rounded"
          >
            Add Step
          </button>
        )}
      </div>
    </div>
  );
};

export default StepsForm;
