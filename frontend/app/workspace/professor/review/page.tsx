import DefaultLayout from "@/components/Layouts/DefaultLayout";
import WorkspaceModulePage from "@/components/Workspace/WorkspaceModulePage";

const ProfessorReviewPage = () => {
  return (
    <DefaultLayout>
      <WorkspaceModulePage
        workspaceRole="professor"
        eyebrow="Professor Review"
        title="Review queues and feedback work"
        description="Faculty can start from a professor-native review route and then move into the current essays and questions pages for operational work."
        links={[
          {
            label: "Open essay queue",
            description: "Review submissions, rubric feedback, and revision loops.",
            href: "/essays",
            kind: "primary",
          },
          {
            label: "Open question review",
            description:
              "Inspect objective and discursive assessment work in the existing questions route.",
            href: "/questions",
          },
          {
            label: "Back to workspace home",
            description:
              "Return to the backend-driven professor snapshot for this teaching context.",
            href: "/workspace/professor",
          },
        ]}
        notes={[
          "The review route keeps faculty navigation role-native while preserving the existing operational review pages.",
          "Queue state still resolves from the current services; the workspace shell reorganizes entry points around role context.",
          "Faculty advisory cues remain separate from deterministic review counts and queue metadata.",
        ]}
      />
    </DefaultLayout>
  );
};

export default ProfessorReviewPage;
