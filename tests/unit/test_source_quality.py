import pytest

from fintendo.data.source_quality import (
    SourceQualityScorer,
    SourceTier,
)


def test_primary_source_gets_highest_score():
    scorer = SourceQualityScorer()

    result = scorer.score("Company Filing")

    assert result.tier == SourceTier.PRIMARY
    assert result.score == 1.0
    assert result.is_primary is True


def test_tier_a_source():
    scorer = SourceQualityScorer()

    result = scorer.score("Reuters")

    assert result.tier == SourceTier.TIER_A
    assert result.score == 0.9
    assert result.is_primary is False


def test_tier_b_source():
    scorer = SourceQualityScorer()

    result = scorer.score("MoneyControl")

    assert result.tier == SourceTier.TIER_B
    assert result.score == 0.75


def test_unknown_source_gets_conservative_score():
    scorer = SourceQualityScorer()

    result = scorer.score("Random Finance Blog")

    assert result.tier == SourceTier.TIER_D
    assert result.score == 0.40


def test_rejects_empty_source():
    scorer = SourceQualityScorer()

    with pytest.raises(ValueError, match="source_name must not be empty"):
        scorer.score("   ")