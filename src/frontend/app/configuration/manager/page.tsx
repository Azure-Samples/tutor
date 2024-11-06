import React from "react";
import { Metadata } from "next";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import ManagerForm from "@/components/Configuration/Managers";


export const metadata: Metadata = {
  title: "Tayra | Manager Configuration",
  description: "Manage Managers and Specialists that own transcriptions and evaluations.",
};


const ManagerManagementPage = () => {
  return (
    <DefaultLayout>
      <Breadcrumb pageName={"Setup"} />
      <div className="flex flex-col md:flex-row justify-between gap-6 p-6">
        <ManagerForm />
      </div>
    </DefaultLayout>
  );
};

export default ManagerManagementPage;