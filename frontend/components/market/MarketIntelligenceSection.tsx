import type { MarketIntelligenceAnalysis } from "@/types/research";

interface MarketIntelligenceSectionProps {
  market: MarketIntelligenceAnalysis;
}

export function MarketIntelligenceSection({
  market,
}: MarketIntelligenceSectionProps) {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
            Market Intelligence
          </p>

          <h2 className="mt-2 text-xl font-semibold text-white">
            News & market developments
          </h2>
        </div>

        <div className="text-left sm:text-right">
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Score
          </p>

          <p className="mt-1 text-3xl font-semibold text-white">
            {market.score.toFixed(1)}
            <span className="ml-1 text-sm font-normal text-slate-500">
              / 100
            </span>
          </p>
        </div>
      </div>

      <div className="mt-6 h-2 overflow-hidden rounded-full bg-slate-800">
        <div
          className="h-full rounded-full bg-slate-300"
          style={{ width: `${market.score}%` }}
        />
      </div>

      <div className="mt-6 flex flex-wrap gap-3">
        <span className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1.5 text-xs font-medium capitalize text-slate-300">
          {market.overall_sentiment}
        </span>

        <span className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1.5 text-xs font-medium capitalize text-slate-400">
          {market.sentiment_strength}
        </span>
      </div>

      <p className="mt-6 max-w-5xl text-sm leading-7 text-slate-300">
        {market.summary}
      </p>

      <div className="mt-8 grid gap-6 lg:grid-cols-3">
        <FactorList
          title="Positive Factors"
          items={market.positive_factors}
        />

        <FactorList
          title="Negative Factors"
          items={market.negative_factors}
        />

        <FactorList
          title="Catalysts"
          items={market.catalysts}
        />
      </div>

      {market.risks.length > 0 && (
        <div className="mt-6 border-t border-slate-800 pt-6">
          <FactorList title="Risks" items={market.risks} />
        </div>
      )}

      <div className="mt-8 border-t border-slate-800 pt-6">
        <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
          Outlook
        </p>

        <div className="mt-4 grid gap-3 md:grid-cols-3">
          <Outlook
            label="Short Term"
            value={market.short_term_outlook}
          />

          <Outlook
            label="Medium Term"
            value={market.medium_term_outlook}
          />

          <Outlook
            label="Long Term"
            value={market.long_term_outlook}
          />
        </div>
      </div>

      {market.key_events.length > 0 && (
        <div className="mt-8 border-t border-slate-800 pt-6">
          <div className="flex items-center justify-between">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Key Events
            </p>

            <span className="text-xs text-slate-600">
              {market.key_events.length} events
            </span>
          </div>

          <div className="mt-4 space-y-3">
            {market.key_events.map((event, index) => (
              <article
                key={`${event.source_url}-${index}`}
                className="rounded-xl border border-slate-800 bg-slate-950/50 p-5"
              >
                <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                  <div>
                    <h3 className="text-sm font-semibold text-slate-200">
                      {event.title}
                    </h3>

                    <p className="mt-1 text-xs text-slate-500">
                      {event.source}
                      {event.published_at
                        ? ` • ${formatDate(event.published_at)}`
                        : ""}
                    </p>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <Tag value={event.sentiment} />
                    <Tag value={event.materiality} />
                    <Tag value={event.time_horizon} />
                  </div>
                </div>

                <p className="mt-4 text-sm leading-6 text-slate-400">
                  {event.summary}
                </p>

                <div className="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-xs text-slate-600">
                  <span>Impact: {event.potential_impact}</span>
                  <span>Scope: {event.entity_scope}</span>
                  {event.affected_areas.length > 0 && (
                    <span>
                      Areas: {event.affected_areas.join(", ")}
                    </span>
                  )}
                </div>

                <a
                  href={event.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-4 inline-block text-xs font-medium text-slate-300 hover:text-white"
                >
                  View source →
                </a>
              </article>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}

function FactorList({
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

function Outlook({
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

      <p className="mt-2 text-sm font-semibold capitalize text-slate-300">
        {value.replace("_", " ")}
      </p>
    </div>
  );
}

function Tag({ value }: { value: string }) {
  return (
    <span className="rounded-full border border-slate-800 bg-slate-900 px-2.5 py-1 text-[11px] font-medium capitalize text-slate-400">
      {value.replace("_", " ")}
    </span>
  );
}

function formatDate(value: string) {
  return new Date(value).toLocaleDateString();
}