import React from "react";
import { FaHamburger } from "react-icons/fa";

interface SidebarSwitcherProps {
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
}

const SidebarSwitcher = React.forwardRef<HTMLButtonElement, SidebarSwitcherProps>(
  ({ sidebarOpen, setSidebarOpen }, ref) => (
    <button
      ref={ref}
      aria-controls="sidebar"
      onClick={e => {
        e.stopPropagation();
        setSidebarOpen(!sidebarOpen);
      }}
      className={`z-99999 block rounded-full border border-stroke p-2 shadow-sm transition-colors duration-300
        ${sidebarOpen ? "bg-gradient-to-br from-orange-400 to-red-500 border-transparent" : "bg-white border-stroke"}`}
      title={sidebarOpen ? "Close sidebar" : "Open sidebar"}
      type="button"
    >
      <span className="flex items-center justify-center w-6 h-6 transition-all duration-300">
        <FaHamburger className="w-6 h-6 transition-all duration-300" color={sidebarOpen ? "white": "orange"} />
      </span>
    </button>
  )
);

SidebarSwitcher.displayName = "SidebarSwitcher";

export default SidebarSwitcher;