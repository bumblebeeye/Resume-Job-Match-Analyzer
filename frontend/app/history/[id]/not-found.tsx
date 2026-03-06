import Link from "next/link";

export default function AnalysisNotFoundPage() {
  return (
    <main className="mx-auto max-w-3xl px-6 pb-16 pt-10 md:px-10">
      <section className="rounded-3xl border border-slate-200 bg-white p-8 shadow-card">
        <h1 className="text-3xl font-semibold text-ink">Analysis not found</h1>
        <p className="mt-3 text-sm text-slate">
          This analysis record does not exist or may have been removed.
        </p>
        <Link
          href="/history"
          className="mt-5 inline-flex rounded-xl bg-ink px-4 py-2 text-sm font-medium text-white transition hover:bg-slate"
        >
          Back to History
        </Link>
      </section>
    </main>
  );
}
