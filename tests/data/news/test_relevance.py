from fintendo.data.company.models import CompanyProfile
from fintendo.data.relevance import MarketArticleRelevanceChecker
from fintendo.models.market_intelligence import NewsArticle


PROFILE = CompanyProfile(
    ticker="INFY",
    company_name="Infosys",
    exchange="NSE",
    official_website="https://www.infosys.com",
    aliases=["Infosys Limited"],
)


def make_article(
    title: str,
    content: str,
    url: str = "https://example.com/article",
) -> NewsArticle:
    return NewsArticle(
        source="Test Source",
        title=title,
        url=url,
        content=content,
        ticker="INFY",
    )


def test_direct_company_article_gets_high_relevance() -> None:
    article = make_article(
        title="Infosys announces new AI partnership",
        content="Infosys will expand its artificial intelligence business.",
    )

    score = MarketArticleRelevanceChecker().score(
        article=article,
        profile=PROFILE,
    )

    assert score >= 60


def test_unrelated_article_gets_low_relevance() -> None:
    article = make_article(
        title="India and China discuss trade relations",
        content="The two countries discussed bilateral trade and diplomacy.",
    )

    score = MarketArticleRelevanceChecker().score(
        article=article,
        profile=PROFILE,
    )

    assert score == 0


def test_company_mentioned_in_body_gets_some_relevance() -> None:
    article = make_article(
        title="Indian IT stocks gain",
        content="Infosys and other IT companies gained during today's session.",
    )

    score = MarketArticleRelevanceChecker().score(
        article=article,
        profile=PROFILE,
    )

    assert score >= 20