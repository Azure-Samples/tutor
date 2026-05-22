import React from "react";
import { FiMenu } from "react-icons/fi";
import { useI18n } from "@/components/I18n/LocaleProvider";

interface SidebarSwitcherProps {
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
}

const SidebarSwitcher = React.forwardRef<HTMLButtonElement, SidebarSwitcherProps>(
  ({ sidebarOpen, setSidebarOpen }, ref) => {
    const { dictionary } = useI18n();
    const label = sidebarOpen ? dictionary.workspace.collapseSidebar : dictionary.workspace.openSidebar;

    return (
      <button
        ref={ref}
        aria-controls="sidebar"
        aria-expanded={sidebarOpen}
        aria-label={label}
        onClick={(e) => {
          e.stopPropagation();
          setSidebarOpen(!sidebarOpen);
        }}
        className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-stone-200 bg-white text-slate-700 shadow-sm transition hover:bg-stone-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800"
        title={label}
        type="button"
      >
        <span className="flex h-5 w-5 items-center justify-center">
          <FiMenu className="h-5 w-5" />
        </span>
      </button>
    );
  },
);

SidebarSwitcher.displayName = "SidebarSwitcher";

export default SidebarSwitcher;
