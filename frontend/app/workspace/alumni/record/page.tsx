import DefaultLayout from "@/components/Layouts/DefaultLayout";
import WorkspaceModulePage from "@/components/Workspace/WorkspaceModulePage";

const AlumniRecordPage = () => {
  return (
    <DefaultLayout>
      <WorkspaceModulePage
        workspaceRole="alumni"
        eyebrow="Alumni Record"
        title="Durable record and re-entry pathways"
        description="This alumni route centers the portable learner record and then points into the current curated programs and trust surfaces for re-entry exploration."
        links={[
          {
            label: "Open curated programs",
            description:
              "Explore continuing-learning and re-entry pathways in the existing programs route.",
            href: "/programs",
            kind: "primary",
          },
          {
            label: "Review evidence and trust",
            description: "Inspect provenance and trust posture for portable record experiences.",
            href: "/evidence-trust",
          },
          {
            label: "Back to workspace home",
            description: "Return to the alumni snapshot and learner-record preview.",
            href: "/workspace/alumni",
          },
        ]}
        notes={[
          "The alumni record route keeps durable evidence and re-entry work inside an alumni-native shell.",
          "Existing program pages remain the current operational destination for continuing-learning exploration.",
          "Learner-record previews on the alumni home route come from the backend timeline contract rather than frontend fixtures.",
        ]}
      />
    </DefaultLayout>
  );
};

export default AlumniRecordPage;
