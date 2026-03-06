import Link from "next/link";
import { notFound } from "next/navigation";

import { ApiError, fetchAnalysisById } from "@/lib/api";

type HistoryDetailPageProps = {
  params: Promise<{ id: string }>;
};

function formatTimestamp(timestamp: string): string {
  return new Date(timestamp).toLocaleString();
}

export default async function HistoryDetailPage({ params }: HistoryDetailPageProps) {
  const { id } = await params;
  const analysisId = Number(id);

  if (!Number.isInteger(analysisId) || analysisId <= 0) {
    notFound();
  }

  try {
    const analysis = await fetchAnalysisById(analysisId);

    return (
      <main className="mx-auto max-w-6xl px-6 pb-16 pt-8 md:px-10">
        <header className="mb-6 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-4xl font-semibold text-ink">Analysis Detail</h1>
            <p className="mt-2 text-sm text-slate">
              Review score, skill gaps, and suggestions for this saved analysis.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Link
              href="/history"
              className="rounded-xl border border-slate-300 bg-white/80 px-4 py-2 text-sm font-medium text-ink transition hover:bg-white"
            >
              Back to History
            </Link>
            <Link
              href="/analyze"
              className="rounded-xl bg-ink px-4 py-2 text-sm font-medium text-white transition hover:bg-slate"
            >
              New Analysis
            </Link>
          </div>
        </header>

        <section className="grid gap-6 lg:grid-cols-[minmax(0,1.15fr)_minmax(0,0.85fr)]">
          <article className="rounded-3xl border border-slate-200 bg-white p-6 shadow-card md:p-8">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <h2 className="text-2xl font-semibold text-ink">{analysis.role_title}</h2>
              <span className="rounded-full bg-sky-soft px-3 py-1 text-xs font-semibold text-teal">
                Score {analysis.match_score.toFixed(2)}%
              </span>
            </div>

            <dl className="mt-5 grid gap-3 rounded-2xl bg-sand-soft p-4 text-sm text-slate sm:grid-cols-2">
              <div>
                <dt className="font-semibold text-ink">Company</dt>
                <dd>{analysis.company_name ?? "-"}</dd>
              </div>
              <div>
                <dt className="font-semibold text-ink">Resume file</dt>
                <dd>{analysis.resume_filename}</dd>
              </div>
              <div>
                <dt className="font-semibold text-ink">Analysis ID</dt>
                <dd>{analysis.id}</dd>
              </div>
              <div>
                <dt className="font-semibold text-ink">Created at</dt>
                <dd>{formatTimestamp(analysis.created_at)}</dd>
              </div>
            </dl>

            <div className="mt-6">
              <h3 className="text-lg font-semibold text-ink">Summary</h3>
              <p className="mt-2 text-sm text-slate">{analysis.summary}</p>
            </div>
          </article>

          <article className="rounded-3xl border border-slate-200 bg-white p-6 shadow-card md:p-8">
            <h3 className="text-xl font-semibold text-ink">Skills</h3>

            <SkillGroup
              title="Overlapping skills"
              emptyText="No overlapping skills were detected."
              skills={analysis.overlapping_skills}
              tone="positive"
            />

            <SkillGroup
              title="Missing skills"
              emptyText="No major missing skills were detected."
              skills={analysis.missing_skills}
              tone="warning"
            />
          </article>
        </section>

        <section className="mt-6 rounded-3xl border border-slate-200 bg-white p-6 shadow-card md:p-8">
          <h3 className="text-xl font-semibold text-ink">Improvement suggestions</h3>
          {analysis.suggestions.length === 0 ? (
            <p className="mt-2 text-sm text-slate">No suggestions available.</p>
          ) : (
            <ul className="mt-3 space-y-2">
              {analysis.suggestions.map((suggestion) => (
                <li
                  key={suggestion}
                  className="rounded-xl border border-slate-200 bg-sand-soft px-4 py-3 text-sm text-slate"
                >
                  {suggestion}
                </li>
              ))}
            </ul>
          )}
        </section>
      </main>
    );
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      notFound();
    }

    throw error;
  }
}

type SkillGroupProps = {
  title: string;
  skills: string[];
  emptyText: string;
  tone: "positive" | "warning";
};

function SkillGroup({ title, skills, emptyText, tone }: SkillGroupProps) {
  const badgeClass =
    tone === "positive"
      ? "bg-emerald-50 text-emerald-800 border-emerald-200"
      : "bg-amber-50 text-amber-800 border-amber-200";

  return (
    <div className="mt-5">
      <h4 className="text-sm font-semibold text-ink">{title}</h4>
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
