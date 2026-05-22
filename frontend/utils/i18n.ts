export const SUPPORTED_LOCALES = ["en", "es", "pt"] as const;

export type Locale = (typeof SUPPORTED_LOCALES)[number];

export interface LocaleMetadata {
  code: Locale;
  label: string;
  nativeName: string;
  htmlLang: string;
  direction: "ltr" | "rtl";
}

export interface AppDictionary {
  language: {
    label: string;
    title: string;
  };
  layout: {
    skipToMain: string;
  };
  header: {
    homeAriaLabel: string;
    currentWorkspaceAriaLabel: string;
    publicNavigationLabel: string;
    publicBrandTagline: string;
    workspaceBrandTagline: string;
    enterPilotWorkspace: string;
    resolvingAccessContext: string;
    fallbackWorkspaceContext: string;
    helpAndTrust: string;
    fallbackContextLabel: string;
    accessContextLabel: string;
    pilotUserAlt: string;
    activeActor: string;
    currentRole: string;
    openCurrentWorkspace: string;
    curatedPrograms: string;
  };
  workspace: {
    roleLabel: string;
    contextLabel: string;
    currentContext: string;
    trustNote: string;
    about: string;
    trust: string;
    reviewTrustPosture: string;
    collapseSidebar: string;
    closeSidebar: string;
    openSidebar: string;
    loadingContextNote: string;
    roleGuidanceTemplate: string;
    roleNavigationTemplate: string;
  };
  workspaceHome: {
    loadingAccessTitle: string;
    loadingAccessDescription: string;
    fallbackShellEyebrow: string;
    fallbackShellTitle: string;
    fallbackShellDescription: string;
    currentContext: string;
    activeActor: string;
    currentSnapshotTemplate: string;
    preparingSnapshotTemplate: string;
    freshness: string;
    waitingFreshness: string;
    generated: string;
    sourceUpdated: string;
    humanReview: string;
    waitingTrust: string;
    provenance: string;
    waitingProvenance: string;
    workflow: string;
    model: string;
    deterministicHighlightsTitle: string;
    deterministicHighlightsDescription: string;
    deterministicHighlightsEmpty: string;
    advisoryItemsTitle: string;
    advisoryItemsDescription: string;
    advisoryItemsEmpty: string;
    attentionItemsTitle: string;
    attentionItemsDescription: string;
    attentionItemsEmpty: string;
    trustGovernance: string;
    evaluationState: string;
    sourceLineage: string;
    advisoryBoundary: string;
    advisoryOnlySnapshot: string;
    deterministicSnapshot: string;
    degradedSnapshot: string;
    trustMetadataPending: string;
    learnerRecordPreview: string;
    learnerRecordPreviewTemplate: string;
    loadingLearnerRecord: string;
    learnerRecordEmpty: string;
    continueExploring: string;
    loadingSectionProjection: string;
  };
  workspaceModule: {
    mockFallback: string;
    howRouteWorks: string;
    backToRoleHomeTemplate: string;
  };
}

export const DEFAULT_LOCALE: Locale = "en";
export const LOCALE_STORAGE_KEY = "tutor.locale";

export const LOCALE_METADATA: Record<Locale, LocaleMetadata> = {
  en: {
    code: "en",
    label: "English",
    nativeName: "English",
    htmlLang: "en",
    direction: "ltr",
  },
  es: {
    code: "es",
    label: "Spanish",
    nativeName: "Español",
    htmlLang: "es",
    direction: "ltr",
  },
  pt: {
    code: "pt",
    label: "Portuguese",
    nativeName: "Português",
    htmlLang: "pt-BR",
    direction: "ltr",
  },
};

// Strategy-style dictionaries keep locale selection behind stable component APIs.
export const APP_DICTIONARIES: Record<Locale, AppDictionary> = {
  en: {
    language: {
      label: "Language",
      title: "Choose language",
    },
    layout: {
      skipToMain: "Skip to main content",
    },
    header: {
      homeAriaLabel: "Go to Tutor home",
      currentWorkspaceAriaLabel: "Go to current workspace",
      publicNavigationLabel: "Public navigation",
      publicBrandTagline: "Lifelong learning platform",
      workspaceBrandTagline: "Role-aware workspace shell",
      enterPilotWorkspace: "Enter pilot workspace",
      resolvingAccessContext: "Resolving access context",
      fallbackWorkspaceContext: "Fallback workspace context",
      helpAndTrust: "Help & Trust",
      fallbackContextLabel: "Fallback context",
      accessContextLabel: "Access context",
      pilotUserAlt: "Pilot user",
      activeActor: "Active actor",
      currentRole: "Current role",
      openCurrentWorkspace: "Open current workspace",
      curatedPrograms: "Curated programs",
    },
    workspace: {
      roleLabel: "Role",
      contextLabel: "Context",
      currentContext: "Current context",
      trustNote: "Trust note",
      about: "About",
      trust: "Trust",
      reviewTrustPosture: "Review trust posture",
      collapseSidebar: "Collapse sidebar",
      closeSidebar: "Close sidebar",
      openSidebar: "Open sidebar",
      loadingContextNote: "Tutor is resolving the latest context note for this role.",
      roleGuidanceTemplate: "{role} guidance",
      roleNavigationTemplate: "{role} navigation",
    },
    workspaceHome: {
      loadingAccessTitle: "Resolving your workspace access",
      loadingAccessDescription:
        "Tutor is loading the backend access context for this role before it requests the latest snapshot.",
      fallbackShellEyebrow: "Fallback workspace shell",
      fallbackShellTitle: "Backend access context is unavailable right now.",
      fallbackShellDescription:
        "The shell is preserving navigation and current routes, but role and context data are temporarily using the local fallback configuration.",
      currentContext: "Current context",
      activeActor: "Active actor",
      currentSnapshotTemplate:
        "Current context: {context}. Highlights, advisory items, and attention states below come from the Insights workspace snapshot for this context.",
      preparingSnapshotTemplate:
        "Tutor is preparing the latest {role} snapshot for this context.",
      freshness: "Freshness",
      waitingFreshness: "Waiting for freshness metadata.",
      generated: "Generated",
      sourceUpdated: "Source updated",
      humanReview: "Human review",
      waitingTrust: "Waiting for trust metadata.",
      provenance: "Provenance",
      waitingProvenance: "Waiting for provenance metadata.",
      workflow: "Workflow",
      model: "Model",
      deterministicHighlightsTitle: "Deterministic highlights",
      deterministicHighlightsDescription:
        "These items come directly from the backend workspace snapshot and should remain inspectable even when advisory layers change.",
      deterministicHighlightsEmpty: "No deterministic highlights were returned for this context.",
      advisoryItemsTitle: "Advisory items",
      advisoryItemsDescription:
        "Advisory content is visible, labelled, and kept separate from deterministic status and evidence.",
      advisoryItemsEmpty: "No advisory items were returned for this context.",
      attentionItemsTitle: "Attention items",
      attentionItemsDescription:
        "These cards surface degraded states, delays, or operational conditions that need review.",
      attentionItemsEmpty: "No attention items are active for this context.",
      trustGovernance: "Trust and governance",
      evaluationState: "Evaluation state",
      sourceLineage: "Source lineage",
      advisoryBoundary: "Advisory boundary",
      advisoryOnlySnapshot:
        "The snapshot includes advisory-only guidance that must be reviewed alongside deterministic evidence.",
      deterministicSnapshot: "The snapshot includes deterministic actions that may be executed directly.",
      degradedSnapshot:
        "This snapshot includes degraded output. Tutor is surfacing the condition explicitly instead of masking it.",
      trustMetadataPending: "Trust metadata will appear once the snapshot finishes loading.",
      learnerRecordPreview: "Learner record preview",
      learnerRecordPreviewTemplate:
        "Previewing {learner} through the learner-record timeline contract.",
      loadingLearnerRecord: "Loading learner record entries...",
      learnerRecordEmpty: "No learner-record entries were returned for this context.",
      continueExploring: "Continue exploring",
      loadingSectionProjection: "Loading the latest section projection...",
    },
    workspaceModule: {
      mockFallback:
        "This route is still available while the backend access context is unavailable. Links below continue to target the existing working pages.",
      howRouteWorks: "How this route works",
      backToRoleHomeTemplate: "Back to {role} home",
    },
  },
  es: {
    language: {
      label: "Idioma",
      title: "Elegir idioma",
    },
    layout: {
      skipToMain: "Saltar al contenido principal",
    },
    header: {
      homeAriaLabel: "Ir al inicio de Tutor",
      currentWorkspaceAriaLabel: "Ir al espacio de trabajo actual",
      publicNavigationLabel: "Navegación pública",
      publicBrandTagline: "Plataforma de aprendizaje permanente",
      workspaceBrandTagline: "Entorno de trabajo por rol",
      enterPilotWorkspace: "Entrar al espacio piloto",
      resolvingAccessContext: "Resolviendo contexto de acceso",
      fallbackWorkspaceContext: "Contexto alternativo del espacio",
      helpAndTrust: "Ayuda y confianza",
      fallbackContextLabel: "Contexto alternativo",
      accessContextLabel: "Contexto de acceso",
      pilotUserAlt: "Usuario piloto",
      activeActor: "Actor activo",
      currentRole: "Rol actual",
      openCurrentWorkspace: "Abrir espacio actual",
      curatedPrograms: "Programas curados",
    },
    workspace: {
      roleLabel: "Rol",
      contextLabel: "Contexto",
      currentContext: "Contexto actual",
      trustNote: "Nota de confianza",
      about: "Acerca de",
      trust: "Confianza",
      reviewTrustPosture: "Revisar postura de confianza",
      collapseSidebar: "Contraer barra lateral",
      closeSidebar: "Cerrar barra lateral",
      openSidebar: "Abrir barra lateral",
      loadingContextNote: "Tutor está resolviendo la nota de contexto más reciente para este rol.",
      roleGuidanceTemplate: "Guía para {role}",
      roleNavigationTemplate: "Navegación de {role}",
    },
    workspaceHome: {
      loadingAccessTitle: "Resolviendo tu acceso al espacio de trabajo",
      loadingAccessDescription:
        "Tutor está cargando el contexto de acceso del backend para este rol antes de solicitar la instantánea más reciente.",
      fallbackShellEyebrow: "Entorno de trabajo alternativo",
      fallbackShellTitle: "El contexto de acceso del backend no está disponible ahora.",
      fallbackShellDescription:
        "El entorno conserva la navegación y las rutas actuales, pero los datos de rol y contexto usan temporalmente la configuración local alternativa.",
      currentContext: "Contexto actual",
      activeActor: "Actor activo",
      currentSnapshotTemplate:
        "Contexto actual: {context}. Los destacados, elementos consultivos y estados de atención de abajo vienen de la instantánea de Insights para este contexto.",
      preparingSnapshotTemplate:
        "Tutor está preparando la instantánea más reciente de {role} para este contexto.",
      freshness: "Actualidad",
      waitingFreshness: "Esperando metadatos de actualidad.",
      generated: "Generado",
      sourceUpdated: "Fuente actualizada",
      humanReview: "Revisión humana",
      waitingTrust: "Esperando metadatos de confianza.",
      provenance: "Procedencia",
      waitingProvenance: "Esperando metadatos de procedencia.",
      workflow: "Flujo",
      model: "Modelo",
      deterministicHighlightsTitle: "Destacados deterministas",
      deterministicHighlightsDescription:
        "Estos elementos vienen directamente de la instantánea del backend y deben seguir siendo inspeccionables aunque cambien las capas consultivas.",
      deterministicHighlightsEmpty: "No se devolvieron destacados deterministas para este contexto.",
      advisoryItemsTitle: "Elementos consultivos",
      advisoryItemsDescription:
        "El contenido consultivo es visible, está etiquetado y se mantiene separado del estado y la evidencia deterministas.",
      advisoryItemsEmpty: "No se devolvieron elementos consultivos para este contexto.",
      attentionItemsTitle: "Elementos de atención",
      attentionItemsDescription:
        "Estas tarjetas muestran estados degradados, demoras o condiciones operativas que necesitan revisión.",
      attentionItemsEmpty: "No hay elementos de atención activos para este contexto.",
      trustGovernance: "Confianza y gobernanza",
      evaluationState: "Estado de evaluación",
      sourceLineage: "Linaje de la fuente",
      advisoryBoundary: "Límite consultivo",
      advisoryOnlySnapshot:
        "La instantánea incluye orientación solo consultiva que debe revisarse junto con la evidencia determinista.",
      deterministicSnapshot: "La instantánea incluye acciones deterministas que pueden ejecutarse directamente.",
      degradedSnapshot:
        "Esta instantánea incluye salida degradada. Tutor muestra la condición explícitamente en vez de ocultarla.",
      trustMetadataPending: "Los metadatos de confianza aparecerán cuando termine de cargar la instantánea.",
      learnerRecordPreview: "Vista previa del registro del estudiante",
      learnerRecordPreviewTemplate:
        "Vista previa de {learner} mediante el contrato de línea de tiempo del registro del estudiante.",
      loadingLearnerRecord: "Cargando entradas del registro del estudiante...",
      learnerRecordEmpty: "No se devolvieron entradas del registro del estudiante para este contexto.",
      continueExploring: "Seguir explorando",
      loadingSectionProjection: "Cargando la proyección más reciente de la sección...",
    },
    workspaceModule: {
      mockFallback:
        "Esta ruta sigue disponible mientras el contexto de acceso del backend no está disponible. Los enlaces de abajo siguen apuntando a las páginas existentes que funcionan.",
      howRouteWorks: "Cómo funciona esta ruta",
      backToRoleHomeTemplate: "Volver al inicio de {role}",
    },
  },
  pt: {
    language: {
      label: "Idioma",
      title: "Escolher idioma",
    },
    layout: {
      skipToMain: "Pular para o conteúdo principal",
    },
    header: {
      homeAriaLabel: "Ir para a página inicial do Tutor",
      currentWorkspaceAriaLabel: "Ir para o espaço de trabalho atual",
      publicNavigationLabel: "Navegação pública",
      publicBrandTagline: "Plataforma de aprendizagem contínua",
      workspaceBrandTagline: "Ambiente de trabalho por função",
      enterPilotWorkspace: "Entrar no espaço piloto",
      resolvingAccessContext: "Resolvendo contexto de acesso",
      fallbackWorkspaceContext: "Contexto alternativo do espaço",
      helpAndTrust: "Ajuda e confiança",
      fallbackContextLabel: "Contexto alternativo",
      accessContextLabel: "Contexto de acesso",
      pilotUserAlt: "Usuário piloto",
      activeActor: "Ator ativo",
      currentRole: "Função atual",
      openCurrentWorkspace: "Abrir espaço atual",
      curatedPrograms: "Programas curados",
    },
    workspace: {
      roleLabel: "Função",
      contextLabel: "Contexto",
      currentContext: "Contexto atual",
      trustNote: "Nota de confiança",
      about: "Sobre",
      trust: "Confiança",
      reviewTrustPosture: "Revisar postura de confiança",
      collapseSidebar: "Recolher barra lateral",
      closeSidebar: "Fechar barra lateral",
      openSidebar: "Abrir barra lateral",
      loadingContextNote: "O Tutor está resolvendo a nota de contexto mais recente para esta função.",
      roleGuidanceTemplate: "Orientação para {role}",
      roleNavigationTemplate: "Navegação de {role}",
    },
    workspaceHome: {
      loadingAccessTitle: "Resolvendo seu acesso ao espaço de trabalho",
      loadingAccessDescription:
        "O Tutor está carregando o contexto de acesso do backend para esta função antes de solicitar a captura mais recente.",
      fallbackShellEyebrow: "Ambiente de trabalho alternativo",
      fallbackShellTitle: "O contexto de acesso do backend não está disponível agora.",
      fallbackShellDescription:
        "O ambiente preserva a navegação e as rotas atuais, mas os dados de função e contexto usam temporariamente a configuração local alternativa.",
      currentContext: "Contexto atual",
      activeActor: "Ator ativo",
      currentSnapshotTemplate:
        "Contexto atual: {context}. Os destaques, itens consultivos e estados de atenção abaixo vêm da captura do espaço Insights para este contexto.",
      preparingSnapshotTemplate:
        "O Tutor está preparando a captura mais recente de {role} para este contexto.",
      freshness: "Atualidade",
      waitingFreshness: "Aguardando metadados de atualidade.",
      generated: "Gerado",
      sourceUpdated: "Fonte atualizada",
      humanReview: "Revisão humana",
      waitingTrust: "Aguardando metadados de confiança.",
      provenance: "Procedência",
      waitingProvenance: "Aguardando metadados de procedência.",
      workflow: "Fluxo",
      model: "Modelo",
      deterministicHighlightsTitle: "Destaques determinísticos",
      deterministicHighlightsDescription:
        "Estes itens vêm diretamente da captura do backend e devem continuar inspecionáveis mesmo quando as camadas consultivas mudarem.",
      deterministicHighlightsEmpty: "Nenhum destaque determinístico foi retornado para este contexto.",
      advisoryItemsTitle: "Itens consultivos",
      advisoryItemsDescription:
        "O conteúdo consultivo é visível, rotulado e mantido separado do estado e da evidência determinísticos.",
      advisoryItemsEmpty: "Nenhum item consultivo foi retornado para este contexto.",
      attentionItemsTitle: "Itens de atenção",
      attentionItemsDescription:
        "Estes cartões mostram estados degradados, atrasos ou condições operacionais que precisam de revisão.",
      attentionItemsEmpty: "Não há itens de atenção ativos para este contexto.",
      trustGovernance: "Confiança e governança",
      evaluationState: "Estado de avaliação",
      sourceLineage: "Linhagem da fonte",
      advisoryBoundary: "Limite consultivo",
      advisoryOnlySnapshot:
        "A captura inclui orientação apenas consultiva que deve ser revisada junto com a evidência determinística.",
      deterministicSnapshot: "A captura inclui ações determinísticas que podem ser executadas diretamente.",
      degradedSnapshot:
        "Esta captura inclui saída degradada. O Tutor mostra a condição explicitamente em vez de mascará-la.",
      trustMetadataPending: "Os metadados de confiança aparecerão quando a captura terminar de carregar.",
      learnerRecordPreview: "Prévia do registro do estudante",
      learnerRecordPreviewTemplate:
        "Prévia de {learner} pelo contrato de linha do tempo do registro do estudante.",
      loadingLearnerRecord: "Carregando entradas do registro do estudante...",
      learnerRecordEmpty: "Nenhuma entrada do registro do estudante foi retornada para este contexto.",
      continueExploring: "Continuar explorando",
      loadingSectionProjection: "Carregando a projeção mais recente da seção...",
    },
    workspaceModule: {
      mockFallback:
        "Esta rota continua disponível enquanto o contexto de acesso do backend não está disponível. Os links abaixo continuam apontando para as páginas existentes que funcionam.",
      howRouteWorks: "Como esta rota funciona",
      backToRoleHomeTemplate: "Voltar ao início de {role}",
    },
  },
};

export function isLocale(value: string | null | undefined): value is Locale {
  return Boolean(value && (SUPPORTED_LOCALES as readonly string[]).includes(value));
}

export function normalizeLocale(value: string | null | undefined): Locale {
  if (!value) {
    return DEFAULT_LOCALE;
  }

  const normalizedValue = value.toLowerCase();
  const directLocale = normalizedValue.split("-")[0];

  return isLocale(directLocale) ? directLocale : DEFAULT_LOCALE;
}

export function getDictionary(locale: Locale): AppDictionary {
  return APP_DICTIONARIES[locale] ?? APP_DICTIONARIES[DEFAULT_LOCALE];
}

export function formatTemplate(
  template: string,
  values: Record<string, string | number>,
): string {
  return Object.entries(values).reduce(
    (message, [key, value]) => message.split(`{${key}}`).join(String(value)),
    template,
  );
}