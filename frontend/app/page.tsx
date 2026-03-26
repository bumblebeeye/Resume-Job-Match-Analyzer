import Link from "next/link";

const workflowSteps = [
  "Upload your resume (PDF/TXT/MD).",
  "Paste role details and hiring requirements.",
  "Run deterministic matching with optional AI-generated suggestions.",
];

const features = [
  "Deterministic skill-overlap scoring for explainable results",
  "Optional Gemini suggestions with rule-based fallback",
  "Saved analysis history with scoring and suggestion metadata",
  "Cloud-ready backend flow with local or S3-backed file storage",
];

export default function HomePage() {
  return (
    <main className="mx-auto max-w-6xl px-6 pb-16 pt-10 md:px-10">
      <header className="rounded-3xl border border-slate-200 bg-white/85 p-8 shadow-card md:p-12">
        <p className="inline-block rounded-full bg-sky-soft px-3 py-1 text-xs font-semibold uppercase tracking-wide text-teal">
          AI Workflow Demo
        </p>
        <h1 className="mt-4 max-w-2xl text-4xl font-semibold leading-tight text-ink md:text-5xl">
          Resume-Job Match Analyzer
        </h1>
        <p className="mt-4 max-w-2xl text-base text-slate md:text-lg">
          A production-minded full-stack app that combines deterministic matching,
          optional LLM suggestions, persisted history, and cloud-ready storage in one
          practical hiring workflow.
        </p>

        <div className="mt-8 flex flex-wrap items-center gap-4">
          <Link
            href="/analyze"
            className="rounded-xl bg-ink px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate"
          >
            Start Analysis
          </Link>
          <Link
            href="/history"
            className="rounded-xl border border-slate-300 bg-white/80 px-6 py-3 text-sm font-semibold text-ink transition hover:bg-white"
          >
            View History
          </Link>
          <span className="text-sm text-slate">
            No sign-in required. Built to demonstrate practical GenAI integration, not
            just prompt output.
          </span>
        </div>
      </header>

      <section className="mt-8 grid gap-6 md:grid-cols-2">
        <article className="rounded-3xl border border-slate-200 bg-white/85 p-6 shadow-card">
          <h2 className="text-2xl font-semibold text-ink">How it works</h2>
          <ol className="mt-4 space-y-3 text-sm text-slate">
            {workflowSteps.map((step, index) => (
              <li key={step} className="flex items-start gap-3">
                <span className="mt-0.5 inline-flex h-6 w-6 items-center justify-center rounded-full bg-sky-soft text-xs font-bold text-teal">
                  {index + 1}
                </span>
                <span>{step}</span>
              </li>
            ))}
          </ol>
        </article>

        <article className="rounded-3xl border border-slate-200 bg-white/85 p-6 shadow-card">
          <h2 className="text-2xl font-semibold text-ink">Production-minded features</h2>
          <ul className="mt-4 space-y-3 text-sm text-slate">
            {features.map((feature) => (
              <li key={feature} className="rounded-xl bg-sand-soft px-4 py-3">
                {feature}
              </li>
            ))}
          </ul>
        </article>
      </section>
    </main>
  );
}
