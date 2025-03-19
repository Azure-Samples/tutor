import React from "react";
import { Metadata } from "next";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import CaseForm from "@/components/Configuration/Cases";


export const metadata: Metadata = {
  title: "Tayra | Case Configuration",
  description: "Manage Cases for Avatar and Chat Interactions.",
};


const ManagerManagementPage = () => {
  return (
    <DefaultLayout>
      <Breadcrumb pageName={"Cases Setup"} />
      <div className="flex flex-col md:flex-row justify-between gap-6 p-6">
        <CaseForm />
      </div>
    </DefaultLayout>
  );
};

export default ManagerManagementPage;