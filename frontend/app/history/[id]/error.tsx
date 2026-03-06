"use client";

import Link from "next/link";

export default function HistoryDetailError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <main className="mx-auto max-w-3xl px-6 pb-16 pt-10 md:px-10">
      <section className="rounded-3xl border border-red-200 bg-white p-8 shadow-card">
        <h1 className="text-3xl font-semibold text-ink">Unable to load analysis</h1>
        <p className="mt-3 text-sm text-red-700">
          {error.message || "Unexpected error while loading analysis detail."}
        </p>
        <div className="mt-5 flex flex-wrap gap-2">
          <button
            type="button"
            onClick={reset}
            className="rounded-xl bg-ink px-4 py-2 text-sm font-medium text-white transition hover:bg-slate"
          >
            Try again
          </button>
          <Link
            href="/history"
            className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium text-ink transition hover:bg-sand-soft"
          >
            Back to History
          </Link>
        </div>
      </section>
    </main>
  );
}
