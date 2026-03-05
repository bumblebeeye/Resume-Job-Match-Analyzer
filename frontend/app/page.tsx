import Link from "next/link";

const workflowSteps = [
  "Upload your resume (PDF/TXT/MD).",
  "Paste role details and hiring requirements.",
  "Get score, overlap, gaps, and practical suggestions.",
];

const features = [
  "Explainable skill-overlap scoring",
  "Readable summary for quick decision-making",
  "Structured suggestions to improve resume targeting",
  "Saved analyses for history view (Phase 3)",
];

export default function HomePage() {
  return (
    <main className="mx-auto max-w-6xl px-6 pb-16 pt-10 md:px-10">
      <header className="rounded-3xl border border-slate-200 bg-white/85 p-8 shadow-card md:p-12">
        <p className="inline-block rounded-full bg-sky-soft px-3 py-1 text-xs font-semibold uppercase tracking-wide text-teal">
          Portfolio MVP
        </p>
        <h1 className="mt-4 max-w-2xl text-4xl font-semibold leading-tight text-ink md:text-5xl">
          Resume-Job Match Analyzer
        </h1>
        <p className="mt-4 max-w-2xl text-base text-slate md:text-lg">
          A practical web app that compares resume content with hiring requirements and
          returns a clear, recruiter-friendly analysis.
        </p>

        <div className="mt-8 flex flex-wrap items-center gap-4">
          <Link
            href="/analyze"
            className="rounded-xl bg-ink px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate"
          >
            Start Analysis
          </Link>
          <span className="text-sm text-slate">
            No sign-in required for MVP. Single-user demo flow.
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
          <h2 className="text-2xl font-semibold text-ink">MVP features</h2>
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

