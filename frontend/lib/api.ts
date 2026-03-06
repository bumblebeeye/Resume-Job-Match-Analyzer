import { AnalysisListItem, AnalysisResult } from "@/types/analysis";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export async function submitAnalysis(formData: FormData): Promise<AnalysisResult> {
  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorBody = await safeParseError(response);
    throw new ApiError(response.status, errorBody ?? "Analysis request failed.");
  }

  return (await response.json()) as AnalysisResult;
}

export async function fetchAnalyses(): Promise<AnalysisListItem[]> {
  return requestJson<AnalysisListItem[]>("/api/analyses");
}

export async function fetchAnalysisById(analysisId: number): Promise<AnalysisResult> {
  return requestJson<AnalysisResult>(`/api/analyses/${analysisId}`);
}

async function requestJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "GET",
    cache: "no-store",
  });

  if (!response.ok) {
    const errorBody = await safeParseError(response);
    throw new ApiError(
      response.status,
      errorBody ?? `Request failed with status ${response.status}.`,
    );
  }

  return (await response.json()) as T;
}

async function safeParseError(response: Response): Promise<string | null> {
  try {
    const parsed = (await response.json()) as { detail?: string };
    return parsed.detail ?? null;
  } catch {
    return null;
  }
}
