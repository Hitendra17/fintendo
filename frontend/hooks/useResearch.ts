"use client";

import { useEffect, useState } from "react";
import { getResearchReport } from "@/lib/research";
import type { ResearchReport } from "@/types/research";

export function useResearch(ticker: string | null) {
  const [report, setReport] = useState<ResearchReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!ticker) {
      setReport(null);
      setLoading(false);
      setError(null);
      return;
    }
    const requestedTicker = ticker;
    let cancelled = false;

    async function loadResearch() {
      setLoading(true);
      setError(null);

      try {
        const data = await getResearchReport(requestedTicker);

        if (!cancelled) {
          setReport(data);
        }
      } catch (err) {
        if (!cancelled) {
          setReport(null);
          setError(
            err instanceof Error
              ? err.message
              : "Unable to generate research report",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadResearch();

    return () => {
      cancelled = true;
    };
  }, [ticker]);

  return {
    report,
    loading,
    error,
  };
}