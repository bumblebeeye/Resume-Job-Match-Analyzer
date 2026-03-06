export default function HistoryLoading() {
  return (
    <main className="mx-auto max-w-6xl px-6 pb-16 pt-8 md:px-10">
      <div className="mb-6 h-10 w-48 animate-pulse rounded-xl bg-slate-200" />
      <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-card">
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, index) => (
            <div key={index} className="h-12 animate-pulse rounded-xl bg-sand-soft" />
          ))}
        </div>
      </div>
    </main>
  );
}
