import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import ThemesList from "@/components/Lists/Themes";
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
      <ThemesList />
    </DefaultLayout>
  );
};

export default ThemesPage;
