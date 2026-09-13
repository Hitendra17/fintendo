from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field
from fintendo.models.technical_confidence import TechnicalConfidence
from fintendo.models.technical_evidence import TechnicalEvidence
from fintendo.models.market_intelligence import MarketIntelligenceAnalysis



class Evidence(BaseModel):
    source: str = Field(min_length=1)
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    timestamp: datetime

class FundamentalEvidence(BaseModel):
    source: str = Field(min_length=1)
    field: str = Field(min_length=1)
    value: float | None = None
    period: datetime
    description: str = Field(min_length=1)

class FundamentalAnalysis(BaseModel):
    ticker: str = Field(min_length=1)
    score: float = Field(ge=0, le=100)
    summary: str = Field(min_length=1)
    strengths: list[str]
    weaknesses: list[str]
    catalysts: list[str]
    risks: list[str]
    evidence: list[FundamentalEvidence]
    confidence: float = Field(ge=0, le=1)


class TechnicalAnalysis(BaseModel):
    ticker: str = Field(min_length=1)
    score: float = Field(ge=0, le=100)
    summary: str = Field(min_length=1)
    trend: Literal["bullish", "bearish", "neutral", "mixed"]
    momentum: Literal["bullish", "bearish", "neutral", "mixed"]
    volatility: Literal["low", "moderate", "high"]
    bullish_signals: list[str]
    bearish_signals: list[str]
    support_levels: list[float]
    resistance_levels: list[float]
    outlook: str = Field(min_length=1)
    evidence: list[TechnicalEvidence]
    confidence: TechnicalConfidence

class SentimentAnalysis(BaseModel):
    ticker: str = Field(min_length=1)
    score: float = Field(ge=0, le=100)
    summary: str = Field(min_length=1)
    sentiment: str = Field(min_length=1)
    key_themes: list[str]
    positive_signals: list[str]
    negative_signals: list[str]
    risks: list[str]
    evidence: list[Evidence]
    confidence: float = Field(ge=0, le=1)

class CommitteeDecision(BaseModel):
    ticker: str = Field(min_length=1)
    recommendation: str = Field(min_length=1)
    conviction: float = Field(ge=0, le=100)
    rationale: str = Field(min_length=1)
    bull_case: list[str]
    bear_case: list[str]
    key_risks: list[str]
    confidence: float = Field(ge=0, le=1)

class ResearchReport(BaseModel):
    ticker: str = Field(min_length=1)
    generated_at: datetime
    fundamental: FundamentalAnalysis
    technical: TechnicalAnalysis
    market_intelligence: MarketIntelligenceAnalysis | None
    committee: CommitteeDecision

class FundamentalAnalysisOutput(BaseModel):
    ticker: str = Field(min_length=1)
    score: float = Field(ge=0, le=100)
    summary: str = Field(min_length=1)
    strengths: list[str]
    weaknesses: list[str]
    catalysts: list[str]
    risks: list[str]
    