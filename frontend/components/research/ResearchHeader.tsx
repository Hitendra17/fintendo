import type { ResearchReport } from "@/types/research";

interface ResearchHeaderProps {
  report: ResearchReport;
  companyName?: string;
}

export function ResearchHeader({
  report,
  companyName,
}: ResearchHeaderProps) {
  return (
    <header className="border-b border-slate-800 pb-8">
      <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.25em] text-slate-500">
            FINTENDO RESEARCH
          </p>

          <div className="mt-3 flex items-center gap-4">
            <h1 className="text-4xl font-semibold tracking-tight text-white">
              {report.ticker}
            </h1>

            <span className="rounded-md border border-slate-700 bg-slate-900 px-2.5 py-1 text-xs font-semibold text-slate-400">
              EQUITY RESEARCH
            </span>
          </div>

          {companyName && (
            <p className="mt-2 text-lg text-slate-400">
              {companyName}
            </p>
          )}
        </div>

        <div className="text-left md:text-right">
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Generated
          </p>

          <p className="mt-1 text-sm text-slate-300">
            {new Date(report.generated_at).toLocaleString()}
          </p>
        </div>
      </div>
    </header>
  );
}