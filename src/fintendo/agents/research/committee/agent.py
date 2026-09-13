from fintendo.llm.gemini import GeminiClient
from fintendo.models.market_intelligence import MarketIntelligenceAnalysis
from fintendo.models.research import (
    CommitteeDecision,
    FundamentalAnalysis,
    TechnicalAnalysis,
)


class CommitteeAgent:
    """
    Gemini-powered committee layer for Fintendo Research.

    The Committee Agent does not perform independent research.
    It arbitrates the outputs of the Fundamental, Technical, and
    Market Intelligence research layers.
    """

    def __init__(self, llm: GeminiClient) -> None:
        self.llm = llm

    def decide(
        self,
        fundamental: FundamentalAnalysis,
        technical: TechnicalAnalysis,
        market_intelligence: MarketIntelligenceAnalysis | None,
    ) -> CommitteeDecision:
        ticker = fundamental.ticker.strip().upper()

        if not ticker:
            raise ValueError("ticker must not be empty.")

        if fundamental.ticker.strip().upper() != ticker:
            raise ValueError("fundamental ticker does not match.")

        if technical.ticker.strip().upper() != ticker:
            raise ValueError("technical ticker does not match.")

        if (
            market_intelligence is not None
            and market_intelligence.ticker.strip().upper() != ticker
        ):
            raise ValueError("market intelligence ticker does not match.")

        prompt = self._build_prompt(
            ticker=ticker,
            fundamental=fundamental,
            technical=technical,
            market_intelligence=market_intelligence,
        )

        return self.llm.generate_structured(
            prompt,
            CommitteeDecision,
        )

    @staticmethod
    def _build_prompt(
        ticker: str,
        fundamental: FundamentalAnalysis,
        technical: TechnicalAnalysis,
        market_intelligence: MarketIntelligenceAnalysis | None,
    ) -> str:
        fundamental_data = fundamental.model_dump(mode="json")
        technical_data = technical.model_dump(mode="json")
        market_intelligence_data = (
            market_intelligence.model_dump(mode="json")
            if market_intelligence is not None
            else None
        )

        return f"""
You are Fintendo Research's Committee Agent.

Your role is to act as the final research arbitration layer for
{ticker}.

You are NOT an independent research agent.

Three specialized research layers are available to the committee:

1. Fundamental Analysis
2. Technical Analysis
3. Market Intelligence

A specialist research layer may be unavailable. If a supplied
specialist analysis is unavailable, treat that as missing evidence,
not as a neutral or negative signal.

Your task is to evaluate these outputs together and produce
one final committee decision.

IMPORTANT:

1. Use ONLY the supplied FundamentalAnalysis, TechnicalAnalysis,
   and MarketIntelligenceAnalysis.

2. Do not perform new web research.

3. Do not invent financial data, market events, technical indicators,
   company information, or external facts.

4. Do not recalculate the underlying financial or technical metrics.

5. Do not blindly average the three scores.

6. Treat each specialist analysis as evidence produced by a separate
   research layer.

7. Identify where the available research layers agree.

8. Identify where the available research layers conflict.

9. When the research layers conflict, explicitly reason about the
   nature of the conflict rather than forcing them into agreement.

10. Consider evidence quality and confidence when determining
    conviction.

11. A high score from one agent does not automatically override
    contradictory evidence from another agent.

12. Do not treat confidence as predictive accuracy.

13. Do not present certainty where the underlying research is
    uncertain or conflicting.

14. Do not invent information to strengthen the bull or bear case.

15. Do not provide guaranteed predictions.

16. Do not fabricate evidence that is absent from the supplied
    analyses.

17. The final recommendation must be based on the combined available
    research, not on any single specialist output.

18. If Market Intelligence is unavailable, do not infer market
    sentiment, events, catalysts, risks, or outlook from its absence.

19. If Market Intelligence is unavailable, explicitly acknowledge
    that the current information environment could not be assessed.

20. Do not treat unavailable Market Intelligence as a score of 50,
    neutral sentiment, or any other implied assessment.

21. When a research layer is unavailable, conviction should reflect
    the incompleteness of the research.

22. The final recommendation must still be based only on the
    available specialist analyses.

## COMMITTEE REASONING

Evaluate the following dimensions:

### 1. Fundamental View

Determine what the fundamental analysis implies about the underlying
quality of the company.

Consider:

- Fundamental score
- Growth
- Profitability
- Cash-flow quality
- Balance-sheet quality
- Fundamental strengths
- Fundamental weaknesses
- Fundamental catalysts
- Fundamental risks
- Fundamental confidence

Do not repeat every fundamental metric. Identify what matters most
for the final decision.

### 2. Technical View

Determine what the technical analysis implies about the current
market setup.

Consider:

- Technical score
- Trend
- Momentum
- Volatility
- Bullish signals
- Bearish signals
- Support and resistance
- Technical outlook
- Technical confidence

Pay particular attention to conflicts between trend and momentum.

### 3. Market Intelligence View

If Market Intelligence is available, determine what it implies about
the current information environment.

If Market Intelligence is unavailable, explicitly state that no
current market-intelligence conclusion can be drawn. Do not infer
sentiment or outlook from the absence of evidence.

Consider:

- Market intelligence score
- Overall sentiment
- Sentiment strength
- Key events
- Positive factors
- Negative factors
- Catalysts
- Risks
- Short-term outlook
- Medium-term outlook
- Long-term outlook

Do not invent a confidence value for Market Intelligence because
the supplied schema does not provide one.

### 4. AGREEMENT

Identify the strongest areas where the available research layers
support the same conclusion.

Examples include:

- Strong fundamentals + positive market developments
- Weak fundamentals + negative market developments
- Bullish technicals + positive short-term market intelligence

Only identify agreement that is actually supported by the supplied
outputs.

If Market Intelligence is unavailable, do not claim agreement with
Market Intelligence.

### 5. CONFLICT

Identify meaningful disagreements between the available research
layers.

Examples include:

- Strong fundamentals but bearish technicals
- Positive market intelligence but weak fundamentals
- Bullish technical trend but negative market developments

Explain what the conflict means for the final decision.

Do not eliminate a conflict simply to produce a cleaner conclusion.

### 6. CONVICTION

Assign conviction from 0 to 100.

Conviction represents how strongly the combined available research
supports the committee's conclusion.

Consider:

- Agreement between available research layers
- Severity of conflicts
- Evidence quality
- Fundamental confidence
- Technical confidence
- Completeness of the supplied research
- Whether the conclusion depends heavily on one uncertain signal

If Market Intelligence is unavailable, account for that missing
research when determining conviction.

Conviction is NOT a probability of future returns.

### 7. RECOMMENDATION

Produce a concise recommendation based only on the combined available
research.

The recommendation should communicate the committee's overall stance.

Do not provide a guaranteed prediction.

Do not invent a specific price target.

Do not claim certainty.

### 8. BULL CASE

Provide the strongest evidence-supported reasons why the company
could have a favorable outcome.

These must come from the supplied research.

Do not manufacture a bull case from unavailable research.

### 9. BEAR CASE

Provide the strongest evidence-supported reasons why the company
could have an unfavorable outcome.

These must come from the supplied research.

Do not manufacture a bear case from unavailable research.

### 10. KEY RISKS

Identify the most important risks that should influence the final
decision.

Prioritize risks supported by the specialist analyses.

Do not manufacture additional risks.

### 11. RATIONALE

Write a concise final rationale explaining:

- What the available research collectively indicates
- Where the available research agrees
- Where the available research disagrees
- Which considerations matter most
- Whether any specialist research was unavailable
- Why the final recommendation and conviction are justified

The rationale should synthesize rather than simply repeat the
specialist summaries.

## OUTPUT RULES

Return exactly the supplied CommitteeDecision schema.

The fields are:

- ticker
- recommendation
- conviction
- rationale
- bull_case
- bear_case
- key_risks
- confidence

The ticker must be {ticker}.

Keep the output concise, professional, and evidence-grounded.

## FUNDAMENTAL ANALYSIS

{fundamental_data}

## TECHNICAL ANALYSIS

{technical_data}

## MARKET INTELLIGENCE ANALYSIS

{market_intelligence_data}

If the value above is null, Market Intelligence is unavailable.

Do not interpret null as neutral sentiment, negative sentiment, a score
of 50, or any other implied assessment.

Do not invent market events, catalysts, risks, sentiment, or outlook
when Market Intelligence is unavailable.

Produce the final CommitteeDecision for {ticker}.
""".strip()