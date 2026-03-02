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
      <Breadcrumb pageName="Converse com seus Dados" subtitle="Chat with your data, ask questions, and get clear, supportive answers. Your curiosity is welcome here!" />
      <ChatCard />
    </DefaultLayout>
  );
};

export default TablesPage;
