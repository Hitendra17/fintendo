from dataclasses import dataclass
from urllib.parse import urlparse

import requests


@dataclass(frozen=True)
class FetchedPage:
    url: str
    content_type: str
    content: str


class WebFetcher:
    """
    Fetches web pages with deterministic network-level guardrails.

    This layer does not interpret page content.
    """

    DEFAULT_TIMEOUT_SECONDS = 10
    MAX_CONTENT_BYTES = 2_000_000

    ALLOWED_SCHEMES = {"http", "https"}
    ALLOWED_CONTENT_TYPES = {
        "text/html",
        "application/xhtml+xml",
    }

    def __init__(
        self,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        max_content_bytes: int = MAX_CONTENT_BYTES,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero.")

        if max_content_bytes <= 0:
            raise ValueError("max_content_bytes must be greater than zero.")

        self.timeout_seconds = timeout_seconds
        self.max_content_bytes = max_content_bytes

    def fetch(self, url: str) -> FetchedPage:
        self._validate_url(url)

        response = requests.get(
            url,
            timeout=self.timeout_seconds,
            headers={
                "User-Agent": "Fintendo/0.1 ResearchBot",
                "Accept": "text/html,application/xhtml+xml",
            },
            allow_redirects=True,
        )

        response.raise_for_status()

        original_host = urlparse(url).netloc.lower()
        final_host = urlparse(response.url).netloc.lower()

        if original_host != final_host:
            raise ValueError(
                f"Redirected to a different host: "
                f"{original_host} -> {final_host}"
            )

        content_type = (
            response.headers.get("Content-Type", "")
            .split(";")[0]
            .lower()
        )

        if content_type not in self.ALLOWED_CONTENT_TYPES:
            raise ValueError(
                f"Unsupported content type: "
                f"{content_type or 'missing'}"
            )

        content_length = response.headers.get("Content-Length")

        if content_length is not None:
            try:
                content_length_value = int(content_length)
            except ValueError:
                content_length_value = None

            if (
                content_length_value is not None
                and content_length_value > self.max_content_bytes
            ):
                raise ValueError(
                    "Response exceeds maximum allowed size."
                )

        content = response.content

        if len(content) > self.max_content_bytes:
            raise ValueError(
                "Response exceeds maximum allowed size."
            )

        return FetchedPage(
            url=str(response.url),
            content_type=content_type,
            content=content.decode(
                response.encoding or "utf-8",
                errors="replace",
            ),
        )

    def _validate_url(self, url: str) -> None:
        parsed = urlparse(url)

        if parsed.scheme.lower() not in self.ALLOWED_SCHEMES:
            raise ValueError(
                "Only HTTP and HTTPS URLs are allowed."
            )

        if not parsed.netloc:
            raise ValueError(
                "URL must contain a valid host."
            )