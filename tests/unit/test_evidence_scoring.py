from datetime import datetime, timedelta, timezone

import pytest

from fintendo.data.evidence_scoring import EvidenceScorer
from fintendo.data.source_quality import SourceQuality, SourceTier


def make_source(score: float = 0.9) -> SourceQuality:
    return SourceQuality(
        source_name="Reuters",
        tier=SourceTier.TIER_A,
        score=score,
        is_primary=False,
        rationale="High-quality financial journalism.",
    )


def test_high_quality_recent_relevant_article_scores_high():
    scorer = EvidenceScorer()

    published_at = datetime.now(timezone.utc) - timedelta(hours=2)

    result = scorer.calculate(
        source_quality=make_source(),
        published_at=published_at,
        ticker="TCS",
        article_title="TCS reports strong quarterly growth",
        article_content="TCS " + ("reported strong revenue growth. " * 100),
    )

    assert result.source_score == 0.9
    assert result.recency_score > 0.9
    assert result.relevance_score == 1.0
    assert result.completeness_score == 1.0
    assert result.overall_score > 0.85


def test_old_article_has_lower_recency():
    scorer = EvidenceScorer()

    published_at = datetime.now(timezone.utc) - timedelta(days=10)

    result = scorer.calculate(
        source_quality=make_source(),
        published_at=published_at,
        ticker="TCS",
        article_title="TCS historical update",
        article_content="TCS " + ("historical business information. " * 100),
    )

    assert result.recency_score < 0.05


def test_missing_publication_date_uses_neutral_recency():
    scorer = EvidenceScorer()

    result = scorer.calculate(
        source_quality=make_source(),
        published_at=None,
        ticker="TCS",
        article_title="TCS business update",
        article_content="TCS " + ("business information. " * 100),
    )

    assert result.recency_score == 0.50


def test_ticker_in_title_gets_highest_relevance():
    scorer = EvidenceScorer()

    result = scorer.calculate(
        source_quality=make_source(),
        published_at=None,
        ticker="TCS",
        article_title="TCS announces major AI partnership",
        article_content="The company announced a new partnership.",
    )

    assert result.relevance_score == 1.0


def test_rejects_empty_ticker():
    scorer = EvidenceScorer()

    with pytest.raises(ValueError, match="ticker must not be empty"):
        scorer.calculate(
            source_quality=make_source(),
            published_at=None,
            ticker="   ",
            article_title="Test article",
            article_content="Some article content.",
        )