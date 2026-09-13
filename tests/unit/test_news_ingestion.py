from fintendo.data.article_deduplicator import ArticleDeduplicator
from fintendo.data.article_metadata import ArticleMetadataExtractor
from fintendo.data.article_normalizer import ArticleNormalizer
from fintendo.data.html_parser import HTMLParser
from fintendo.data.news_ingestion import NewsIngestionService
from fintendo.data.url_normalizer import URLNormalizer
from fintendo.data.web_fetcher import FetchedPage


def test_ingests_valid_article():
    class FakeFetcher:
        def fetch(self, url: str) -> FetchedPage:
            return FetchedPage(
                url=url,
                content_type="text/html",
                content="""
                    <html>
                        <head>
                            <title>TCS quarterly update</title>
                            <meta
                                property="article:published_time"
                                content="2026-09-05T10:30:00Z"
                            >
                            <meta
                                name="author"
                                content="Jane Doe"
                            >
                        </head>
                        <body>
                            <main>
                                <p>
                                    TCS reported strong quarterly revenue growth
                                    and improved operating margins across its major
                                    business segments. Management highlighted continued
                                    demand for digital services and expects business
                                    conditions to remain favorable in the coming
                                    quarters. The company also indicated that demand
                                    remains resilient across key markets and expects
                                    continued investment in technology services.
                                </p>
                            </main>
                        </body>
                    </html>
                """,
            )

    service = NewsIngestionService(
        web_fetcher=FakeFetcher(),
        html_parser=HTMLParser(),
        article_normalizer=ArticleNormalizer(),
        url_normalizer=URLNormalizer(),
        article_deduplicator=ArticleDeduplicator(),
        metadata_extractor=ArticleMetadataExtractor(),
    )

    result = service.ingest(
        urls=["https://example.com/tcs"],
        ticker="TCS",
        source="Example News",
    )

    assert len(result) == 1
    assert result[0].ticker == "TCS"
    assert result[0].source == "Example News"
    assert result[0].title == "TCS quarterly update"
    assert "strong quarterly revenue growth" in result[0].content

    assert result[0].author == "Jane Doe"
    assert result[0].published_at is not None
    assert result[0].published_at.year == 2026
    assert result[0].published_at.month == 9
    assert result[0].published_at.day == 5


def test_skips_failed_source():
    class FakeFetcher:
        def fetch(self, url: str) -> FetchedPage:
            raise ValueError("source unavailable")

    service = NewsIngestionService(
        web_fetcher=FakeFetcher(),
        html_parser=HTMLParser(),
        article_normalizer=ArticleNormalizer(),
        url_normalizer=URLNormalizer(),
        article_deduplicator=ArticleDeduplicator(),
        metadata_extractor=ArticleMetadataExtractor(),
    )

    result = service.ingest(
        urls=["https://example.com/broken"],
        ticker="TCS",
        source="Example News",
    )

    assert result == []


def test_deduplicates_articles():
    class FakeFetcher:
        def fetch(self, url: str) -> FetchedPage:
            return FetchedPage(
                url=url,
                content_type="text/html",
                content="""
                    <html>
                        <head>
                            <title>TCS results</title>
                        </head>
                        <body>
                            <main>
                                <p>
                                    TCS reported strong quarterly revenue growth
                                    and improved operating margins across its major
                                    business segments. Management highlighted continued
                                    demand for digital services and expects business
                                    conditions to remain favorable in the coming
                                    quarters. The company also indicated that demand
                                    remains resilient across key markets and expects
                                    continued investment in technology services.
                                </p>
                            </main>
                        </body>
                    </html>
                """,
            )

    service = NewsIngestionService(
        web_fetcher=FakeFetcher(),
        html_parser=HTMLParser(),
        article_normalizer=ArticleNormalizer(),
        url_normalizer=URLNormalizer(),
        article_deduplicator=ArticleDeduplicator(),
        metadata_extractor=ArticleMetadataExtractor(),
    )

    result = service.ingest(
        urls=[
            "https://example.com/article/123?utm_source=x",
            "https://example.com/article/123?utm_source=y",
        ],
        ticker="TCS",
        source="Example News",
    )

    assert len(result) == 1