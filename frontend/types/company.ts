export interface CompanySearchResult {
  ticker: string;
  company_name: string;
  exchange: string;
  sector?: string | null;
}
