from datetime import datetime, timezone

from pydantic import BaseModel, Field

from fintendo.data.source_quality import SourceQuality


class EvidenceScore(BaseModel):
    """
    Deterministic assessment of how much weight an article should receive.

    This is an evidence-quality score, not a sentiment score.
    """

    source_score: float = Field(ge=0, le=1)
    recency_score: float = Field(ge=0, le=1)
    relevance_score: float = Field(ge=0, le=1)
    completeness_score: float = Field(ge=0, le=1)

    overall_score: float = Field(ge=0, le=1)


class EvidenceScorer:
    """
    Calculates article-level evidence priority.

    No LLM reasoning occurs here.
    """

    SOURCE_WEIGHT = 0.40
    RECENCY_WEIGHT = 0.25
    RELEVANCE_WEIGHT = 0.20
    COMPLETENESS_WEIGHT = 0.15

    RECENCY_HALF_LIFE_HOURS = 48

    def calculate(
        self,
        source_quality: SourceQuality,
        published_at: datetime | None,
        ticker: str,
        article_title: str,
        article_content: str,
    ) -> EvidenceScore:
        if not ticker.strip():
            raise ValueError("ticker must not be empty.")

        if not article_title.strip():
            raise ValueError("article_title must not be empty.")

        if not article_content.strip():
            raise ValueError("article_content must not be empty.")

        recency_score = self._calculate_recency_score(
            published_at
        )

        relevance_score = self._calculate_relevance_score(
            ticker=ticker,
            title=article_title,
            content=article_content,
        )

        completeness_score = self._calculate_completeness_score(
            published_at=published_at,
            article_title=article_title,
            article_content=article_content,
        )

        overall_score = (
            source_quality.score * self.SOURCE_WEIGHT
            + recency_score * self.RECENCY_WEIGHT
            + relevance_score * self.RELEVANCE_WEIGHT
            + completeness_score * self.COMPLETENESS_WEIGHT
        )

        return EvidenceScore(
            source_score=source_quality.score,
            recency_score=recency_score,
            relevance_score=relevance_score,
            completeness_score=completeness_score,
            overall_score=round(overall_score, 4),
        )

    def _calculate_recency_score(
        self,
        published_at: datetime | None,
    ) -> float:
        if published_at is None:
            return 0.50

        now = datetime.now(timezone.utc)

        if published_at.tzinfo is None:
            published_at = published_at.replace(tzinfo=timezone.utc)

        age_hours = max(
            0,
            (now - published_at).total_seconds() / 3600,
        )

        return round(
            0.5 ** (age_hours / self.RECENCY_HALF_LIFE_HOURS),
            4,
        )

    @staticmethod
    def _calculate_relevance_score(
        ticker: str,
        title: str,
        content: str,
    ) -> float:
        ticker_upper = ticker.strip().upper()

        title_upper = title.upper()
        content_upper = content.upper()

        if ticker_upper in title_upper:
            return 1.0

        if ticker_upper in content_upper:
            return 0.85

        return 0.30

    @staticmethod
    def _calculate_completeness_score(
        published_at: datetime | None,
        article_title: str,
        article_content: str,
    ) -> float:
        score = 0.0

        if article_title.strip():
            score += 0.25

        if published_at is not None:
            score += 0.25

        if len(article_content.strip()) >= 500:
            score += 0.50
        elif len(article_content.strip()) >= 200:
            score += 0.30

        return min(score, 1.0)