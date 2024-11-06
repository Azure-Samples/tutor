import DefaultLayout from "@/components/Layouts/DefaultLayout";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import ChatCard from "@/components/Chat/ChatCard";

import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Avaliação de Trascrições | Gerentes",
  description: "Página de Avaliação de Transcrições",
};

const TablesPage = () => {
  return (
    <DefaultLayout>
      <Breadcrumb pageName="Converse com seus Dados" />
      <div className="flex flex-col gap-10">
        <ChatCard />
      </div>
    </DefaultLayout>
  );
};

export default TablesPage;
