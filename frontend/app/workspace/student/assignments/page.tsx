import DefaultLayout from "@/components/Layouts/DefaultLayout";
import WorkspaceModulePage from "@/components/Workspace/WorkspaceModulePage";

const StudentAssignmentsPage = () => {
  return (
    <DefaultLayout>
      <WorkspaceModulePage
        workspaceRole="student"
        eyebrow="Student Assignments"
        title="Assignments, revisions, and practice"
        description="This student route groups the existing writing and questions surfaces under one assignment-oriented entry point so the shell can stay role-native while the underlying tools remain unchanged."
        links={[
          {
            label: "Open essay review",
            description: "Continue rubric-backed writing work in the existing essays route.",
            href: "/essays",
            kind: "primary",
          },
          {
            label: "Open question practice",
            description:
              "Continue objective and discursive practice from the current questions flow.",
            href: "/questions",
          },
          {
            label: "Back to workspace home",
            description: "Return to the student snapshot and learner-record preview.",
            href: "/workspace/student",
          },
        ]}
        notes={[
          "Assignments now have a stable student-native route instead of relying on direct links from the public shell.",
          "The existing essay and question pages are still the operational surfaces underneath this route.",
          "Backend snapshots can continue to deep-link into these existing routes without changing their URLs.",
        ]}
      />
    </DefaultLayout>
  );
};

export default StudentAssignmentsPage;
