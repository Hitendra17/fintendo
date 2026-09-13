from bs4 import BeautifulSoup

from fintendo.rag.document_fetcher import FetchedDocument
from fintendo.rag.pdf_extractor import PDFTextExtractor


class DocumentTextExtractor:
    def __init__(
        self,
        pdf_extractor: PDFTextExtractor,
    ) -> None:
        self.pdf_extractor = pdf_extractor

    def extract(
        self,
        document: FetchedDocument,
    ) -> tuple[str, str]:
        if document.content_type == "application/pdf":
            text = self.pdf_extractor.extract(
                document.content
            )

            return text, self._title_from_url(document.url)

        if document.content_type in {
            "text/html",
            "application/xhtml+xml",
        }:
            return self._extract_html(document.content)

        raise ValueError(
            f"Unsupported content type: "
            f"{document.content_type}"
        )

    @staticmethod
    def _extract_html(
        content: bytes,
    ) -> tuple[str, str]:
        soup = BeautifulSoup(
            content,
            "html.parser",
        )

        for tag_name in {
            "script",
            "style",
            "noscript",
            "iframe",
            "svg",
            "nav",
            "footer",
            "header",
        }:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        title = ""

        if soup.title and soup.title.string:
            title = soup.title.string.strip()

        body = soup.find("body")

        if body is None:
            raise ValueError(
                "No readable body found in HTML."
            )

        text = body.get_text(
            " ",
            strip=True,
        )

        if not text:
            raise ValueError(
                "No readable text found in HTML."
            )

        return text, title

    @staticmethod
    def _title_from_url(url: str) -> str:
        from urllib.parse import urlparse

        parsed = urlparse(url)

        filename = (
            parsed.path
            .rstrip("/")
            .split("/")[-1]
        )

        if not filename:
            return "Untitled document"

        return (
            filename
            .replace("-", " ")
            .replace("_", " ")
            .rsplit(".", 1)[0]
        )