import React from "react";
import Link from "next/link";
import Image from "next/image";
import { Metadata } from "next";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";

export const metadata: Metadata = {
  title: "Tayra | Transcription Configuration",
  description: "This is the Transcription configuration page for Tayra.",
};

const ConfigurationPage = () => {
  return (
    <DefaultLayout>
      <Breadcrumb pageName={"Setup"} />
      <div className="flex flex-col md:flex-row justify-center gap-6 p-6">

        <Link href="/configuration/manager">
          <div className="flex flex-col items-center min-w-100 w-full md:w-1/2 p-6 bg-white hover:bg-light-cyan shadow-lg rounded-lg hover:shadow-xl transition-shadow cursor-pointer text-center">
            <Image
              width={250}
              height={250}
              src="/images/manager.png"
              alt="Manager Icon"
              className="mb-4"
            />
            <h3 className="text-2xl font-semibold text-gray-800">Configure Managers</h3>
            <p className="mt-2 text-gray-600">
              Configure and manage call center managers and their specialists.
            </p>
          </div>
        </Link>

        <Link href="/configuration/rules">
          <div className="flex flex-col items-center min-w-100 w-full md:w-1/2 p-6 bg-white hover:bg-light-cyan shadow-lg rounded-lg hover:shadow-xl transition-shadow cursor-pointer text-center">
            <Image
              width={250}
              height={250}
              src="/images/rules.png"
              alt="Rules Icon"
              className="mb-4"
            />
            <h3 className="text-2xl font-semibold text-gray-800">Configure Rules</h3>
            <p className="mt-2 text-gray-600">
              Set up and manage transcription and evaluation rules.
            </p>
          </div>
        </Link>

      </div>
    </DefaultLayout>
  );
};

export default ConfigurationPage;
