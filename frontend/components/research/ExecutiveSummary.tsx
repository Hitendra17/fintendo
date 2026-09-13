import type { ResearchReport } from "@/types/research";

interface ExecutiveSummaryProps {
  report: ResearchReport;
}

export function ExecutiveSummary({
  report,
}: ExecutiveSummaryProps) {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
            Executive Summary
          </p>

          <h2 className="mt-2 text-xl font-semibold text-white">
            Research at a glance
          </h2>
        </div>

        <div className="text-right">
          <p className="text-xs text-slate-500">Overall confidence</p>
          <p className="mt-1 text-lg font-semibold text-slate-200">
            {(report.committee.confidence * 100).toFixed(0)}%
          </p>
        </div>
      </div>

      <p className="mt-6 max-w-5xl text-sm leading-7 text-slate-300">
        {report.fundamental.summary}
      </p>

      <div className="mt-6 grid gap-4 md:grid-cols-3">
        <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Fundamental
          </p>

          <p className="mt-2 text-2xl font-semibold text-white">
            {report.fundamental.score.toFixed(1)}
          </p>

          <p className="mt-1 text-xs text-slate-500">
            / 100
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Technical
          </p>

          <p className="mt-2 text-2xl font-semibold text-white">
            {report.technical.score.toFixed(1)}
          </p>

          <p className="mt-1 text-xs text-slate-500">
            / 100
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Market Intelligence
          </p>

          <p className="mt-2 text-2xl font-semibold text-white">
            {report.market_intelligence
              ? report.market_intelligence.score.toFixed(1)
              : "—"}
          </p>

          <p className="mt-1 text-xs text-slate-500">
            / 100
          </p>
        </div>
      </div>
    </section>
  );
}