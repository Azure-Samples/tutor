import type { Theme } from "@/types/theme";
import { configurationApi } from "@/utils/api";
import { useState } from "react";
import { FaBullseye, FaFileAlt, FaListOl, FaPalette, FaPen, FaPlus, FaTimes } from "react-icons/fa";

type CriterionDraft = {
  id: string;
  value: string;
};

type ThemeDraft = Omit<Theme, "criteria"> & {
  criteria: CriterionDraft[];
};

const createDraftId = (prefix: string) => {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }

  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2)}`;
};

const createThemeDraft = (themeData?: Theme): ThemeDraft =>
  themeData
    ? {
        ...themeData,
        criteria: themeData.criteria.map((criterion) => ({
          id: createDraftId("criterion"),
          value: criterion,
        })),
      }
    : { id: "", name: "", objective: "", description: "", criteria: [] };

const toThemePayload = (form: ThemeDraft): Theme => ({
  id: form.id,
  name: form.name,
  objective: form.objective,
  description: form.description,
  criteria: form.criteria.map((criterion) => criterion.value),
});

const ThemeForm: React.FC<{ themeData?: Theme; onSuccess?: () => void }> = ({
  themeData,
  onSuccess,
}) => {
  const [form, setForm] = useState<ThemeDraft>(() => createThemeDraft(themeData));
  const [status, setStatus] = useState("");
  const isEdit = !!themeData;

  const handleCriteriaChange = (criterionId: string, value: string) => {
    setForm((currentForm) => ({
      ...currentForm,
      criteria: currentForm.criteria.map((criterion) =>
        criterion.id === criterionId ? { ...criterion, value } : criterion,
      ),
    }));
  };

  const addCriterion = () => {
    setForm((currentForm) => ({
      ...currentForm,
      criteria: [...currentForm.criteria, { id: createDraftId("criterion"), value: "" }],
    }));
  };

  const removeCriterion = (criterionId: string) => {
    setForm((currentForm) => ({
      ...currentForm,
      criteria: currentForm.criteria.filter((criterion) => criterion.id !== criterionId),
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("Saving...");
    try {
      const themeId =
        form.id?.trim() ||
        (typeof crypto !== "undefined" && "randomUUID" in crypto
          ? crypto.randomUUID()
          : `theme-${Date.now()}`);
      const payload = { ...toThemePayload(form), id: themeId };
      const res = isEdit
        ? await configurationApi.put(`/themes/${themeId}`, payload)
        : await configurationApi.post("/themes", payload);
      if (res.status === 200 || res.status === 201) {
        setStatus(isEdit ? "Theme updated!" : "Theme created!");
        if (onSuccess) onSuccess();
        if (!isEdit) setForm(createThemeDraft());
      } else {
        setStatus("Error saving theme.");
      }
    } catch {
      setStatus("Error saving theme.");
    }
  };

  return (
    <form
      className="flex flex-col gap-4 w-full max-w-xl mx-auto p-0 form-dot-scrollbar overflow-y-auto"
      id="modal-form"
      onSubmit={handleSubmit}
    >
      <label htmlFor="theme-form-name" className="flex items-center gap-2 text-cyan-700 font-bold">
        <FaPalette /> Name
      </label>
      <input
        id="theme-form-name"
        type="text"
        value={form.name}
        onChange={(e) => setForm({ ...form, name: e.target.value })}
        className="w-full rounded-2xl border-2 border-cyan-200 focus:border-green-400 focus:ring-2 focus:ring-green-200 px-4 py-3 text-lg transition-all duration-200 bg-cyan-50 dark:bg-cyan-900 placeholder:text-cyan-400 focus:bg-white dark:focus:bg-boxdark"
        placeholder="Theme name"
      />
      <label
        htmlFor="theme-form-objective"
        className="flex items-center gap-2 text-green-700 font-bold"
      >
        <FaBullseye /> Objective
      </label>
      <input
        id="theme-form-objective"
        type="text"
        value={form.objective}
        onChange={(e) => setForm({ ...form, objective: e.target.value })}
        className="w-full rounded-2xl border-2 border-green-200 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-200 px-4 py-3 text-lg transition-all duration-200 bg-green-50 dark:bg-green-900 placeholder:text-green-400 focus:bg-white dark:focus:bg-boxdark"
        placeholder="Theme objective"
      />
      <label
        htmlFor="theme-form-description"
        className="flex items-center gap-2 text-blue-700 font-bold"
      >
        <FaFileAlt /> Description
      </label>
      <textarea
        id="theme-form-description"
        value={form.description}
        onChange={(e) => setForm({ ...form, description: e.target.value })}
        className="w-full rounded-2xl border-2 border-blue-200 focus:border-yellow-400 focus:ring-2 focus:ring-yellow-200 px-4 py-3 text-lg transition-all duration-200 bg-blue-50 dark:bg-blue-900 placeholder:text-blue-400 focus:bg-white dark:focus:bg-boxdark resize-y min-h-[48px] max-h-[240px]"
        placeholder="Theme description"
        rows={3}
      />
      <p className="flex items-center gap-2 text-purple-700 font-bold">
        <FaListOl /> Criteria
      </p>
      {form.criteria.map((criterion, index) => (
        <div key={criterion.id} className="flex items-center gap-2">
          <input
            type="text"
            aria-label={`Criterion ${index + 1}`}
            value={criterion.value}
            onChange={(e) => handleCriteriaChange(criterion.id, e.target.value)}
            className="flex-1 rounded-2xl border-2 border-purple-200 focus:border-blue-400 focus:ring-2 focus:ring-blue-200 px-4 py-3 text-lg transition-all duration-200 bg-purple-50 dark:bg-purple-900 placeholder:text-purple-400 focus:bg-white dark:focus:bg-boxdark"
            placeholder={`Criterion ${index + 1}`}
          />
          <button
            type="button"
            onClick={() => removeCriterion(criterion.id)}
            className="bg-gradient-to-br from-red-400 to-orange-400 text-white rounded-full p-2 shadow hover:scale-110 transition-all duration-200"
            title="Remove criterion"
          >
            <FaTimes />
          </button>
        </div>
      ))}
      <button
        type="button"
        onClick={addCriterion}
        className="flex items-center gap-2 self-start px-4 py-2 bg-gradient-to-br from-green-400 to-emerald-500 text-white font-bold rounded-2xl shadow hover:scale-105 transition-all duration-200"
      >
        <FaPlus /> Add Criterion
      </button>
      <button
        type="submit"
        className="mt-4 px-4 py-3 bg-gradient-to-br from-green-400 to-cyan-400 hover:from-cyan-400 hover:to-yellow-300 text-white font-bold rounded-2xl shadow-lg w-full flex items-center justify-center gap-2 text-lg transition-all duration-200"
      >
        {isEdit ? <FaPen /> : <FaPlus />} {isEdit ? "Update Theme" : "Add Theme"}
      </button>
      {status && (
        <p className="mt-2 text-center text-sm text-gray-700 dark:text-gray-300">{status}</p>
      )}
    </form>
  );
};

export default ThemeForm;
