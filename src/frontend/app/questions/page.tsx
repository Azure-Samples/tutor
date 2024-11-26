import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import CardLayout from "@/components/Cards/Cards";

import { Metadata } from "next";
import DefaultLayout from "@/components/Layouts/DefaultLayout";

export const metadata: Metadata = {
  title: "Avaliação de Trascrições | Gerentes",
  description:
    "This is Next.js Tables page for TailAdmin - Next.js Tailwind CSS Admin Dashboard Template",
};

const TablesPage = () => {
  return (
    <DefaultLayout>
      <Breadcrumb pageName="Transcription Evaluation" />
      <div className="flex flex-col gap-10">
        <CardLayout />
      </div>
    </DefaultLayout>
  );
};

export default TablesPage;
