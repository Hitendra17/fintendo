import { apiFetch } from "@/lib/api";
import type { CompanySearchResult } from "@/types/company";

export async function searchCompanies(
  query: string,
): Promise<CompanySearchResult[]> {
  const trimmedQuery = query.trim();

  if (!trimmedQuery) {
    return [];
  }

  return apiFetch<CompanySearchResult[]>("/api/v1/companies/search", {
    params: {
      q: trimmedQuery,
    },
  });
}
