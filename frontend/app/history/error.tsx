"use client";

export default function HistoryError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <main className="mx-auto max-w-3xl px-6 pb-16 pt-10 md:px-10">
      <section className="rounded-3xl border border-red-200 bg-white p-8 shadow-card">
        <h1 className="text-3xl font-semibold text-ink">Unable to load history</h1>
        <p className="mt-3 text-sm text-red-700">
          {error.message || "Unexpected error while loading analyses."}
        </p>
        <button
          type="button"
          onClick={reset}
          className="mt-5 rounded-xl bg-ink px-4 py-2 text-sm font-medium text-white transition hover:bg-slate"
        >
          Try again
        </button>
      </section>
    </main>
  );
}
