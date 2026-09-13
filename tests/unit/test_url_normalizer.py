import pytest

from fintendo.data.url_normalizer import URLNormalizer


def test_removes_tracking_parameters():
    normalizer = URLNormalizer()

    result = normalizer.normalize(
        "https://NewsSite.com/article/123/"
        "?utm_source=twitter&utm_medium=social&id=123"
    )

    assert result == "https://newssite.com/article/123?id=123"


def test_preserves_meaningful_query_parameters():
    normalizer = URLNormalizer()

    result = normalizer.normalize(
        "https://example.com/article?id=123"
    )

    assert result == "https://example.com/article?id=123"


def test_rejects_invalid_scheme():
    normalizer = URLNormalizer()

    with pytest.raises(ValueError, match="Only HTTP and HTTPS"):
        normalizer.normalize("ftp://example.com/article")


def test_rejects_empty_url():
    normalizer = URLNormalizer()

    with pytest.raises(ValueError, match="must not be empty"):
        normalizer.normalize("   ")