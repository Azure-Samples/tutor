import DefaultLayout from "@/components/Layouts/DefaultLayout";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import AssembliesList from "@/components/Lists/Assemblies";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Agent Configuration | Tutor",
  description: "Manage AI agent assemblies for essay and question workflows.",
};

const AgentsPage = () => {
  return (
    <DefaultLayout>
      <Breadcrumb 
        pageName="Agent Configuration" 
        subtitle="Create and manage AI agent assemblies used in essay and question evaluation." 
      />
      <AssembliesList />
    </DefaultLayout>
  );
};

export default AgentsPage;
