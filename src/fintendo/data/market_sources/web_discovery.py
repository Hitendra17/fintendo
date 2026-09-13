import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from fintendo.data.company.models import CompanyProfile
from fintendo.data.market_sources.discovery import MarketSourceDiscovery
from fintendo.data.market_sources.models import (
    MarketDiscoveryMethod,
    MarketSource,
)
from fintendo.data.web_fetcher import WebFetcher


class WebPageMarketSourceDiscovery(MarketSourceDiscovery):
    """
    Discovers company-relevant article URLs from a publisher webpage.

    Discovery is intentionally broader than the final article-level
    relevance gate. Its job is to produce plausible company/event
    candidates, while NewsIngestionService applies the final 45-point
    relevance threshold after the actual article has been fetched.
    """

    DEFAULT_MIN_CANDIDATE_SCORE = 30.0

    def __init__(
        self,
        web_fetcher: WebFetcher | None = None,
        min_candidate_score: float = DEFAULT_MIN_CANDIDATE_SCORE,
    ) -> None:
        if min_candidate_score < 0:
            raise ValueError(
                "min_candidate_score must not be negative."
            )

        self.web_fetcher = web_fetcher or WebFetcher()
        self.min_candidate_score = min_candidate_score

    def discover(
        self,
        profile: CompanyProfile,
        source: MarketSource,
    ) -> list[str]:
        if not profile.ticker.strip():
            raise ValueError(
                "profile ticker must not be empty."
            )

        if source.discovery_method != MarketDiscoveryMethod.WEB_PAGE:
            raise ValueError(
                "WebPageMarketSourceDiscovery requires "
                "a web_page source."
            )

        fetched_page = self.web_fetcher.fetch(
            str(source.url)
        )

        return self._extract_links(
            html=fetched_page.content,
            base_url=fetched_page.url,
            profile=profile,
        )

    def _extract_links(
        self,
        html: str,
        base_url: str,
        profile: CompanyProfile,
    ) -> list[str]:
        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        base_domain = urlparse(
            base_url
        ).netloc.lower()

        results: list[str] = []
        seen: set[str] = set()

        for link in soup.find_all(
            "a",
            href=True,
        ):
            href = str(
                link["href"]
            ).strip()

            if not href:
                continue

            absolute_url = urljoin(
                base_url,
                href,
            )

            parsed = urlparse(
                absolute_url
            )

            if parsed.scheme.lower() not in {
                "http",
                "https",
            }:
                continue

            if parsed.netloc.lower() != base_domain:
                continue

            if parsed.fragment:
                continue

            path = parsed.path.rstrip(
                "/"
            ).lower()

            if self._is_navigation_path(path):
                continue

            link_text = link.get_text(
                " ",
                strip=True,
            )

            candidate_score = self._candidate_score(
                link_text=link_text,
                path=parsed.path,
                query=parsed.query,
                profile=profile,
            )

            if candidate_score < self.min_candidate_score:
                continue

            normalized_url = absolute_url.rstrip(
                "/"
            )

            if normalized_url in seen:
                continue

            seen.add(normalized_url)
            results.append(normalized_url)

        return results

    @staticmethod
    def _candidate_score(
        link_text: str,
        path: str,
        query: str,
        profile: CompanyProfile,
    ) -> float:
        value = (
            f"{link_text} "
            f"{path} "
            f"{query}"
        ).lower()

        title = link_text.lower()

        company_name = (
            profile.company_name
            .strip()
            .lower()
        )

        ticker = (
            profile.ticker
            .strip()
            .lower()
        )

        aliases = [
            alias.strip().lower()
            for alias in profile.aliases
            if alias.strip()
        ]

        score = 0.0

        # ---------------------------------------------------------
        # Company-specific signals
        # ---------------------------------------------------------

        if WebPageMarketSourceDiscovery._contains_term(
            title,
            company_name,
        ):
            score += 60.0

        if WebPageMarketSourceDiscovery._contains_term(
            title,
            ticker,
        ):
            score += 50.0

        for alias in aliases:
            if WebPageMarketSourceDiscovery._contains_term(
                title,
                alias,
            ):
                score += 40.0
                break

        if WebPageMarketSourceDiscovery._contains_term(
            value,
            company_name,
        ):
            score += 25.0

        if WebPageMarketSourceDiscovery._contains_term(
            value,
            ticker,
        ):
            score += 20.0

        for alias in aliases:
            if WebPageMarketSourceDiscovery._contains_term(
                value,
                alias,
            ):
                score += 15.0
                break

        # ---------------------------------------------------------
        # Market-event signals
        # ---------------------------------------------------------

        event_keywords = {
            "announcement",
            "announces",
            "press-release",
            "press release",
            "media-release",
            "media release",
            "filing",
            "results",
            "quarterly",
            "financial",
            "drhp",
            "ipo",
            "merger",
            "acquisition",
            "partnership",
            "investment",
            "order",
            "contract",
            "agreement",
            "appointment",
            "resignation",
            "approval",
            "expansion",
            "launch",
            "project",
            "sebi",
            "exchange",
        }

        if any(
            keyword in value
            for keyword in event_keywords
        ):
            score += 20.0

        # ---------------------------------------------------------
        # Obviously non-article pages
        # ---------------------------------------------------------

        excluded_keywords = {
            "board of directors",
            "board-and-committee",
            "board and committee",
            "committee charter",
            "investor relations",
            "corporate governance",
            "annual report",
            "financial reports",
            "privacy policy",
            "terms of use",
            "contact us",
            "about us",
            "login",
            "subscribe",
        }

        if any(
            keyword in value
            for keyword in excluded_keywords
        ):
            return 0.0

        return min(
            score,
            100.0,
        )

    @staticmethod
    def _contains_term(
        text: str,
        term: str,
    ) -> bool:
        """
        Check whether a meaningful company term occurs in text.

        Full company names often contain legal suffixes such as
        'Limited', 'Ltd', 'Inc', etc. A page may therefore mention
        'HDFC Bank' while the profile contains 'HDFC Bank Limited'.

        We first try the complete phrase, then fall back to the
        meaningful words from the term.
        """
        if not term:
            return False

        normalized_text = text.lower().strip()
        normalized_term = term.lower().strip()

        if not normalized_text or not normalized_term:
            return False

        # Exact phrase match.
        escaped_term = re.escape(
            normalized_term
        )

        if re.search(
            rf"\b{escaped_term}\b",
            normalized_text,
        ):
            return True

        # Remove common legal/entity suffixes.
        meaningful_term = re.sub(
            r"\b("
            r"limited|ltd|private|pvt|"
            r"incorporated|inc|corporation|corp|"
            r"company|co"
            r")\b",
            " ",
            normalized_term,
        )

        meaningful_term = " ".join(
            meaningful_term.split()
        )

        if not meaningful_term:
            return False

        escaped_meaningful_term = re.escape(
            meaningful_term
        )

        return (
            re.search(
                rf"\b{escaped_meaningful_term}\b",
                normalized_text,
            )
            is not None
        )

    @staticmethod
    def _is_navigation_path(
        path: str,
    ) -> bool:
        return path in {
            "",
            "/investors",
            "/investor-relations",
            "/newsroom",
            "/newsroom/media-releases",
            "/about",
            "/contact",
            "/login",
            "/subscribe",
        }