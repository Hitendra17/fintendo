from fintendo.models.market_intelligence import MarketEvent


class MarketEventGuardrail:
    """
    Deterministic validation layer for Gemini-extracted market events.

    This component validates structural integrity and provenance.
    It does not make investment judgments or alter Gemini's
    interpretation of an event.
    """

    def validate(
        self,
        ticker: str,
        events: list[MarketEvent],
    ) -> list[MarketEvent]:
        if not ticker.strip():
            raise ValueError("ticker must not be empty.")

        validated_events: list[MarketEvent] = []
        seen_events: set[tuple[str, str]] = set()

        normalized_ticker = ticker.strip().upper()

        for event in events:
            self._validate_event(
                event=event,
                ticker=normalized_ticker,
            )

            event_key = self._event_key(event)

            if event_key in seen_events:
                continue

            seen_events.add(event_key)
            validated_events.append(event)

        return validated_events

    @staticmethod
    def _validate_event(
        event: MarketEvent,
        ticker: str,
    ) -> None:
        if event.ticker.strip().upper() != ticker:
            raise ValueError(
                f"Event ticker {event.ticker!r} does not match "
                f"requested ticker {ticker!r}."
            )

        if not event.source.strip():
            raise ValueError(
                "Event source must not be empty."
            )

        if not str(event.source_url).strip():
            raise ValueError(
                "Event source_url must not be empty."
            )

        if not event.title.strip():
            raise ValueError(
                "Event title must not be empty."
            )

        if not event.summary.strip():
            raise ValueError(
                "Event summary must not be empty."
            )

        if not event.event_type.strip():
            raise ValueError(
                "Event event_type must not be empty."
            )

        if not event.affected_areas:
            raise ValueError(
                "Event affected_areas must not be empty."
            )

    @staticmethod
    def _event_key(event: MarketEvent) -> tuple[str, str]:
        """
        Generate a deterministic identity for duplicate detection.

        Two events from the same source with the same title are
        considered duplicates.
        """
        return (
            str(event.source_url).strip().lower(),
            event.title.strip().lower(),
        )