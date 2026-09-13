import pytest

from fintendo.data.web_fetcher import WebFetcher, FetchedPage


def test_rejects_non_http_url():
    fetcher = WebFetcher()

    with pytest.raises(ValueError, match="Only HTTP and HTTPS URLs are allowed"):
        fetcher.fetch("ftp://example.com/page")


def test_rejects_invalid_url():
    fetcher = WebFetcher()

    with pytest.raises(ValueError, match="valid host"):
        fetcher.fetch("https:///page")


def test_accepts_html_response(monkeypatch):
    class MockResponse:
        url = "https://example.com/article"
        headers = {"Content-Type": "text/html; charset=utf-8"}
        content = b"<html><body>Hello</body></html>"
        encoding = "utf-8"

        def raise_for_status(self):
            pass

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr("fintendo.data.web_fetcher.requests.get", mock_get)

    fetcher = WebFetcher()
    result = fetcher.fetch("https://example.com/article")

    assert isinstance(result, FetchedPage)
    assert result.url == "https://example.com/article"
    assert result.content_type == "text/html"
    assert result.content == "<html><body>Hello</body></html>"


def test_rejects_unsupported_content_type(monkeypatch):
    class MockResponse:
        url = "https://example.com/file"
        headers = {"Content-Type": "application/pdf"}
        content = b"fake pdf"
        encoding = "utf-8"

        def raise_for_status(self):
            pass

    monkeypatch.setattr(
        "fintendo.data.web_fetcher.requests.get",
        lambda *args, **kwargs: MockResponse(),
    )

    fetcher = WebFetcher()

    with pytest.raises(ValueError, match="Unsupported content type"):
        fetcher.fetch("https://example.com/file")


def test_rejects_oversized_response(monkeypatch):
    class MockResponse:
        url = "https://example.com/article"
        headers = {
            "Content-Type": "text/html",
            "Content-Length": "100",
        }
        content = b"x" * 101
        encoding = "utf-8"

        def raise_for_status(self):
            pass

    monkeypatch.setattr(
        "fintendo.data.web_fetcher.requests.get",
        lambda *args, **kwargs: MockResponse(),
    )

    fetcher = WebFetcher(max_content_bytes=100)

    with pytest.raises(ValueError, match="maximum allowed size"):
        fetcher.fetch("https://example.com/article")