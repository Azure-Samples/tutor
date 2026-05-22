import type { IconType } from "react-icons";
import { DEFAULT_LOCALE, type Locale } from "@/utils/i18n";
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

export type WorkspaceNavMatchStrategy = "exact" | "prefix" | "none";

export interface WorkspaceNavRouteMatch {
  route: string;
  strategy: Exclude<WorkspaceNavMatchStrategy, "none">;
}

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
  matchStrategy?: WorkspaceNavMatchStrategy;
  matchRoutes?: WorkspaceNavRouteMatch[];
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

export interface PublicNavLink {
  label: string;
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

export interface PublicPageContent {
  home: {
    heroEyebrow: string;
    heroTitle: string;
    heroDescription: string;
    primaryCta: string;
    programsCta: string;
    trustCta: string;
    trustPostureEyebrow: string;
    programsEyebrow: string;
    programsTitle: string;
    programCardCta: string;
    rolePreviewsEyebrow: string;
    rolePreviewsTitle: string;
    institutionalEyebrow: string;
    institutionalTitle: string;
    institutionalDescription: string;
    institutionCta: string;
    professorCta: string;
  };
  programs: {
    eyebrow: string;
    title: string;
    description: string;
    cardCta: string;
    limitTitle: string;
    limitDescription: string;
  };
  institutions: {
    eyebrow: string;
    title: string;
    description: string;
    honestyTitle: string;
    honestyDescription: string;
    adminCta: string;
    supervisorCta: string;
  };
  evidenceTrust: {
    eyebrow: string;
    title: string;
    description: string;
    cards: PublicHighlight[];
  };
}

export interface PublicContent {
  navLinks: PublicNavLink[];
  highlights: PublicHighlight[];
  programs: PublicProgramCard[];
  trustPrinciples: TrustPrinciple[];
  institutionPriorities: PublicHighlight[];
  pages: PublicPageContent;
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
        matchStrategy: "exact",
      },
      {
        label: "Learning",
        route: "/workspace/student/learning",
        description: "Guided coaching, live practice, and supported study.",
        icon: FiBookOpen,
        matchRoutes: [
          { route: "/avatar", strategy: "prefix" },
          { route: "/chat", strategy: "prefix" },
        ],
      },
      {
        label: "Assignments",
        route: "/workspace/student/assignments",
        description: "Essay, revision, and question work in one queue.",
        icon: FiClipboard,
        matchRoutes: [
          { route: "/essays", strategy: "prefix" },
          { route: "/questions", strategy: "prefix" },
        ],
      },
      {
        label: "Progress",
        route: "/workspace/student",
        description: "Competency movement, evidence, and milestones.",
        icon: FiTrendingUp,
        matchStrategy: "none",
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
        matchStrategy: "exact",
      },
      {
        label: "Review",
        route: "/workspace/professor/review",
        description: "Essay and question work needing faculty attention.",
        icon: FiFileText,
        matchRoutes: [
          { route: "/essays", strategy: "prefix" },
          { route: "/questions", strategy: "prefix" },
        ],
      },
      {
        label: "Content",
        route: "/configuration",
        description: "Program setup, rubric inputs, and content controls.",
        icon: FiLayers,
        matchStrategy: "exact",
        matchRoutes: [
          { route: "/configuration/questions", strategy: "exact" },
          { route: "/configuration/questions/answers", strategy: "exact" },
          { route: "/configuration/questions/graders", strategy: "exact" },
        ],
      },
      {
        label: "Cohort progress",
        route: "/workspace/professor",
        description: "Progress and risk framing for the active section.",
        icon: FiBarChart2,
        matchStrategy: "none",
      },
      {
        label: "Interventions",
        route: "/workspace/professor",
        description: "Faculty-owned next steps and learner follow-through.",
        icon: FiFlag,
        matchStrategy: "none",
      },
      {
        label: "Teaching plans",
        route: "/workspace/professor/teaching-plans",
        description: "Structured teaching-plan analysis and iteration.",
        icon: FiCompass,
        matchRoutes: [{ route: "/upskilling", strategy: "prefix" }],
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
        matchStrategy: "exact",
      },
      {
        label: "School health",
        route: "/workspace/principal/school-health",
        description: "Current school indicators and briefing inputs.",
        icon: FiActivity,
        matchRoutes: [{ route: "/configuration/supervisor", strategy: "prefix" }],
      },
      {
        label: "Programs",
        route: "/workspace/principal",
        description: "Program-level milestones and performance framing.",
        icon: FiLayers,
        matchStrategy: "none",
      },
      {
        label: "Interventions",
        route: "/workspace/principal",
        description: "Priority watchlist and follow-through.",
        icon: FiFlag,
        matchStrategy: "none",
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
        matchStrategy: "exact",
      },
      {
        label: "Schools",
        route: "/configuration/supervisor",
        description: "School-scoped briefings and profiles.",
        icon: FiGlobe,
        matchStrategy: "prefix",
      },
      {
        label: "Briefings",
        route: "/workspace/supervisor/briefings",
        description: "Narrative briefings layered over read models.",
        icon: FiFileText,
      },
      {
        label: "Visits",
        route: "/workspace/supervisor",
        description: "Preparation cues and open visit tasks.",
        icon: FiBriefcase,
        matchStrategy: "none",
      },
      {
        label: "Trends",
        route: "/workspace/supervisor",
        description: "Network-level movement and watch areas.",
        icon: FiTrendingUp,
        matchStrategy: "none",
      },
      {
        label: "Alerts",
        route: "/workspace/supervisor",
        description: "Escalations, sync delays, and validation needs.",
        icon: FiFlag,
        matchStrategy: "none",
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
      "An operations shell for Configuration, Avatar cases, Integrations, Policies, and AI governance.",
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
        matchStrategy: "exact",
      },
      {
        label: "Configuration",
        route: "/configuration",
        description: "Content, policy, integration, and admin utility hub.",
        icon: FiLayers,
        matchStrategy: "exact",
      },
      {
        label: "Avatar cases",
        route: "/configuration/cases",
        description: "Practice scenarios, avatar profiles, and case steps.",
        icon: FiMessageSquare,
        matchStrategy: "exact",
      },
      {
        label: "Integrations",
        route: "/configuration/lms-gateway",
        description: "Gateway operations and sync posture.",
        icon: FiDatabase,
        matchStrategy: "exact",
        matchRoutes: [{ route: "/lms-gateway", strategy: "exact" }],
      },
      {
        label: "Policies",
        route: "/configuration/questions",
        description: "Question, grading, and rules configuration.",
        icon: FiSettings,
        matchStrategy: "exact",
        matchRoutes: [
          { route: "/configuration/questions/answers", strategy: "exact" },
          { route: "/configuration/questions/graders", strategy: "exact" },
        ],
      },
      {
        label: "AI governance",
        route: "/workspace/admin/ai-governance",
        description: "Evaluation coverage and degraded-state visibility.",
        icon: FiShield,
        matchStrategy: "exact",
        matchRoutes: [{ route: "/evaluation", strategy: "prefix" }],
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
          "This shell keeps admin work aligned to the available surfaces: Configuration, Avatar cases, Integrations, Policies, and AI governance.",
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
        matchStrategy: "exact",
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
        matchStrategy: "none",
      },
      {
        label: "Career",
        route: "/workspace/alumni",
        description: "Role of the record in re-skilling and advancement.",
        icon: FiBriefcase,
        matchStrategy: "none",
      },
      {
        label: "Mentoring",
        route: "/workspace/alumni",
        description: "Community and mentoring positioning for later waves.",
        icon: FiUsers,
        matchStrategy: "none",
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

type WorkspaceContextCopy = Pick<WorkspaceContextOption, "label" | "scope" | "note">;
type WorkspaceNavItemCopy = Pick<WorkspaceNavItem, "label" | "description" | "badge">;

interface WorkspaceRoleShellCopy {
  label: string;
  shortLabel: string;
  workspaceTitle: string;
  publicPitch: string;
  contextLabel: string;
  trustLabel: string;
  personaName: string;
  personaDetail: string;
  contexts: WorkspaceContextCopy[];
  navigation: WorkspaceNavItemCopy[];
}

const ROLE_CONFIG_SHELL_TRANSLATIONS = {
  es: {
    student: {
      label: "Estudiante",
      shortLabel: "Estudiante",
      workspaceTitle: "Espacio de estudiante",
      publicPitch:
        "Una vista de Hoy para aprendizaje guiado, retroalimentación de escritura, progreso de competencias y crecimiento de un registro confiable.",
      contextLabel: "Programa y período",
      trustLabel:
        "El progreso, los plazos y la evidencia deterministas siguen siendo lo principal. Las recomendaciones son consultivas.",
      personaName: "Amelia Ortiz",
      personaDetail: "Estudiante MBA · Ruta de escritura y analítica",
      contexts: [
        {
          label: "Executive MBA · Primavera 2026",
          scope: "Cohorte 3 · Comunicación de liderazgo",
          note: "Contexto simulado del estudiante para Wave 1 hasta conectar la autenticación con relaciones.",
        },
        {
          label: "Certificado de reingreso · Piloto de verano",
          scope: "Ruta puente de egresados · Actualización de evidencia",
          note: "Usa este contexto para previsualizar cómo los estudiantes que regresan retoman sin perder su registro.",
        },
      ],
      navigation: [
        {
          label: "Hoy",
          description: "Prioridades, evidencia y próximas acciones actuales.",
        },
        {
          label: "Aprendizaje",
          description: "Acompañamiento guiado, práctica en vivo y estudio con apoyo.",
        },
        {
          label: "Tareas",
          description: "Ensayos, revisiones y preguntas en una sola cola.",
        },
        {
          label: "Progreso",
          description: "Movimiento de competencias, evidencia e hitos.",
        },
        {
          label: "Credenciales",
          description: "Rutas curadas y resultados listos para credencial.",
        },
      ],
    },
    professor: {
      label: "Profesor",
      shortLabel: "Profesor",
      workspaceTitle: "Espacio de profesor",
      publicPitch:
        "Un solo lugar para colas de revisión, progreso de cohortes, contenido fundamentado y planes de enseñanza listos para intervención.",
      contextLabel: "Sección y período",
      trustLabel:
        "Las colas de revisión y los resúmenes de clase son primero deterministas. Cualquier señal de IA sigue siendo un borrador que confirma el profesorado.",
      personaName: "Dra. Helena Costa",
      personaDetail: "Líder docente · Estudio ejecutivo de escritura",
      contexts: [
        {
          label: "Estudio de escritura · Sección A",
          scope: "Período 2 · 34 estudiantes",
          note: "Contexto docente simulado que muestra cómo se comportará la navegación por sección cuando llegue la autenticación.",
        },
        {
          label: "Grupo de asesoría de capstone",
          scope: "MBA · Revisión de portafolio",
          note: "Usa este contexto para previsualizar flujos de intervención docente y supervisión de portafolios.",
        },
      ],
      navigation: [
        {
          label: "Inicio",
          description: "Salud de la sección, presión de revisión y próximas acciones.",
        },
        {
          label: "Revisión",
          description: "Ensayos y preguntas que necesitan atención docente.",
        },
        {
          label: "Contenido",
          description: "Configuración del programa, rúbricas y controles de contenido.",
        },
        {
          label: "Progreso de cohorte",
          description: "Progreso y riesgo para la sección activa.",
        },
        {
          label: "Intervenciones",
          description: "Próximos pasos docentes y seguimiento del estudiante.",
        },
        {
          label: "Planes de enseñanza",
          description: "Análisis e iteración estructurados de planes de enseñanza.",
        },
      ],
    },
    principal: {
      label: "Director",
      shortLabel: "Director",
      workspaceTitle: "Espacio de dirección",
      publicPitch:
        "Un inicio para la escuela con indicadores de salud, listas de intervención y briefings narrativos fundamentados.",
      contextLabel: "Año escolar y programa",
      trustLabel:
        "Las narrativas se apoyan en indicadores escolares deterministas y se mantienen visiblemente fundamentadas.",
      personaName: "Marcos Azevedo",
      personaDetail: "Líder escolar · Piloto institucional",
      contexts: [
        {
          label: "Aurora Campus Norte",
          scope: "Año escolar 2026 · Ruta de liderazgo",
          note: "Contexto escolar simulado que representa el acceso de líderes basado en relaciones.",
        },
        {
          label: "Piloto de desarrollo docente",
          scope: "Trimestre 2 · Iniciativa de calidad docente",
          note: "Usa este contexto para previsualizar supervisión y apoyo a nivel de programa.",
        },
      ],
      navigation: [
        {
          label: "Inicio",
          description: "Salud escolar, intervenciones y briefings.",
        },
        {
          label: "Salud escolar",
          description: "Indicadores escolares actuales e insumos para briefing.",
        },
        {
          label: "Programas",
          description: "Hitos de programa y marco de desempeño.",
        },
        {
          label: "Intervenciones",
          description: "Lista de prioridad y seguimiento.",
        },
        {
          label: "Desarrollo docente",
          description: "Planes de crecimiento docente y ciclos de apoyo.",
        },
      ],
    },
    supervisor: {
      label: "Supervisor",
      shortLabel: "Supervisor",
      workspaceTitle: "Espacio de supervisión",
      publicPitch:
        "Una vista de red para escuelas, preparación de visitas, alertas y briefings narrativos con confianza explícita.",
      contextLabel: "Región y período de reporte",
      trustLabel:
        "Comparaciones, alertas y briefings permanecen vinculados al alcance de red y a la frescura de las fuentes.",
      personaName: "Renata Mendes",
      personaDetail: "Supervisora regional · Supervisión de red escolar",
      contexts: [
        {
          label: "Red norte",
          scope: "12 escuelas · Ciclo de visitas de abril",
          note: "Alcance de supervisión simulado que luego se resolverá desde relaciones de red y escuela.",
        },
        {
          label: "Cohorte piloto de alfabetización",
          scope: "5 escuelas · Ventana de intervención focalizada",
          note: "Usa este contexto para previsualizar tendencias acotadas y planificación de visitas.",
        },
      ],
      navigation: [
        {
          label: "Inicio",
          description: "Resumen de red, preparación de visitas y alertas actuales.",
        },
        {
          label: "Escuelas",
          description: "Briefings y perfiles por escuela.",
        },
        {
          label: "Briefings",
          description: "Briefings narrativos sobre modelos de lectura.",
        },
        {
          label: "Visitas",
          description: "Señales de preparación y tareas abiertas de visita.",
        },
        {
          label: "Tendencias",
          description: "Movimiento de red y áreas de seguimiento.",
        },
        {
          label: "Alertas",
          description: "Escalamientos, demoras de sincronización y validaciones.",
        },
      ],
    },
    admin: {
      label: "Administrador",
      shortLabel: "Admin",
      workspaceTitle: "Espacio de administración",
      publicPitch:
        "Un entorno operativo para Configuración, casos de Avatar, Integraciones, Políticas y gobernanza de IA.",
      contextLabel: "Tenant y entorno",
      trustLabel:
        "La vista administrativa expone señales de política, evaluación y estado degradado como asuntos operativos, no detalles ocultos.",
      personaName: "Luciana Vieira",
      personaDetail: "Administradora de plataforma · Gobernanza y operaciones",
      contexts: [
        {
          label: "Tenant piloto de Tutor",
          scope: "Espacio similar a producción · Piloto de educación superior",
          note: "Contexto de tenant simulado para Wave 1 hasta que exista resolución de tenant y relaciones.",
        },
        {
          label: "Entorno de preparación",
          scope: "Validación y controles de política",
          note: "Usa este contexto para previsualizar vistas operativas por entorno.",
        },
      ],
      navigation: [
        {
          label: "Inicio",
          description: "Postura operativa, incidentes y acciones administrativas pendientes.",
        },
        {
          label: "Configuración",
          description: "Centro de contenido, políticas, integración y utilidades administrativas.",
        },
        {
          label: "Casos de Avatar",
          description: "Escenarios de práctica, perfiles de avatar y pasos de casos.",
        },
        {
          label: "Integraciones",
          description: "Operaciones de gateway y postura de sincronización.",
        },
        {
          label: "Políticas",
          description: "Configuración de preguntas, calificación y reglas.",
        },
        {
          label: "Gobernanza de IA",
          description: "Cobertura de evaluación y visibilidad de estados degradados.",
        },
      ],
    },
    alumni: {
      label: "Egresado",
      shortLabel: "Egresado",
      workspaceTitle: "Espacio de egresados",
      publicPitch:
        "Una vista durable de registro y reingreso para credenciales, rutas, mentoría y oportunidades de volver a aprender.",
      contextLabel: "Afiliación y ruta",
      trustLabel:
        "La vista de egresados trata el registro del estudiante y la evidencia de credenciales como activos duraderos que superan un período.",
      personaName: "Paulo Nogueira",
      personaDetail: "Mentor egresado · Ruta de reingreso profesional",
      contexts: [
        {
          label: "Cohorte MBA 2024",
          scope: "Vista de credencial y portafolio",
          note: "Afiliación simulada de egresado que muestra acceso persistente a registros y resultados.",
        },
        {
          label: "Ruta de reentrenamiento en analítica",
          scope: "Educación continua de formato corto",
          note: "Usa este contexto para previsualizar reenganche curado en vez de una experiencia tipo mercado.",
        },
      ],
      navigation: [
        {
          label: "Inicio",
          description: "Registro, rutas y señales de reenganche.",
        },
        {
          label: "Registro",
          description: "Evidencia persistente y línea de tiempo de logros.",
        },
        {
          label: "Credenciales",
          description: "Marco de credenciales y próximos resultados elegibles.",
        },
        {
          label: "Rutas",
          description: "Ofertas curadas de reingreso y aprendizaje continuo.",
        },
        {
          label: "Carrera",
          description: "Papel del registro en recualificación y avance.",
        },
        {
          label: "Mentoría",
          description: "Comunidad y mentoría para olas posteriores.",
        },
      ],
    },
  },
  pt: {
    student: {
      label: "Estudante",
      shortLabel: "Estudante",
      workspaceTitle: "Espaço do estudante",
      publicPitch:
        "Uma visão de Hoje para aprendizagem guiada, feedback de escrita, progresso de competências e crescimento de um registro confiável.",
      contextLabel: "Programa e período",
      trustLabel:
        "Progresso, prazos e evidências determinísticos continuam em primeiro plano. Recomendações seguem consultivas.",
      personaName: "Amelia Ortiz",
      personaDetail: "Estudante de MBA · Trilha de escrita e análise",
      contexts: [
        {
          label: "Executive MBA · Primavera de 2026",
          scope: "Coorte 3 · Comunicação de liderança",
          note: "Contexto simulado do estudante para Wave 1 até a autenticação com relações ser conectada.",
        },
        {
          label: "Certificado de reentrada · Piloto de verão",
          scope: "Trilha ponte de ex-alunos · Atualização de evidências",
          note: "Use este contexto para prever como estudantes que retornam retomam sem perder o registro.",
        },
      ],
      navigation: [
        {
          label: "Hoje",
          description: "Prioridades, evidências e próximas ações atuais.",
        },
        {
          label: "Aprendizagem",
          description: "Orientação guiada, prática ao vivo e estudo apoiado.",
        },
        {
          label: "Tarefas",
          description: "Ensaios, revisões e perguntas em uma única fila.",
        },
        {
          label: "Progresso",
          description: "Movimento de competências, evidências e marcos.",
        },
        {
          label: "Credenciais",
          description: "Trilhas curadas e resultados prontos para credenciais.",
        },
      ],
    },
    professor: {
      label: "Professor",
      shortLabel: "Professor",
      workspaceTitle: "Espaço do professor",
      publicPitch:
        "Um lugar para filas de revisão, progresso da coorte, conteúdo fundamentado e planos de ensino prontos para intervenção.",
      contextLabel: "Turma e período",
      trustLabel:
        "Filas de revisão e resumos de turma são determinísticos primeiro. Qualquer sinal de IA permanece como rascunho a ser confirmado pelo docente.",
      personaName: "Dra. Helena Costa",
      personaDetail: "Líder docente · Estúdio executivo de escrita",
      contexts: [
        {
          label: "Estúdio de escrita · Turma A",
          scope: "Período 2 · 34 estudantes",
          note: "Contexto docente simulado mostrando como a navegação por turma funcionará quando a autenticação chegar.",
        },
        {
          label: "Grupo de orientação de capstone",
          scope: "MBA · Revisão de portfólio",
          note: "Use este contexto para prever fluxos de intervenção docente e supervisão de portfólios.",
        },
      ],
      navigation: [
        {
          label: "Início",
          description: "Saúde da turma, pressão de revisão e próximas ações.",
        },
        {
          label: "Revisão",
          description: "Ensaios e perguntas que precisam de atenção docente.",
        },
        {
          label: "Conteúdo",
          description: "Configuração do programa, rubricas e controles de conteúdo.",
        },
        {
          label: "Progresso da coorte",
          description: "Progresso e risco para a turma ativa.",
        },
        {
          label: "Intervenções",
          description: "Próximos passos docentes e acompanhamento do estudante.",
        },
        {
          label: "Planos de ensino",
          description: "Análise e iteração estruturadas de planos de ensino.",
        },
      ],
    },
    principal: {
      label: "Diretor",
      shortLabel: "Diretor",
      workspaceTitle: "Espaço da direção",
      publicPitch:
        "Um início para a escola com indicadores de saúde, listas de intervenção e briefings narrativos fundamentados.",
      contextLabel: "Ano escolar e programa",
      trustLabel:
        "Narrativas ficam sobre indicadores escolares determinísticos e permanecem visivelmente fundamentadas.",
      personaName: "Marcos Azevedo",
      personaDetail: "Líder escolar · Piloto institucional",
      contexts: [
        {
          label: "Aurora Campus Norte",
          scope: "Ano escolar 2026 · Trilha de liderança",
          note: "Contexto escolar simulado que representa o acesso de líderes baseado em relações.",
        },
        {
          label: "Piloto de desenvolvimento docente",
          scope: "Trimestre 2 · Iniciativa de qualidade docente",
          note: "Use este contexto para prever supervisão e apoio em nível de programa.",
        },
      ],
      navigation: [
        {
          label: "Início",
          description: "Saúde escolar, intervenções e briefings.",
        },
        {
          label: "Saúde escolar",
          description: "Indicadores escolares atuais e insumos para briefing.",
        },
        {
          label: "Programas",
          description: "Marcos de programa e enquadramento de desempenho.",
        },
        {
          label: "Intervenções",
          description: "Lista prioritária e acompanhamento.",
        },
        {
          label: "Desenvolvimento docente",
          description: "Planos de crescimento docente e ciclos de apoio.",
        },
      ],
    },
    supervisor: {
      label: "Supervisor",
      shortLabel: "Supervisor",
      workspaceTitle: "Espaço de supervisão",
      publicPitch:
        "Uma visão de rede para escolas, preparação de visitas, alertas e briefings narrativos com confiança explícita.",
      contextLabel: "Região e período de relatório",
      trustLabel:
        "Comparações, alertas e briefings permanecem ligados ao escopo de rede e à atualidade das fontes.",
      personaName: "Renata Mendes",
      personaDetail: "Supervisora regional · Supervisão de rede escolar",
      contexts: [
        {
          label: "Rede norte",
          scope: "12 escolas · Ciclo de visitas de abril",
          note: "Escopo de supervisão simulado que depois será resolvido a partir de relações de rede e escola.",
        },
        {
          label: "Coorte piloto de alfabetização",
          scope: "5 escolas · Janela de intervenção direcionada",
          note: "Use este contexto para prever tendências delimitadas e planejamento de visitas.",
        },
      ],
      navigation: [
        {
          label: "Início",
          description: "Resumo de rede, preparação de visitas e alertas atuais.",
        },
        {
          label: "Escolas",
          description: "Briefings e perfis por escola.",
        },
        {
          label: "Briefings",
          description: "Briefings narrativos sobre modelos de leitura.",
        },
        {
          label: "Visitas",
          description: "Sinais de preparação e tarefas abertas de visita.",
        },
        {
          label: "Tendências",
          description: "Movimento de rede e áreas de atenção.",
        },
        {
          label: "Alertas",
          description: "Escalonamentos, atrasos de sincronização e validações.",
        },
      ],
    },
    admin: {
      label: "Administrador",
      shortLabel: "Admin",
      workspaceTitle: "Espaço de administração",
      publicPitch:
        "Um ambiente operacional para Configuração, casos de Avatar, Integrações, Políticas e governança de IA.",
      contextLabel: "Tenant e ambiente",
      trustLabel:
        "A área administrativa expõe sinais de política, avaliação e estado degradado como questões operacionais, não detalhes ocultos.",
      personaName: "Luciana Vieira",
      personaDetail: "Administradora da plataforma · Governança e operações",
      contexts: [
        {
          label: "Tenant piloto do Tutor",
          scope: "Espaço semelhante à produção · Piloto de ensino superior",
          note: "Contexto de tenant simulado para Wave 1 até haver resolução de tenant e relações.",
        },
        {
          label: "Ambiente de prontidão",
          scope: "Validação e verificações de política",
          note: "Use este contexto para prever visões operacionais por ambiente.",
        },
      ],
      navigation: [
        {
          label: "Início",
          description: "Postura operacional, incidentes e ações administrativas pendentes.",
        },
        {
          label: "Configuração",
          description: "Centro de conteúdo, políticas, integração e utilidades administrativas.",
        },
        {
          label: "Casos de Avatar",
          description: "Cenários de prática, perfis de avatar e etapas de casos.",
        },
        {
          label: "Integrações",
          description: "Operações de gateway e postura de sincronização.",
        },
        {
          label: "Políticas",
          description: "Configuração de perguntas, avaliação e regras.",
        },
        {
          label: "Governança de IA",
          description: "Cobertura de avaliação e visibilidade de estados degradados.",
        },
      ],
    },
    alumni: {
      label: "Ex-aluno",
      shortLabel: "Ex-aluno",
      workspaceTitle: "Espaço de ex-alunos",
      publicPitch:
        "Uma visão durável de registro e reentrada para credenciais, trilhas, mentoria e oportunidades de voltar a aprender.",
      contextLabel: "Afiliação e trilha",
      trustLabel:
        "A área de ex-alunos trata o registro do estudante e a evidência de credenciais como ativos duráveis que sobrevivem a um período.",
      personaName: "Paulo Nogueira",
      personaDetail: "Mentor ex-aluno · Trilha de reentrada profissional",
      contexts: [
        {
          label: "Coorte MBA 2024",
          scope: "Visão de credencial e portfólio",
          note: "Afiliação simulada de ex-aluno demonstrando acesso persistente a registros e resultados.",
        },
        {
          label: "Trilha de requalificação em análise",
          scope: "Educação continuada de curta duração",
          note: "Use este contexto para prever reengajamento curado em vez de uma experiência de marketplace.",
        },
      ],
      navigation: [
        {
          label: "Início",
          description: "Registro, trilhas e sinais de reengajamento.",
        },
        {
          label: "Registro",
          description: "Evidência persistente e linha do tempo de conquistas.",
        },
        {
          label: "Credenciais",
          description: "Enquadramento de credenciais e próximos resultados elegíveis.",
        },
        {
          label: "Trilhas",
          description: "Ofertas curadas de reentrada e aprendizagem contínua.",
        },
        {
          label: "Carreira",
          description: "Papel do registro na requalificação e avanço.",
        },
        {
          label: "Mentoria",
          description: "Comunidade e mentoria para ondas posteriores.",
        },
      ],
    },
  },
} satisfies Record<Exclude<Locale, "en">, Record<WorkspaceRole, WorkspaceRoleShellCopy>>;

function applyRoleShellCopy(
  config: WorkspaceRoleConfig,
  copy: WorkspaceRoleShellCopy,
): WorkspaceRoleConfig {
  return {
    ...config,
    label: copy.label,
    shortLabel: copy.shortLabel,
    workspaceTitle: copy.workspaceTitle,
    publicPitch: copy.publicPitch,
    contextLabel: copy.contextLabel,
    trustLabel: copy.trustLabel,
    personaName: copy.personaName,
    personaDetail: copy.personaDetail,
    contexts: config.contexts.map((context, index) => ({
      ...context,
      ...(copy.contexts[index] ?? {}),
    })),
    navigation: config.navigation.map((item, index) => ({
      ...item,
      ...(copy.navigation[index] ?? {}),
    })),
  };
}

function createLocalizedRoleConfigs(locale: Exclude<Locale, "en">) {
  return Object.fromEntries(
    WORKSPACE_ROLES.map((role) => [
      role,
      applyRoleShellCopy(ROLE_CONFIGS[role], ROLE_CONFIG_SHELL_TRANSLATIONS[locale][role]),
    ]),
  ) as Record<WorkspaceRole, WorkspaceRoleConfig>;
}

const LOCALIZED_ROLE_CONFIGS: Record<Locale, Record<WorkspaceRole, WorkspaceRoleConfig>> = {
  en: ROLE_CONFIGS,
  es: createLocalizedRoleConfigs("es"),
  pt: createLocalizedRoleConfigs("pt"),
};

const PUBLIC_CONTENT: Record<Locale, PublicContent> = {
  en: {
    navLinks: [
      { label: "Programs", href: "/programs" },
      { label: "Evidence & Trust", href: "/evidence-trust" },
      { label: "For Institutions", href: "/institutions" },
    ],
    highlights: [
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
    ],
    programs: [
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
    ],
    trustPrinciples: [
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
    ],
    institutionPriorities: [
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
    ],
    pages: {
      home: {
        heroEyebrow: "Institution-owned lifelong learning",
        heroTitle:
          "A professional academic front door for learner records, guided work, leadership briefings, and curated re-entry.",
        heroDescription:
          "Tutor is moving from feature launcher to role-aware platform. Wave 1 keeps current capabilities intact while introducing calmer navigation, role-native workspaces, evidence-first trust messaging, and curated program framing.",
        primaryCta: "Enter a pilot workspace",
        programsCta: "Explore curated programs",
        trustCta: "Review evidence and trust",
        trustPostureEyebrow: "Trust posture",
        programsEyebrow: "Curated programs and re-entry",
        programsTitle:
          "Pilot offerings with clear audience, evidence framing, and role entry points.",
        programCardCta: "Open relevant workspace",
        rolePreviewsEyebrow: "Role previews",
        rolePreviewsTitle: "One shell, different density and emphasis by audience.",
        institutionalEyebrow: "Institutional framing",
        institutionalTitle:
          "Reposition the product without pretending the whole platform migration is already done.",
        institutionalDescription:
          "This first slice is intentionally narrow. It introduces a credible academic front door, a shared role-aware shell, and first workspace homes while preserving the current route structure behind those surfaces.",
        institutionCta: "See institution-facing positioning",
        professorCta: "Preview professor workspace",
      },
      programs: {
        eyebrow: "Curated pilot catalog",
        title: "Programs and re-entry offers with clear audience, scope, and outcome framing.",
        description:
          "Wave 1 intentionally avoids a broad marketplace. These entries preview how Tutor can expose institution-owned programs, alumni re-entry, and leadership pilots without turning the public surface into a feature menu.",
        cardCta: "Open related workspace",
        limitTitle: "Wave 1 limit",
        limitDescription:
          "These entries are curated placeholders for the first slice. They are not a full enrollment, entitlement, or commerce implementation.",
      },
      institutions: {
        eyebrow: "For institutions",
        title:
          "Reposition Tutor as the institution-owned control plane for lifelong learning and outcomes.",
        description:
          "Wave 1 focuses on product posture and navigation: role-aware shells, curated entry points, and trust-first presentation. Existing routes and backend flows remain in place while the frontend stops behaving like a demo launcher.",
        honestyTitle: "This slice stays honest about what is implemented.",
        honestyDescription:
          "No full route migration, no fake auth, and no invented authority. The value here is a cleaner academic front door, role-native shell, and visible governance language that the rest of the product can grow into.",
        adminCta: "Preview admin workspace",
        supervisorCta: "Preview supervisor workspace",
      },
      evidenceTrust: {
        eyebrow: "Evidence and trust",
        title: "Tutor does not pretend AI output is institutional truth.",
        description:
          "This Wave 1 slice makes trust boundaries visible in the UI. Deterministic summaries stay primary, role and context are explicitly mocked, and degraded orchestration paths remain legible instead of being polished away.",
        cards: [
          {
            title: "Visible provenance",
            description:
              "Role dashboards explain what comes from queue state, school indicators, current workflow context, and advisory synthesis.",
          },
          {
            title: "Mocked context honesty",
            description:
              "Role and context switching are local-state pilots for now. The shell says so openly instead of simulating finished relationship-aware auth.",
          },
          {
            title: "Degraded-state clarity",
            description:
              "If orchestration falls back or a source is delayed, Tutor shows that state and downgrades the authority of the generated layer.",
          },
        ],
      },
    },
  },
  es: {
    navLinks: [
      { label: "Programas", href: "/programs" },
      { label: "Evidencia y confianza", href: "/evidence-trust" },
      { label: "Para instituciones", href: "/institutions" },
    ],
    highlights: [
      {
        title: "Registro del estudiante al centro",
        description:
          "Tutor se reposiciona alrededor de evidencia, resultados y continuidad, no de demostraciones aisladas.",
      },
      {
        title: "Programas curados y reingreso",
        description:
          "La entrada pública ahora enfatiza rutas curadas para estudiantes actuales y egresados que regresan.",
      },
      {
        title: "Límites de confianza visibles",
        description:
          "Los datos deterministas siguen primero, la orientación consultiva se etiqueta y los estados degradados no se ocultan.",
      },
    ],
    programs: [
      {
        title: "Estudio ejecutivo de escritura y liderazgo",
        audience: "MBA y educación ejecutiva",
        format: "Ruta curada de 8 semanas",
        description:
          "Combina revisión de escritura, tutoría guiada y evidencia lista para portafolio en trabajo de comunicación de liderazgo.",
        outcomes: ["Feedback con rúbrica", "Instantáneas de progreso", "Evidencia lista para portafolio"],
        href: "/workspace/student",
      },
      {
        title: "Reingreso de egresados: enseñanza informada por datos",
        audience: "Profesionales y egresados que regresan",
        format: "Oferta curada de actualización",
        description:
          "Un piloto acotado para estudiantes que necesitan actualizar enseñanza, analítica y práctica basada en evidencia sin empezar de cero.",
        outcomes: ["Registro persistente", "Reingreso curado", "Marco de aprendizaje continuo"],
        href: "/workspace/alumni",
      },
      {
        title: "Piloto de briefings de mejora escolar",
        audience: "Directores y supervisores",
        format: "Piloto institucional acotado",
        description:
          "Muestra briefings escolares y de red con indicadores deterministas, soporte narrativo y manejo visible de estados degradados.",
        outcomes: ["Briefings acotados", "Preparación de visitas", "Resúmenes con confianza primero"],
        href: "/workspace/supervisor",
      },
    ],
    trustPrinciples: [
      {
        title: "Resúmenes deterministas primero",
        description:
          "Colas, contexto, evidencia y estado vienen antes de cualquier narrativa generada o capa de recomendación.",
      },
      {
        title: "Consultivo significa consultivo",
        description:
          "Tutor puede sugerir próximos pasos, pero no cambia silenciosamente puntajes, progreso, intervenciones ni credenciales.",
      },
      {
        title: "Los estados degradados permanecen visibles",
        description:
          "Si una orquestación recurre a fallback o una fuente se demora, el entorno expone esa condición en lugar de ocultarla.",
      },
      {
        title: "Postura de integración institucional",
        description:
          "Tutor trabaja con LMS, SIS, CRM, analítica y ecosistemas de credenciales sin dejar que esos sistemas dicten el modelo de registro del estudiante.",
      },
    ],
    institutionPriorities: [
      {
        title: "Ser dueños del registro del estudiante",
        description:
          "Mantener evidencia, resultados y contexto longitudinal dentro de un plano de control institucional, no dispersos en salidas de herramientas.",
      },
      {
        title: "Reutilizar servicios actuales sin una UI de lanzador cosmético",
        description:
          "Wave 1 preserva las rutas frontend existentes mientras las reorganiza en entornos y espacios por rol.",
      },
      {
        title: "Hacer legible la confianza para cada audiencia",
        description:
          "Estudiantes, docentes, líderes, administradores y egresados deben ver dónde terminan los datos deterministas y empieza la ayuda consultiva.",
      },
    ],
    pages: {
      home: {
        heroEyebrow: "Aprendizaje permanente propiedad de la institución",
        heroTitle:
          "Una entrada académica profesional para registros de estudiantes, trabajo guiado, briefings de liderazgo y reingreso curado.",
        heroDescription:
          "Tutor pasa de lanzador de funciones a plataforma consciente del rol. Wave 1 mantiene intactas las capacidades actuales mientras introduce navegación más calmada, espacios nativos por rol, mensajes de confianza basados en evidencia y marco de programas curados.",
        primaryCta: "Entrar a un espacio piloto",
        programsCta: "Explorar programas curados",
        trustCta: "Revisar evidencia y confianza",
        trustPostureEyebrow: "Postura de confianza",
        programsEyebrow: "Programas curados y reingreso",
        programsTitle:
          "Ofertas piloto con audiencia clara, marco de evidencia y puntos de entrada por rol.",
        programCardCta: "Abrir espacio relevante",
        rolePreviewsEyebrow: "Vistas por rol",
        rolePreviewsTitle: "Un entorno, distinta densidad y énfasis por audiencia.",
        institutionalEyebrow: "Marco institucional",
        institutionalTitle:
          "Reposicionar el producto sin fingir que toda la migración de plataforma ya está completa.",
        institutionalDescription:
          "Esta primera porción es intencionalmente estrecha. Introduce una entrada académica creíble, un entorno compartido por rol y los primeros inicios de espacio mientras preserva la estructura de rutas actual detrás de esas superficies.",
        institutionCta: "Ver posicionamiento para instituciones",
        professorCta: "Previsualizar espacio de profesor",
      },
      programs: {
        eyebrow: "Catálogo piloto curado",
        title: "Programas y ofertas de reingreso con audiencia, alcance y resultados claros.",
        description:
          "Wave 1 evita intencionalmente un marketplace amplio. Estas entradas muestran cómo Tutor puede exponer programas institucionales, reingreso de egresados y pilotos de liderazgo sin convertir la superficie pública en un menú de funciones.",
        cardCta: "Abrir espacio relacionado",
        limitTitle: "Límite de Wave 1",
        limitDescription:
          "Estas entradas son marcadores curados para la primera porción. No son una implementación completa de inscripción, derechos o comercio.",
      },
      institutions: {
        eyebrow: "Para instituciones",
        title:
          "Reposicionar Tutor como el plano de control institucional para aprendizaje permanente y resultados.",
        description:
          "Wave 1 se enfoca en postura de producto y navegación: entornos por rol, entradas curadas y presentación basada primero en confianza. Las rutas existentes y los flujos backend se mantienen mientras el frontend deja de comportarse como lanzador de demos.",
        honestyTitle: "Esta porción se mantiene honesta sobre lo implementado.",
        honestyDescription:
          "Sin migración completa de rutas, sin autenticación falsa y sin autoridad inventada. El valor está en una entrada académica más clara, un entorno nativo por rol y lenguaje de gobernanza visible sobre el que el resto del producto puede crecer.",
        adminCta: "Previsualizar espacio de administración",
        supervisorCta: "Previsualizar espacio de supervisión",
      },
      evidenceTrust: {
        eyebrow: "Evidencia y confianza",
        title: "Tutor no finge que la salida de IA sea verdad institucional.",
        description:
          "Esta porción de Wave 1 hace visibles los límites de confianza en la UI. Los resúmenes deterministas siguen primero, el rol y el contexto se simulan explícitamente, y los caminos degradados de orquestación permanecen legibles en vez de quedar pulidos y ocultos.",
        cards: [
          {
            title: "Procedencia visible",
            description:
              "Los dashboards por rol explican qué viene del estado de cola, indicadores escolares, contexto de flujo actual y síntesis consultiva.",
          },
          {
            title: "Honestidad del contexto simulado",
            description:
              "El cambio de rol y contexto es por ahora un piloto de estado local. El entorno lo dice abiertamente en vez de simular autenticación relacional terminada.",
          },
          {
            title: "Claridad de estados degradados",
            description:
              "Si la orquestación recurre a fallback o una fuente se demora, Tutor muestra ese estado y reduce la autoridad de la capa generada.",
          },
        ],
      },
    },
  },
  pt: {
    navLinks: [
      { label: "Programas", href: "/programs" },
      { label: "Evidência e confiança", href: "/evidence-trust" },
      { label: "Para instituições", href: "/institutions" },
    ],
    highlights: [
      {
        title: "Registro do estudante no centro",
        description:
          "O Tutor se reposiciona em torno de evidências, resultados e continuidade, não de demonstrações isoladas.",
      },
      {
        title: "Programas curados e reentrada",
        description:
          "A entrada pública agora enfatiza trilhas curadas para estudantes atuais e ex-alunos que retornam.",
      },
      {
        title: "Limites de confiança visíveis",
        description:
          "Dados determinísticos ficam em primeiro plano, orientação consultiva é rotulada e estados degradados nunca são ocultados.",
      },
    ],
    programs: [
      {
        title: "Estúdio executivo de escrita e liderança",
        audience: "MBA e educação executiva",
        format: "Trilha curada de 8 semanas",
        description:
          "Combina revisão de escrita, tutoria guiada e evidência pronta para portfólio em trabalho de comunicação de liderança.",
        outcomes: ["Feedback com rubrica", "Capturas de progresso", "Evidência pronta para portfólio"],
        href: "/workspace/student",
      },
      {
        title: "Reentrada de ex-alunos: ensino informado por dados",
        audience: "Profissionais e ex-alunos que retornam",
        format: "Oferta curada de atualização",
        description:
          "Um piloto estreito para estudantes que precisam atualizar ensino, análise e prática baseada em evidências sem recomeçar.",
        outcomes: ["Registro persistente", "Reentrada curada", "Enquadramento de aprendizagem contínua"],
        href: "/workspace/alumni",
      },
      {
        title: "Piloto de briefings de melhoria escolar",
        audience: "Diretores e supervisores",
        format: "Piloto institucional delimitado",
        description:
          "Apresenta briefings escolares e de rede com indicadores determinísticos, suporte narrativo e tratamento visível de estado degradado.",
        outcomes: ["Briefings delimitados", "Preparação de visitas", "Resumos com confiança primeiro"],
        href: "/workspace/supervisor",
      },
    ],
    trustPrinciples: [
      {
        title: "Resumos determinísticos primeiro",
        description:
          "Filas, contexto, evidência e estado vêm antes de qualquer narrativa gerada ou camada de recomendação.",
      },
      {
        title: "Consultivo significa consultivo",
        description:
          "O Tutor pode sugerir próximos passos, mas não altera silenciosamente notas, progressão, intervenções ou credenciais.",
      },
      {
        title: "Estados degradados permanecem visíveis",
        description:
          "Se uma orquestração recorrer a fallback ou uma fonte atrasar, o ambiente expõe essa condição em vez de escondê-la.",
      },
      {
        title: "Postura de integração institucional",
        description:
          "O Tutor trabalha com LMS, SIS, CRM, análise e ecossistemas de credenciais sem deixar que esses sistemas ditem o modelo de registro do estudante.",
      },
    ],
    institutionPriorities: [
      {
        title: "Controlar o registro do estudante",
        description:
          "Manter evidências, resultados e contexto longitudinal dentro de um plano de controle institucional, não espalhados por saídas de ferramentas.",
      },
      {
        title: "Reutilizar serviços atuais sem uma UI cosmética de lançador",
        description:
          "Wave 1 preserva as rotas frontend existentes enquanto as reorganiza em ambientes e espaços por função.",
      },
      {
        title: "Tornar a confiança legível para cada público",
        description:
          "Estudantes, docentes, líderes, administradores e ex-alunos devem ver onde os dados determinísticos terminam e a ajuda consultiva começa.",
      },
    ],
    pages: {
      home: {
        heroEyebrow: "Aprendizagem contínua controlada pela instituição",
        heroTitle:
          "Uma entrada acadêmica profissional para registros de estudantes, trabalho guiado, briefings de liderança e reentrada curada.",
        heroDescription:
          "O Tutor passa de lançador de recursos para plataforma consciente da função. Wave 1 mantém as capacidades atuais intactas enquanto introduz navegação mais calma, espaços nativos por função, mensagens de confiança baseadas em evidência e enquadramento de programas curados.",
        primaryCta: "Entrar em um espaço piloto",
        programsCta: "Explorar programas curados",
        trustCta: "Revisar evidência e confiança",
        trustPostureEyebrow: "Postura de confiança",
        programsEyebrow: "Programas curados e reentrada",
        programsTitle:
          "Ofertas piloto com público claro, enquadramento de evidência e pontos de entrada por função.",
        programCardCta: "Abrir espaço relevante",
        rolePreviewsEyebrow: "Prévia por função",
        rolePreviewsTitle: "Um ambiente, densidade e ênfase diferentes por público.",
        institutionalEyebrow: "Enquadramento institucional",
        institutionalTitle:
          "Reposicionar o produto sem fingir que toda a migração da plataforma já terminou.",
        institutionalDescription:
          "Esta primeira fatia é intencionalmente estreita. Ela introduz uma entrada acadêmica confiável, um ambiente compartilhado por função e os primeiros inícios de espaço enquanto preserva a estrutura de rotas atual por trás dessas superfícies.",
        institutionCta: "Ver posicionamento para instituições",
        professorCta: "Pré-visualizar espaço do professor",
      },
      programs: {
        eyebrow: "Catálogo piloto curado",
        title: "Programas e ofertas de reentrada com público, escopo e resultados claros.",
        description:
          "Wave 1 evita intencionalmente um marketplace amplo. Estas entradas mostram como o Tutor pode expor programas institucionais, reentrada de ex-alunos e pilotos de liderança sem transformar a superfície pública em um menu de recursos.",
        cardCta: "Abrir espaço relacionado",
        limitTitle: "Limite de Wave 1",
        limitDescription:
          "Estas entradas são marcadores curados para a primeira fatia. Elas não são uma implementação completa de matrícula, direitos ou comércio.",
      },
      institutions: {
        eyebrow: "Para instituições",
        title:
          "Reposicionar o Tutor como o plano de controle institucional para aprendizagem contínua e resultados.",
        description:
          "Wave 1 foca postura de produto e navegação: ambientes por função, entradas curadas e apresentação com confiança em primeiro lugar. Rotas existentes e fluxos de backend permanecem enquanto o frontend deixa de agir como lançador de demos.",
        honestyTitle: "Esta fatia é honesta sobre o que está implementado.",
        honestyDescription:
          "Sem migração completa de rotas, sem autenticação falsa e sem autoridade inventada. O valor está em uma entrada acadêmica mais clara, ambiente nativo por função e linguagem de governança visível para o restante do produto crescer.",
        adminCta: "Pré-visualizar espaço de administração",
        supervisorCta: "Pré-visualizar espaço de supervisão",
      },
      evidenceTrust: {
        eyebrow: "Evidência e confiança",
        title: "O Tutor não finge que saída de IA seja verdade institucional.",
        description:
          "Esta fatia de Wave 1 torna visíveis os limites de confiança na UI. Resumos determinísticos ficam em primeiro plano, função e contexto são explicitamente simulados, e caminhos degradados de orquestração permanecem legíveis em vez de serem polidos e escondidos.",
        cards: [
          {
            title: "Procedência visível",
            description:
              "Painéis por função explicam o que vem do estado da fila, indicadores escolares, contexto de fluxo atual e síntese consultiva.",
          },
          {
            title: "Honestidade do contexto simulado",
            description:
              "A troca de função e contexto é por enquanto um piloto de estado local. O ambiente diz isso abertamente em vez de simular autenticação relacional finalizada.",
          },
          {
            title: "Clareza de estados degradados",
            description:
              "Se a orquestração recorrer a fallback ou uma fonte atrasar, o Tutor mostra esse estado e reduz a autoridade da camada gerada.",
          },
        ],
      },
    },
  },
};

export const ROLE_CONFIG_LIST = WORKSPACE_ROLES.map((role) => LOCALIZED_ROLE_CONFIGS.en[role]);

export const PUBLIC_NAV_LINKS = PUBLIC_CONTENT.en.navLinks;
export const PUBLIC_HIGHLIGHTS = PUBLIC_CONTENT.en.highlights;
export const PUBLIC_PROGRAMS = PUBLIC_CONTENT.en.programs;
export const TRUST_PRINCIPLES = PUBLIC_CONTENT.en.trustPrinciples;
export const INSTITUTION_PRIORITIES = PUBLIC_CONTENT.en.institutionPriorities;

export function getRoleConfigList(locale: Locale = DEFAULT_LOCALE): WorkspaceRoleConfig[] {
  const roleConfigs = LOCALIZED_ROLE_CONFIGS[locale] ?? LOCALIZED_ROLE_CONFIGS[DEFAULT_LOCALE];

  return WORKSPACE_ROLES.map((role) => roleConfigs[role]);
}

export function getPublicContent(locale: Locale = DEFAULT_LOCALE): PublicContent {
  return PUBLIC_CONTENT[locale] ?? PUBLIC_CONTENT[DEFAULT_LOCALE];
}

export function isWorkspaceRole(value: string): value is WorkspaceRole {
  return (WORKSPACE_ROLES as readonly string[]).includes(value);
}

export function getRoleConfig(
  role: WorkspaceRole,
  locale: Locale = DEFAULT_LOCALE,
): WorkspaceRoleConfig {
  const roleConfigs = LOCALIZED_ROLE_CONFIGS[locale] ?? LOCALIZED_ROLE_CONFIGS[DEFAULT_LOCALE];

  return roleConfigs[role];
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
