import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { HomePageContent } from "@/components/Public/PublicPageContent";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Tutor | Lifelong Learning Platform",
  description:
    "Institution-owned lifelong learning platform for learner records, guided learning, leadership briefings, and curated re-entry.",
};

const HomePage = () => {
  return (
    <DefaultLayout metadata={metadata} variant="public">
      <HomePageContent />
    </DefaultLayout>
  );
};

export default HomePage;
