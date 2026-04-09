import DefaultLayout from "@/components/Layouts/DefaultLayout";
import WorkspaceModulePage from "@/components/Workspace/WorkspaceModulePage";

const PrincipalSchoolHealthPage = () => {
  return (
    <DefaultLayout>
      <WorkspaceModulePage
        workspaceRole="principal"
        eyebrow="Principal School Health"
        title="School health and intervention readiness"
        description="This route gives principals a school-health entry point that can still fan into the current supervisor briefing pages and staff development surfaces."
        links={[
          {
            label: "Open school briefings",
            description: "Inspect the current supervisor briefing and school indicator views.",
            href: "/configuration/supervisor",
            kind: "primary",
          },
          {
            label: "Open staff development",
            description:
              "Review teaching and staff-development work in the existing upskilling route.",
            href: "/upskilling",
          },
          {
            label: "Back to workspace home",
            description: "Return to the principal snapshot for this school context.",
            href: "/workspace/principal",
          },
        ]}
        notes={[
          "The route is principal-native, but it still uses the existing supervisor and upskilling pages underneath.",
          "Freshness and trust metadata remain visible in the workspace shell so leaders can judge briefing quality quickly.",
          "The goal is to anchor leadership work in school context, not to create a new detached reporting tool.",
        ]}
      />
    </DefaultLayout>
  );
};

export default PrincipalSchoolHealthPage;
