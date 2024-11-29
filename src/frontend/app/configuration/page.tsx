import React from "react";
import Link from "next/link";
import Image from "next/image";
import { Metadata } from "next";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";

export const metadata: Metadata = {
  title: "Tutor | Configuration",
  description: "This is the Transcription configuration page for Tutor.",
};

const ConfigurationPage = () => {
  return (
    <DefaultLayout>
      <Breadcrumb pageName={"Setup"} />
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 p-6">
        <Link
          href="/configuration/cases"
          className="flex flex-col items-center p-6 bg-white hover:bg-light-cyan shadow-lg rounded-lg hover:shadow-xl transition-shadow cursor-pointer text-center"
        >
          <Image
            width={250}
            height={250}
            src="/images/logo/logo.webp"
            alt="Cases"
            className="mb-4"
          />
          <h3 className="text-2xl font-semibold text-gray-800">Cases</h3>
          <p className="mt-2 text-gray-600">Configure and Manage cases to be spoken and trained on.</p>
        </Link>

        <Link
          href="/configuration/themes"
          className="flex flex-col items-center p-6 bg-white hover:bg-light-cyan shadow-lg rounded-lg hover:shadow-xl transition-shadow cursor-pointer text-center"
        >
          <Image
            width={250}
            height={250}
            src="/images/logo/logo.webp"
            alt="Evaluation Icon"
            className="mb-4"
          />
          <h3 className="text-2xl font-semibold text-gray-800">Themes</h3>
          <p className="mt-2 text-gray-600">
            Create and test arguing skills.
          </p>
        </Link>

        <Link
          href="/configuration/questions"
          className="flex flex-col items-center p-6 bg-white hover:bg-light-cyan shadow-lg rounded-lg hover:shadow-xl transition-shadow cursor-pointer text-center"
        >
          <Image
            width={250}
            height={250}
            src="/images/logo/logo.webp"
            alt="Evaluation Icon"
            className="mb-4"
          />
          <h3 className="text-2xl font-semibold text-gray-800">Questions</h3>
          <p className="mt-2 text-gray-600">
            Validate learning objectively.
          </p>
        </Link>
      </div>
    </DefaultLayout>
  );
};

export default ConfigurationPage;
