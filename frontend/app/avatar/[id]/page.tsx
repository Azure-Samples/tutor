"use client";

import { useParams } from "next/navigation";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import AvatarChat from "@/components/Avatar/Avatar";

const AvatarCasePage = () => {
  const params = useParams<{ id: string }>();
  const caseId = Array.isArray(params?.id) ? params.id[0] : params?.id;

  return (
    <DefaultLayout>
      <Breadcrumb
        pageName="Avatar Interaction"
        subtitle="Interact with the selected avatar case routed through the API gateway."
      />
      <div className="flex flex-col gap-10">
        <AvatarChat initialCaseId={caseId} />
      </div>
    </DefaultLayout>
  );
};

export default AvatarCasePage;
