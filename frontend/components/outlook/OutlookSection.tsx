import type { ResearchReport } from "@/types/research";

interface OutlookSectionProps {
  report: ResearchReport;
}

export function OutlookSection({ report }: OutlookSectionProps) {
  const market = report.market_intelligence;

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
          Outlook
        </p>

        <h2 className="mt-2 text-xl font-semibold text-white">
          Forward-looking view
        </h2>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-3">
        <OutlookCard
          title="Short Term"
          value={market?.short_term_outlook ?? "uncertain"}
        />

        <OutlookCard
          title="Medium Term"
          value={market?.medium_term_outlook ?? "uncertain"}
        />

        <OutlookCard
          title="Long Term"
          value={market?.long_term_outlook ?? "uncertain"}
        />
      </div>
    </section>
  );
}

function OutlookCard({
  title,
  value,
}: {
  title: string;
  value: string;
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-5">
      <p className="text-xs uppercase tracking-wider text-slate-500">
        {title}
      </p>

      <p className="mt-3 text-lg font-semibold capitalize text-slate-200">
        {value.replace("_", " ")}
      </p>

      <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-slate-800">
        <div
          className="h-full rounded-full bg-slate-400"
          style={{
            width:
              value === "positive"
                ? "85%"
                : value === "negative"
                  ? "25%"
                  : value === "neutral"
                    ? "50%"
                    : "35%",
          }}
        />
      </div>
    </div>
  );
}