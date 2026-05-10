export type RouteCategory =
  | "public"
  | "workspace"
  | "configuration"
  | "adapter"
  | "blocked"
  | "planned";

interface BaseRouteMetadata {
  path: string;
  label: string;
  capability: string;
  audience: string;
  category: RouteCategory;
  notes?: string;
}

export interface ImplementedRouteMetadata extends BaseRouteMetadata {
  status: "implemented";
  category: "public" | "workspace" | "configuration";
  href: string;
  apimPath?: string;
}

export interface AdapterRouteMetadata extends BaseRouteMetadata {
  status: "adapter";
  category: "adapter";
  href: string;
  adaptsTo: string;
}

export interface BlockedRouteMetadata extends BaseRouteMetadata {
  status: "blocked";
  category: "blocked";
  blocker: string;
  requiredBackendContract: readonly string[];
}

export interface PlannedRouteMetadata extends BaseRouteMetadata {
  status: "planned";
  category: "planned";
  dependsOn: readonly string[];
}

export type RouteMetadata =
  | ImplementedRouteMetadata
  | AdapterRouteMetadata
  | BlockedRouteMetadata
  | PlannedRouteMetadata;

export const ROUTE_STATUS_LABELS = {
  implemented: "Implemented",
  adapter: "Adapter",
  blocked: "Blocked",
  planned: "Planned",
} as const satisfies Record<RouteMetadata["status"], string>;

export const ROUTE_CATEGORY_LABELS = {
  public: "Public routes",
  workspace: "Workspace routes",
  configuration: "Configuration routes",
  adapter: "Adapter routes",
  blocked: "Blocked routes",
  planned: "Planned routes",
} as const satisfies Record<RouteCategory, string>;

export const ROUTE_METADATA = [
  {
    status: "implemented",
    category: "public",
    path: "/",
    href: "/",
    label: "Institution front door",
    capability: "Public platform positioning with role-aware workspace entry points.",
    audience: "All pilot users",
  },
  {
    status: "implemented",
    category: "public",
    path: "/avatar",
    href: "/avatar",
    label: "Avatar practice",
    capability: "Student conversation practice backed by avatar cases and speech brokering.",
    audience: "Students and faculty reviewers",
    apimPath: "/api/avatar",
  },
  {
    status: "implemented",
    category: "public",
    path: "/chat",
    href: "/chat",
    label: "Tutor chat",
    capability: "General conversational tutoring and support through the chat service.",
    audience: "All authenticated pilot users",
    apimPath: "/api/chat",
  },
  {
    status: "implemented",
    category: "public",
    path: "/essays",
    href: "/essays",
    label: "Essay work",
    capability: "Essay submission, review queues, and feedback workflows.",
    audience: "Students and professors",
    apimPath: "/api/essays",
  },
  {
    status: "implemented",
    category: "public",
    path: "/questions",
    href: "/questions",
    label: "Question practice",
    capability: "Objective question answering and evaluation feedback.",
    audience: "Students and professors",
    apimPath: "/api/questions",
  },
  {
    status: "implemented",
    category: "public",
    path: "/upskilling",
    href: "/upskilling",
    label: "Teaching-plan review",
    capability: "Faculty upskilling analysis for teaching plans and coaching feedback.",
    audience: "Professors and leaders",
    apimPath: "/api/upskilling",
  },
  {
    status: "implemented",
    category: "public",
    path: "/lms-gateway",
    href: "/lms-gateway",
    label: "LMS gateway",
    capability: "LMS sync readiness, job inspection, and integration operations.",
    audience: "Admins and platform operators",
    apimPath: "/api/lms-gateway",
  },
  {
    status: "implemented",
    category: "public",
    path: "/evaluation",
    href: "/evaluation",
    label: "Evaluation dashboard",
    capability: "Dataset inventory, dataset creation, and evaluation run launch.",
    audience: "Admins and AI governance reviewers",
    apimPath: "/api/evaluation",
  },
  {
    status: "implemented",
    category: "public",
    path: "/evaluation/[runId]",
    href: "/evaluation",
    label: "Evaluation run viewer",
    capability: "Direct inspection of one evaluation run by run identifier.",
    audience: "Admins and AI governance reviewers",
    apimPath: "/api/evaluation/evaluation/run/{run_id}",
    notes: "Open concrete run links from the evaluation dashboard after a run is queued.",
  },
  {
    status: "implemented",
    category: "public",
    path: "/evidence-trust",
    href: "/evidence-trust",
    label: "Evidence and trust",
    capability: "Trust posture, provenance, and degraded-state framing.",
    audience: "Pilot evaluators and leaders",
  },
  {
    status: "implemented",
    category: "public",
    path: "/institutions",
    href: "/institutions",
    label: "Institution framing",
    capability: "Institution-facing narrative and platform positioning.",
    audience: "Decision makers",
  },
  {
    status: "implemented",
    category: "public",
    path: "/programs",
    href: "/programs",
    label: "Program catalog",
    capability: "Curated program framing and role entry points.",
    audience: "Learners and institutional leaders",
  },
  {
    status: "implemented",
    category: "workspace",
    path: "/workspace/[role]",
    href: "/workspace/student",
    label: "Role workspace home",
    capability: "Strategy-configured workspace shells for student, professor, leaders, and admins.",
    audience: "Role-scoped pilot users",
  },
  {
    status: "implemented",
    category: "workspace",
    path: "/workspace/student/learning",
    href: "/workspace/student/learning",
    label: "Student learning",
    capability:
      "Student learning route that adapts existing learning tools into the workspace shell.",
    audience: "Students",
  },
  {
    status: "implemented",
    category: "workspace",
    path: "/workspace/student/assignments",
    href: "/workspace/student/assignments",
    label: "Student assignments",
    capability: "Assignment-centered entry to essay, question, and practice work.",
    audience: "Students",
  },
  {
    status: "implemented",
    category: "workspace",
    path: "/workspace/professor/review",
    href: "/workspace/professor/review",
    label: "Professor review",
    capability: "Faculty review route for essay and question queues.",
    audience: "Professors",
  },
  {
    status: "implemented",
    category: "workspace",
    path: "/workspace/professor/teaching-plans",
    href: "/workspace/professor/teaching-plans",
    label: "Teaching plans",
    capability: "Faculty route for teaching-plan analysis and coaching.",
    audience: "Professors",
    apimPath: "/api/upskilling",
  },
  {
    status: "implemented",
    category: "workspace",
    path: "/workspace/principal/school-health",
    href: "/workspace/principal/school-health",
    label: "School health",
    capability:
      "Principal route for school-unit intelligence, briefing inputs, and conformal-risk governance.",
    audience: "Principals",
    apimPath: "/api/insights/school-unit-intelligence",
  },
  {
    status: "implemented",
    category: "workspace",
    path: "/workspace/supervisor/briefings",
    href: "/workspace/supervisor/briefings",
    label: "Supervisor briefings",
    capability:
      "Network-level briefing review with school-unit intelligence, causal-study drafts, and conformal-risk governance.",
    audience: "Supervisors",
    apimPath: "/api/insights/school-unit-intelligence",
  },
  {
    status: "implemented",
    category: "workspace",
    path: "/workspace/admin/ai-governance",
    href: "/workspace/admin/ai-governance",
    label: "AI governance",
    capability: "Admin shell for evaluation coverage and degraded-state visibility.",
    audience: "Admins",
  },
  {
    status: "implemented",
    category: "workspace",
    path: "/workspace/alumni/record",
    href: "/workspace/alumni/record",
    label: "Alumni record",
    capability:
      "Learner record preview with lifelong-network credentials, portfolio, re-entry, and research governance.",
    audience: "Alumni",
    apimPath: "/api/insights/lifelong-network/{learner_id}",
  },
  {
    status: "implemented",
    category: "configuration",
    path: "/configuration",
    href: "/configuration",
    label: "Configuration hub",
    capability: "Entry point for content, policy, integration, and administrative utilities.",
    audience: "Admins and faculty operators",
  },
  {
    status: "implemented",
    category: "configuration",
    path: "/configuration/cases",
    href: "/configuration/cases",
    label: "Cases management",
    capability: "Create and manage avatar cases, profiles, and steps.",
    audience: "Admins and faculty operators",
    apimPath: "/api/avatar/cases",
  },
  {
    status: "implemented",
    category: "configuration",
    path: "/configuration/themes",
    href: "/configuration/themes",
    label: "Theme management",
    capability: "Manage essay and argumentation themes.",
    audience: "Admins and faculty operators",
    apimPath: "/api/configuration/themes",
  },
  {
    status: "implemented",
    category: "configuration",
    path: "/configuration/questions",
    href: "/configuration/questions",
    label: "Question management",
    capability: "Configure objective questions and related evaluation policy.",
    audience: "Admins and faculty operators",
    apimPath: "/api/questions",
  },
  {
    status: "implemented",
    category: "configuration",
    path: "/configuration/questions/answers",
    href: "/configuration/questions/answers",
    label: "Answer records",
    capability: "Manage answer records used by question evaluation flows.",
    audience: "Admins and faculty operators",
    apimPath: "/api/questions",
  },
  {
    status: "implemented",
    category: "configuration",
    path: "/configuration/questions/graders",
    href: "/configuration/questions/graders",
    label: "Grader definitions",
    capability: "Manage grader agent definitions for question evaluation.",
    audience: "Admins and faculty operators",
    apimPath: "/api/questions",
  },
  {
    status: "implemented",
    category: "configuration",
    path: "/configuration/agents",
    href: "/configuration/agents",
    label: "Agent assemblies",
    capability: "Configure AI agent assemblies, deployment metadata, and instructions.",
    audience: "Admins and AI operators",
  },
  {
    status: "implemented",
    category: "configuration",
    path: "/configuration/supervisor",
    href: "/configuration/supervisor",
    label: "Supervisor setup",
    capability: "School briefing and supervisor read-model utilities.",
    audience: "Leaders and admins",
    apimPath: "/api/insights",
  },
  {
    status: "implemented",
    category: "configuration",
    path: "/configuration/lms-gateway",
    href: "/configuration/lms-gateway",
    label: "LMS gateway utility",
    capability: "Advanced LMS synchronization configuration and inspection.",
    audience: "Admins and platform operators",
    apimPath: "/api/lms-gateway",
  },
  {
    status: "implemented",
    category: "configuration",
    path: "/configuration/upskilling",
    href: "/configuration/upskilling",
    label: "Upskilling utility",
    capability:
      "Configuration-facing utility for teaching-plan analysis and review-required advisory training drafts.",
    audience: "Admins and faculty operators",
    apimPath: "/api/upskilling",
  },
  {
    status: "adapter",
    category: "adapter",
    path: "/configuration/evaluation",
    href: "/configuration/evaluation",
    label: "Evaluation utility adapter",
    capability: "Advanced utility page preserved for direct APIM evaluation checks.",
    audience: "Admins and AI operators",
    adaptsTo: "/evaluation",
    notes: "The mature dashboard lives at /evaluation; this page remains for compatibility.",
  },
  {
    status: "blocked",
    category: "blocked",
    path: "/avatar/settings",
    label: "Avatar settings",
    capability: "User and tenant scoped avatar preferences, voice defaults, and safety settings.",
    audience: "Students, faculty, and admins",
    blocker: "The avatar backend settings contract has not been implemented or approved.",
    requiredBackendContract: [
      "GET /api/avatar/settings returns the effective user and tenant avatar settings.",
      "PUT /api/avatar/settings validates and persists allowed avatar settings changes.",
      "Responses include speech brokering state, default voice/avatar identifiers, and errors.",
    ],
    notes: "No /api/avatar/config endpoint is assumed by the frontend.",
  },
  {
    status: "planned",
    category: "planned",
    path: "/workspace/admin/audit",
    label: "Admin audit review",
    capability: "Tenant-scoped audit, policy evidence, and release readiness review.",
    audience: "Admins and platform operators",
    dependsOn: ["Audit read-model contract", "Workspace navigation prioritization"],
  },
] as const satisfies readonly RouteMetadata[];

export const getRouteMetadata = (path: string): RouteMetadata | undefined =>
  ROUTE_METADATA.find((route) => route.path === path);

export const getRoutesByCategory = (category: RouteCategory): readonly RouteMetadata[] =>
  ROUTE_METADATA.filter((route) => route.category === category);

export const getRoutesByStatus = (status: RouteMetadata["status"]): readonly RouteMetadata[] =>
  ROUTE_METADATA.filter((route) => route.status === status);
