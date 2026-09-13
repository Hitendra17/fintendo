import pytest
import requests

from fintendo.data.market_sources.models import MarketDiscoveryMethod
from fintendo.data.market_sources.registry import get_global_market_sources


EXPECTED_CONTENT_TYPES = {
    MarketDiscoveryMethod.WEB_PAGE: {
        "text/html",
        "application/xhtml+xml",
    },
    MarketDiscoveryMethod.RSS: {
        "application/rss+xml",
        "application/xml",
        "text/xml",
    },
}

TIMEOUT_SECONDS = 10


@pytest.mark.integration
def test_global_market_sources_are_reachable() -> None:
    sources = get_global_market_sources()
    failures: list[str] = []

    for source in sources:
        if source.discovery_method == MarketDiscoveryMethod.RSS:
            # Skip RSS sources for this test, as they may have different
            # availability characteristics than web pages.
            continue
        try:
            response = requests.get(
                str(source.url),
                timeout=TIMEOUT_SECONDS,
                headers={
                    "User-Agent": "Fintendo/0.1 ResearchBot",
                    "Accept": (
                        "text/html,"
                        "application/xhtml+xml,"
                        "application/rss+xml,"
                        "application/xml,"
                        "text/xml"
                    ),
                },
                allow_redirects=True,
            )

            content_type = (
                response.headers.get("Content-Type", "")
                .split(";")[0]
                .strip()
                .lower()
            )

            if not 200 <= response.status_code < 300:
                failures.append(
                    f"{source.name}: HTTP {response.status_code} "
                    f"({response.url})"
                )
                continue

            expected_types = EXPECTED_CONTENT_TYPES[source.discovery_method]

            if content_type not in expected_types:
                failures.append(
                    f"{source.name}: unexpected content type "
                    f"'{content_type}' for "
                    f"{source.discovery_method.value} source "
                    f"({response.url})"
                )

        except requests.Timeout:
            failures.append(
                f"{source.name}: request timed out after "
                f"{TIMEOUT_SECONDS}s"
            )

        except requests.RequestException as exc:
            failures.append(
                f"{source.name}: request failed: {exc}"
            )

    if failures:
        pytest.fail(
            "Market source health check failed:\n"
            + "\n".join(f"- {failure}" for failure in failures)
        )