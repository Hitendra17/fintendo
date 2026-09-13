"use client";

import { useEffect, useState } from "react";
import { searchCompanies } from "@/lib/companies";
import type { CompanySearchResult } from "@/types/company";

export function useCompanySearch(query: string) {
  const [results, setResults] = useState<CompanySearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const trimmedQuery = query.trim();

    if (!trimmedQuery) {
      setResults([]);
      setLoading(false);
      setError(null);
      return;
    }

    let cancelled = false;

    const timeout = window.setTimeout(async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await searchCompanies(trimmedQuery);

        if (!cancelled) {
          setResults(data);
        }
      } catch (err) {
        if (!cancelled) {
          setResults([]);
          setError(
            err instanceof Error
              ? err.message
              : "Unable to search companies",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }, 300);

    return () => {
      cancelled = true;
      window.clearTimeout(timeout);
    };
  }, [query]);

  return { results, loading, error };
}