import { useState } from "react";
import { avatarEngine } from "@/utils/api";
import { Case } from "@/types/cases";
import { CaseStep } from "@/types/steps";
import { Profile } from "@/types/profile";
import { FaUser, FaPen, FaListOl, FaInfoCircle, FaTransgender, FaHashtag, FaLayerGroup, FaPlus, FaTrash } from "react-icons/fa";

const CaseForm: React.FC<{ caseData?: Case; onSuccess?: () => void }> = ({ caseData, onSuccess }) => {
  const [useCase, setCase] = useState<Case>(
    caseData || {
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
    }
  );
  const [status, setStatus] = useState<string>("");
  const [newObjectives, setNewObjectives] = useState<string[]>([]);
  const isEdit = !!caseData?.id;

  const handleJobSubmission = async () => {
    try {
      setStatus("Sending request...");
      let response;
      if (isEdit) {
        response = await avatarEngine.put(`/cases/${useCase.id}`, useCase);
      } else {
        response = await avatarEngine.post("/create-case", useCase);
      }
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
    <form className="flex flex-col items-center justify-start w-full mx-auto p-0">
      <div className="w-full flex flex-col gap-4 mb-6">
        <label className="flex items-center gap-2 text-cyan-700 font-bold">
          <FaPen /> Case Name
        </label>
        <input
          type="text"
          value={useCase.name}
          onChange={(e) => setCase({ ...useCase, name: e.target.value })}
          className="w-full rounded-2xl border-2 border-cyan-200 focus:border-green-400 focus:ring-2 focus:ring-green-200 px-4 py-3 text-lg transition-all duration-200 bg-cyan-50 dark:bg-cyan-900 placeholder:text-cyan-400 focus:bg-white dark:focus:bg-boxdark"
          placeholder="Case name, used to identify the case"
        />
      </div>
      <div className="w-full flex flex-col gap-4 mb-6">
        <label className="flex items-center gap-2 text-green-700 font-bold">
          <FaUser /> Case Role
        </label>
        <input
          type="text"
          value={useCase.role}
          onChange={(e) => setCase({ ...useCase, role: e.target.value })}
          className="w-full rounded-2xl border-2 border-green-200 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-200 px-4 py-3 text-lg transition-all duration-200 bg-green-50 dark:bg-green-900 placeholder:text-green-400 focus:bg-white dark:focus:bg-boxdark"
          placeholder="Case Role, used to define the type of case the Avatar will interpret"
        />
      </div>
      <div className="w-full flex flex-col gap-4 mb-6">
        <label className="flex items-center gap-2 text-blue-700 font-bold">
          <FaInfoCircle /> Profile
        </label>
        <div className="flex flex-col gap-2">
          <div className="flex gap-2">
            <input
              type="text"
              value={useCase.profile?.name || ""}
              onChange={(e) => handleProfileChange("name", e.target.value)}
              className="w-full rounded-2xl border-2 border-blue-200 focus:border-yellow-400 focus:ring-2 focus:ring-yellow-200 px-4 py-3 text-lg transition-all duration-200 bg-blue-50 dark:bg-blue-900 placeholder:text-blue-400 focus:bg-white dark:focus:bg-boxdark"
              placeholder="Avatar Name"
            />
            <input
              type="text"
              value={useCase.profile?.gender || ""}
              onChange={(e) => handleProfileChange("gender", e.target.value)}
              className="w-full rounded-2xl border-2 border-pink-200 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-200 px-4 py-3 text-lg transition-all duration-200 bg-pink-50 dark:bg-pink-900 placeholder:text-pink-400 focus:bg-white dark:focus:bg-boxdark"
              placeholder="Gender"
            />
            <input
              type="number"
              value={useCase.profile?.age || ""}
              onChange={(e) => handleProfileChange("age", parseInt(e.target.value))}
              className="w-full rounded-2xl border-2 border-yellow-200 focus:border-green-400 focus:ring-2 focus:ring-green-200 px-4 py-3 text-lg transition-all duration-200 bg-yellow-50 dark:bg-yellow-900 placeholder:text-yellow-400 focus:bg-white dark:focus:bg-boxdark"
              placeholder="Age"
            />
          </div>
          <input
            type="text"
            value={useCase.profile?.role || ""}
            onChange={(e) => handleProfileChange("role", e.target.value)}
            className="w-full rounded-2xl border-2 border-green-200 focus:border-blue-400 focus:ring-2 focus:ring-blue-200 px-4 py-3 text-lg transition-all duration-200 bg-green-50 dark:bg-green-900 placeholder:text-green-400 focus:bg-white dark:focus:bg-boxdark"
            placeholder="Avatar Role"
          />
          <input
            type="text"
            value={useCase.profile?.level || ""}
            onChange={(e) => handleProfileChange("level", e.target.value)}
            className="w-full rounded-2xl border-2 border-cyan-200 focus:border-yellow-400 focus:ring-2 focus:ring-yellow-200 px-4 py-3 text-lg transition-all duration-200 bg-cyan-50 dark:bg-cyan-900 placeholder:text-cyan-400 focus:bg-white dark:focus:bg-boxdark"
            placeholder="Level"
          />
          <textarea
            value={useCase.profile?.details || ""}
            onChange={(e) => handleProfileChange("details", e.target.value)}
            className="w-full rounded-2xl border-2 border-gray-200 focus:border-blue-400 focus:ring-2 focus:ring-blue-200 px-4 py-3 text-lg transition-all duration-200 bg-gray-50 dark:bg-gray-900 placeholder:text-gray-400 focus:bg-white dark:focus:bg-boxdark resize-y min-h-[48px] max-h-[320px]"
            placeholder="Any other important detail"
            rows={2}
          ></textarea>
        </div>
      </div>
      <div className="w-full mb-6">
        <label className="flex items-center gap-2 text-yellow-700 font-bold mb-2">
          <FaListOl /> Case Steps
        </label>
        {useCase.steps.map((step, index) => (
          <div key={index} className="mb-4 rounded-2xl shadow bg-yellow-50 dark:bg-yellow-900 border border-yellow-200 dark:border-yellow-800">
            <div className="flex items-center justify-between px-4 py-2 bg-yellow-100 dark:bg-yellow-800 rounded-t-2xl">
              <span className="font-bold text-yellow-800 dark:text-yellow-200 flex items-center gap-2">
                <FaListOl /> Step {index + 1}: {step.name || "(No name)"}
              </span>
              <button
                type="button"
                onClick={() => removeStep(index)}
                className="text-red-500 hover:text-red-700 flex items-center gap-1 px-2 py-1 rounded-full bg-red-100 dark:bg-red-900"
                title="Remove Step"
              >
                <FaTrash />
              </button>
            </div>
            <div className="flex flex-col gap-2 px-4 py-3">
              <div className="flex flex-row gap-4 items-center">
                <label className="w-24 font-semibold text-yellow-700">Number</label>
                <input
                  type="number"
                  value={step.order}
                  onChange={(e) => handleStepChange(index, "order", parseInt(e.target.value))}
                  className="w-24 rounded-2xl border-2 border-yellow-200 focus:border-green-400 focus:ring-2 focus:ring-green-200 px-3 py-2 text-lg transition-all duration-200 bg-yellow-50 dark:bg-yellow-900 placeholder:text-yellow-400 focus:bg-white dark:focus:bg-boxdark"
                  placeholder="Order"
                />
              </div>
              <div className="flex flex-row gap-4 items-center">
                <label className="w-24 font-semibold text-blue-700">Name</label>
                <input
                  type="text"
                  value={step.name}
                  onChange={(e) => handleStepChange(index, "name", e.target.value)}
                  className="flex-1 rounded-2xl border-2 border-blue-200 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-200 px-3 py-2 text-lg transition-all duration-200 bg-blue-50 dark:bg-blue-900 placeholder:text-blue-400 focus:bg-white dark:focus:bg-boxdark"
                  placeholder="Specialist Name"
                />
              </div>
              <div className="flex flex-col gap-2">
                <label className="font-semibold text-green-700">Objectives</label>
                <div className="flex flex-wrap gap-2 mb-2">
                  {step.objectives.map((obj, objIdx) => (
                    <span key={objIdx} className="flex items-center gap-1 bg-green-200 dark:bg-green-800 text-green-900 dark:text-green-100 px-3 py-1 rounded-full">
                      {obj}
                      <button
                        type="button"
                        className="ml-1 text-red-500 hover:text-red-700"
                        onClick={() => {
                          const newObjs = step.objectives.filter((_, i) => i !== objIdx);
                          handleStepChange(index, "objectives", newObjs);
                        }}
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
                    value={newObjectives[index] || ""}
                    onChange={e => {
                      const arr = [...newObjectives];
                      arr[index] = e.target.value;
                      setNewObjectives(arr);
                    }}
                    className="flex-1 rounded-2xl border-2 border-green-200 focus:border-yellow-400 focus:ring-2 focus:ring-yellow-200 px-3 py-2 text-lg transition-all duration-200 bg-green-50 dark:bg-green-900 placeholder:text-green-400 focus:bg-white dark:focus:bg-boxdark"
                    placeholder="Add objective"
                    onKeyDown={e => {
                      if (e.key === 'Enter' && (newObjectives[index] || '').trim()) {
                        e.preventDefault();
                        const newObjs = [...step.objectives, newObjectives[index].trim()];
                        handleStepChange(index, "objectives", newObjs);
                        const arr = [...newObjectives];
                        arr[index] = "";
                        setNewObjectives(arr);
                      }
                    }}
                  />
                  <button
                    type="button"
                    className="px-4 py-2 rounded-2xl bg-green-400 text-white font-bold hover:bg-green-500 transition-all"
                    onClick={() => {
                      if ((newObjectives[index] || '').trim()) {
                        const newObjs = [...step.objectives, newObjectives[index].trim()];
                        handleStepChange(index, "objectives", newObjs);
                        const arr = [...newObjectives];
                        arr[index] = "";
                        setNewObjectives(arr);
                      }
                    }}
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
