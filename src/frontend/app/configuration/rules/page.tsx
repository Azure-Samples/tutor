import React from "react";
import { Metadata } from "next";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import RuleForm from "@/components/Configuration/Rules";


export const metadata: Metadata = {
  title: "Tayra | Rules Configuration",
  description: "Manage Rules to evaluate transcriptions.",
};


const RulesManagementPage = () => {
  return (
    <DefaultLayout>
      <Breadcrumb pageName={"Rule Setup"} />
      <div className="flex flex-col md:flex-row justify-between gap-6 p-6">
        <RuleForm />
      </div>
    </DefaultLayout>
  );
};

export default RulesManagementPage;