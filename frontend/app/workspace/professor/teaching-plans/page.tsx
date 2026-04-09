import DefaultLayout from "@/components/Layouts/DefaultLayout";
import WorkspaceModulePage from "@/components/Workspace/WorkspaceModulePage";

const ProfessorTeachingPlansPage = () => {
  return (
    <DefaultLayout>
      <WorkspaceModulePage
        workspaceRole="professor"
        eyebrow="Professor Teaching Plans"
        title="Teaching plans and instructional iteration"
        description="Use this role-native route to enter the current upskilling surfaces while keeping teaching-plan work anchored in the professor workspace."
        links={[
          {
            label: "Open teaching plans",
            description: "Continue the existing upskilling flow for plan analysis and revision.",
            href: "/upskilling",
            kind: "primary",
          },
          {
            label: "Open configuration",
            description:
              "Jump to current program and rubric configuration when planning needs grounded inputs.",
            href: "/configuration",
          },
          {
            label: "Back to workspace home",
            description: "Return to the faculty snapshot for the active section.",
            href: "/workspace/professor",
          },
        ]}
        notes={[
          "Teaching-plan analysis remains in the existing upskilling app while the workspace shell provides a role-native entry point.",
          "Faculty can move from snapshot cues into planning work without leaving the professor information architecture.",
          "Configuration stays reachable, but the shell leads with faculty work rather than admin-oriented setup screens.",
        ]}
      />
    </DefaultLayout>
  );
};

export default ProfessorTeachingPlansPage;
