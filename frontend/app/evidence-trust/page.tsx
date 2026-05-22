import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { EvidenceTrustPageContent } from "@/components/Public/PublicPageContent";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Evidence and Trust | Tutor",
  description:
    "How Tutor distinguishes deterministic record surfaces, advisory guidance, and degraded states.",
};

const EvidenceTrustPage = () => {
  return (
    <DefaultLayout variant="public">
      <EvidenceTrustPageContent />
    </DefaultLayout>
  );
};

export default EvidenceTrustPage;
