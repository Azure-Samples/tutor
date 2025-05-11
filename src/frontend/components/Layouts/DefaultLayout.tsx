"use client";
import React, { useRef, useState } from "react";
import Sidebar from "@/components/Sidebar";
import Header from "@/components/Header";
import { Metadata } from "next";

export default function DefaultLayout({
  children,
  metadata,
}: {
  children: React.ReactNode;
  metadata?: Metadata;
}) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const sidebarSwitcherRef = useRef<HTMLButtonElement>(null);
  return (
    <main>
      {metadata && (
        <>
          {metadata.title && (
            <title>{typeof metadata.title === "string" ? metadata.title : String(metadata.title)}</title>
          )}
          {metadata.description && (
            <meta name="description" content={metadata.description} />
          )}
        </>
      )}
      <div className="fixed z-9999 w-full top-0 left-0">
        <Header sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} sidebarSwitcherRef={sidebarSwitcherRef} />
      </div>
      <div className="flex pt-16">
        {!sidebarOpen && (
          <div className="flex-1">
            <div className="mx-auto max-w-screen-2xl p-4 md:p-6 2xl:p-10 bg-white dark:bg-black">
              {children}
            </div>
          </div>
        )}
        {sidebarOpen && (
          <div className="relative flex flex-1 flex-col lg:ml-72.5">
            <Sidebar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} exceptionRef={sidebarSwitcherRef} />
            <div className="mx-auto max-w-screen-2xl p-4 md:p-6 2xl:p-10 bg-white dark:bg-black">
              {children}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
