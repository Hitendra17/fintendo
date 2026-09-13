import type { TechnicalAnalysis } from "@/types/research";

interface TechnicalSectionProps {
  technical: TechnicalAnalysis;
}

export function TechnicalSection({
  technical,
}: TechnicalSectionProps) {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
            Technical Analysis
          </p>

          <h2 className="mt-2 text-xl font-semibold text-white">
            Price action & market structure
          </h2>
        </div>

        <div className="text-left sm:text-right">
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Score
          </p>

          <p className="mt-1 text-3xl font-semibold text-white">
            {technical.score.toFixed(1)}
            <span className="ml-1 text-sm font-normal text-slate-500">
              / 100
            </span>
          </p>
        </div>
      </div>

      <div className="mt-6 h-2 overflow-hidden rounded-full bg-slate-800">
        <div
          className="h-full rounded-full bg-slate-300"
          style={{ width: `${technical.score}%` }}
        />
      </div>

      <p className="mt-6 max-w-5xl text-sm leading-7 text-slate-300">
        {technical.summary}
      </p>

      <div className="mt-8 grid gap-4 md:grid-cols-3">
        <TechnicalMetric
          label="Trend"
          value={technical.trend}
        />

        <TechnicalMetric
          label="Momentum"
          value={technical.momentum}
        />

        <TechnicalMetric
          label="Volatility"
          value={technical.volatility}
        />
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <SignalList
          title="Bullish Signals"
          items={technical.bullish_signals}
        />

        <SignalList
          title="Bearish Signals"
          items={technical.bearish_signals}
        />
      </div>

      <div className="mt-8 grid gap-6 border-t border-slate-800 pt-6 md:grid-cols-2">
        <LevelList
          title="Support"
          levels={technical.support_levels}
        />

        <LevelList
          title="Resistance"
          levels={technical.resistance_levels}
        />
      </div>

      <div className="mt-8 border-t border-slate-800 pt-6">
        <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
          Technical Outlook
        </p>

        <p className="mt-3 text-sm leading-7 text-slate-300">
          {technical.outlook}
        </p>
      </div>

      <div className="mt-6 border-t border-slate-800 pt-4 text-xs text-slate-500">
        Model confidence {(technical.confidence.score * 100).toFixed(0)}%
        <span className="mx-2 text-slate-700">•</span>
        {technical.confidence.observations} observations
      </div>
    </section>
  );
}

function TechnicalMetric({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
      <p className="text-xs uppercase tracking-wider text-slate-500">
        {label}
      </p>

      <p className="mt-2 text-lg font-semibold capitalize text-slate-200">
        {value.replace("_", " ")}
      </p>
    </div>
  );
}

function SignalList({
  title,
  items,
}: {
  title: string;
  items: string[];
}) {
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
        {title}
      </p>

      {items.length > 0 ? (
        <ul className="mt-3 space-y-3">
          {items.map((item, index) => (
            <li
              key={`${title}-${index}`}
              className="text-sm leading-6 text-slate-300"
            >
              {item}
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-3 text-sm text-slate-600">
          None identified.
        </p>
      )}
    </div>
  );
}

function LevelList({
  title,
  levels,
}: {
  title: string;
  levels: number[];
}) {
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
        {title}
      </p>

      <div className="mt-3 flex flex-wrap gap-2">
        {levels.length > 0 ? (
          levels.map((level) => (
            <span
              key={level}
              className="rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-sm font-medium text-slate-300"
            >
              {level.toFixed(2)}
            </span>
          ))
        ) : (
          <p className="text-sm text-slate-600">
            None identified.
          </p>
        )}
      </div>
    </div>
  );
}