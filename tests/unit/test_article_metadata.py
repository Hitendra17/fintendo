from datetime import datetime, timezone

from fintendo.data.article_metadata import ArticleMetadataExtractor


def test_extracts_publication_time_and_author():
    html = """
    <html>
        <head>
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
            <p>Article content.</p>
        </body>
    </html>
    """

    extractor = ArticleMetadataExtractor()

    published_at, author = extractor.extract(html)

    assert published_at == datetime(
        2026,
        9,
        5,
        10,
        30,
        tzinfo=timezone.utc,
    )
    assert author == "Jane Doe"


def test_extracts_rfc2822_date():
    html = """
    <html>
        <head>
            <meta
                name="date"
                content="Sat, 05 Sep 2026 10:30:00 GMT"
            >
        </head>
        <body>
            <p>Article content.</p>
        </body>
    </html>
    """

    extractor = ArticleMetadataExtractor()

    published_at, author = extractor.extract(html)

    assert published_at == datetime(
        2026,
        9,
        5,
        10,
        30,
        tzinfo=timezone.utc,
    )
    assert author is None


def test_returns_none_when_metadata_is_missing():
    html = """
    <html>
        <head>
            <title>Article</title>
        </head>
        <body>
            <p>Article content.</p>
        </body>
    </html>
    """

    extractor = ArticleMetadataExtractor()

    published_at, author = extractor.extract(html)

    assert published_at is None
    assert author is None


def test_ignores_invalid_publication_date():
    html = """
    <html>
        <head>
            <meta
                property="article:published_time"
                content="not-a-date"
            >
        </head>
        <body>
            <p>Article content.</p>
        </body>
    </html>
    """

    extractor = ArticleMetadataExtractor()

    published_at, author = extractor.extract(html)

    assert published_at is None
    assert author is None


def test_rejects_empty_html():
    extractor = ArticleMetadataExtractor()

    try:
        extractor.extract("   ")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "HTML content must not be empty."