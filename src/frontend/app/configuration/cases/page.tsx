import React from "react";
import { Metadata } from "next";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import CasesList from "@/components/Lists/Cases";


export const metadata: Metadata = {
  title: "Tayra | Case Configuration",
  description: "Manage Cases for Avatar and Chat Interactions.",
};


const ManagerManagementPage = () => {
  return (
    <DefaultLayout metadata={metadata}>
      <Breadcrumb pageName={"Avatar Cases & Profiles"} subtitle="Manage, create, and organize real-world scenarios for student practice and evaluation. Empower your students with authentic learning experiences." />
      <div className="flex flex-col md:flex-row justify-between gap-6">
        <CasesList />
      </div>
    </DefaultLayout>
  );
};

export default ManagerManagementPage;