import DefaultLayout from "@/components/Layouts/DefaultLayout";
import WorkspaceModulePage from "@/components/Workspace/WorkspaceModulePage";

const StudentLearningPage = () => {
  return (
    <DefaultLayout>
      <WorkspaceModulePage
        workspaceRole="student"
        eyebrow="Student Learning"
        title="Guided learning and coaching"
        description="Use the role-native learning route to move between guided coaching, conversation-based practice, and the latest learner-facing priorities without losing the current workspace shell."
        links={[
          {
            label: "Open guided coaching",
            description: "Continue the current coaching flow in the existing avatar experience.",
            href: "/avatar",
            kind: "primary",
          },
          {
            label: "Open learning chat",
            description: "Use the existing chat route for conversation-based study support.",
            href: "/chat",
          },
          {
            label: "Back to workspace home",
            description: "Return to the backend-driven snapshot for this student context.",
            href: "/workspace/student",
          },
        ]}
        notes={[
          "The learning route is role-native, but it still points into the current working coaching and chat pages.",
          "Context selection in the shell continues to come from the backend access-context contract.",
          "Trust posture stays visible in the shell while deterministic and advisory content remain separate.",
        ]}
      />
    </DefaultLayout>
  );
};

export default StudentLearningPage;
