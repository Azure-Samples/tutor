import React from "react";
import { Metadata } from "next";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import ThemeForm from "@/components/Configuration/Theme";


export const metadata: Metadata = {
  title: "Tutor | Theme Configuration",
  description: "Manage Themes for distinct activities.",
};


const RulesManagementPage = () => {
  return (
    <DefaultLayout>
      <Breadcrumb pageName={"Theme Setup"} />
      <div className="flex flex-col md:flex-row justify-between gap-6 p-6">
        <ThemeForm />
      </div>
    </DefaultLayout>
  );
};

export default RulesManagementPage;