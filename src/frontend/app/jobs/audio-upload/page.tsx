import React from "react";
import { Metadata } from "next";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import UploadFile from "@/components/UploadFile";


export const metadata: Metadata = {
  title: "Tayra | Audio Upload",
  description: "Enables audio file uploads.",
};


const AudioUploadPage = () => {
  return (
    <DefaultLayout>
      <Breadcrumb pageName={"Audio Upload"} />
      <div className="flex flex-col md:flex-row justify-center w-full">
        <UploadFile />
      </div>
    </DefaultLayout>
  );
};

export default AudioUploadPage;