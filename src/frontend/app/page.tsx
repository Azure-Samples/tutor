import Link from "next/link";
import Image from "next/image";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";

import { Metadata } from "next";
import DefaultLayout from "@/components/Layouts/DefaultLayout";

export const metadata: Metadata = {
  title: "The Tutor",
  description: "Support for students in all dimensions.",
};

const TablesPage = () => {
  return (
    <DefaultLayout>
      <Breadcrumb pageName="Tutor" />
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 p-6">
        <Link
          href="/avatar"
          className="flex flex-col items-center p-6 bg-white hover:bg-light-cyan shadow-lg rounded-lg hover:shadow-xl transition-shadow cursor-pointer text-center"
        >
          <Image
            width={250}
            height={250}
            src="/images/logo/logo.webp"
            alt="Avatar"
            className="mb-4"
          />
          <h3 className="text-2xl font-semibold text-gray-800">Avatar</h3>
          <p className="mt-2 text-gray-600">Live, Interactive Tasks.</p>
        </Link>

        <Link
          href="/jobs/transcribe"
          className="flex flex-col items-center p-6 bg-white hover:bg-light-cyan shadow-lg rounded-lg hover:shadow-xl transition-shadow cursor-pointer text-center"
        >
          <Image
            width={250}
            height={250}
            src="/images/logo/logo.webp"
            alt="Transcription Icon"
            className="mb-4"
          />
          <h3 className="text-2xl font-semibold text-gray-800">Chat</h3>
          <p className="mt-2 text-gray-600">
            Talk when you want, what you want.
          </p>
        </Link>

        <Link
          href="/jobs/evaluate"
          className="flex flex-col items-center p-6 bg-white hover:bg-light-cyan shadow-lg rounded-lg hover:shadow-xl transition-shadow cursor-pointer text-center"
        >
          <Image
            width={250}
            height={250}
            src="/images/logo/logo.webp"
            alt="Evaluation Icon"
            className="mb-4"
          />
          <h3 className="text-2xl font-semibold text-gray-800">Essays</h3>
          <p className="mt-2 text-gray-600">
            Stand your point and defend it.
          </p>
        </Link>

        <Link
          href="/jobs/evaluate"
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
            Test your knowledge on objective concepts.
          </p>
        </Link>
      </div>
    </DefaultLayout>
  );
};

export default TablesPage;
