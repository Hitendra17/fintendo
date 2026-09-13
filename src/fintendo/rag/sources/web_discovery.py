from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from fintendo.data.company.models import CompanyProfile
from fintendo.rag.sources.discovery import DocumentDiscoverySource
from fintendo.rag.sources.models import DiscoveredDocument, DocumentType


class WebDocumentDiscoverySource(DocumentDiscoverySource):
    """
    Discovers real company documents from a company's website.

    Discovery is deterministic:

        1. Resolve the best available company website.
        2. Fetch the landing page.
        3. Discover relevant same-domain section pages.
        4. Crawl those section pages.
        5. Extract PDF document links.
        6. Classify documents.
        7. Score documents by financial relevance.
        8. Deduplicate and return the highest-value documents.

    Gemini is deliberately not involved here.

    Company website information is optional. If neither an investor
    relations URL nor an official website is available, this source
    simply returns no documents instead of failing the research run.
    """

    DEFAULT_TIMEOUT_SECONDS = 15
    MAX_SECTION_PAGES = 10
    MAX_DOCUMENTS = 50

    ALLOWED_CONTENT_TYPES = {
        "text/html",
        "application/xhtml+xml",
    }

    DOCUMENT_TYPE_PRIORITY = {
        DocumentType.ANNUAL_REPORT: 100,
        DocumentType.QUARTERLY_RESULT: 95,
        DocumentType.INVESTOR_PRESENTATION: 90,
        DocumentType.TRANSCRIPT: 85,
        DocumentType.CORPORATE_FILING: 75,
        DocumentType.SUSTAINABILITY_REPORT: 60,
        DocumentType.PRESS_RELEASE: 55,
        DocumentType.OTHER: 0,
    }

    HIGH_VALUE_KEYWORDS = {
        "annual report": 40,
        "annual-report": 40,
        "annual_report": 40,
        "financial results": 35,
        "financial result": 35,
        "quarterly results": 35,
        "quarterly result": 35,
        "financial performance": 30,
        "investor presentation": 30,
        "investor-presentation": 30,
        "earnings presentation": 30,
        "earnings": 25,
        "results": 20,
        "transcript": 25,
        "conference call": 25,
        "earnings call": 25,
        "corporate filing": 20,
        "corporate announcement": 20,
        "exchange filing": 20,
        "financial statement": 30,
        "financial statements": 30,
        "balance sheet": 20,
        "profit and loss": 20,
        "cash flow": 20,
        "sustainability report": 15,
        "esg report": 15,
    }

    LOW_VALUE_KEYWORDS = {
        "policy": -35,
        "policies": -35,
        "charter": -35,
        "customer": -30,
        "grievance": -30,
        "complaint": -30,
        "interest rate": -30,
        "application": -25,
        "form": -20,
        "terms": -25,
        "conditions": -25,
        "disclosure": -10,
        "notice": -10,
        "code of conduct": -25,
        "privacy": -35,
        "security": -35,
    }

    def __init__(
        self,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds must be greater than zero."
            )

        self.timeout_seconds = timeout_seconds

    def discover(
        self,
        profile: CompanyProfile,
    ) -> list[DiscoveredDocument]:
        if not profile.ticker.strip():
            raise ValueError("Ticker must not be empty.")

        base_url = self._resolve_base_url(profile)

        # Company website information is optional.
        # If neither an IR URL nor an official website exists,
        # simply skip this discovery source.
        if not base_url:
            return []

        try:
            landing_page = self._fetch_page(base_url)
        except requests.HTTPError as exc:
            if (
                profile.investor_relations_url
                and profile.official_website
                and exc.response is not None
                and exc.response.status_code == 404
            ):
                base_url = str(profile.official_website)
                landing_page = self._fetch_page(base_url)
            else:
                raise

        section_urls = self._discover_section_urls(
            landing_page,
            base_url=base_url,
        )

        pages_to_crawl = [
            base_url,
            *section_urls,
        ]

        document_candidates: dict[
            str,
            tuple[str, DocumentType, int],
        ] = {}

        for page_url in pages_to_crawl[
            : self.MAX_SECTION_PAGES + 1
        ]:
            try:
                html = self._fetch_page(page_url)
            except (
                requests.RequestException,
                ValueError,
            ):
                continue

            discovered_links = self._extract_document_links(
                html,
                base_url=page_url,
            )

            for url, title, document_type in discovered_links:
                normalized_url = self._normalize_url(url)

                score = self._score_document(
                    url=normalized_url,
                    title=title,
                    document_type=document_type,
                )

                existing = document_candidates.get(
                    normalized_url
                )

                if (
                    existing is None
                    or score > existing[2]
                ):
                    document_candidates[normalized_url] = (
                        title,
                        document_type,
                        score,
                    )

        ranked_documents = sorted(
            document_candidates.items(),
            key=lambda item: item[1][2],
            reverse=True,
        )

        selected_documents = ranked_documents[
            : self.MAX_DOCUMENTS
        ]

        return [
            DiscoveredDocument(
                url=url,
                title=title,
                source=self._source_name(profile),
                document_type=document_type,
                ticker=profile.ticker,
                published_at=None,
            )
            for url, (
                title,
                document_type,
                _score,
            ) in selected_documents
        ]

    @staticmethod
    def _resolve_base_url(
        profile: CompanyProfile,
    ) -> str | None:
        if profile.investor_relations_url:
            return str(profile.investor_relations_url)

        if profile.official_website:
            return str(profile.official_website)

        return None

    @staticmethod
    def _source_name(
        profile: CompanyProfile,
    ) -> str:
        return f"{profile.company_name} Investor Relations"

    def _fetch_page(
        self,
        url: str,
    ) -> str:
        parsed = urlparse(url)

        if parsed.scheme.lower() not in {
            "http",
            "https",
        }:
            raise ValueError(
                "Only HTTP and HTTPS URLs are allowed."
            )

        if not parsed.netloc:
            raise ValueError(
                "URL must contain a valid host."
            )

        response = requests.get(
            url,
            timeout=self.timeout_seconds,
            headers={
                "User-Agent": (
                    "Fintendo/0.1 ResearchBot"
                ),
                "Accept": (
                    "text/html,"
                    "application/xhtml+xml"
                ),
            },
            allow_redirects=True,
        )

        response.raise_for_status()

        content_type = (
            response.headers
            .get("Content-Type", "")
            .split(";")[0]
            .strip()
            .lower()
        )

        if content_type not in self.ALLOWED_CONTENT_TYPES:
            raise ValueError(
                "Unsupported discovery content type: "
                f"{content_type or 'missing'}"
            )

        return response.text

    def _discover_section_urls(
        self,
        html: str,
        base_url: str,
    ) -> list[str]:
        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        base_domain = urlparse(
            base_url
        ).netloc.lower()

        candidates: list[tuple[str, int]] = []
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

            normalized_url = self._normalize_url(
                absolute_url
            )

            if normalized_url in seen:
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

            score = self._section_score(
                link_text=link_text,
                path=parsed.path,
            )

            if score <= 0:
                continue

            seen.add(normalized_url)
            candidates.append(
                (
                    normalized_url,
                    score,
                )
            )

        candidates.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        return [
            url
            for url, _score in candidates[
                : self.MAX_SECTION_PAGES
            ]
        ]

    @staticmethod
    def _section_score(
        link_text: str,
        path: str,
    ) -> int:
        value = (
            f"{link_text} {path}"
        ).lower()

        keywords = {
            "investor": 50,
            "investors": 50,
            "investor relations": 60,
            "financial": 40,
            "results": 45,
            "annual report": 50,
            "reports": 40,
            "presentation": 40,
            "earnings": 45,
            "quarterly": 45,
            "stock": 20,
            "shareholder": 40,
            "shareholders": 40,
            "corporate": 20,
            "news": 15,
            "media": 15,
        }

        return sum(
            score
            for keyword, score in keywords.items()
            if keyword in value
        )

    @staticmethod
    def _is_navigation_path(
        path: str,
    ) -> bool:
        navigation_terms = {
            "/about",
            "/careers",
            "/career",
            "/contact",
            "/privacy",
            "/terms",
            "/cookie",
            "/login",
            "/signin",
            "/signup",
        }

        return any(
            path == term
            or path.startswith(f"{term}/")
            for term in navigation_terms
        )

    def _extract_document_links(
        self,
        html: str,
        base_url: str,
    ) -> list[tuple[str, str, DocumentType]]:
        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        results: list[
            tuple[str, str, DocumentType]
        ] = []

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

            title = link.get_text(
                " ",
                strip=True,
            )

            document_type = self._classify_document(
                url=absolute_url,
                title=title,
            )

            if document_type == DocumentType.OTHER:
                continue

            results.append(
                (
                    absolute_url,
                    title or absolute_url,
                    document_type,
                )
            )

        return results

    @classmethod
    def _classify_document(
        cls,
        url: str,
        title: str,
    ) -> DocumentType:
        value = (
            f"{url} {title}"
        ).lower()

        if (
            "annual report" in value
            or "annual-report" in value
            or "annual_report" in value
        ):
            return DocumentType.ANNUAL_REPORT

        if (
            "quarterly result" in value
            or "quarterly results" in value
            or "financial result" in value
            or "financial results" in value
        ):
            return DocumentType.QUARTERLY_RESULT

        if (
            "investor presentation" in value
            or "investor-presentation" in value
            or "earnings presentation" in value
        ):
            return DocumentType.INVESTOR_PRESENTATION

        if (
            "transcript" in value
            or "conference call" in value
            or "earnings call" in value
        ):
            return DocumentType.TRANSCRIPT

        if (
            "corporate filing" in value
            or "exchange filing" in value
        ):
            return DocumentType.CORPORATE_FILING

        if (
            "sustainability report" in value
            or "esg report" in value
        ):
            return DocumentType.SUSTAINABILITY_REPORT

        if (
            "press release" in value
            or "press-release" in value
            or "media release" in value
            or "media-release" in value
        ):
            return DocumentType.PRESS_RELEASE

        return DocumentType.OTHER

    @classmethod
    def _score_document(
        cls,
        url: str,
        title: str,
        document_type: DocumentType,
    ) -> int:
        value = (
            f"{url} {title}"
        ).lower()

        score = cls.DOCUMENT_TYPE_PRIORITY.get(
            document_type,
            0,
        )

        for keyword, weight in cls.HIGH_VALUE_KEYWORDS.items():
            if keyword in value:
                score += weight

        for keyword, weight in cls.LOW_VALUE_KEYWORDS.items():
            if keyword in value:
                score += weight

        return score

    @staticmethod
    def _normalize_url(
        url: str,
    ) -> str:
        parsed = urlparse(url)

        normalized = parsed._replace(
            fragment=""
        )

        return normalized.geturl().rstrip("/")