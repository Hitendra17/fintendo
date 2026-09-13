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

        try:
            landing_page = self._fetch_page(base_url)
        except requests.HTTPError as exc:
            if (
                profile.investor_relations_url
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
    ) -> str:
        if profile.investor_relations_url:
            return str(profile.investor_relations_url)

        return str(profile.official_website)

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

        section_candidates: list[
            tuple[int, str]
        ] = []

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

            if (
                parsed.netloc.lower()
                != base_domain
            ):
                continue

            normalized_url = self._normalize_url(
                absolute_url
            )

            if normalized_url in seen:
                continue

            if self._looks_like_document(
                normalized_url
            ):
                continue

            title = link.get_text(
                " ",
                strip=True,
            ).lower()

            combined = (
                f"{title} "
                f"{normalized_url.lower()}"
            )

            score = self._score_section_page(
                combined
            )

            if score <= 0:
                continue

            seen.add(normalized_url)

            section_candidates.append(
                (score, normalized_url)
            )

        section_candidates.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        return [
            url
            for _, url in section_candidates
        ]

    def _extract_document_links(
        self,
        html: str,
        base_url: str,
    ) -> list[
        tuple[str, str, DocumentType]
    ]:
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

            normalized_url = (
                self._normalize_url(
                    absolute_url
                )
            )

            parsed = urlparse(
                normalized_url
            )

            if parsed.scheme.lower() not in {
                "http",
                "https",
            }:
                continue

            if not self._looks_like_document(
                normalized_url
            ):
                continue

            title = link.get_text(
                " ",
                strip=True,
            )

            if not title:
                title = self._title_from_url(
                    normalized_url
                )

            document_type = (
                self._classify_document(
                    url=normalized_url,
                    title=title,
                )
            )

            if document_type is None:
                continue

            results.append(
                (
                    normalized_url,
                    title,
                    document_type,
                )
            )

        return results

    @staticmethod
    def _score_section_page(
        value: str,
    ) -> int:
        section_keywords = {
            "investor": 50,
            "financial reporting": 45,
            "financial results": 45,
            "annual report": 45,
            "quarterly results": 45,
            "results": 30,
            "presentation": 35,
            "transcript": 35,
            "earnings": 35,
            "press release": 25,
            "investor relations": 50,
            "shareholder": 25,
            "statutory filing": 40,
            "corporate filing": 40,
            "corporate announcement": 35,
            "financial information": 40,
            "reports": 30,
        }

        return sum(
            score
            for keyword, score
            in section_keywords.items()
            if keyword in value
        )

    def _score_document(
        self,
        url: str,
        title: str,
        document_type: DocumentType,
    ) -> int:
        combined = (
            f"{title.lower()} "
            f"{url.lower()}"
        )

        score = self.DOCUMENT_TYPE_PRIORITY.get(
            document_type,
            0,
        )

        for keyword, weight in (
            self.HIGH_VALUE_KEYWORDS.items()
        ):
            if keyword in combined:
                score += weight

        for keyword, weight in (
            self.LOW_VALUE_KEYWORDS.items()
        ):
            if keyword in combined:
                score += weight

        return score

    @staticmethod
    def _looks_like_document(
        url: str,
    ) -> bool:
        path = urlparse(url).path.lower()

        return path.endswith(".pdf")

    @staticmethod
    def _classify_document(
        url: str,
        title: str,
    ) -> DocumentType | None:
        path_lower = urlparse(url).path.lower()

        if not path_lower.endswith(".pdf"):
            return None

        combined = (
            f"{title.lower()} "
            f"{url.lower()}"
        )

        # Check the most specific document types first.
        if "annual report" in combined:
            return DocumentType.ANNUAL_REPORT

        if (
            "transcript" in combined
            or "conference call" in combined
            or "earnings call" in combined
        ):
            return DocumentType.TRANSCRIPT

        if (
            "presentation" in combined
            or "earnings presentation" in combined
        ):
            return DocumentType.INVESTOR_PRESENTATION

        if (
            "quarter" in combined
            or "financial performance" in combined
            or "financial result" in combined
            or "financial results" in combined
        ):
            return DocumentType.QUARTERLY_RESULT

        if "press release" in combined:
            return DocumentType.PRESS_RELEASE

        if (
            "sustainability" in combined
            or "csr" in combined
            or "esg" in combined
        ):
            return DocumentType.SUSTAINABILITY_REPORT

        if (
            "filing" in combined
            or "corporate" in combined
            or "announcement" in combined
        ):
            return DocumentType.CORPORATE_FILING

        return DocumentType.OTHER

    @staticmethod
    def _normalize_url(
        url: str,
    ) -> str:
        parsed = urlparse(url)

        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()

        path = (
            parsed.path.rstrip("/")
            or "/"
        )

        return (
            f"{scheme}://{netloc}{path}"
        )

    @staticmethod
    def _title_from_url(
        url: str,
    ) -> str:
        path = urlparse(
            url
        ).path.rstrip("/")

        if not path:
            return "Untitled Document"

        filename = path.split("/")[-1]

        if filename.lower().endswith(".pdf"):
            filename = filename[:-4]

        return (
            filename
            .replace("-", " ")
            .replace("_", " ")
            .strip()
            .title()
        )