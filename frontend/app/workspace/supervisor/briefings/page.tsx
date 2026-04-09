import DefaultLayout from "@/components/Layouts/DefaultLayout";
import WorkspaceModulePage from "@/components/Workspace/WorkspaceModulePage";

const SupervisorBriefingsPage = () => {
  return (
    <DefaultLayout>
      <WorkspaceModulePage
        workspaceRole="supervisor"
        eyebrow="Supervisor Briefings"
        title="Network briefings and school visits"
        description="Supervisors can start from a briefing-native route and then move into the existing school-report pages without losing the workspace context or trust framing."
        links={[
          {
            label: "Open school briefings",
            description: "Continue into the current supervisor configuration and report views.",
            href: "/configuration/supervisor",
            kind: "primary",
          },
          {
            label: "Review evidence and trust",
            description: "Inspect the trust posture that now accompanies briefings and snapshots.",
            href: "/evidence-trust",
          },
          {
            label: "Back to workspace home",
            description: "Return to the network-level supervisor snapshot.",
            href: "/workspace/supervisor",
          },
        ]}
        notes={[
          "Briefings now have a supervisor-native route instead of depending on direct configuration navigation.",
          "Existing report pages remain the operational detail views for schools and visits.",
          "Trust, freshness, and deep-link metadata now travel with the underlying report payloads as well.",
        ]}
      />
    </DefaultLayout>
  );
};

export default SupervisorBriefingsPage;
