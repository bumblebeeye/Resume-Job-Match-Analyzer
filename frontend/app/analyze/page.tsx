import Link from "next/link";

import AnalyzerForm from "@/components/analyzer-form";

export default function AnalyzePage() {
  return (
    <main className="mx-auto max-w-6xl px-6 pb-16 pt-8 md:px-10">
      <div className="mb-6 flex items-center justify-between gap-4">
        <div>
          <h1 className="text-4xl font-semibold text-ink">Analyzer</h1>
          <p className="mt-2 text-sm text-slate">
            Upload one resume and compare it with one job description.
          </p>
        </div>
        <Link
          href="/"
          className="rounded-xl border border-slate-300 bg-white/80 px-4 py-2 text-sm font-medium text-ink transition hover:bg-white"
        >
          Back Home
        </Link>
      </div>

      <AnalyzerForm />
    </main>
  );
}

