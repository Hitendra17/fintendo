"use client";

import type { CompanySearchResult } from "@/types/company";

interface SearchResultsProps {
  results: CompanySearchResult[];
  loading: boolean;
  error: string | null;
  onSelect: (ticker: string) => void;
}

export function SearchResults({
  results,
  loading,
  error,
  onSelect,
}: SearchResultsProps) {
  if (loading) {
    return (
      <div className="mt-2 rounded-xl border border-slate-800 bg-slate-900 p-4">
        <p className="text-sm text-slate-400">Searching...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mt-2 rounded-xl border border-red-900/50 bg-red-950/20 p-4">
        <p className="text-sm text-red-400">{error}</p>
      </div>
    );
  }

  if (results.length === 0) {
    return null;
  }

  return (
    <div className="mt-2 overflow-hidden rounded-xl border border-slate-800 bg-slate-900 shadow-xl">
      {results.map((company) => (
        <button
          key={company.ticker}
          type="button"
          onClick={() => onSelect(company.ticker)}
          className="flex w-full items-center justify-between border-b border-slate-800 px-4 py-4 text-left last:border-b-0 hover:bg-slate-800/70"
        >
          <div>
            <p className="font-medium text-slate-100">
              {company.company_name}
            </p>

            <p className="mt-1 text-xs text-slate-500">
              {company.exchange}
            </p>
          </div>

          <span className="rounded-md bg-slate-800 px-3 py-1.5 text-sm font-semibold text-slate-300">
            {company.ticker}
          </span>
        </button>
      ))}
    </div>
  );
}