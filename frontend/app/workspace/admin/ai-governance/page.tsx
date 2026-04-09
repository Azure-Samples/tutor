import DefaultLayout from "@/components/Layouts/DefaultLayout";
import WorkspaceModulePage from "@/components/Workspace/WorkspaceModulePage";

const AdminAiGovernancePage = () => {
  return (
    <DefaultLayout>
      <WorkspaceModulePage
        workspaceRole="admin"
        eyebrow="Admin AI Governance"
        title="AI governance, evaluation, and degraded-state review"
        description="Admins can now enter governance work through a role-native route while continuing to use the existing evaluation and configuration pages underneath."
        links={[
          {
            label: "Open evaluation",
            description:
              "Inspect evaluation coverage, runs, and governance readiness in the existing route.",
            href: "/evaluation",
            kind: "primary",
          },
          {
            label: "Open configuration",
            description: "Review operational controls and policy-related configuration.",
            href: "/configuration",
          },
          {
            label: "Back to workspace home",
            description: "Return to the admin snapshot for the active tenant context.",
            href: "/workspace/admin",
          },
        ]}
        notes={[
          "The governance route keeps evaluation work inside the admin information architecture without changing the evaluation URL.",
          "Degraded-state handling remains visible to admins as an operational concern, not just as an implementation detail.",
          "The route is intentionally thin so it can evolve while the existing admin tools continue to operate unchanged.",
        ]}
      />
    </DefaultLayout>
  );
};

export default AdminAiGovernancePage;
