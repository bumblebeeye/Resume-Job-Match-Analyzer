export default function HistoryDetailLoading() {
  return (
    <main className="mx-auto max-w-6xl px-6 pb-16 pt-8 md:px-10">
      <div className="mb-6 h-10 w-56 animate-pulse rounded-xl bg-slate-200" />
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.15fr)_minmax(0,0.85fr)]">
        <div className="h-64 animate-pulse rounded-3xl border border-slate-200 bg-white" />
        <div className="h-64 animate-pulse rounded-3xl border border-slate-200 bg-white" />
      </div>
      <div className="mt-6 h-52 animate-pulse rounded-3xl border border-slate-200 bg-white" />
    </main>
  );
}
