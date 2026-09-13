import pytest

from fintendo.data.article_normalizer import ArticleNormalizer


def test_normalizes_whitespace():
    normalizer = ArticleNormalizer()

    text = (
        "Revenue   increased\n\nby 15% during the quarter. "
        "The company reported strong demand across its major business "
        "segments, while operating margins improved compared with the "
        "previous period. Management expects continued growth in the "
        "coming quarters."
    )

    result = normalizer.normalize_text(text)

    assert "  " not in result
    assert "\n" not in result
    assert result.startswith("Revenue increased by 15%")

def test_rejects_short_content():
    normalizer = ArticleNormalizer()

    with pytest.raises(ValueError, match="at least 200 characters"):
        normalizer.normalize_text("Too short.")


def test_same_content_produces_same_fingerprint():
    normalizer = ArticleNormalizer()

    text = "Revenue increased significantly during the quarter."

    first = normalizer.fingerprint(text)
    second = normalizer.fingerprint(text)

    assert first == second


def test_whitespace_differences_do_not_change_fingerprint():
    normalizer = ArticleNormalizer()

    first = normalizer.fingerprint(
        "Revenue increased significantly during the quarter."
    )

    second = normalizer.fingerprint(
        "Revenue   increased\nsignificantly during the quarter."
    )

    assert first == second


def test_different_content_produces_different_fingerprint():
    normalizer = ArticleNormalizer()

    first = normalizer.fingerprint(
        "Revenue increased significantly during the quarter."
    )

    second = normalizer.fingerprint(
        "Revenue declined significantly during the quarter."
    )

    assert first != second