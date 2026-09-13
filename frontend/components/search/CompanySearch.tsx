"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { SearchInput } from "./SearchInput";
import { SearchResults } from "./SearchResults";
import { useCompanySearch } from "@/hooks/useCompanySearch";

export function CompanySearch() {
  const [query, setQuery] = useState("");
  const router = useRouter();

  const { results, loading, error } = useCompanySearch(query);

  function handleSelect(ticker: string) {
    router.push(`/research?ticker=${encodeURIComponent(ticker)}`);
  }

  return (
    <div className="w-full">
      <SearchInput
        value={query}
        onChange={setQuery}
      />

      <SearchResults
        results={results}
        loading={loading}
        error={error}
        onSelect={handleSelect}
      />
    </div>
  );
}