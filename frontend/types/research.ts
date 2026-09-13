export type TechnicalEvidenceType = "observed" | "derived" | "level";

export interface TechnicalConfidence {
  score: number;
  observations: number;
  history_score: number;
  trend_score: number;
  momentum_score: number;
  volatility_score: number;
  levels_score: number;
  missing_indicators: string[];
  limitations: string[];
}

export interface TechnicalEvidence {
  source: string;
  field: string;
  evidence_type: TechnicalEvidenceType;
  value: number;
  period: string;
  description: string;
}

export interface FundamentalEvidence {
  source: string;
  field: string;
  value: number | null;
  period: string;
  description: string;
}

export interface FundamentalAnalysis {
  ticker: string;
  score: number;
  summary: string;
  strengths: string[];
  weaknesses: string[];
  catalysts: string[];
  risks: string[];
  evidence: FundamentalEvidence[];
  confidence: number;
}

export type TechnicalTrend = "bullish" | "bearish" | "neutral" | "mixed";
export type TechnicalMomentum = "bullish" | "bearish" | "neutral" | "mixed";
export type TechnicalVolatility = "low" | "moderate" | "high";

export interface TechnicalAnalysis {
  ticker: string;
  score: number;
  summary: string;
  trend: TechnicalTrend;
  momentum: TechnicalMomentum;
  volatility: TechnicalVolatility;
  bullish_signals: string[];
  bearish_signals: string[];
  support_levels: number[];
  resistance_levels: number[];
  outlook: string;
  evidence: TechnicalEvidence[];
  confidence: TechnicalConfidence;
}

export type Sentiment =
  | "positive"
  | "negative"
  | "neutral"
  | "mixed";

export type SentimentStrength = "weak" | "moderate" | "strong";

export type Materiality = "low" | "moderate" | "high";

export type ImpactDirection =
  | "positive"
  | "negative"
  | "neutral"
  | "uncertain";

export type TimeHorizon =
  | "short_term"
  | "medium_term"
  | "long_term"
  | "uncertain";

export interface NewsArticle {
  source: string;
  title: string;
  url: string;
  published_at: string | null;
  author: string | null;
  content: string;
  ticker: string;
}

export interface MarketEvent {
  ticker: string;
  event_type: string;
  title: string;
  summary: string;
  sentiment: Sentiment;
  sentiment_strength: SentimentStrength;
  materiality: Materiality;
  potential_impact: ImpactDirection;
  affected_areas: string[];
  time_horizon: TimeHorizon;
  entity_scope: string;
  source: string;
  source_url: string;
  published_at: string | null;
}

export interface MarketIntelligenceAnalysis {
  ticker: string;
  score: number;
  overall_sentiment: Sentiment;
  sentiment_strength: SentimentStrength;
  summary: string;
  key_events: MarketEvent[];
  positive_factors: string[];
  negative_factors: string[];
  catalysts: string[];
  risks: string[];
  short_term_outlook: ImpactDirection;
  medium_term_outlook: ImpactDirection;
  long_term_outlook: ImpactDirection;
}

export interface Evidence {
  source: string;
  title: string;
  content: string;
  timestamp: string;
}

export interface SentimentAnalysis {
  ticker: string;
  score: number;
  summary: string;
  sentiment: string;
  key_themes: string[];
  positive_signals: string[];
  negative_signals: string[];
  risks: string[];
  evidence: Evidence[];
  confidence: number;
}

export interface CommitteeDecision {
  ticker: string;
  recommendation: string;
  conviction: number;
  rationale: string;
  bull_case: string[];
  bear_case: string[];
  key_risks: string[];
  confidence: number;
}

export interface ResearchReport {
  ticker: string;
  generated_at: string;
  fundamental: FundamentalAnalysis;
  technical: TechnicalAnalysis;
  market_intelligence: MarketIntelligenceAnalysis | null;
  committee: CommitteeDecision;
}