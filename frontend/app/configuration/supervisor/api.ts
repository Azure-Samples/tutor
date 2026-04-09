import { insightsApi } from "@/utils/api";
import type { DeepLink, FreshnessMetadata, TrustMetadata } from "@/utils/workspace-api";

export interface InsightIndicator {
  indicator: string;
  score: number;
  trend: string;
  summary: string;
}

export interface InsightReport {
  report_id: string;
  school_id: string;
  supervisor_id: string;
  week_of: string | null;
  generated_at: string;
  source: string;
  indicators: InsightIndicator[];
  trends: string[];
  alerts: string[];
  focus_points: string[];
  improvements: string[];
  feedback_count: number;
  trust?: TrustMetadata;
  freshness?: FreshnessMetadata;
  deep_links?: DeepLink[];
}

export interface CreateBriefingInput {
  schoolId: string;
  weekOf?: string;
  onDemand?: boolean;
}

// Facade pattern: route pages consume typed operations without coupling to HTTP details.
export async function listInsightReports(schoolId?: string): Promise<InsightReport[]> {
  const response = await insightsApi.get<InsightReport[]>("/reports", {
    params: schoolId ? { school_id: schoolId } : undefined,
  });
  return response.data;
}

export async function getInsightReport(reportId: string): Promise<InsightReport> {
  const response = await insightsApi.get<InsightReport>(`/reports/${encodeURIComponent(reportId)}`);
  return response.data;
}

export async function createInsightBriefing(input: CreateBriefingInput): Promise<InsightReport> {
  const response = await insightsApi.post<InsightReport>("/briefing", {
    school_id: input.schoolId,
    week_of: input.weekOf,
    on_demand: input.onDemand ?? true,
  });
  return response.data;
}
