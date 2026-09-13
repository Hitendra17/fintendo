from urllib.parse import quote_plus, urlparse

import requests
from bs4 import BeautifulSoup

from fintendo.data.company.models import CompanyProfile
from fintendo.data.market_sources.discovery import MarketSourceDiscovery
from fintendo.data.market_sources.models import (
    MarketDiscoveryMethod,
    MarketSource,
)


class RSSMarketSourceDiscovery(MarketSourceDiscovery):
    """
    Discovers recent company-relevant article URLs from RSS feeds.

    Publisher feeds are filtered using RSS metadata before their URLs
    are returned.

    Google News is queried dynamically for the company and its ticker.
    Google News wrapper URLs are resolved to the underlying publisher
    URLs before being returned.
    """

    DEFAULT_TIMEOUT_SECONDS = 10
    DEFAULT_MAX_ITEMS = 20

    def __init__(
        self,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        max_items: int = DEFAULT_MAX_ITEMS,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds must be positive."
            )

        if max_items <= 0:
            raise ValueError(
                "max_items must be positive."
            )

        self.timeout_seconds = timeout_seconds
        self.max_items = max_items

    def discover(
        self,
        profile: CompanyProfile,
        source: MarketSource,
    ) -> list[str]:
        if not profile.ticker.strip():
            raise ValueError(
                "profile ticker must not be empty."
            )

        if source.discovery_method != MarketDiscoveryMethod.RSS:
            raise ValueError(
                "RSSMarketSourceDiscovery requires an RSS source."
            )

        source_host = urlparse(
            str(source.url)
        ).netloc.lower()

        is_google_news = (
            "news.google.com" in source_host
        )

        feed_url = self._build_feed_url(
            profile=profile,
            source=source,
        )

        response = requests.get(
            feed_url,
            timeout=self.timeout_seconds,
            headers={
                "User-Agent": "Fintendo/0.1 ResearchBot",
                "Accept": (
                    "application/rss+xml,"
                    "application/xml,"
                    "text/xml"
                ),
            },
            allow_redirects=True,
        )

        response.raise_for_status()

        content_type = (
            response.headers.get("Content-Type", "")
            .split(";")[0]
            .lower()
        )

        if content_type not in {
            "application/rss+xml",
            "application/xml",
            "text/xml",
        }:
            raise ValueError(
                f"Expected RSS/XML content, got '{content_type}'."
            )

        if is_google_news:
            return self._extract_google_news_urls(
                xml=response.text,
                profile=profile,
            )

        return self._extract_publisher_urls(
            xml=response.text,
            profile=profile,
        )

    def _extract_google_news_urls(
        self,
        xml: str,
        profile: CompanyProfile,
    ) -> list[str]:
        soup = BeautifulSoup(
            xml,
            "xml",
        )

        results: list[str] = []
        seen: set[str] = set()

        for item in soup.find_all("item"):
            title_element = item.find("title")
            link_element = item.find("link")

            if (
                title_element is None
                or link_element is None
            ):
                continue

            title = title_element.get_text(
                " ",
                strip=True,
            )

            wrapper_url = link_element.get_text(
                strip=True
            )

            if not title or not wrapper_url:
                continue

            if not self._matches_profile(
                text=title,
                profile=profile,
            ):
                continue

            resolved_url = self._resolve_google_news_url(
                wrapper_url
            )

            if resolved_url is None:
                continue

            if resolved_url in seen:
                continue

            seen.add(resolved_url)
            results.append(resolved_url)

            if len(results) >= self.max_items:
                break

        return results

    def _extract_publisher_urls(
        self,
        xml: str,
        profile: CompanyProfile,
    ) -> list[str]:
        soup = BeautifulSoup(
            xml,
            "xml",
        )

        results: list[str] = []
        seen: set[str] = set()

        for item in soup.find_all("item"):
            title_element = item.find("title")
            description_element = item.find(
                "description"
            )
            link_element = item.find("link")

            if (
                title_element is None
                or link_element is None
            ):
                continue

            title = title_element.get_text(
                " ",
                strip=True,
            )

            description = (
                description_element.get_text(
                    " ",
                    strip=True,
                )
                if description_element is not None
                else ""
            )

            if not self._matches_profile(
                text=f"{title} {description}",
                profile=profile,
            ):
                continue

            url = link_element.get_text(
                strip=True
            )

            if not self._is_valid_http_url(url):
                continue

            normalized_url = url.rstrip("/")

            if normalized_url in seen:
                continue

            seen.add(normalized_url)
            results.append(normalized_url)

            if len(results) >= self.max_items:
                break

        return results

    def _resolve_google_news_url(
        self,
        wrapper_url: str,
    ) -> str | None:
        if not self._is_valid_http_url(
            wrapper_url
        ):
            return None

        try:
            response = requests.get(
                wrapper_url,
                timeout=self.timeout_seconds,
                headers={
                    "User-Agent": (
                        "Fintendo/0.1 ResearchBot"
                    )
                },
                allow_redirects=True,
            )

            response.raise_for_status()

        except requests.RequestException:
            return None

        final_url = response.url

        if not self._is_valid_http_url(
            final_url
        ):
            return None

        final_host = urlparse(
            final_url
        ).netloc.lower()

        if "news.google.com" in final_host:
            return None

        return final_url.rstrip("/")

    @staticmethod
    def _build_feed_url(
        profile: CompanyProfile,
        source: MarketSource,
    ) -> str:
        source_host = urlparse(
            str(source.url)
        ).netloc.lower()

        if "news.google.com" in source_host:
            company_name = (
                profile.company_name.strip()
            )

            ticker = (
                profile.ticker.strip().upper()
            )

            query = (
                f'"{company_name}" '
                f"{ticker} "
                "when:7d"
            )

            return (
                "https://news.google.com/rss/search"
                f"?q={quote_plus(query)}"
                "&hl=en-IN"
                "&gl=IN"
                "&ceid=IN:en"
            )

        return str(source.url).rstrip("/")

    @staticmethod
    def _matches_profile(
        text: str,
        profile: CompanyProfile,
    ) -> bool:
        normalized_text = " ".join(
            text.lower().split()
        )

        company_name = " ".join(
            profile.company_name.lower().split()
        )

        ticker = profile.ticker.strip().lower()

        aliases = [
            " ".join(alias.lower().split())
            for alias in profile.aliases
            if alias.strip()
        ]

        # Exact company-name match.
        if (
            company_name
            and company_name in normalized_text
        ):
            return True

        # Ticker match.
        if (
            ticker
            and RSSMarketSourceDiscovery._contains_word(
                normalized_text,
                ticker,
            )
        ):
            return True

        # Alias match.
        for alias in aliases:
            if (
                alias
                and RSSMarketSourceDiscovery._contains_word(
                    normalized_text,
                    alias,
                )
            ):
                return True

        # Remove legal suffixes and match the meaningful
        # company name.
        meaningful_name = company_name

        for suffix in (
            " limited",
            " ltd",
            " private",
            " pvt",
            " incorporated",
            " inc",
            " corporation",
            " corp",
            " company",
            " co",
        ):
            if meaningful_name.endswith(suffix):
                meaningful_name = meaningful_name[
                    :-len(suffix)
                ].strip()
                break

        if (
            meaningful_name
            and meaningful_name in normalized_text
        ):
            return True

        return False

    @staticmethod
    def _contains_word(
        text: str,
        term: str,
    ) -> bool:
        import re

        return (
            re.search(
                rf"\b{re.escape(term)}\b",
                text,
            )
            is not None
        )

    @staticmethod
    def _is_valid_http_url(
        url: str,
    ) -> bool:
        parsed = urlparse(url)

        return (
            parsed.scheme.lower()
            in {"http", "https"}
            and bool(parsed.netloc)
        )