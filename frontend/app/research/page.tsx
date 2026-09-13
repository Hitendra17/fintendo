"use client";

import { ArrowLeft } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";

import { CommitteeCard } from "@/components/committee/CommitteeCard";
import { FundamentalSection } from "@/components/fundamental/FundamentalSection";
import { MarketIntelligenceSection } from "@/components/market/MarketIntelligenceSection";
import { ExecutiveSummary } from "@/components/research/ExecutiveSummary";
import { ResearchHeader } from "@/components/research/ResearchHeader";
import { TechnicalSection } from "@/components/technical/TechnicalSection";
import { OutlookSection } from "@/components/outlook/OutlookSection";
import { useResearch } from "@/hooks/useResearch";

export default function ResearchPage() {
  const searchParams = useSearchParams();
  const ticker = searchParams.get("ticker");
  const router = useRouter();
  const { report, loading, error } = useResearch(ticker);

  if (!ticker) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-white">
        <div className="text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.25em] text-slate-500">
            FINTENDO RESEARCH
          </p>

          <h1 className="mt-4 text-2xl font-semibold">
            No company selected
          </h1>

          <p className="mt-2 text-sm text-slate-500">
            Search for a company to generate a research report.
          </p>
        </div>
      </main>
    );
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-950 px-6 py-16 text-white">
        <div className="mx-auto flex min-h-[70vh] max-w-3xl flex-col items-center justify-center text-center">
          <div className="h-10 w-10 animate-spin rounded-full border-2 border-slate-800 border-t-slate-300" />

          <p className="mt-6 text-sm font-medium text-slate-300">
            Generating research report
          </p>

          <p className="mt-2 max-w-md text-sm leading-6 text-slate-600">
            Analyzing fundamentals, technical signals, and market intelligence
            for {ticker.toUpperCase()}.
          </p>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-white">
        <div className="w-full max-w-lg rounded-2xl border border-red-900/40 bg-red-950/10 p-8 text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.25em] text-red-500">
            Research Error
          </p>

          <h1 className="mt-4 text-xl font-semibold text-white">
            Unable to generate report
          </h1>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            {error}
          </p>
        </div>
      </main>
    );
  }

  if (!report) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-white">
        <div className="text-center">
          <p className="text-sm text-slate-500">
            No research report available.
          </p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-8 text-white sm:px-6 lg:px-8">
    <div className="mx-auto max-w-7xl">
    <button
    type="button"
    onClick={() => router.push("/")}
    className="mb-6 inline-flex items-center gap-2 text-sm text-slate-500 transition hover:text-slate-200"
    >
    <ArrowLeft size={16} />
    Back to search
    </button>

  <ResearchHeader report={report} />

        <div className="mt-8">
          <CommitteeCard committee={report.committee} />
        </div>

        <div className="mt-6">
          <ExecutiveSummary report={report} />
        </div>

        <div className="mt-6">
          <FundamentalSection fundamental={report.fundamental} />
        </div>

        <div className="mt-6">
          <TechnicalSection technical={report.technical} />
        </div>

        {report.market_intelligence && (
          <div className="mt-6">
            <MarketIntelligenceSection
              market={report.market_intelligence}
            />
          </div>
        )}

        <div className="mt-6">
          <OutlookSection report={report} />
        </div>

        <footer className="border-t border-slate-800 py-8 text-center text-xs text-slate-600">
          Fintendo Research
        </footer>
      </div>
    </main>
  );
}