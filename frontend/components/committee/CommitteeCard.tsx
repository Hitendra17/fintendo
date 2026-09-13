import type { CommitteeDecision } from "@/types/research";

interface CommitteeCardProps {
  committee: CommitteeDecision;
}

export function CommitteeCard({ committee }: CommitteeCardProps) {
  const conviction = Math.round(committee.conviction);

  const recommendation = committee.recommendation.toLowerCase();

  const isPositive =
    recommendation.includes("buy") || recommendation.includes("bullish");

  const isNegative =
    recommendation.includes("sell") || recommendation.includes("bearish");

  const recommendationTone = isPositive
    ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
    : isNegative
      ? "border-red-500/30 bg-red-500/10 text-red-400"
      : "border-amber-500/30 bg-amber-500/10 text-amber-400";

  const convictionTone = isPositive
    ? "bg-emerald-400"
    : isNegative
      ? "bg-red-400"
      : "bg-amber-400";

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-2xl shadow-black/10">
      <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
            Committee Decision
          </p>

          <div className="mt-3 flex items-center gap-4">
            <h2 className="text-3xl font-semibold tracking-tight text-white">
              {committee.recommendation}
            </h2>

            <span
              className={`rounded-full border px-3 py-1 text-xs font-semibold ${recommendationTone}`}
            >
              {conviction}% conviction
            </span>
          </div>

          <p className="mt-4 max-w-3xl text-sm leading-7 text-slate-400">
            {committee.rationale}
          </p>
        </div>

        <div className="w-full shrink-0 lg:w-64">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-500">Conviction</span>

            <span className="font-semibold text-slate-300">
              {conviction}%
            </span>
          </div>

          <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-800">
            <div
              className={`h-full rounded-full transition-all ${convictionTone}`}
              style={{ width: `${conviction}%` }}
            />
          </div>

          <p className="mt-2 text-right text-xs text-slate-600">
            Model confidence {(committee.confidence * 100).toFixed(0)}%
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 border-t border-slate-800 pt-6 md:grid-cols-3">
        <div>
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Bull Case
          </p>

          <ul className="mt-3 space-y-2">
            {committee.bull_case.map((item, index) => (
              <li
                key={index}
                className="text-sm leading-6 text-slate-300"
              >
                {item}
              </li>
            ))}
          </ul>
        </div>

        <div>
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Bear Case
          </p>

          <ul className="mt-3 space-y-2">
            {committee.bear_case.map((item, index) => (
              <li
                key={index}
                className="text-sm leading-6 text-slate-300"
              >
                {item}
              </li>
            ))}
          </ul>
        </div>

        <div>
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Key Risks
          </p>

          <ul className="mt-3 space-y-2">
            {committee.key_risks.map((item, index) => (
              <li
                key={index}
                className="text-sm leading-6 text-slate-300"
              >
                {item}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}