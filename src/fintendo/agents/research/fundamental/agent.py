from fintendo.llm.gemini import GeminiClient
from fintendo.models.fundamental import FundamentalSnapshot
from fintendo.models.research import (
    FundamentalAnalysis,
    FundamentalAnalysisOutput,
)
from fintendo.quant.confidence import FundamentalConfidenceCalculator
from fintendo.quant.evidence import FundamentalEvidenceBuilder


class FundamentalAgent:
    def __init__(self, llm: GeminiClient) -> None:
        self.llm = llm
        self.confidence_calculator = FundamentalConfidenceCalculator()
        self.evidence_builder = FundamentalEvidenceBuilder()

    def analyze(
        self,
        snapshot: FundamentalSnapshot,
    ) -> FundamentalAnalysis:

        prompt = f"""
You are the Fundamental Analysis Agent for Fintendo,
an India-centric quantitative research platform.

Your job is to interpret a deterministic fundamental snapshot
for {snapshot.ticker}.

The financial calculations have already been performed by
Fintendo's Fundamental Engine.

You must NOT recalculate financial metrics.
You must interpret the relationships between the supplied metrics.

Evaluate the company across the following areas.

1. GROWTH

Consider:

- Revenue year-over-year growth
- Net income year-over-year growth
- Revenue CAGR
- Net income CAGR

Determine:

- Whether the company is growing
- Whether earnings are growing faster or slower than revenue
- Whether the growth profile appears stable or divergent

Do not describe growth as "strong" or "weak" without considering
the other supplied metrics.

2. PROFITABILITY

Consider:

- Operating margin
- Net income margin
- Return on equity
- Return on assets

Evaluate:

- Overall profitability
- Efficiency of the company's asset base
- Returns generated on shareholder capital
- Whether the profitability profile is a strength or weakness

Do not compare these metrics with industry averages because
industry benchmark data has not been supplied.

3. CASH FLOW QUALITY

Consider:

- Operating cash flow
- Operating cash flow margin
- Free cash flow
- Free cash flow margin
- Free cash flow growth
- Free cash flow conversion

Evaluate:

- Whether accounting earnings are supported by cash generation
- Whether the company is generating positive free cash flow
- Whether free cash flow is improving or deteriorating
- Whether cash generation appears strong relative to earnings

If any cash-flow metric is unavailable, explicitly acknowledge
the missing information.

4. BALANCE SHEET AND LEVERAGE

Consider:

- Total debt
- Debt-to-equity
- Current ratio
- Net debt-to-operating-income

Evaluate:

- Financial leverage
- Short-term liquidity
- Debt burden relative to operating income
- Whether the balance sheet represents a material risk

Do not automatically classify a ratio as good or bad without
considering the complete supplied balance-sheet picture.

5. RELATIONSHIPS BETWEEN METRICS

Look for important relationships such as:

- Revenue growth versus earnings growth
- Revenue growth versus profitability
- Net income versus free cash flow
- ROE versus ROA
- Debt versus operating income
- Liquidity versus leverage

These relationships are more important than discussing each
metric independently.

6. STRENGTHS

Identify the most important fundamental strengths supported
by the supplied data.

Do not invent business characteristics that are not present
in the snapshot.

7. WEAKNESSES

Identify the most important fundamental weaknesses or areas
of concern supported by the supplied data.

Do not manufacture risks when the supplied data does not support them.

8. CATALYSTS

Identify potential fundamental catalysts that could improve
the company's financial profile.

Catalysts must be grounded in the supplied data.

Do not invent future company initiatives.

9. RISKS

Identify the most important financial risks supported by
the supplied data.

Distinguish between:

- observed weakness
- potential risk
- missing information

Do not present speculation as fact.

10. OVERALL ASSESSMENT

Synthesize the complete fundamental picture.

Assign a fundamental score from 0 to 100.

The score should reflect the quality of the supplied
fundamental evidence.

Consider:

- growth
- profitability
- cash generation
- balance-sheet quality
- consistency between metrics
- data completeness

The score must not be based on a single metric.

IMPORTANT RULES:

- Use ONLY the supplied FundamentalSnapshot.
- Do not invent financial values.
- Do not invent company information.
- Do not use external knowledge.
- Do not assume industry benchmarks that were not supplied.
- Treat null values as unavailable.
- Never infer a missing metric.
- Do not make guaranteed predictions.
- Clearly distinguish facts from interpretation.
- Avoid repeating the same information across fields.
- Keep the summary concise and professional.

Fintendo will independently construct evidence and calculate
confidence after your analysis.

Do not provide evidence objects.
Do not provide a confidence value.

Fundamental snapshot:

{snapshot.model_dump_json(indent=2)}

Return the analysis using the provided structured schema.
"""

        analysis = self.llm.generate_structured(
            prompt,
            FundamentalAnalysisOutput,
        )

        evidence = self.evidence_builder.build(snapshot)

        confidence = self.confidence_calculator.calculate(snapshot)

        return FundamentalAnalysis(
            **analysis.model_dump(),
            evidence=evidence,
            confidence=confidence,
        )