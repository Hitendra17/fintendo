from fintendo.data.article_deduplicator import ArticleDeduplicator
from fintendo.models.market_intelligence import NewsArticle


def make_article(
    url: str,
    title: str,
    content: str,
) -> NewsArticle:
    return NewsArticle(
        source="Test Source",
        title=title,
        url=url,
        published_at=None,
        author=None,
        content=content,
        ticker="TCS",
    )


def test_removes_duplicate_urls():
    content = (
        "TCS reported strong quarterly revenue growth and improved "
        "operating margins across its major business segments. "
        "Management highlighted continued demand for digital services "
        "and expects business conditions to remain favorable in the "
        "coming quarters."
    )

    articles = [
        make_article(
            "https://example.com/article/123?utm_source=twitter",
            "TCS reports strong growth",
            content,
        ),
        make_article(
            "https://example.com/article/123?utm_source=google",
            "TCS reports strong growth",
            content + " Different formatting.",
        ),
    ]

    deduplicator = ArticleDeduplicator()
    result = deduplicator.deduplicate(articles)

    assert len(result) == 1


def test_removes_duplicate_content_from_different_urls():
    content = (
        "TCS reported strong quarterly revenue growth and improved "
        "operating margins across its major business segments. "
        "Management highlighted continued demand for digital services "
        "and expects business conditions to remain favorable in the "
        "coming quarters."
    )

    articles = [
        make_article(
            "https://source-a.com/article/123",
            "TCS reports strong growth",
            content,
        ),
        make_article(
            "https://source-b.com/story/456",
            "TCS quarterly update",
            content,
        ),
    ]

    deduplicator = ArticleDeduplicator()
    result = deduplicator.deduplicate(articles)

    assert len(result) == 1


def test_keeps_distinct_articles():
    content_a = (
        "TCS reported strong quarterly revenue growth and improved "
        "operating margins across its major business segments. "
        "Management highlighted continued demand for digital services "
        "and expects business conditions to remain favorable in the "
        "coming quarters."
    )

    content_b = (
        "TCS announced a major new partnership with an international "
        "technology company focused on artificial intelligence services. "
        "The agreement is expected to expand the company's presence "
        "in several important global markets."
    )

    articles = [
        make_article(
            "https://example.com/article/123",
            "TCS quarterly results",
            content_a,
        ),
        make_article(
            "https://example.com/article/456",
            "TCS announces partnership",
            content_b,
        ),
    ]

    deduplicator = ArticleDeduplicator()
    result = deduplicator.deduplicate(articles)

    assert len(result) == 2


def test_empty_input_returns_empty_list():
    deduplicator = ArticleDeduplicator()

    assert deduplicator.deduplicate([]) == []