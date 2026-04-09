"use client";

import {
  DEFAULT_WORKSPACE_ROLE,
  ROLE_CONFIG_LIST,
  type WorkspaceContextOption,
  type WorkspaceRole,
  type WorkspaceRoleConfig,
  getRoleConfig,
  getWorkspaceRoleFromPathname,
  isWorkspaceRole,
} from "@/utils/workspace";
import {
  type AccessActor,
  type AccessContextItem,
  type AccessContextPayload,
  describeAccessContext,
  findRoleContext,
  getAccessContext,
  summarizeScope,
} from "@/utils/workspace-api";
import { usePathname } from "next/navigation";
import { type ReactNode, createContext, useContext, useEffect, useMemo, useState } from "react";

const ROLE_STORAGE_KEY = "tutor.workspace.role";
const CONTEXT_STORAGE_KEY = "tutor.workspace.contexts";
const MOCK_MODE_STORAGE_KEY = "tutor.workspace.mock";

type StoredContextMap = Partial<Record<WorkspaceRole, string>>;

interface WorkspaceStore {
  currentRole: WorkspaceRole;
  roleConfig: WorkspaceRoleConfig;
  currentContext: WorkspaceContextOption;
  contextOptions: WorkspaceContextOption[];
  availableRoles: WorkspaceRoleConfig[];
  actor: AccessActor | null;
  accessContext: AccessContextPayload | null;
  featureFlags: string[];
  isLoading: boolean;
  isMockMode: boolean;
  error: string | null;
  setRole: (role: WorkspaceRole) => void;
  setContext: (contextId: string) => void;
}

const WorkspaceContext = createContext<WorkspaceStore | null>(null);

function readStoredValue<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") {
    return fallback;
  }

  try {
    const rawValue = window.localStorage.getItem(key);
    return rawValue ? (JSON.parse(rawValue) as T) : fallback;
  } catch {
    return fallback;
  }
}

function writeStoredValue<T>(key: string, value: T) {
  if (typeof window === "undefined") {
    return;
  }

  try {
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Ignore storage failures in pilot mode.
  }
}

function toContextOption(role: WorkspaceRole, context: AccessContextItem): WorkspaceContextOption {
  return {
    id: context.context_id,
    label: context.label,
    scope: summarizeScope(context.scope, context.context_type),
    note: describeAccessContext(context),
    role,
    relationship: context.relationship,
    contextType: context.context_type,
    workspacePath: context.workspace_path,
    learnerIds: context.scope.learner_ids,
    staffIds: context.scope.staff_ids,
  };
}

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const pathnameRole = getWorkspaceRoleFromPathname(pathname);
  const [storedRole, setStoredRole] = useState<WorkspaceRole>(() =>
    readStoredValue<WorkspaceRole>(ROLE_STORAGE_KEY, DEFAULT_WORKSPACE_ROLE),
  );
  const [storedContexts, setStoredContexts] = useState<StoredContextMap>(() =>
    readStoredValue<StoredContextMap>(CONTEXT_STORAGE_KEY, {}),
  );
  const [accessContext, setAccessContext] = useState<AccessContextPayload | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;

    const loadAccessContext = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const payload = await getAccessContext();
        if (!isActive) {
          return;
        }

        setAccessContext(payload);
      } catch (caughtError: unknown) {
        if (!isActive) {
          return;
        }

        setAccessContext(null);
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "Failed to load workspace access context.",
        );
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    };

    void loadAccessContext();

    return () => {
      isActive = false;
    };
  }, []);

  const availableRoles = useMemo<WorkspaceRoleConfig[]>(() => {
    const apiRoles =
      accessContext?.roles
        .map((roleContext) => roleContext.role)
        .filter(isWorkspaceRole)
        .map((role) => getRoleConfig(role)) ?? [];

    if (apiRoles.length === 0) {
      return ROLE_CONFIG_LIST;
    }

    return Array.from(new Map(apiRoles.map((role) => [role.key, role])).values());
  }, [accessContext]);

  const defaultRole = useMemo<WorkspaceRole>(() => {
    if (
      accessContext?.default_role &&
      isWorkspaceRole(accessContext.default_role) &&
      availableRoles.some((role) => role.key === accessContext.default_role)
    ) {
      return accessContext.default_role;
    }

    return availableRoles[0]?.key ?? DEFAULT_WORKSPACE_ROLE;
  }, [accessContext?.default_role, availableRoles]);

  const requestedRole = pathnameRole ?? storedRole;
  const currentRole = availableRoles.some((role) => role.key === requestedRole)
    ? requestedRole
    : defaultRole;
  const roleConfig = getRoleConfig(currentRole);
  const roleContext = findRoleContext(accessContext, currentRole);
  const contextOptions =
    roleContext?.contexts.length && !isLoading
      ? roleContext.contexts.map((context) => toContextOption(currentRole, context))
      : roleConfig.contexts;
  const currentContextId =
    storedContexts[currentRole] ??
    roleContext?.default_context_id ??
    (accessContext?.default_context?.role === currentRole
      ? accessContext.default_context.context_id
      : null) ??
    contextOptions[0].id;
  const currentContext =
    contextOptions.find((option) => option.id === currentContextId) ?? contextOptions[0];

  useEffect(() => {
    if (!isLoading) {
      writeStoredValue(MOCK_MODE_STORAGE_KEY, !accessContext);
    }
  }, [accessContext, isLoading]);

  useEffect(() => {
    writeStoredValue(ROLE_STORAGE_KEY, storedRole);
  }, [storedRole]);

  useEffect(() => {
    writeStoredValue(CONTEXT_STORAGE_KEY, storedContexts);
  }, [storedContexts]);

  useEffect(() => {
    if (currentRole !== storedRole) {
      setStoredRole(currentRole);
    }
  }, [currentRole, storedRole]);

  useEffect(() => {
    setStoredContexts((previous) => {
      const selectedContextId = previous[currentRole];

      if (selectedContextId && contextOptions.some((option) => option.id === selectedContextId)) {
        return previous;
      }

      return {
        ...previous,
        [currentRole]: contextOptions[0].id,
      };
    });
  }, [currentRole, contextOptions]);

  const value = useMemo<WorkspaceStore>(
    () => ({
      currentRole,
      roleConfig,
      currentContext,
      contextOptions,
      availableRoles,
      actor: accessContext?.actor ?? null,
      accessContext,
      featureFlags: accessContext?.feature_flags ?? [],
      isLoading,
      isMockMode: !isLoading && !accessContext,
      error,
      setRole: (role) => {
        setStoredRole(role);
        setStoredContexts((previous) => {
          if (previous[role]) {
            return previous;
          }

          return {
            ...previous,
            [role]: getRoleConfig(role).contexts[0].id,
          };
        });
      },
      setContext: (contextId) => {
        setStoredContexts((previous) => ({
          ...previous,
          [currentRole]: contextId,
        }));
      },
    }),
    [
      accessContext,
      availableRoles,
      contextOptions,
      currentContext,
      currentRole,
      error,
      isLoading,
      roleConfig,
    ],
  );

  return <WorkspaceContext.Provider value={value}>{children}</WorkspaceContext.Provider>;
}

export function useWorkspace() {
  const value = useContext(WorkspaceContext);

  if (!value) {
    throw new Error("useWorkspace must be used within WorkspaceProvider");
  }

  return value;
}
