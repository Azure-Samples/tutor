import { configurationApi, insightsApi } from "@/utils/api";
import type { WorkspaceRole } from "@/utils/workspace";

export interface AccessScope {
  institution_ids: string[];
  school_ids: string[];
  program_ids: string[];
  course_ids: string[];
  class_ids: string[];
  learner_ids: string[];
  staff_ids: string[];
}

export interface AccessGrantItem {
  role: string;
  relationship: string;
  scope: AccessScope;
}

export interface AccessContextItem {
  context_id: string;
  role: string;
  context_type: string;
  relationship: string;
  label: string;
  scope: AccessScope;
  workspace_path: string;
}

export interface AccessRoleContext {
  role: string;
  grants: AccessGrantItem[];
  contexts: AccessContextItem[];
  default_context_id: string | null;
}

export interface AccessActor {
  subject: string;
  tenant_id: string;
  object_id: string;
  display_name: string | null;
  email: string | null;
}

export interface AccessContextPayload {
  actor: AccessActor;
  available_roles: string[];
  default_role: string | null;
  default_context: AccessContextItem | null;
  roles: AccessRoleContext[];
  feature_flags: string[];
}

export interface DeepLink {
  label: string;
  href: string;
}

export interface FreshnessMetadata {
  generated_at: string;
  source_updated_at: string | null;
  status: "fresh" | "derived" | "stale" | "degraded";
  note: string;
}

export interface ProvenanceMetadata {
  source_type: string;
  source_ids: string[];
  generator: string;
  workflow_version: string;
  model: string | null;
}

export interface ReviewMetadata {
  status: "required" | "recommended" | "not_required" | "completed";
  summary: string;
}

export interface TrustMetadata {
  provenance: ProvenanceMetadata;
  evaluation_state: "evaluated" | "pending" | "not_required";
  human_review: ReviewMetadata;
  degraded: boolean;
  advisory_only: boolean;
  note: string;
}

export interface SnapshotItem {
  item_id: string;
  tone: "deterministic" | "advisory" | "attention";
  title: string;
  summary: string;
  metric: string | null;
  deep_link: DeepLink;
}

export interface WorkspaceSnapshotPayload {
  role: string;
  context_id: string;
  context_label: string;
  summary: string;
  freshness: FreshnessMetadata;
  trust: TrustMetadata;
  deterministic_highlights: SnapshotItem[];
  advisory_items: SnapshotItem[];
  attention_items: SnapshotItem[];
  deep_links: DeepLink[];
}

export interface TimelineEvidence {
  evidence_id: string;
  label: string;
  kind: string;
  deep_link: DeepLink | null;
}

export interface LearnerRecordEntry {
  record_id: string;
  occurred_at: string;
  event_type: string;
  source_service: string;
  title: string;
  summary: string;
  status: "confirmed" | "advisory" | "degraded" | "needs_review";
  actor_role: string;
  evidence: TimelineEvidence[];
  trust: TrustMetadata;
  deep_link: DeepLink;
}

export interface CursorPage {
  limit: number;
  cursor: string | null;
  next_cursor: string | null;
  has_more: boolean;
}

export interface LearnerRecordTimelinePayload {
  learner_id: string;
  context_id: string;
  context_label: string;
  summary: string;
  freshness: FreshnessMetadata;
  page: CursorPage;
  entries: LearnerRecordEntry[];
  deep_links: DeepLink[];
}

const SCOPE_LABELS = [
  ["institution_ids", "Institution"],
  ["school_ids", "School"],
  ["program_ids", "Program"],
  ["course_ids", "Course"],
  ["class_ids", "Class"],
  ["learner_ids", "Learner"],
  ["staff_ids", "Staff"],
] as const satisfies ReadonlyArray<readonly [keyof AccessScope, string]>;

const PRIMARY_SCOPE_BY_CONTEXT_TYPE: Record<string, keyof AccessScope> = {
  institution: "institution_ids",
  school: "school_ids",
  program: "program_ids",
  course: "course_ids",
  class: "class_ids",
  learner: "learner_ids",
  staff: "staff_ids",
};

export async function getAccessContext(): Promise<AccessContextPayload> {
  const response = await configurationApi.get<AccessContextPayload>("/access-context");
  return response.data;
}

export async function getWorkspaceSnapshot(
  role: WorkspaceRole,
  contextId: string,
): Promise<WorkspaceSnapshotPayload> {
  const response = await insightsApi.get<WorkspaceSnapshotPayload>(
    `/workspace-snapshots/${encodeURIComponent(role)}`,
    {
      params: { context_id: contextId },
    },
  );
  return response.data;
}

export async function getLearnerRecordTimeline(
  learnerId: string,
  options: { contextId: string; limit?: number; cursor?: string | null },
): Promise<LearnerRecordTimelinePayload> {
  const response = await insightsApi.get<LearnerRecordTimelinePayload>(
    `/learner-records/${encodeURIComponent(learnerId)}`,
    {
      params: {
        context_id: options.contextId,
        limit: options.limit,
        cursor: options.cursor ?? undefined,
      },
    },
  );
  return response.data;
}

export function humanizeIdentifier(value: string): string {
  return value
    .replace(/[_:-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

export function summarizeScope(scope: AccessScope, contextType?: string): string {
  const primaryField = contextType ? PRIMARY_SCOPE_BY_CONTEXT_TYPE[contextType] : undefined;
  const parts = SCOPE_LABELS.flatMap(([fieldName, label]) => {
    if (fieldName === primaryField || scope[fieldName].length === 0) {
      return [];
    }

    const preview = scope[fieldName].slice(0, 2).map(humanizeIdentifier).join(", ");
    const suffix = scope[fieldName].length > 2 ? ` +${scope[fieldName].length - 2}` : "";
    return [`${label}: ${preview}${suffix}`];
  });

  if (parts.length > 0) {
    return parts.slice(0, 2).join(" · ");
  }

  if (contextType) {
    return `${humanizeIdentifier(contextType)} context`;
  }

  return "Active scope";
}

export function describeAccessContext(context: AccessContextItem): string {
  const relationship = humanizeIdentifier(context.relationship);
  const scopeSummary = summarizeScope(context.scope, context.context_type);
  return `Resolved from ${relationship} access · ${scopeSummary}`;
}

export function findRoleContext(
  payload: AccessContextPayload | null,
  role: WorkspaceRole,
): AccessRoleContext | null {
  if (!payload) {
    return null;
  }

  return payload.roles.find((item) => item.role === role) ?? null;
}

export function getScopedLearnerId(
  context: Pick<AccessContextItem, "scope"> | null | undefined,
  actor: Pick<AccessActor, "subject"> | null | undefined,
): string | null {
  const scopedLearnerId = context?.scope.learner_ids[0];
  if (scopedLearnerId) {
    return scopedLearnerId;
  }

  return actor?.subject ?? null;
}
