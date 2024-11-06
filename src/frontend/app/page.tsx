import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import CardLayout from "@/components/Cards/Cards";

import { Metadata } from "next";
import DefaultLayout from "@/components/Layouts/DefaultLayout";

export const metadata: Metadata = {
  title: "Transcription Evaluation | Managers",
  description:
    "Evaluate the transcriptions of your team's managers and specialists.",
};

const TablesPage = () => {
  return (
    <DefaultLayout>
      <Breadcrumb pageName="Transcription Analysis" />
      <div className="flex flex-col gap-10">
        <CardLayout />
      </div>
    </DefaultLayout>
  );
};

export default TablesPage;
