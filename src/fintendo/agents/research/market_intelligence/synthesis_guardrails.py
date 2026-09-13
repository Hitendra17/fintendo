from fintendo.models.market_intelligence import (
    MarketEvent,
    MarketIntelligenceAnalysis,
)


class MarketIntelligenceSynthesisGuardrail:
    """
    Deterministic validation layer for synthesized market intelligence.

    This component checks that the final synthesis is structurally
    consistent with the validated events supplied to the synthesizer.

    It does not replace Gemini's reasoning or make investment decisions.
    """

    def validate(
        self,
        ticker: str,
        analysis: MarketIntelligenceAnalysis,
        events: list[MarketEvent],
    ) -> MarketIntelligenceAnalysis:
        if not ticker.strip():
            raise ValueError("ticker must not be empty.")

        if not events:
            raise ValueError("events must not be empty.")

        normalized_ticker = ticker.strip().upper()

        self._validate_ticker(
            analysis=analysis,
            ticker=normalized_ticker,
        )

        self._validate_score(analysis)
        self._validate_summary(analysis)
        self._validate_outlook(analysis)

        analysis = self._validate_event_references(
            analysis=analysis,
            events=events,
        )

        return analysis

    @staticmethod
    def _validate_ticker(
        analysis: MarketIntelligenceAnalysis,
        ticker: str,
    ) -> None:
        if analysis.ticker.strip().upper() != ticker:
            raise ValueError(
                f"Analysis ticker {analysis.ticker!r} does not match "
                f"requested ticker {ticker!r}."
            )

    @staticmethod
    def _validate_score(
        analysis: MarketIntelligenceAnalysis,
    ) -> None:
        if not 0 <= analysis.score <= 100:
            raise ValueError(
                f"Analysis score {analysis.score} must be between 0 and 100."
            )

    @staticmethod
    def _validate_summary(
        analysis: MarketIntelligenceAnalysis,
    ) -> None:
        if not analysis.summary.strip():
            raise ValueError(
                "Analysis summary must not be empty."
            )

    @staticmethod
    def _validate_outlook(
        analysis: MarketIntelligenceAnalysis,
    ) -> None:
        outlooks = (
            analysis.short_term_outlook,
            analysis.medium_term_outlook,
            analysis.long_term_outlook,
        )

        if any(outlook is None for outlook in outlooks):
            raise ValueError(
                "All time-horizon outlooks must be present."
            )

    @staticmethod
    def _validate_event_references(
        analysis: MarketIntelligenceAnalysis,
        events: list[MarketEvent],
    ) -> MarketIntelligenceAnalysis:
        event_sources = {
            str(event.source_url).strip().lower()
            for event in events
        }

        validated_key_events: list[MarketEvent] = []

        for event in analysis.key_events:
            if (
                event.ticker.strip().upper()
                != analysis.ticker.strip().upper()
            ):
                continue

            event_source = str(event.source_url).strip().lower()

            if event_source not in event_sources:
                continue

            validated_key_events.append(event)

        return analysis.model_copy(
            update={
                "key_events": validated_key_events,
            }
        )