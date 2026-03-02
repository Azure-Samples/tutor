"use client";

import React from "react";
import { usePathname } from "next/navigation";
import SidebarItem from "@/components/Sidebar/SidebarItem";
import useLocalStorage from "@/hooks/useLocalStorage";
import { FaCog, FaFileAlt, FaQuestionCircle, FaUserGraduate, FaComments } from "react-icons/fa";

interface SidebarProps {
  sidebarOpen: boolean;
  setSidebarOpen: (arg: boolean) => void;
  exceptionRef?: React.RefObject<HTMLElement>;
}

const menuGroups = [
  {
    name: "The Tutor - Student Assistant",
    menuItems: [
      {
        icon: (
          <span className="sidebar-icon flex items-center justify-center w-10 h-10 rounded-full p-2 bg-gradient-to-br from-cyan-400 to-blue-500 transition-all duration-300 group-hover:bg-white">
            <FaCog className="w-6 h-6 transition-all duration-300 group-hover:bg-gradient-to-br group-hover:from-cyan-400 group-hover:to-blue-500 group-hover:text-transparent group-hover:bg-clip-text" />
          </span>
        ),
        label: "Configuration",
        route: "/configuration",
        gradient: "from-cyan-400 to-blue-500",
        hoverText: "text-cyan-500"
      },
      {
        icon: (
          <span className="sidebar-icon flex items-center justify-center w-10 h-10 rounded-full p-2 bg-gradient-to-br from-yellow-400 to-pink-500 transition-all duration-300 group-hover:bg-white">
            <FaFileAlt className="w-6 h-6 transition-all duration-300 group-hover:bg-gradient-to-br group-hover:from-yellow-400 group-hover:to-pink-500 group-hover:text-transparent group-hover:bg-clip-text" />
          </span>
        ),
        label: "Essays",
        route: "/essays",
        gradient: "from-yellow-400 to-pink-500",
        hoverText: "text-pink-500"
      },
      {
        icon: (
          <span className="sidebar-icon flex items-center justify-center w-10 h-10 rounded-full p-2 bg-gradient-to-br from-green-400 to-lime-500 transition-all duration-300 group-hover:bg-white">
            <FaQuestionCircle className="w-6 h-6 transition-all duration-300 group-hover:bg-gradient-to-br group-hover:from-green-400 group-hover:to-lime-500 group-hover:text-transparent group-hover:bg-clip-text" />
          </span>
        ),
        label: "Questions",
        route: "/questions",
        gradient: "from-green-400 to-lime-500",
        hoverText: "text-green-500"
      },
      {
        icon: (
          <span className="sidebar-icon flex items-center justify-center w-10 h-10 rounded-full p-2 bg-gradient-to-br from-purple-400 to-fuchsia-500 transition-all duration-300 group-hover:bg-white">
            <FaUserGraduate className="w-6 h-6 transition-all duration-300 group-hover:bg-gradient-to-br group-hover:from-purple-400 group-hover:to-fuchsia-500 group-hover:text-transparent group-hover:bg-clip-text" />
          </span>
        ),
        label: "Avatar",
        route: "/avatar",
        gradient: "from-purple-400 to-fuchsia-500",
        hoverText: "text-fuchsia-500"
      },
      {
        icon: (
          <span className="sidebar-icon flex items-center justify-center w-10 h-10 rounded-full p-2 bg-gradient-to-br from-orange-400 to-pink-500 transition-all duration-300 group-hover:bg-white">
            <FaComments className="w-6 h-6 transition-all duration-300 group-hover:bg-gradient-to-br group-hover:from-orange-400 group-hover:to-pink-500 group-hover:text-transparent group-hover:bg-clip-text" />
          </span>
        ),
        label: "Chat",
        route: "/chat",
        gradient: "from-orange-400 to-pink-500",
        hoverText: "text-orange-500"
      }
    ]
  }
];

const Sidebar = ({ sidebarOpen, setSidebarOpen, exceptionRef }: SidebarProps) => {
  const pathname = usePathname();
  const [pageName, setPageName] = useLocalStorage("selectedMenu", "dashboard");

  return (
    <aside
      className={`fixed left-0 top-10 z-50 flex h-screen w-max flex-col overflow-y-hidden bg-white duration-300 ease-linear dark:bg-boxdark lg:translate-x-0 ${
        sidebarOpen ? "translate-x-0" : "-translate-x-full pointer-events-none opacity-0"
      }`}
    >
      <div className="no-scrollbar flex flex-col overflow-y-auto duration-300 ease-linear">
        {/* <!-- Sidebar Menu --> */}
        <nav className="mt-5 px-4 py-4 lg:mt-9 lg:px-6">
          {menuGroups.map((group, groupIndex) => (
            <div key={groupIndex}>
              <h3 className="mb-4 ml-4 text-sm font-semibold text-bodydark2">
                {group.name}
              </h3>
              <ul className="mb-6 flex flex-col gap-1.5">
                {group.menuItems.map((menuItem, menuIndex) => (
                  <SidebarItem
                    key={menuIndex}
                    item={menuItem}
                    pageName={pageName}
                    setPageName={setPageName}
                    className="group"
                  />
                ))}
              </ul>
            </div>
          ))}
        </nav>
      </div>
    </aside>
  );
};

export default Sidebar;
