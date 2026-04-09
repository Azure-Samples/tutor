import DefaultLayout from "@/components/Layouts/DefaultLayout";
import WorkspaceHome from "@/components/Workspace/WorkspaceHome";
import { WORKSPACE_ROLES, getRoleConfig, isWorkspaceRole } from "@/utils/workspace";
import type { Metadata } from "next";
import { notFound } from "next/navigation";

type WorkspaceRolePageProps = {
  params: Promise<{
    role: string;
  }>;
};

export function generateStaticParams() {
  return WORKSPACE_ROLES.map((role) => ({ role }));
}

export async function generateMetadata({ params }: WorkspaceRolePageProps): Promise<Metadata> {
  const { role } = await params;

  if (!isWorkspaceRole(role)) {
    return {
      title: "Workspace | Tutor",
      description: "Role-aware workspace slice for Tutor.",
    };
  }

  const config = getRoleConfig(role);

  return {
    title: `${config.label} Workspace | Tutor`,
    description: config.publicPitch,
  };
}

const WorkspaceRolePage = async ({ params }: WorkspaceRolePageProps) => {
  const { role } = await params;

  if (!isWorkspaceRole(role)) {
    notFound();
  }

  return (
    <DefaultLayout>
      <WorkspaceHome />
    </DefaultLayout>
  );
};

export default WorkspaceRolePage;
