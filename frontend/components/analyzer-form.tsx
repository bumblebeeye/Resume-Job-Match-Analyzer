"use client";

import { FormEvent, useMemo, useState } from "react";

import { submitAnalysis } from "@/lib/api";
import { AnalysisResult } from "@/types/analysis";

type SubmissionState = "idle" | "loading" | "success" | "error";

export default function AnalyzerForm() {
  const [submissionState, setSubmissionState] = useState<SubmissionState>("idle");
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);

  const statusText = useMemo(() => {
    if (submissionState === "loading") return "Running analysis...";
    if (submissionState === "success") return "Analysis complete.";
    if (submissionState === "error") return "Analysis failed.";
    return "Ready to analyze.";
  }, [submissionState]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmissionState("loading");
    setErrorMessage("");

    const form = event.currentTarget;
    const formData = new FormData(form);

    try {
      const result = await submitAnalysis(formData);
      setAnalysisResult(result);
      setSubmissionState("success");
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Unexpected error occurred.";
      setErrorMessage(message);
      setSubmissionState("error");
    }
  }

  return (
    <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
      <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-card md:p-8">
        <h2 className="text-2xl font-semibold text-ink">Start An Analysis</h2>
        <p className="mt-2 text-sm text-slate">
          Upload a resume and compare it with one job description.
        </p>

        <form className="mt-6 space-y-5" onSubmit={handleSubmit}>
          <div>
            <label className="mb-2 block text-sm font-medium text-ink" htmlFor="resume_file">
              Resume file (PDF, TXT, MD)
            </label>
            <input
              id="resume_file"
              name="resume_file"
              type="file"
              accept=".pdf,.txt,.md"
              required
              className="block w-full rounded-xl border border-slate-300 bg-sand-soft px-3 py-2 text-sm text-ink file:mr-3 file:rounded-lg file:border-0 file:bg-teal file:px-3 file:py-2 file:text-sm file:font-medium file:text-white hover:file:bg-cyan-700"
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-ink" htmlFor="role_title">
              Role title
            </label>
            <input
              id="role_title"
              name="role_title"
              type="text"
              required
              placeholder="e.g. Backend Engineer"
              className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm text-ink outline-none transition focus:border-teal"
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-ink" htmlFor="company_name">
              Company name (optional)
            </label>
            <input
              id="company_name"
              name="company_name"
              type="text"
              placeholder="e.g. Atlassian"
              className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm text-ink outline-none transition focus:border-teal"
            />
          </div>

          <div>
            <label
              className="mb-2 block text-sm font-medium text-ink"
              htmlFor="job_description"
            >
              Job description / hiring information
            </label>
            <textarea
              id="job_description"
              name="job_description"
              required
              rows={9}
              placeholder="Paste the job details here..."
              className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm text-ink outline-none transition focus:border-teal"
            />
          </div>

          <button
            type="submit"
            disabled={submissionState === "loading"}
            className="w-full rounded-xl bg-ink px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate disabled:cursor-not-allowed disabled:opacity-60"
          >
            {submissionState === "loading" ? "Analyzing..." : "Run Match Analysis"}
          </button>
        </form>
      </section>

      <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-card md:p-8">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-2xl font-semibold text-ink">Result</h2>
          <span className="rounded-full bg-sky-soft px-3 py-1 text-xs font-medium text-teal">
            {statusText}
          </span>
        </div>

        {submissionState === "error" && (
          <p className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {errorMessage}
          </p>
        )}

        {!analysisResult && submissionState !== "error" && (
          <p className="mt-6 text-sm text-slate">
            Your analysis output will appear here after submission.
          </p>
        )}

        {analysisResult && (
          <div className="mt-6 space-y-5">
            <div className="rounded-2xl bg-sand-soft p-4">
              <p className="text-xs uppercase tracking-wide text-slate">Match score</p>
              <p className="mt-1 text-3xl font-bold text-ink">
                {analysisResult.match_score.toFixed(2)}%
              </p>
              <div className="mt-3 h-2 rounded-full bg-white">
                <div
                  className="h-2 rounded-full bg-teal transition-all duration-500"
                  style={{ width: `${Math.min(analysisResult.match_score, 100)}%` }}
                />
              </div>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-ink">Summary</h3>
              <p className="mt-1 text-sm text-slate">{analysisResult.summary}</p>
            </div>

            <SkillList
              title="Overlapping skills"
              skills={analysisResult.overlapping_skills}
              emptyText="No overlapping skills were detected."
              tone="positive"
            />

            <SkillList
              title="Missing skills"
              skills={analysisResult.missing_skills}
              emptyText="No major missing skills were detected."
              tone="neutral"
            />

            <div>
              <h3 className="text-sm font-semibold text-ink">Improvement suggestions</h3>
              <ul className="mt-2 space-y-2">
                {analysisResult.suggestions.map((suggestion) => (
                  <li
                    key={suggestion}
                    className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate"
                  >
                    {suggestion}
                  </li>
                ))}
              </ul>
            </div>

            <p className="text-xs text-slate">
              Analysis ID: {analysisResult.id} | Saved at:{" "}
              {new Date(analysisResult.created_at).toLocaleString()}
            </p>
          </div>
        )}
      </section>
    </div>
  );
}

type SkillListProps = {
  title: string;
  skills: string[];
  emptyText: string;
  tone: "positive" | "neutral";
};

function SkillList({ title, skills, emptyText, tone }: SkillListProps) {
  const badgeClass =
    tone === "positive"
      ? "bg-emerald-50 text-emerald-800 border-emerald-200"
      : "bg-amber-50 text-amber-800 border-amber-200";

  return (
    <div>
      <h3 className="text-sm font-semibold text-ink">{title}</h3>
      {skills.length === 0 ? (
        <p className="mt-1 text-sm text-slate">{emptyText}</p>
      ) : (
        <div className="mt-2 flex flex-wrap gap-2">
          {skills.map((skill) => (
            <span
              key={skill}
              className={`rounded-full border px-3 py-1 text-xs font-semibold ${badgeClass}`}
            >
              {skill}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

