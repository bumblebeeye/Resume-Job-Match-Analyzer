"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { fetchAnalyses } from "@/lib/api";
import { AnalysisListItem } from "@/types/analysis";

function formatScore(score: number): string {
  return `${score.toFixed(2)}%`;
}

function formatTimestamp(timestamp: string): string {
  return new Date(timestamp).toLocaleString();
}

export default function HistoryPage() {
  const [analyses, setAnalyses] = useState<AnalysisListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string>("");

  useEffect(() => {
    let active = true;

    async function loadHistory() {
      setIsLoading(true);
      setErrorMessage("");
      try {
        const data = await fetchAnalyses();
        if (active) {
          setAnalyses(data);
        }
      } catch (error) {
        if (!active) return;
        const message =
          error instanceof Error ? error.message : "Unable to load history.";
        setErrorMessage(message);
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    }

    void loadHistory();

    return () => {
      active = false;
    };
  }, []);

  return (
    <main className="mx-auto max-w-6xl px-6 pb-16 pt-8 md:px-10">
      <header className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-4xl font-semibold text-ink">History</h1>
          <p className="mt-2 text-sm text-slate">
            Review previous resume-job analyses and open details for each run.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link
            href="/analyze"
            className="rounded-xl bg-ink px-4 py-2 text-sm font-medium text-white transition hover:bg-slate"
          >
            New Analysis
          </Link>
          <Link
            href="/"
            className="rounded-xl border border-slate-300 bg-white/80 px-4 py-2 text-sm font-medium text-ink transition hover:bg-white"
          >
            Back Home
          </Link>
        </div>
      </header>

      {isLoading ? (
        <section className="rounded-3xl border border-slate-200 bg-white p-8 shadow-card">
          <p className="text-sm font-medium text-ink">Loading history…</p>
          <p className="mt-2 text-sm text-slate">
            First load may take longer if the backend is waking up.
          </p>
        </section>
      ) : errorMessage ? (
        <section className="rounded-3xl border border-red-200 bg-white p-8 shadow-card">
          <h2 className="text-2xl font-semibold text-ink">Unable to load history</h2>
          <p className="mt-3 text-sm text-red-700">{errorMessage}</p>
        </section>
      ) : analyses.length === 0 ? (
        <section className="rounded-3xl border border-slate-200 bg-white p-8 shadow-card">
          <h2 className="text-2xl font-semibold text-ink">No saved analyses yet</h2>
          <p className="mt-3 text-sm text-slate">
            Run your first analysis to populate this history page.
          </p>
          <Link
            href="/analyze"
            className="mt-5 inline-flex rounded-xl bg-ink px-4 py-2 text-sm font-medium text-white transition hover:bg-slate"
          >
            Go to Analyzer
          </Link>
        </section>
      ) : (
        <section className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-card">
          <div className="hidden grid-cols-[1.5fr_1.2fr_120px_220px_120px] gap-4 border-b border-slate-200 bg-sand-soft px-5 py-3 text-xs font-semibold uppercase tracking-wide text-slate md:grid">
            <span>Role</span>
            <span>Company</span>
            <span>Score</span>
            <span>Created</span>
            <span className="text-right">Action</span>
          </div>

          <ul>
            {analyses.map((analysis) => (
              <li
                key={analysis.id}
                className="border-b border-slate-100 px-5 py-4 last:border-b-0"
              >
                <div className="hidden grid-cols-[1.5fr_1.2fr_120px_220px_120px] items-center gap-4 md:grid">
                  <p className="font-medium text-ink">{analysis.role_title}</p>
                  <p className="text-sm text-slate">{analysis.company_name ?? "-"}</p>
                  <p className="text-sm font-semibold text-teal">
                    {formatScore(analysis.match_score)}
                  </p>
                  <p className="text-sm text-slate">{formatTimestamp(analysis.created_at)}</p>
                  <div className="text-right">
                    <Link
                      href={`/history/${analysis.id}`}
                      className="inline-flex rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium text-ink transition hover:bg-sand-soft"
                    >
                      View
                    </Link>
                  </div>
                </div>

                <div className="space-y-2 md:hidden">
                  <p className="text-base font-medium text-ink">{analysis.role_title}</p>
                  <p className="text-sm text-slate">
                    Company: <span className="text-ink">{analysis.company_name ?? "-"}</span>
                  </p>
                  <p className="text-sm text-slate">
                    Score: <span className="font-semibold text-teal">{formatScore(analysis.match_score)}</span>
                  </p>
                  <p className="text-sm text-slate">Created: {formatTimestamp(analysis.created_at)}</p>
                  <Link
                    href={`/history/${analysis.id}`}
                    className="inline-flex rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium text-ink transition hover:bg-sand-soft"
                  >
                    View details
                  </Link>
                </div>
              </li>
            ))}
          </ul>
        </section>
      )}
    </main>
  );
}
