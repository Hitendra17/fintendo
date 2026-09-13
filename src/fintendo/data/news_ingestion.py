import logging
from fintendo.data.company.models import CompanyProfile
from fintendo.data.web_fetcher import WebFetcher
from fintendo.models.market_intelligence import NewsArticle

logger = logging.getLogger(__name__)


class NewsIngestionService:
    """
    Converts discovered article URLs into normalized, deduplicated
    NewsArticle objects.

    No LLM reasoning occurs in this service.

    A deterministic relevance checkpoint scores each article against
    the target company after normalization. Articles below the
    configured relevance threshold are discarded before they reach
    downstream market-intelligence processing.
    """

    def __init__(
        self,
        web_fetcher: WebFetcher,
        html_parser: HTMLParser,
        article_normalizer: ArticleNormalizer,
        url_normalizer: URLNormalizer,
        article_deduplicator: ArticleDeduplicator,
        metadata_extractor: ArticleMetadataExtractor,
        relevance_checker: MarketArticleRelevanceChecker | None = None,
        relevance_threshold: float = 45.0,
    ) -> None:
        self.web_fetcher = web_fetcher
        self.html_parser = html_parser
        self.article_normalizer = article_normalizer
        self.url_normalizer = url_normalizer
        self.article_deduplicator = article_deduplicator
        self.metadata_extractor = metadata_extractor
        self.relevance_checker = (
            relevance_checker or MarketArticleRelevanceChecker()
        )
        self.relevance_threshold = relevance_threshold

    def ingest(
        self,
        urls: list[str],
        ticker: str,
        source: str,
        profile: CompanyProfile | None = None,
    ) -> list[NewsArticle]:
        articles: list[NewsArticle] = []

        for url in urls:
            try:
                fetched_page = self.web_fetcher.fetch(url)

                parsed_page = self.html_parser.parse(
                    fetched_page.content
                )

                published_at, author = self.metadata_extractor.extract(
                    fetched_page.content
                )

                normalized_text = self.article_normalizer.normalize_text(
                    parsed_page.text
                )

                normalized_url = self.url_normalizer.normalize(
                    fetched_page.url
                )

                article = NewsArticle(
                    source=source,
                    title=parsed_page.title,
                    url=normalized_url,
                    published_at=published_at,
                    author=author,
                    content=normalized_text,
                    ticker=ticker,
                )

                if profile is not None:
                    relevance_score = self.relevance_checker.score(
                        article=article,
                        profile=profile,
                    )

                    if relevance_score < self.relevance_threshold:
                        print(
                            f"[RELEVANCE] DISCARD | "
                            f"{profile.ticker} | "
                            f"{relevance_score:.1f} | "
                            f"{article.title}"
                        )
                        continue

                    print(
                        f"[RELEVANCE] KEEP    | "
                        f"{profile.ticker} | "
                        f"{relevance_score:.1f} | "
                        f"{article.title}"
                    )

                articles.append(article)

            except (ValueError, RuntimeError) as exc:
                logger.warning(
                    "Failed to ingest article URL %s: %s",
                    url,
                    exc,
                )
                continue

        return self.article_deduplicator.deduplicate(articles)