import type { IconType } from "react-icons";
import {
  FiActivity,
  FiAward,
  FiBarChart2,
  FiBookOpen,
  FiBriefcase,
  FiClipboard,
  FiCompass,
  FiDatabase,
  FiEdit3,
  FiFileText,
  FiFlag,
  FiGlobe,
  FiHome,
  FiLayers,
  FiMessageSquare,
  FiSettings,
  FiShield,
  FiTrendingUp,
  FiUsers,
} from "react-icons/fi";

export const WORKSPACE_ROLES = [
  "student",
  "professor",
  "principal",
  "supervisor",
  "admin",
  "alumni",
] as const;

export type WorkspaceRole = (typeof WORKSPACE_ROLES)[number];

export interface WorkspaceContextOption {
  id: string;
  label: string;
  scope: string;
  note: string;
  role?: WorkspaceRole;
  relationship?: string;
  contextType?: string;
  workspacePath?: string;
  learnerIds?: string[];
  staffIds?: string[];
}

export interface WorkspaceNavItem {
  label: string;
  route: string;
  description: string;
  icon: IconType;
  badge?: string;
  exactMatch?: boolean;
  matchRoutes?: string[];
}

export interface WorkspaceStat {
  label: string;
  value: string;
  detail: string;
}

export interface WorkspaceAction {
  label: string;
  href: string;
  description: string;
  kind: "primary" | "secondary";
}

export interface WorkspaceSectionItem {
  eyebrow: string;
  title: string;
  description: string;
  href?: string;
  tone: "deterministic" | "advisory" | "attention";
}

export interface WorkspaceSection {
  title: string;
  description: string;
  items: WorkspaceSectionItem[];
}

export interface WorkspaceRoleConfig {
  key: WorkspaceRole;
  label: string;
  shortLabel: string;
  workspaceTitle: string;
  publicPitch: string;
  contextLabel: string;
  trustLabel: string;
  personaName: string;
  personaDetail: string;
  contexts: WorkspaceContextOption[];
  navigation: WorkspaceNavItem[];
  hero: {
    eyebrow: string;
    title: string;
    description: string;
  };
  stats: WorkspaceStat[];
  actions: WorkspaceAction[];
  sections: WorkspaceSection[];
  provenance: string;
  advisory: string;
  degraded: string;
}

export interface PublicProgramCard {
  title: string;
  audience: string;
  format: string;
  description: string;
  outcomes: string[];
  href: string;
}

export interface TrustPrinciple {
  title: string;
  description: string;
}

export interface PublicHighlight {
  title: string;
  description: string;
}

export const DEFAULT_WORKSPACE_ROLE: WorkspaceRole = "student";

// Strategy-style role configuration keeps navigation and dashboard behavior data-driven.
const ROLE_CONFIGS: Record<WorkspaceRole, WorkspaceRoleConfig> = {
  student: {
    key: "student",
    label: "Student",
    shortLabel: "Student",
    workspaceTitle: "Student workspace",
    publicPitch:
      "A Today view for guided learning, writing feedback, competency progress, and trusted record growth.",
    contextLabel: "Program and term",
    trustLabel:
      "Deterministic progress, deadlines, and evidence remain primary. Recommendations stay advisory.",
    personaName: "Amelia Ortiz",
    personaDetail: "MBA learner · Writing and analytics pathway",
    contexts: [
      {
        id: "student-mba-spring",
        label: "Executive MBA · Spring 2026",
        scope: "Cohort 3 · Leadership communication",
        note: "Mocked learner context for Wave 1 until relationship-aware auth is connected.",
      },
      {
        id: "student-certificate-reentry",
        label: "Re-entry certificate · Summer pilot",
        scope: "Alumni bridge track · Evidence refresh",
        note: "Use this context to preview how returning learners re-engage without losing their record.",
      },
    ],
    navigation: [
      {
        label: "Today",
        route: "/workspace/student",
        description: "Current priorities, evidence, and next actions.",
        icon: FiHome,
        exactMatch: true,
      },
      {
        label: "Learning",
        route: "/workspace/student/learning",
        description: "Guided coaching, live practice, and supported study.",
        icon: FiBookOpen,
        matchRoutes: ["/avatar", "/chat"],
      },
      {
        label: "Assignments",
        route: "/workspace/student/assignments",
        description: "Essay, revision, and question work in one queue.",
        icon: FiClipboard,
        matchRoutes: ["/essays", "/questions"],
      },
      {
        label: "Progress",
        route: "/workspace/student",
        description: "Competency movement, evidence, and milestones.",
        icon: FiTrendingUp,
      },
      {
        label: "Credentials",
        route: "/programs",
        description: "Curated pathways and credential-ready outcomes.",
        icon: FiAward,
      },
    ],
    hero: {
      eyebrow: "Student Today",
      title: "See what matters now, not a wall of disconnected tools.",
      description:
        "Wave 1 organizes current tutoring, writing, and question flows around your learner record, upcoming work, and trusted evidence.",
    },
    stats: [
      {
        label: "Due this week",
        value: "3 items",
        detail: "1 essay revision and 2 question sets are already queued.",
      },
      {
        label: "Evidence added",
        value: "4 entries",
        detail: "Recent essay and coaching events remain visible in the record.",
      },
      {
        label: "Credential progress",
        value: "68%",
        detail: "Your current pathway is on track for the next portfolio checkpoint.",
      },
    ],
    actions: [
      {
        label: "Open essay feedback",
        href: "/essays",
        description: "Continue rubric-backed writing work.",
        kind: "primary",
      },
      {
        label: "Practice questions",
        href: "/questions",
        description: "Move through formative assessment with visible progress.",
        kind: "secondary",
      },
      {
        label: "Meet the learning coach",
        href: "/avatar",
        description: "Use guided support without pretending the coach is authoritative.",
        kind: "secondary",
      },
    ],
    sections: [
      {
        title: "Today queue",
        description:
          "Deterministic summaries stay first so learners know what is due, what changed, and what needs review.",
        items: [
          {
            eyebrow: "Deterministic",
            title: "Essay revision ready for submission",
            description:
              "A writing draft is waiting with rubric-linked feedback and preserved provenance.",
            href: "/essays",
            tone: "deterministic",
          },
          {
            eyebrow: "Deterministic",
            title: "Question set re-opened after yesterday's attempt",
            description: "The next practice block is available with prior results still visible.",
            href: "/questions",
            tone: "deterministic",
          },
          {
            eyebrow: "Attention",
            title: "Record update pending sync",
            description:
              "Wave 1 surfaces timing and degraded states instead of implying data is fully reconciled.",
            tone: "attention",
          },
        ],
      },
      {
        title: "Advisory guidance",
        description:
          "Recommendations are explicitly labelled advisory and never silently change scores, progression, or eligibility.",
        items: [
          {
            eyebrow: "Advisory",
            title: "Revisit argument structure before the next essay review",
            description: "Generated from recent feedback patterns and current rubric criteria.",
            href: "/chat",
            tone: "advisory",
          },
          {
            eyebrow: "Advisory",
            title: "Book a short avatar session for oral rehearsal",
            description: "Suggested because your next milestone includes a live presentation.",
            href: "/avatar",
            tone: "advisory",
          },
        ],
      },
      {
        title: "Record and re-entry framing",
        description:
          "The student shell already hints at the long-lived record that later powers alumni and credential experiences.",
        items: [
          {
            eyebrow: "Deterministic",
            title: "Evidence remains attached to outcomes",
            description:
              "Tutor keeps a visible link between work performed, feedback received, and the milestone it supports.",
            tone: "deterministic",
          },
          {
            eyebrow: "Advisory",
            title: "Portfolio draft support is planned, not authoritative",
            description:
              "Wave 1 shows how AI can assist with narrative framing while keeping the underlying evidence legible.",
            tone: "advisory",
          },
        ],
      },
    ],
    provenance:
      "Every high-impact surface in this workspace points back to a source record, rubric, or workflow status.",
    advisory:
      "Recommendations are advisory only. They do not update grades, milestones, or credential state without a separate deterministic step.",
    degraded:
      "If a scoring or coaching flow falls back, Tutor labels the result as degraded and suppresses authoritative language.",
  },
  professor: {
    key: "professor",
    label: "Professor",
    shortLabel: "Professor",
    workspaceTitle: "Professor workspace",
    publicPitch:
      "One place for review queues, cohort progress, content grounding, and intervention-ready teaching plans.",
    contextLabel: "Section and term",
    trustLabel:
      "Review queues and class summaries are deterministic first. Any AI cue remains a draft to be confirmed by faculty.",
    personaName: "Dr. Helena Costa",
    personaDetail: "Faculty lead · Executive writing studio",
    contexts: [
      {
        id: "professor-writing-a",
        label: "Writing Studio · Section A",
        scope: "Term 2 · 34 learners",
        note: "Mocked faculty context showing how section-specific navigation will behave once auth lands.",
      },
      {
        id: "professor-capstone",
        label: "Capstone advising cluster",
        scope: "MBA · Portfolio review",
        note: "Use this context to preview faculty intervention and portfolio oversight flows.",
      },
    ],
    navigation: [
      {
        label: "Home",
        route: "/workspace/professor",
        description: "Section health, review pressure, and next actions.",
        icon: FiHome,
        exactMatch: true,
      },
      {
        label: "Review",
        route: "/workspace/professor/review",
        description: "Essay and question work needing faculty attention.",
        icon: FiFileText,
        matchRoutes: ["/essays", "/questions"],
      },
      {
        label: "Content",
        route: "/configuration",
        description: "Program setup, rubric inputs, and content controls.",
        icon: FiLayers,
        matchRoutes: [
          "/configuration/questions",
          "/configuration/questions/answers",
          "/configuration/questions/graders",
        ],
      },
      {
        label: "Cohort progress",
        route: "/workspace/professor",
        description: "Progress and risk framing for the active section.",
        icon: FiBarChart2,
      },
      {
        label: "Interventions",
        route: "/workspace/professor",
        description: "Faculty-owned next steps and learner follow-through.",
        icon: FiFlag,
      },
      {
        label: "Teaching plans",
        route: "/workspace/professor/teaching-plans",
        description: "Structured teaching-plan analysis and iteration.",
        icon: FiCompass,
        matchRoutes: ["/upskilling"],
      },
    ],
    hero: {
      eyebrow: "Professor Home",
      title: "Review, cohort insight, and teaching action in one calm shell.",
      description:
        "Wave 1 reframes today's essays, questions, and upskilling capabilities as faculty work rather than service launchers.",
    },
    stats: [
      {
        label: "Review queue",
        value: "18 items",
        detail: "Essay and question work is grouped by urgency, not by tool name.",
      },
      {
        label: "At-risk learners",
        value: "5 learners",
        detail: "Deterministic indicators drive this count before any advisory ranking.",
      },
      {
        label: "Plan updates",
        value: "2 drafts",
        detail: "Teaching plans are awaiting faculty review after advisory analysis.",
      },
    ],
    actions: [
      {
        label: "Open review queue",
        href: "/essays",
        description: "Start from current submissions and feedback cycles.",
        kind: "primary",
      },
      {
        label: "Open question review",
        href: "/questions",
        description: "See the latest objective and discursive work.",
        kind: "secondary",
      },
      {
        label: "Open teaching plans",
        href: "/upskilling",
        description: "Continue structured planning and coaching work.",
        kind: "secondary",
      },
    ],
    sections: [
      {
        title: "Deterministic class view",
        description:
          "Faculty should start from the things that are undeniably true: queue state, learner status, and section context.",
        items: [
          {
            eyebrow: "Deterministic",
            title: "Section A now has 7 essay revisions awaiting review",
            description: "The queue is preserved even if advisory services are unavailable.",
            href: "/essays",
            tone: "deterministic",
          },
          {
            eyebrow: "Deterministic",
            title: "Question completion dipped for one subgroup",
            description:
              "The underlying completion data stays visible before narrative interpretation.",
            href: "/questions",
            tone: "deterministic",
          },
        ],
      },
      {
        title: "Advisory intervention cues",
        description:
          "Tutor can rank and summarize likely attention points, but faculty judgment remains the active control surface.",
        items: [
          {
            eyebrow: "Advisory",
            title: "Consider a short feedback clinic before the next milestone",
            description: "Suggested from rubric drift and repeated revision patterns.",
            href: "/chat",
            tone: "advisory",
          },
          {
            eyebrow: "Advisory",
            title: "Use upskilling review before publishing the next sequence",
            description: "The plan draft indicates complexity may exceed the current cohort pace.",
            href: "/upskilling",
            tone: "advisory",
          },
        ],
      },
      {
        title: "Grounding and trust",
        description:
          "Rubric and content grounding are part of the interface, not buried inside a black box.",
        items: [
          {
            eyebrow: "Attention",
            title: "One queue item is in degraded mode",
            description:
              "Tutor shows that a fallback path ran and avoids presenting the result as final feedback.",
            href: "/evaluation",
            tone: "attention",
          },
          {
            eyebrow: "Deterministic",
            title: "Configuration stays accessible without dominating the faculty shell",
            description:
              "Admin-heavy setup still works, but faculty navigation now leads with work and outcomes.",
            href: "/configuration",
            tone: "deterministic",
          },
        ],
      },
    ],
    provenance:
      "Faculty-facing summaries link back to rubrics, queue state, and cohort indicators that can be inspected directly.",
    advisory: "Tutor can suggest priorities, but interventions remain faculty-owned decisions.",
    degraded:
      "When a review artifact is degraded, the shell marks it and routes attention to validation rather than hiding the uncertainty.",
  },
  principal: {
    key: "principal",
    label: "Principal",
    shortLabel: "Principal",
    workspaceTitle: "Principal workspace",
    publicPitch:
      "A school-facing home for health indicators, intervention watchlists, and grounded narrative briefings.",
    contextLabel: "School year and program",
    trustLabel:
      "Narratives sit on top of deterministic school indicators and stay visibly grounded.",
    personaName: "Marcos Azevedo",
    personaDetail: "School leader · Institutional pilot",
    contexts: [
      {
        id: "principal-campus-north",
        label: "Aurora Campus North",
        scope: "2026 school year · Leadership pathway",
        note: "Mocked school-scoped context standing in for relationship-aware leader access.",
      },
      {
        id: "principal-prof-dev",
        label: "Staff development pilot",
        scope: "Quarter 2 · Teaching quality initiative",
        note: "Use this context to preview program-level oversight and support.",
      },
    ],
    navigation: [
      {
        label: "Home",
        route: "/workspace/principal",
        description: "School health, interventions, and briefings.",
        icon: FiHome,
        exactMatch: true,
      },
      {
        label: "School health",
        route: "/workspace/principal/school-health",
        description: "Current school indicators and briefing inputs.",
        icon: FiActivity,
        matchRoutes: ["/configuration/supervisor"],
      },
      {
        label: "Programs",
        route: "/workspace/principal",
        description: "Program-level milestones and performance framing.",
        icon: FiLayers,
      },
      {
        label: "Interventions",
        route: "/workspace/principal",
        description: "Priority watchlist and follow-through.",
        icon: FiFlag,
      },
      {
        label: "Staff development",
        route: "/upskilling",
        description: "Faculty growth plans and support loops.",
        icon: FiUsers,
      },
    ],
    hero: {
      eyebrow: "Principal Home",
      title: "Lead from evidence, not dashboard sprawl.",
      description:
        "The principal slice emphasizes school health, intervention cues, and narrative support grounded in deterministic indicators.",
    },
    stats: [
      {
        label: "Programs on watch",
        value: "2 programs",
        detail:
          "Tutor elevates them because underlying participation and review signals have shifted.",
      },
      {
        label: "Intervention reviews",
        value: "6 cases",
        detail: "Leader action stays visible and distinct from advisory suggestions.",
      },
      {
        label: "Briefing freshness",
        value: "Updated 4h ago",
        detail: "Source timing is visible so leaders know what is current.",
      },
    ],
    actions: [
      {
        label: "Open school briefings",
        href: "/configuration/supervisor",
        description: "Inspect narrative and school indicator inputs.",
        kind: "primary",
      },
      {
        label: "Open staff development",
        href: "/upskilling",
        description: "Review teaching-plan and support activity.",
        kind: "secondary",
      },
      {
        label: "Review trust posture",
        href: "/evidence-trust",
        description: "See provenance and degraded-state expectations.",
        kind: "secondary",
      },
    ],
    sections: [
      {
        title: "School health",
        description:
          "Deterministic read models come first so leadership decisions do not depend on narrative alone.",
        items: [
          {
            eyebrow: "Deterministic",
            title: "Writing completion slowed in one program cluster",
            description:
              "Underlying completion indicators are surfaced before any generated summary.",
            href: "/configuration/supervisor",
            tone: "deterministic",
          },
          {
            eyebrow: "Deterministic",
            title: "Faculty plan review cadence improved this week",
            description: "Staff development progress is visible alongside learner outcomes.",
            href: "/upskilling",
            tone: "deterministic",
          },
        ],
      },
      {
        title: "Narrative support",
        description:
          "Narratives help leaders move faster, but the shell keeps those narratives explicitly grounded and inspectable.",
        items: [
          {
            eyebrow: "Advisory",
            title: "Briefing suggests a targeted writing-support visit",
            description: "This suggestion is based on recent rubric and participation shifts.",
            href: "/configuration/supervisor",
            tone: "advisory",
          },
          {
            eyebrow: "Advisory",
            title: "Recommended talking points for the next faculty check-in",
            description: "Use as a starting point, not as final institutional judgment.",
            tone: "advisory",
          },
        ],
      },
      {
        title: "Governance posture",
        description:
          "The leader shell makes data freshness, provenance, and degraded state visible because those are decision-quality issues.",
        items: [
          {
            eyebrow: "Attention",
            title: "One briefing source is delayed",
            description:
              "The shell preserves the delay signal rather than masking it behind a polished summary.",
            tone: "attention",
          },
        ],
      },
    ],
    provenance:
      "Leadership summaries remain linked to school indicators and source timing so humans can challenge them quickly.",
    advisory:
      "Narrative briefings are advisory accelerators for human action, not autonomous institutional decisions.",
    degraded:
      "Degraded leadership outputs suppress high-confidence language and expose the affected source path.",
  },
  supervisor: {
    key: "supervisor",
    label: "Supervisor",
    shortLabel: "Supervisor",
    workspaceTitle: "Supervisor workspace",
    publicPitch:
      "A network-level view of schools, visit preparation, alerts, and narrative briefings with explicit trust framing.",
    contextLabel: "Region and reporting period",
    trustLabel:
      "Comparisons, alerts, and briefings remain visibly tied to network scope and source freshness.",
    personaName: "Renata Mendes",
    personaDetail: "Regional supervisor · School network oversight",
    contexts: [
      {
        id: "supervisor-north-network",
        label: "North network",
        scope: "12 schools · April visit cycle",
        note: "Mocked supervisory scope that will later be resolved from network and school relationships.",
      },
      {
        id: "supervisor-literacy-pilot",
        label: "Literacy pilot cohort",
        scope: "5 schools · Targeted intervention window",
        note: "Use this context to preview scoped trend and visit planning behavior.",
      },
    ],
    navigation: [
      {
        label: "Home",
        route: "/workspace/supervisor",
        description: "Network summary, visit prep, and current alerts.",
        icon: FiHome,
        exactMatch: true,
      },
      {
        label: "Schools",
        route: "/configuration/supervisor",
        description: "School-scoped briefings and profiles.",
        icon: FiGlobe,
      },
      {
        label: "Briefings",
        route: "/workspace/supervisor/briefings",
        description: "Narrative briefings layered over read models.",
        icon: FiFileText,
        matchRoutes: ["/configuration/supervisor"],
      },
      {
        label: "Visits",
        route: "/workspace/supervisor",
        description: "Preparation cues and open visit tasks.",
        icon: FiBriefcase,
      },
      {
        label: "Trends",
        route: "/workspace/supervisor",
        description: "Network-level movement and watch areas.",
        icon: FiTrendingUp,
      },
      {
        label: "Alerts",
        route: "/workspace/supervisor",
        description: "Escalations, sync delays, and validation needs.",
        icon: FiFlag,
      },
    ],
    hero: {
      eyebrow: "Supervisor Home",
      title: "Move from school-by-school searching to scoped network oversight.",
      description:
        "The first supervisor slice packages current insight capabilities into a role-native workspace with transparent trust messaging.",
    },
    stats: [
      {
        label: "Schools requiring follow-up",
        value: "4 schools",
        detail: "Escalations are derived from current scoped indicators, not hidden heuristics.",
      },
      {
        label: "Visit packets ready",
        value: "3 packets",
        detail: "Briefings and supporting evidence are available for immediate review.",
      },
      {
        label: "Active alerts",
        value: "5 alerts",
        detail: "This includes degraded summaries and delayed indicator feeds.",
      },
    ],
    actions: [
      {
        label: "Open school briefings",
        href: "/configuration/supervisor",
        description: "Inspect current network and school narratives.",
        kind: "primary",
      },
      {
        label: "Review evidence and trust",
        href: "/evidence-trust",
        description: "Reconfirm how degraded states are surfaced.",
        kind: "secondary",
      },
      {
        label: "View institution framing",
        href: "/institutions",
        description: "See how this slice fits the broader platform direction.",
        kind: "secondary",
      },
    ],
    sections: [
      {
        title: "Scoped network view",
        description:
          "Supervisor experiences depend on clear scope boundaries, so this shell makes region and school context explicit.",
        items: [
          {
            eyebrow: "Deterministic",
            title: "One school cluster is slipping on task completion",
            description:
              "The comparison is preserved as a read-model signal with context visible in the shell.",
            href: "/configuration/supervisor",
            tone: "deterministic",
          },
          {
            eyebrow: "Deterministic",
            title: "Visit cycle now includes two high-priority schools",
            description:
              "Scheduling and visit support remain deterministic even when narrative services are unavailable.",
            tone: "deterministic",
          },
        ],
      },
      {
        title: "Narrative acceleration",
        description:
          "Briefings can help supervisors read faster, but they never erase the underlying evidence or source health.",
        items: [
          {
            eyebrow: "Advisory",
            title: "Suggested visit framing for the next school review",
            description:
              "Use this to prepare, then confirm it against the school profile and current evidence.",
            href: "/configuration/supervisor",
            tone: "advisory",
          },
          {
            eyebrow: "Attention",
            title: "One summary is degraded after a source delay",
            description:
              "Tutor preserves the degradation flag and avoids authoritative intervention labels.",
            tone: "attention",
          },
        ],
      },
      {
        title: "Operational trust",
        description:
          "Supervision is high-governance work, so provenance and degraded-state visibility are part of the default shell.",
        items: [
          {
            eyebrow: "Deterministic",
            title: "All scoped summaries show source freshness",
            description:
              "Leaders can see whether they are looking at same-day or lagged information.",
            tone: "deterministic",
          },
        ],
      },
    ],
    provenance:
      "Every briefing card needs a visible path back to school scope, source health, and supporting indicators.",
    advisory:
      "Supervisor recommendations stay advisory and never perform interventions on their own.",
    degraded:
      "If a briefing degrades, Tutor suppresses risk labels and routes attention to the affected source path.",
  },
  admin: {
    key: "admin",
    label: "Admin",
    shortLabel: "Admin",
    workspaceTitle: "Admin workspace",
    publicPitch:
      "An operations shell for programs, users, integrations, audit posture, and AI governance visibility.",
    contextLabel: "Tenant and environment",
    trustLabel:
      "The admin slice surfaces policy, evaluation, and degraded-state signals as operational concerns, not hidden implementation details.",
    personaName: "Luciana Vieira",
    personaDetail: "Platform administrator · Governance and operations",
    contexts: [
      {
        id: "admin-main-tenant",
        label: "Tutor pilot tenant",
        scope: "Production-like workspace · Higher-ed pilot",
        note: "Mocked tenant context for Wave 1 until tenant and relationship resolution is available.",
      },
      {
        id: "admin-prep-env",
        label: "Readiness environment",
        scope: "Validation and policy checks",
        note: "Use this context to preview environment-scoped operational views.",
      },
    ],
    navigation: [
      {
        label: "Home",
        route: "/workspace/admin",
        description: "Operational posture, incidents, and pending admin action.",
        icon: FiHome,
        exactMatch: true,
      },
      {
        label: "Programs",
        route: "/configuration",
        description: "Program and platform configuration surfaces.",
        icon: FiLayers,
      },
      {
        label: "Users",
        route: "/configuration/cases",
        description: "Access and workflow-adjacent setup.",
        icon: FiUsers,
      },
      {
        label: "Integrations",
        route: "/lms-gateway",
        description: "Gateway operations and sync posture.",
        icon: FiDatabase,
      },
      {
        label: "Policies",
        route: "/configuration/questions",
        description: "Question, grading, and rules configuration.",
        icon: FiSettings,
      },
      {
        label: "AI governance",
        route: "/workspace/admin/ai-governance",
        description: "Evaluation coverage and degraded-state visibility.",
        icon: FiShield,
        matchRoutes: ["/evaluation"],
      },
    ],
    hero: {
      eyebrow: "Admin Home",
      title: "Operate the platform with governance in view, not off to the side.",
      description:
        "Wave 1 collects today's config, gateway, and evaluation routes under a role-native operations shell without changing those endpoints.",
    },
    stats: [
      {
        label: "Policy checks",
        value: "3 pending",
        detail: "Governance review remains visible alongside runtime activity.",
      },
      {
        label: "Sync health",
        value: "92%",
        detail: "Gateway activity and readiness cues remain one click away.",
      },
      {
        label: "Degraded incidents",
        value: "2 open",
        detail: "The shell treats degraded AI outputs as operational signals worth attention.",
      },
    ],
    actions: [
      {
        label: "Open integrations",
        href: "/lms-gateway",
        description: "Check synchronization and gateway operations.",
        kind: "primary",
      },
      {
        label: "Open evaluation",
        href: "/evaluation",
        description: "Inspect evaluation runs and governance readiness.",
        kind: "secondary",
      },
      {
        label: "Open configuration",
        href: "/configuration",
        description: "Adjust current operational settings without leaving the shell concept.",
        kind: "secondary",
      },
    ],
    sections: [
      {
        title: "Operations posture",
        description:
          "The admin workspace starts with system state, not hidden service implementation details.",
        items: [
          {
            eyebrow: "Deterministic",
            title: "Gateway sync completed for the active pilot",
            description: "Operational surfaces remain usable in the existing route structure.",
            href: "/lms-gateway",
            tone: "deterministic",
          },
          {
            eyebrow: "Deterministic",
            title: "Question policy configuration changed this morning",
            description:
              "Admins can still reach current setup routes while the shell changes around them.",
            href: "/configuration/questions",
            tone: "deterministic",
          },
        ],
      },
      {
        title: "Governance and evaluation",
        description:
          "High-impact AI work needs evaluation and explicit degraded handling, so those signals live in the shell itself.",
        items: [
          {
            eyebrow: "Advisory",
            title: "Review evaluation coverage before expanding faculty access",
            description:
              "The shell highlights this as a readiness suggestion, not an automated release gate.",
            href: "/evaluation",
            tone: "advisory",
          },
          {
            eyebrow: "Attention",
            title: "A degraded path was exposed in a current pilot flow",
            description:
              "Admins see degraded state counts instead of discovering them only through logs.",
            href: "/evaluation",
            tone: "attention",
          },
        ],
      },
      {
        title: "Platform direction",
        description:
          "This shell previews how admin work will eventually include program, user, integration, policy, and audit domains.",
        items: [
          {
            eyebrow: "Deterministic",
            title: "Wave 1 remains intentionally narrow",
            description:
              "No auth or route migration is faked here. Current endpoints remain unchanged.",
            tone: "deterministic",
          },
        ],
      },
    ],
    provenance:
      "Operational surfaces expose where outputs came from and whether evaluation or degraded states affect confidence.",
    advisory:
      "Readiness suggestions help admins prioritize, but policy and release decisions remain human-controlled.",
    degraded:
      "Degraded-state counts are visible in the shell so admins can respond before trust issues become user surprises.",
  },
  alumni: {
    key: "alumni",
    label: "Alumni",
    shortLabel: "Alumni",
    workspaceTitle: "Alumni workspace",
    publicPitch:
      "A durable record-and-re-entry view for credentials, pathways, mentoring, and return-to-learning opportunities.",
    contextLabel: "Affiliation and pathway",
    trustLabel:
      "The alumni slice treats the learner record and credential evidence as durable assets that outlive a single term.",
    personaName: "Paulo Nogueira",
    personaDetail: "Alumni mentor · Career re-entry pathway",
    contexts: [
      {
        id: "alumni-mba-2024",
        label: "MBA 2024 cohort",
        scope: "Credential and portfolio view",
        note: "Mocked alumni affiliation demonstrating persistent access to records and outcomes.",
      },
      {
        id: "alumni-reskill-analytics",
        label: "Analytics re-entry pathway",
        scope: "Short-form continuing education",
        note: "Use this context to preview curated re-engagement instead of a marketplace sprawl.",
      },
    ],
    navigation: [
      {
        label: "Home",
        route: "/workspace/alumni",
        description: "Record, pathways, and re-engagement cues.",
        icon: FiHome,
        exactMatch: true,
      },
      {
        label: "Record",
        route: "/workspace/alumni/record",
        description: "Persistent evidence and achievement timeline.",
        icon: FiFileText,
      },
      {
        label: "Credentials",
        route: "/programs",
        description: "Credential framing and next eligible outcomes.",
        icon: FiAward,
      },
      {
        label: "Pathways",
        route: "/programs",
        description: "Curated re-entry and continuing-learning offers.",
        icon: FiCompass,
      },
      {
        label: "Career",
        route: "/workspace/alumni",
        description: "Role of the record in re-skilling and advancement.",
        icon: FiBriefcase,
      },
      {
        label: "Mentoring",
        route: "/workspace/alumni",
        description: "Community and mentoring positioning for later waves.",
        icon: FiUsers,
      },
    ],
    hero: {
      eyebrow: "Alumni Home",
      title: "Keep a trusted academic record alive after graduation.",
      description:
        "The alumni slice previews how Tutor can extend beyond coursework into credentials, mentoring, and curated re-entry pathways.",
    },
    stats: [
      {
        label: "Credential-ready evidence",
        value: "12 entries",
        detail: "Wave 1 frames how portable outcomes can remain visible over time.",
      },
      {
        label: "Re-entry options",
        value: "3 curated tracks",
        detail: "This remains a curated pilot, not a broad marketplace.",
      },
      {
        label: "Mentoring opportunities",
        value: "2 matches",
        detail:
          "Community and mentoring are positioned for later waves without pretending they are fully implemented now.",
      },
    ],
    actions: [
      {
        label: "Explore curated programs",
        href: "/programs",
        description: "See re-entry pathways and continuing-learning options.",
        kind: "primary",
      },
      {
        label: "Review evidence and trust",
        href: "/evidence-trust",
        description: "Understand how provenance and degraded states will apply to record surfaces.",
        kind: "secondary",
      },
      {
        label: "See institution view",
        href: "/institutions",
        description: "Preview the institutional framing behind lifelong record continuity.",
        kind: "secondary",
      },
    ],
    sections: [
      {
        title: "Durable record",
        description:
          "The alumni slice emphasizes that evidence, feedback, and achievements should outlast a single course shell.",
        items: [
          {
            eyebrow: "Deterministic",
            title: "Prior achievements stay attached to evidence",
            description:
              "Tutor's record framing remains the anchor for future credential and re-entry experiences.",
            tone: "deterministic",
          },
          {
            eyebrow: "Deterministic",
            title: "Credential posture remains inspectable",
            description:
              "Wave 1 shows the shape of a future wallet without claiming issuance is complete.",
            tone: "deterministic",
          },
        ],
      },
      {
        title: "Re-entry and career framing",
        description: "Alumni work is curated and outcomes-oriented, not a generic catalog dump.",
        items: [
          {
            eyebrow: "Advisory",
            title: "Analytics refresher pathway may fit your current profile",
            description: "Suggested from mock alumni context and current pilot offerings.",
            href: "/programs",
            tone: "advisory",
          },
          {
            eyebrow: "Advisory",
            title: "Mentoring opportunity aligned to your prior pathway",
            description:
              "Future community logic is previewed as guidance, not as an active matching system.",
            tone: "advisory",
          },
        ],
      },
      {
        title: "Trust and portability",
        description:
          "The lifelong-learning story depends on trusted record continuity, so provenance and evidence remain visible.",
        items: [
          {
            eyebrow: "Attention",
            title: "Portfolio narrative generation is still advisory",
            description:
              "Tutor can help draft, but the evidence itself remains the authoritative artifact.",
            tone: "attention",
          },
        ],
      },
    ],
    provenance:
      "Record, credential, and re-entry surfaces are only trustworthy if evidence remains visible and portable.",
    advisory:
      "Career and re-entry guidance remains advisory and cannot silently alter record or credential state.",
    degraded:
      "If any narrative aid degrades, Tutor keeps the durable record visible and downgrades the generated layer.",
  },
};

export const ROLE_CONFIG_LIST = WORKSPACE_ROLES.map((role) => ROLE_CONFIGS[role]);

export const PUBLIC_NAV_LINKS = [
  { label: "Programs", href: "/programs" },
  { label: "Evidence & Trust", href: "/evidence-trust" },
  { label: "For Institutions", href: "/institutions" },
];

export const PUBLIC_HIGHLIGHTS: PublicHighlight[] = [
  {
    title: "Learner record at the center",
    description:
      "Tutor is repositioning around evidence, outcomes, and continuity rather than isolated feature demos.",
  },
  {
    title: "Curated programs and re-entry",
    description:
      "The public front door now emphasizes curated pathways for current learners and returning alumni.",
  },
  {
    title: "Visible trust boundaries",
    description:
      "Deterministic data stays primary, advisory guidance is labelled, and degraded states are never hidden.",
  },
];

export const PUBLIC_PROGRAMS: PublicProgramCard[] = [
  {
    title: "Executive Writing and Leadership Studio",
    audience: "MBA and executive education",
    format: "8-week curated pathway",
    description:
      "Combines writing review, guided tutoring, and portfolio-ready evidence for leadership communication work.",
    outcomes: ["Rubric-backed feedback", "Progress snapshots", "Portfolio-ready evidence"],
    href: "/workspace/student",
  },
  {
    title: "Alumni Re-entry: Data-Informed Teaching",
    audience: "Returning professionals and alumni",
    format: "Curated refresher offering",
    description:
      "A narrow pilot for learners who need to refresh teaching, analytics, and evidence-backed practice without starting over.",
    outcomes: ["Persistent learner record", "Curated re-entry", "Continuing-learning framing"],
    href: "/workspace/alumni",
  },
  {
    title: "School Improvement Briefing Pilot",
    audience: "Principals and supervisors",
    format: "Scoped institutional pilot",
    description:
      "Surfaces school and network briefings with deterministic indicators, narrative support, and visible degraded-state handling.",
    outcomes: ["Scoped briefings", "Visit preparation", "Trust-first summaries"],
    href: "/workspace/supervisor",
  },
];

export const TRUST_PRINCIPLES: TrustPrinciple[] = [
  {
    title: "Deterministic summaries first",
    description:
      "Queues, context, evidence, and status come before any generated narrative or recommendation layer.",
  },
  {
    title: "Advisory means advisory",
    description:
      "Tutor can suggest next steps, but it does not silently change scores, progression, interventions, or credential status.",
  },
  {
    title: "Degraded states stay visible",
    description:
      "If an orchestration path falls back or source data is delayed, the shell exposes that condition instead of hiding it.",
  },
  {
    title: "Institution-owned integration posture",
    description:
      "Tutor works with LMS, SIS, CRM, analytics, and credential ecosystems without letting those systems dictate the learner-record model.",
  },
];

export const INSTITUTION_PRIORITIES: PublicHighlight[] = [
  {
    title: "Own the learner record",
    description:
      "Keep evidence, outcomes, and longitudinal context inside an institution-owned control plane instead of scattered tool outputs.",
  },
  {
    title: "Reuse current services without cosmetic launcher UI",
    description:
      "Wave 1 preserves existing frontend routes while reorganizing them into role-aware shells and workspaces.",
  },
  {
    title: "Make trust legible to every audience",
    description:
      "Students, faculty, leaders, admins, and alumni should all see where deterministic data ends and advisory help begins.",
  },
];

export function isWorkspaceRole(value: string): value is WorkspaceRole {
  return (WORKSPACE_ROLES as readonly string[]).includes(value);
}

export function getRoleConfig(role: WorkspaceRole): WorkspaceRoleConfig {
  return ROLE_CONFIGS[role];
}

export function getWorkspaceRoleFromPathname(pathname: string | null): WorkspaceRole | null {
  if (!pathname) {
    return null;
  }

  const match = pathname.match(/^\/workspace\/([^/?#]+)/);
  if (!match) {
    return null;
  }

  return isWorkspaceRole(match[1]) ? match[1] : null;
}
