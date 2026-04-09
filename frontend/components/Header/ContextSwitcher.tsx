"use client";

import { useWorkspace } from "@/components/Workspace/WorkspaceProvider";
import { useId } from "react";

const inputClassName =
  "mt-1 w-full rounded-xl border border-stone-200 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100";

const ContextSwitcher = () => {
  const id = useId();
  const { currentContext, contextOptions, isLoading, setContext } = useWorkspace();

  return (
    <div className="min-w-[15rem]">
      <label
        htmlFor={id}
        className="block text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500"
      >
        Context
      </label>
      <select
        id={id}
        value={currentContext.id}
        onChange={(event) => setContext(event.target.value)}
        disabled={isLoading || contextOptions.length === 0}
        className={inputClassName}
      >
        {contextOptions.map((context) => (
          <option key={context.id} value={context.id}>
            {context.label} · {context.scope}
          </option>
        ))}
      </select>
      <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{currentContext.note}</p>
    </div>
  );
};

export default ContextSwitcher;
