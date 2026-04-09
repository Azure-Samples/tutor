import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import ChatCard from "@/components/Chat/ChatCard";
import DefaultLayout from "@/components/Layouts/DefaultLayout";

import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Chat | Tutor",
  description: "Chat with your data, ask questions, and get clear, supportive answers.",
};

const TablesPage = () => {
  return (
    <DefaultLayout metadata={metadata}>
      <Breadcrumb
        pageName="Converse com seus Dados"
        subtitle="Chat with your data, ask questions, and get clear, supportive answers. Your curiosity is welcome here!"
      />
      <ChatCard />
    </DefaultLayout>
  );
};

export default TablesPage;
