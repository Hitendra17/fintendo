import pytest

from fintendo.agents.research.market_intelligence.event_extractor import (
    MarketEventExtractor,
)
from fintendo.data.article_deduplicator import ArticleDeduplicator
from fintendo.data.article_metadata import ArticleMetadataExtractor
from fintendo.data.article_normalizer import ArticleNormalizer
from fintendo.data.html_parser import HTMLParser
from fintendo.data.news_ingestion import NewsIngestionService
from fintendo.data.url_normalizer import URLNormalizer
from fintendo.data.web_fetcher import WebFetcher
from fintendo.llm.gemini import GeminiClient


@pytest.mark.integration
def test_real_market_event_extractor():
    ticker = "RELIANCE"

    # ---------------------------------------------------------
    # 1. Real Reliance corporate-announcements page
    # ---------------------------------------------------------

    urls = [
        (
            "https://www.ril.com/"
            "investor/resource-center/"
            "corporate-announcements"
        )
    ]

    # ---------------------------------------------------------
    # 2. Build the real web ingestion layer
    # ---------------------------------------------------------

    url_normalizer = URLNormalizer()
    article_normalizer = ArticleNormalizer()

    ingestion = NewsIngestionService(
        web_fetcher=WebFetcher(),
        html_parser=HTMLParser(),
        article_normalizer=article_normalizer,
        url_normalizer=url_normalizer,
        article_deduplicator=ArticleDeduplicator(
            url_normalizer=url_normalizer,
            article_normalizer=article_normalizer,
        ),
        metadata_extractor=ArticleMetadataExtractor(),
    )

    # ---------------------------------------------------------
    # 3. Fetch and normalize the real Reliance page
    # ---------------------------------------------------------

    articles = ingestion.ingest(
        urls=urls,
        ticker=ticker,
        source="Reliance Investor Relations",
    )

    assert articles, (
        "Expected the real Reliance corporate-announcements "
        "page to be successfully fetched and normalized."
    )

    print(
        f"\nIngested {len(articles)} real "
        "market-information page(s)."
    )

    for article in articles:
        print("\n" + "=" * 70)
        print(f"SOURCE: {article.source}")
        print(f"TITLE: {article.title}")
        print(f"URL: {article.url}")
        print(f"PUBLISHED: {article.published_at}")
        print(f"CONTENT LENGTH: {len(article.content)}")

        print("\nCONTENT PREVIEW:")
        print(article.content[:1500])

    # ---------------------------------------------------------
    # 4. Real Gemini #1
    # ---------------------------------------------------------

    extractor = MarketEventExtractor(
        llm=GeminiClient(),
    )

    events = extractor.extract(
        ticker=ticker,
        articles=articles,
        rag_context=[],
    )

    # ---------------------------------------------------------
    # 5. Validate Gemini's structured output
    # ---------------------------------------------------------

    assert isinstance(events, list)

    print(
        f"\nGemini extracted {len(events)} "
        "market event(s)."
    )

    for event in events:
        print("\n" + "=" * 70)
        print(f"EVENT TYPE: {event.event_type}")
        print(f"TITLE: {event.title}")
        print(f"SUMMARY: {event.summary}")
        print(f"SENTIMENT: {event.sentiment}")
        print(
            f"SENTIMENT STRENGTH: "
            f"{event.sentiment_strength}"
        )
        print(f"MATERIALITY: {event.materiality}")
        print(
            f"POTENTIAL IMPACT: "
            f"{event.potential_impact}"
        )
        print(
            f"AFFECTED AREAS: "
            f"{event.affected_areas}"
        )
        print(
            f"TIME HORIZON: "
            f"{event.time_horizon}"
        )
        print(f"SOURCE: {event.source}")
        print(f"SOURCE URL: {event.source_url}")

    # ---------------------------------------------------------
    # 6. Validate event integrity
    # ---------------------------------------------------------

    assert all(
        event.ticker.upper() == ticker
        for event in events
    )

    assert all(
        event.source
        for event in events
    )

    assert all(
        event.source_url
        for event in events
    )