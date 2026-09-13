from dataclasses import dataclass

import requests


@dataclass(frozen=True)
class FetchedDocument:
    url: str
    content_type: str
    content: bytes


class DocumentFetcher:
    DEFAULT_TIMEOUT_SECONDS = 20
    MAX_CONTENT_BYTES = 20_000_000

    ALLOWED_CONTENT_TYPES = {
        "text/html",
        "application/xhtml+xml",
        "application/pdf",
    }

    def __init__(
        self,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        max_content_bytes: int = MAX_CONTENT_BYTES,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds must be greater than zero."
            )

        if max_content_bytes <= 0:
            raise ValueError(
                "max_content_bytes must be greater than zero."
            )

        self.timeout_seconds = timeout_seconds
        self.max_content_bytes = max_content_bytes

    def fetch(self, url: str) -> FetchedDocument:
        if not url.strip():
            raise ValueError("url must not be empty.")

        response = requests.get(
            url,
            timeout=self.timeout_seconds,
            headers={
                "User-Agent": "Fintendo/0.1 ResearchBot",
                "Accept": (
                    "text/html,"
                    "application/xhtml+xml,"
                    "application/pdf"
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
                "Unsupported content type: "
                f"{content_type or 'missing'}"
            )

        content_length = response.headers.get(
            "Content-Length"
        )

        if content_length is not None:
            try:
                if int(content_length) > self.max_content_bytes:
                    raise ValueError(
                        "Response exceeds maximum allowed size."
                    )
            except ValueError as exc:
                if str(exc) == (
                    "Response exceeds maximum allowed size."
                ):
                    raise

        content = response.content

        if len(content) > self.max_content_bytes:
            raise ValueError(
                "Response exceeds maximum allowed size."
            )

        return FetchedDocument(
            url=str(response.url),
            content_type=content_type,
            content=content,
        )