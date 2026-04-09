export interface ApiEnvelope<T> {
  success: boolean;
  title?: string | null;
  message?: string | null;
  content: T;
  type?: string | null;
  detail?: unknown;
}

export interface ApiErrorEnvelope {
  success: false;
  type?: string | null;
  title?: string | null;
  detail?: unknown;
}

export function isApiEnvelope<T>(value: unknown): value is ApiEnvelope<T> {
  return (
    typeof value === "object" && value !== null && "content" in (value as Record<string, unknown>)
  );
}

export function unwrapContent<T>(value: ApiEnvelope<T> | T): T {
  if (isApiEnvelope<T>(value)) {
    return value.content;
  }
  return value as T;
}
