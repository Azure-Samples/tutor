import { CaseStep } from "@/types/steps";
import { useState } from "react";
import { configurationApi } from "@/utils/api";

interface StepsFormProps {
  steps: CaseStep[];
  onChange: (steps: CaseStep[]) => void;
  readOnly?: boolean;
  caseId?: string;
}

const StepsForm: React.FC<StepsFormProps> = ({ steps, onChange, readOnly, caseId }) => {
  const [localSteps, setLocalSteps] = useState<CaseStep[]>(steps);
  const [status, setStatus] = useState<string>("");

  const handleStepChange = async (index: number, field: keyof CaseStep, value: any) => {
    const updated = localSteps.map((step, i) =>
      i === index ? { ...step, [field]: value } : step
    );
    setLocalSteps(updated);
    onChange(updated);
    // Inline PATCH on blur/enter
    if (caseId) {
      try {
        setStatus("Saving...");
        await configurationApi.patch(`/cases/${caseId}/steps`, updated);
        setStatus("Saved");
      } catch (e) {
        setStatus("Error saving");
      }
    }
  };

  const addStep = () => {
    const newStep: CaseStep = { order: localSteps.length + 1, name: "", objectives: [], files: [] };
    const updated = [...localSteps, newStep];
    setLocalSteps(updated);
    onChange(updated);
  };

  const removeStep = (index: number) => {
    const updated = localSteps.filter((_, i) => i !== index);
    setLocalSteps(updated);
    onChange(updated);
  };

  return (
    <div className="flex flex-col items-center justify-start w-full max-w-2xl mx-auto bg-gray-100 dark:bg-gray-900 p-6">
      <div className="w-full bg-white shadow-default dark:bg-boxdark p-6 rounded-lg">
        {status && <div className="text-xs text-gray-500">{status}</div>}
        {localSteps.map((step, idx) => (
          <div key={idx} className="flex gap-2 items-center">
            <input
              type="number"
              value={step.order}
              onBlur={e => handleStepChange(idx, "order", parseInt(e.target.value))}
              onChange={e => handleStepChange(idx, "order", parseInt(e.target.value))}
              className="input w-16"
              placeholder="Order"
              disabled={readOnly}
            />
            <input
              type="text"
              value={step.name}
              onBlur={e => handleStepChange(idx, "name", e.target.value)}
              onChange={e => handleStepChange(idx, "name", e.target.value)}
              className="input"
              placeholder="Name"
              disabled={readOnly}
            />
            <input
              type="text"
              value={step.objectives.join(", ")}
              onBlur={e => handleStepChange(idx, "objectives", e.target.value.split(",").map((obj: string) => obj.trim()))}
              onChange={e => handleStepChange(idx, "objectives", e.target.value.split(",").map((obj: string) => obj.trim()))}
              className="input"
              placeholder="Objectives (comma-separated)"
              disabled={readOnly}
            />
            <button type="button" onClick={() => removeStep(idx)} disabled={readOnly} className="text-red-500">Remove</button>
          </div>
        ))}
        {!readOnly && (
          <button type="button" onClick={addStep} className="bg-green-600 text-white px-2 py-1 rounded">Add Step</button>
        )}
      </div>
    </div>
  );
};

export default StepsForm;
