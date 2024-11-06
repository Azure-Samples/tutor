"use client";

import React, { useEffect, useRef, useState } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import SidebarItem from "@/components/Sidebar/SidebarItem";
import ClickOutside from "@/components/ClickOutside";
import useLocalStorage from "@/hooks/useLocalStorage";

interface SidebarProps {
  sidebarOpen: boolean;
  setSidebarOpen: (arg: boolean) => void;
}

const menuGroups = [
  {
    name: "TAYRA - CALLCENTER ANALYTICS",
    menuItems: [
      {
        icon: (
          <svg
              width="25"
              height="25"
              viewBox="0 0 100 100"
              xmlns="http://www.w3.org/2000/svg"
          >
              <circle cx="50" cy="50" r="45" stroke="black" stroke-width="2" fill="none" />
              <g fill="black">
                  <rect x="47" y="5" width="6" height="10" />
                  <rect x="47" y="85" width="6" height="10" />
                  <rect x="5" y="47" width="10" height="6" />
                  <rect x="85" y="47" width="10" height="6" />
                  
                  <rect x="20" y="20" width="6" height="10" transform="rotate(45 20 20)" />
                  <rect x="75" y="20" width="6" height="10" transform="rotate(-45 75 20)" />
                  <rect x="20" y="75" width="6" height="10" transform="rotate(-45 20 75)" />
                  <rect x="75" y="75" width="6" height="10" transform="rotate(45 75 75)" />
              </g>
              <circle cx="50" cy="50" r="20" fill="none" stroke="black" stroke-width="2" />
              <circle cx="50" cy="50" r="6" fill="black" />
          </svg>
        ),
        label: "Configuration",
        route: "/configuration",
      },
      {
        icon: (
          <svg
            className="fill-current"
            width="25"
            height="25"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 20C7.59 20 4 16.41 4 12C4 7.59 7.59 4 12 4C16.41 4 20 7.59 20 12C20 16.41 16.41 20 12 20ZM13 11V16H11V11H8L12 7L16 11H13Z"
              fill=""
            />
          </svg>
        ),
        label: "Job Management",
        route: "/jobs",
      },
      {
        icon: (
          <svg
            className="fill-current"
            width="25"
            height="25"
            viewBox="0 0 18 18"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M9.0002 7.79065C11.0814 7.79065 12.7689 6.1594 12.7689 4.1344C12.7689 2.1094 11.0814 0.478149 9.0002 0.478149C6.91895 0.478149 5.23145 2.1094 5.23145 4.1344C5.23145 6.1594 6.91895 7.79065 9.0002 7.79065ZM9.0002 1.7719C10.3783 1.7719 11.5033 2.84065 11.5033 4.16252C11.5033 5.4844 10.3783 6.55315 9.0002 6.55315C7.62207 6.55315 6.49707 5.4844 6.49707 4.16252C6.49707 2.84065 7.62207 1.7719 9.0002 1.7719Z"
              fill=""
            />
            <path
              d="M10.8283 9.05627H7.17207C4.16269 9.05627 1.71582 11.5313 1.71582 14.5406V16.875C1.71582 17.2125 1.99707 17.5219 2.3627 17.5219C2.72832 17.5219 3.00957 17.2407 3.00957 16.875V14.5406C3.00957 12.2344 4.89394 10.3219 7.22832 10.3219H10.8564C13.1627 10.3219 15.0752 12.2063 15.0752 14.5406V16.875C15.0752 17.2125 15.3564 17.5219 15.7221 17.5219C16.0877 17.5219 16.3689 17.2407 16.3689 16.875V14.5406C16.2846 11.5313 13.8377 9.05627 10.8283 9.05627Z"
              fill=""
            />
          </svg>
        ),
        label: "Transcription Analysis",
        route: "/transcriptions",
      },
      {
        icon: (
          <svg
            className="fill-current"
            width="25"
            height="25"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M12 2C6.48 2 2 5.58 2 10C2 11.68 2.69 13.21 3.82 14.44C3.58 15.69 2.65 16.92 2.65 16.92C2.65 16.92 3.96 16.84 5.16 15.97C6.24 15.19 7.31 15.49 8.24 15.97C9.37 16.72 10.65 17 12 17C17.52 17 22 13.42 22 9C22 5.58 17.52 2 12 2ZM12 15C7.59 15 4 12.69 4 10C4 7.31 7.59 5 12 5C16.41 5 20 7.31 20 10C20 12.69 16.41 15 12 15Z"
              fill="currentColor"
            />
          </svg>
        ),
        label: "Chat with your Data",
        route: "/chat",
      }
    ]
  }
];

const Sidebar = ({ sidebarOpen, setSidebarOpen }: SidebarProps) => {
  const pathname = usePathname();
  const [pageName, setPageName] = useLocalStorage("selectedMenu", "dashboard");

  return (
    <ClickOutside onClick={() => setSidebarOpen(false)}>
      <aside
        className={`fixed left-0 top-0 z-9999 flex h-screen w-max flex-col overflow-y-hidden bg-white duration-300 ease-linear dark:bg-boxdark lg:translate-x-0 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex flex-col items-center justify-center">
          <Link href="/">
            <Image
              width={150}
              height={50}
              src={"/images/logo/logo.png"}
              alt="Logo"
              priority
            />
          </Link>
        </div>
       
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
                    />
                  ))}
                </ul>
              </div>
            ))}
          </nav>
          {/* <!-- Sidebar Menu --> */}
        </div>
      </aside>
    </ClickOutside>
  );
};

export default Sidebar;
