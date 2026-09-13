import { apiFetch } from "@/lib/api";
import type { ResearchReport } from "@/types/research";

const inFlightRequests = new Map<string, Promise<ResearchReport>>();

export function getResearchReport(
  ticker: string,
): Promise<ResearchReport> {
  const normalizedTicker = ticker.trim().toUpperCase();

  const existingRequest = inFlightRequests.get(normalizedTicker);

  if (existingRequest) {
    return existingRequest;
  }

  const request = apiFetch<ResearchReport>(
    "/api/v1/research/company",
    {
      method: "POST",
      body: JSON.stringify({
        ticker: normalizedTicker,
      }),
    },
  ).finally(() => {
    inFlightRequests.delete(normalizedTicker);
  });

  inFlightRequests.set(normalizedTicker, request);

  return request;
}