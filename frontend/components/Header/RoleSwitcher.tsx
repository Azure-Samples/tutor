"use client";

import { useI18n } from "@/components/I18n/LocaleProvider";
import { useWorkspace } from "@/components/Workspace/WorkspaceProvider";
import type { WorkspaceRole } from "@/utils/workspace";
import { useRouter } from "next/navigation";
import { startTransition, useId } from "react";

const inputClassName =
  "mt-1 min-h-9 w-full rounded-lg border border-stone-200 bg-white px-3 py-1.5 text-sm text-slate-900 shadow-sm transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100";

const RoleSwitcher = () => {
  const id = useId();
  const router = useRouter();
  const { dictionary } = useI18n();
  const { availableRoles, currentRole, isLoading, setRole } = useWorkspace();

  return (
    <div className="min-w-[10rem]">
      <label
        htmlFor={id}
        className="block text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500"
      >
        {dictionary.workspace.roleLabel}
      </label>
      <select
        id={id}
        value={currentRole}
        onChange={(event) => {
          const nextRole = event.target.value as WorkspaceRole;
          setRole(nextRole);
          startTransition(() => {
            router.push(`/workspace/${nextRole}`);
          });
        }}
        disabled={isLoading}
        className={inputClassName}
      >
        {availableRoles.map((role) => (
          <option key={role.key} value={role.key}>
            {role.label}
          </option>
        ))}
      </select>
    </div>
  );
};

export default RoleSwitcher;
