import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { ProgramsPageContent } from "@/components/Public/PublicPageContent";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Programs | Tutor",
  description:
    "Curated programs and re-entry offers aligned to Tutor's lifelong-learning platform direction.",
};

const ProgramsPage = () => {
  return (
    <DefaultLayout variant="public">
      <ProgramsPageContent />
    </DefaultLayout>
  );
};

export default ProgramsPage;
