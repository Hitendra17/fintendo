from datetime import datetime, timezone

from fintendo.data.article_ranking import ArticleRankingService
from fintendo.data.evidence_scoring import EvidenceScorer
from fintendo.data.source_quality import SourceQualityScorer
from fintendo.models.market_intelligence import NewsArticle


def make_article(
    source: str,
    title: str,
    content: str,
    published_at: datetime | None,
) -> NewsArticle:
    return NewsArticle(
        source=source,
        title=title,
        url="https://example.com/article",
        published_at=published_at,
        author=None,
        content=content,
        ticker="TCS",
    )


def test_ranks_articles_by_evidence_score():
    service = ArticleRankingService(
        source_quality_scorer=SourceQualityScorer(),
        evidence_scorer=EvidenceScorer(),
    )

    articles = [
        make_article(
            source="Random Finance Blog",
            title="TCS business update",
            content="TCS " + ("business information. " * 100),
            published_at=datetime.now(timezone.utc),
        ),
        make_article(
            source="Reuters",
            title="TCS reports strong growth",
            content="TCS " + ("strong revenue growth. " * 100),
            published_at=datetime.now(timezone.utc),
        ),
    ]

    result = service.rank(articles)

    assert len(result) == 2
    assert result[0].article.source == "Reuters"
    assert (
        result[0].evidence_score.overall_score
        > result[1].evidence_score.overall_score
    )


def test_empty_input_returns_empty_list():
    service = ArticleRankingService(
        source_quality_scorer=SourceQualityScorer(),
        evidence_scorer=EvidenceScorer(),
    )

    assert service.rank([]) == []