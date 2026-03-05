import { AnalysisResult } from "@/types/analysis";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function submitAnalysis(formData: FormData): Promise<AnalysisResult> {
  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorBody = await safeParseError(response);
    throw new Error(errorBody ?? "Analysis request failed.");
  }

  return (await response.json()) as AnalysisResult;
}

async function safeParseError(response: Response): Promise<string | null> {
  try {
    const parsed = (await response.json()) as { detail?: string };
    return parsed.detail ?? null;
  } catch {
    return null;
  }
}

