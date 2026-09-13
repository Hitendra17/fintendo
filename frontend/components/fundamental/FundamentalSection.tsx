import type { FundamentalAnalysis } from "@/types/research";

interface FundamentalSectionProps {
  fundamental: FundamentalAnalysis;
}

export function FundamentalSection({
  fundamental,
}: FundamentalSectionProps) {
  const score = Math.round(fundamental.score);

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
      <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
            Fundamental Analysis
          </p>

          <h2 className="mt-2 text-xl font-semibold text-white">
            Business and financial quality
          </h2>

          <p className="mt-4 max-w-4xl text-sm leading-7 text-slate-400">
            {fundamental.summary}
          </p>
        </div>

        <div className="shrink-0 lg:w-72">
          <div className="flex items-end justify-between">
            <div>
              <p className="text-xs uppercase tracking-wider text-slate-500">
                Fundamental Score
              </p>

              <p className="mt-1 text-4xl font-semibold tracking-tight text-white">
                {score}
                <span className="ml-1 text-base font-normal text-slate-600">
                  / 100
                </span>
              </p>
            </div>

            <span className="text-sm font-medium text-slate-400">
              {Math.round(fundamental.confidence * 100)}% confidence
            </span>
          </div>

          <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-800">
            <div
              className="h-full rounded-full bg-slate-300"
              style={{ width: `${Math.min(Math.max(score, 0), 100)}%` }}
            />
          </div>
        </div>
      </div>

      <div className="mt-8 grid gap-4 lg:grid-cols-3">
        <InsightCard
          title="Strengths"
          items={fundamental.strengths}
          tone="positive"
        />

        <InsightCard
          title="Catalysts"
          items={fundamental.catalysts}
          tone="positive"
        />

        <InsightCard
          title="Risks"
          items={fundamental.risks}
          tone="negative"
        />
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <InsightCard
          title="Weaknesses"
          items={fundamental.weaknesses}
          tone="negative"
        />

        <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-5">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Evidence
          </p>

          <p className="mt-3 text-3xl font-semibold text-white">
            {fundamental.evidence.length}
          </p>

          <p className="mt-1 text-sm text-slate-500">
            validated fundamental data points
          </p>
        </div>
      </div>
    </section>
  );
}

function InsightCard({
  title,
  items,
  tone,
}: {
  title: string;
  items: string[];
  tone: "positive" | "negative";
}) {
  const marker =
    tone === "positive"
      ? "bg-emerald-400"
      : "bg-red-400";

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-5">
      <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
        {title}
      </p>

      {items.length > 0 ? (
        <ul className="mt-4 space-y-3">
          {items.map((item, index) => (
            <li
              key={index}
              className="flex gap-3 text-sm leading-6 text-slate-300"
            >
              <span
                className={`mt-2 h-1.5 w-1.5 shrink-0 rounded-full ${marker}`}
              />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-4 text-sm text-slate-600">
          No items reported.
        </p>
      )}
    </div>
  );
}