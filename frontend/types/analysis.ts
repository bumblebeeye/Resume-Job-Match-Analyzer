export type AnalysisResult = {
  id: number;
  resume_id: number;
  job_description_id: number;
  resume_filename: string;
  role_title: string;
  company_name: string | null;
  match_score: number;
  summary: string;
  overlapping_skills: string[];
  missing_skills: string[];
  suggestions: string[];
  analysis_metadata: Record<string, unknown>;
  created_at: string;
};

