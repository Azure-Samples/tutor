import DefaultLayout from "@/components/Layouts/DefaultLayout";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import AvatarChat from "@/components/Avatar/Avatar";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Tutor | Avatar Interaction",
  description: "Avatar interaction based on configuration",
};

const AvatarPage = () => {
  return (
    <DefaultLayout metadata={metadata}>
      <Breadcrumb 
        pageName="Avatar Interaction" 
        subtitle="Interact with the AI avatar based on your configuration. Experience dynamic, agentic conversations tailored to your needs." 
      />
      <div className="flex flex-col gap-10">
        <AvatarChat />
      </div>
    </DefaultLayout>
  );
};

export default AvatarPage;
