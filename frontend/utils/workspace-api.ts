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

export interface GovernanceAssumption {
  assumption_id: string;
  statement: string;
  category: "data_quality" | "causal" | "model" | "policy" | "access";
  evidence_refs: string[];
  required_for_use: boolean;
}

export interface IntelligenceProvenance {
  source_type: string;
  source_ids: string[];
  generator: string;
  workflow_version: string;
  model: string | null;
  prompt_version?: string | null;
}

export interface UncertaintyMetadata {
  point_estimate: number | null;
  lower_bound: number | null;
  upper_bound: number | null;
  confidence_level: number;
  interval_width: number | null;
  method: string;
  wide: boolean;
  rationale: string;
}

export interface CalibrationMetadata {
  calibration_set_id: string;
  calibrated_at: string;
  method: string;
  sample_count: number;
  expected_coverage: number;
  observed_coverage: number;
}

export interface CoverageMetadata {
  population: string;
  eligible_count: number;
  covered_count: number;
  coverage_rate: number;
  minimum_required: number;
}

export interface DriftMetadata {
  metric_name: string;
  status: "stable" | "watch" | "drifted" | "unknown";
  score: number | null;
  threshold: number | null;
  measured_at: string;
  reference_window: string;
  current_window: string;
}

export interface SuppressionMetadata {
  suppressed: boolean;
  reason:
    | "none"
    | "small_cell"
    | "wide_uncertainty"
    | "low_sample"
    | "low_coverage"
    | "policy"
    | "manual_review";
  minimum_count: number | null;
  observed_count: number | null;
  suppressed_fields: string[];
  rationale: string;
}

export interface IntelligenceReviewState {
  status: "required" | "recommended" | "not_required" | "completed";
  required: boolean;
  summary: string;
  reviewer_id?: string | null;
  reviewed_at?: string | null;
}

export interface AppealState {
  status: "unavailable" | "available" | "requested" | "in_review" | "resolved";
  available: boolean;
  appeal_id?: string | null;
  submitted_at?: string | null;
  resolution_summary?: string | null;
}

export interface AbstentionMetadata {
  abstained: boolean;
  degraded: boolean;
  reason: string | null;
  fallback_behavior: "deterministic_only" | "human_review" | "show_advisory" | "suppress_prediction";
}

export interface IntelligenceGovernanceMetadata {
  provenance: IntelligenceProvenance;
  assumptions: GovernanceAssumption[];
  uncertainty: UncertaintyMetadata;
  calibration: CalibrationMetadata;
  coverage: CoverageMetadata;
  drift: DriftMetadata[];
  suppression: SuppressionMetadata;
  review: IntelligenceReviewState;
  appeal: AppealState;
  abstention: AbstentionMetadata;
  advisory_only: boolean;
  final_decision: boolean;
}

export interface SchoolUnitMetric {
  metric_id: string;
  label: string | null;
  value: number | null;
  sample_count: number;
  status: "visible" | "suppressed";
  suppression: SuppressionMetadata;
}

export interface SchoolUnitIntelligencePayload {
  school_id: string;
  unit_id: string;
  tenant_id: string | null;
  generated_at: string;
  metrics: SchoolUnitMetric[];
  governance: IntelligenceGovernanceMetadata;
}

export interface CausalDagEdge {
  source: string;
  target: string;
}

export interface CausalStudyCommand {
  school_id: string;
  tenant_id?: string | null;
  dag?: string | null;
  dag_edges?: CausalDagEdge[] | null;
  treatment?: string | null;
  outcome?: string | null;
  estimand?: string | null;
  population?: string | null;
  confounders?: string[] | null;
  refutation_checks?: string[] | null;
}

export interface CausalSensitivityCheck {
  check_id: string;
  method: string;
  target: string;
  status: "planned" | "passed" | "needs_review";
  summary: string;
}

export interface CausalRefutationResult {
  check: string;
  status: "passed" | "needs_review";
  result: string;
}

export interface CausalStudyReport {
  study_id: string;
  school_id: string;
  tenant_id: string | null;
  generated_at: string;
  dag: string;
  dag_edges: CausalDagEdge[];
  treatment: string;
  outcome: string;
  estimand: string;
  population: string;
  adjustment_set: string[];
  refutation_checks: string[];
  sensitivity_checks: CausalSensitivityCheck[];
  refutation_results: CausalRefutationResult[];
  effect_estimate: number;
  uncertainty: UncertaintyMetadata;
  governance: IntelligenceGovernanceMetadata;
}

export interface ConformalRiskItem {
  risk_id: string;
  risk_type: "attendance" | "performance" | "engagement" | "completion";
  risk_label: string | null;
  score: number | null;
  sample_count: number;
  uncertainty: UncertaintyMetadata;
  suppression: SuppressionMetadata;
}

export interface ConformalRiskReport {
  learner_id: string;
  context_id: string;
  tenant_id: string | null;
  generated_at: string;
  calibration: CalibrationMetadata;
  coverage: CoverageMetadata;
  drift: DriftMetadata;
  abstention: AbstentionMetadata;
  risks: ConformalRiskItem[];
  governance: IntelligenceGovernanceMetadata;
}

export interface CredentialDefinition {
  credential_id: string;
  title: string;
  issuer_id: string;
  level: string;
  criteria_refs: string[];
  status: "draft" | "active" | "retired";
  version: string;
}

export interface CredentialAward {
  award_id: string;
  credential_id: string;
  learner_id: string;
  awarded_at: string | null;
  status: "pending_review" | "active" | "expired" | "revoked";
  evidence_refs: string[];
  expires_at?: string | null;
}

export interface PortfolioArtifact {
  artifact_id: string;
  learner_id: string;
  title: string;
  artifact_type: string;
  evidence_refs: string[];
  visibility: "private" | "institution" | "public";
  created_at: string;
}

export interface VerificationRequest {
  request_id: string;
  credential_award_id: string;
  requester_type: string;
  requested_at: string;
  status: "requested" | "verified" | "rejected" | "expired";
  purpose: string;
}

export interface AlumniAffiliation {
  affiliation_id: string;
  learner_id: string;
  institution_id: string;
  program_id: string | null;
  status: "active" | "inactive" | "opted_out";
  started_at: string;
}

export interface ReEntryPathway {
  pathway_id: string;
  learner_id: string;
  title: string;
  target_program_id: string;
  readiness: "eligible" | "needs_review" | "not_ready";
  status: "open" | "waitlist" | "closed";
  recommended_steps: string[];
}

export interface MentorRelationship {
  relationship_id: string;
  learner_id: string;
  mentor_id: string;
  status: "proposed" | "active" | "paused" | "ended";
  started_at?: string | null;
  focus_areas: string[];
}

export interface CommunityEvent {
  event_id: string;
  title: string;
  host_id: string;
  starts_at: string;
  status: "scheduled" | "completed" | "cancelled";
  audience: "learners" | "alumni" | "mentors" | "research_participants";
}

export interface ResearchDataset {
  dataset_id: string;
  title: string;
  steward_id: string;
  data_categories: string[];
  de_identified: boolean;
  consent_basis: string;
  retention_until: string;
}

export interface DataUseAgreement {
  agreement_id: string;
  dataset_id: string;
  status: "draft" | "active" | "expired" | "revoked";
  allowed_uses: string[];
  prohibited_uses: string[];
  expires_at: string;
}

export interface DeIdentificationRun {
  run_id: string;
  dataset_id: string;
  method: string;
  completed_at: string;
  residual_risk: "low" | "medium" | "high";
  reviewer_id?: string | null;
}

export interface PublicationApproval {
  approval_id: string;
  dataset_id: string;
  status: "draft" | "review_required" | "approved" | "rejected" | "revoked";
  submitted_at: string;
  reviewer_id?: string | null;
  conditions: string[];
}

export interface LifelongLearnerNetworkPayload {
  learner_id: string;
  context_id: string;
  tenant_id: string | null;
  generated_at: string;
  credential_definitions: CredentialDefinition[];
  credentials: CredentialAward[];
  portfolio_artifacts: PortfolioArtifact[];
  verification_requests: VerificationRequest[];
  alumni_affiliations: AlumniAffiliation[];
  re_entry_pathways: ReEntryPathway[];
  mentor_relationships: MentorRelationship[];
  community_events: CommunityEvent[];
  research_datasets: ResearchDataset[];
  data_use_agreements: DataUseAgreement[];
  de_identification_runs: DeIdentificationRun[];
  publication_approvals: PublicationApproval[];
  data_minimization: Record<string, string>;
  governance: IntelligenceGovernanceMetadata;
}

export interface SchoolUnitIntelligenceOptions {
  schoolId: string;
  unitId?: string | null;
  tenantId?: string | null;
}

export interface GovernedLearnerReportOptions {
  contextId: string;
  tenantId?: string | null;
  schoolId?: string | null;
  sampleCount?: number;
  intervalWidth?: number;
}

export interface LifelongNetworkOptions {
  contextId: string;
  tenantId?: string | null;
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

// Facade pattern: route components call these typed helpers instead of raw service paths.
export async function getSchoolUnitIntelligence(
  options: SchoolUnitIntelligenceOptions,
): Promise<SchoolUnitIntelligencePayload> {
  const response = await insightsApi.get<SchoolUnitIntelligencePayload>("/school-unit-intelligence", {
    params: {
      school_id: options.schoolId,
      unit_id: options.unitId ?? undefined,
      tenant_id: options.tenantId ?? undefined,
    },
  });
  return response.data;
}

export async function createCausalStudy(
  command: CausalStudyCommand,
): Promise<CausalStudyReport> {
  const response = await insightsApi.post<CausalStudyReport>("/causal-studies", command);
  return response.data;
}

export async function getConformalRisk(
  learnerId: string,
  options: GovernedLearnerReportOptions,
): Promise<ConformalRiskReport> {
  const response = await insightsApi.get<ConformalRiskReport>(
    `/conformal-risk/${encodeURIComponent(learnerId)}`,
    {
      params: {
        context_id: options.contextId,
        tenant_id: options.tenantId ?? undefined,
        school_id: options.schoolId ?? undefined,
        sample_count: options.sampleCount ?? undefined,
        interval_width: options.intervalWidth ?? undefined,
      },
    },
  );
  return response.data;
}

export async function getLifelongNetwork(
  learnerId: string,
  options: LifelongNetworkOptions,
): Promise<LifelongLearnerNetworkPayload> {
  const response = await insightsApi.get<LifelongLearnerNetworkPayload>(
    `/lifelong-network/${encodeURIComponent(learnerId)}`,
    {
      params: {
        context_id: options.contextId,
        tenant_id: options.tenantId ?? undefined,
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
