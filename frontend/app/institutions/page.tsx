import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { InstitutionsPageContent } from "@/components/Public/PublicPageContent";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "For Institutions | Tutor",
  description:
    "Institution-facing positioning for Tutor's learner-record-centered lifelong-learning platform direction.",
};

const InstitutionsPage = () => {
  return (
    <DefaultLayout variant="public">
      <InstitutionsPageContent />
    </DefaultLayout>
  );
};

export default InstitutionsPage;
