import DefaultLayout from "@/components/Layouts/DefaultLayout";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import ThemeForm from "@/components/Configuration/Theme";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Theme Configuration | Tutor",
  description: "Manage essay themes and rubric criteria for the showcase scenarios.",
};

const ThemesPage = () => {
  return (
    <DefaultLayout>
      <Breadcrumb 
        pageName="Theme Configuration" 
        subtitle="Create and manage themes used in essay evaluation workflows." 
      />
      <ThemeForm />
    </DefaultLayout>
  );
};

export default ThemesPage;
