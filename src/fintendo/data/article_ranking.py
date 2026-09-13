from pydantic import BaseModel

from fintendo.data.evidence_scoring import EvidenceScore, EvidenceScorer
from fintendo.data.source_quality import SourceQualityScorer
from fintendo.models.market_intelligence import NewsArticle


class RankedArticle(BaseModel):
    article: NewsArticle
    evidence_score: EvidenceScore


class ArticleRankingService:
    """
    Assigns deterministic evidence priority to normalized news articles.

    This service does not perform sentiment analysis or investment reasoning.
    """

    def __init__(
        self,
        source_quality_scorer: SourceQualityScorer,
        evidence_scorer: EvidenceScorer,
    ) -> None:
        self.source_quality_scorer = source_quality_scorer
        self.evidence_scorer = evidence_scorer

    def rank(
        self,
        articles: list[NewsArticle],
    ) -> list[RankedArticle]:
        ranked_articles: list[RankedArticle] = []

        for article in articles:
            source_quality = self.source_quality_scorer.score(
                article.source
            )

            evidence_score = self.evidence_scorer.calculate(
                source_quality=source_quality,
                published_at=article.published_at,
                ticker=article.ticker,
                article_title=article.title,
                article_content=article.content,
            )

            ranked_articles.append(
                RankedArticle(
                    article=article,
                    evidence_score=evidence_score,
                )
            )

        return sorted(
            ranked_articles,
            key=lambda item: item.evidence_score.overall_score,
            reverse=True,
        )