from enum import StrEnum

from pydantic import BaseModel, Field


class SourceTier(StrEnum):
    PRIMARY = "primary"
    TIER_A = "tier_a"
    TIER_B = "tier_b"
    TIER_C = "tier_c"
    TIER_D = "tier_d"


class SourceQuality(BaseModel):
    """
    Deterministic assessment of a source's evidentiary quality.

    This score represents source reliability, not whether the information
    itself is positive or negative.
    """

    source_name: str = Field(min_length=1)
    tier: SourceTier
    score: float = Field(ge=0, le=1)
    is_primary: bool
    rationale: str = Field(min_length=1)


class SourceQualityScorer:
    """
    Assigns deterministic quality scores to known source types.

    No LLM reasoning occurs here.
    """

    PRIMARY_SOURCES = {
        "company filing",
        "company investor relations",
        "stock exchange filing",
        "regulatory filing",
        "company press release",
    }

    TIER_A_SOURCES = {
        "reuters",
        "bloomberg",
        "financial times",
        "wall street journal",
    }

    TIER_B_SOURCES = {
        "cnbc",
        "economic times",
        "moneycontrol",
        "business standard",
        "mint",
    }

    TIER_C_SOURCES = {
        "industry publication",
        "specialist publication",
    }

    def score(self, source_name: str) -> SourceQuality:
        normalized_source = source_name.strip().lower()

        if not normalized_source:
            raise ValueError("source_name must not be empty.")

        if normalized_source in self.PRIMARY_SOURCES:
            return SourceQuality(
                source_name=source_name,
                tier=SourceTier.PRIMARY,
                score=1.0,
                is_primary=True,
                rationale="Primary source directly reporting the underlying information.",
            )

        if normalized_source in self.TIER_A_SOURCES:
            return SourceQuality(
                source_name=source_name,
                tier=SourceTier.TIER_A,
                score=0.9,
                is_primary=False,
                rationale="High-quality financial journalism with strong editorial standards.",
            )

        if normalized_source in self.TIER_B_SOURCES:
            return SourceQuality(
                source_name=source_name,
                tier=SourceTier.TIER_B,
                score=0.75,
                is_primary=False,
                rationale="Established financial or business media source.",
            )

        if normalized_source in self.TIER_C_SOURCES:
            return SourceQuality(
                source_name=source_name,
                tier=SourceTier.TIER_C,
                score=0.65,
                is_primary=False,
                rationale="Specialized industry publication.",
            )

        return SourceQuality(
            source_name=source_name,
            tier=SourceTier.TIER_D,
            score=0.40,
            is_primary=False,
            rationale="Unclassified or lower-confidence secondary source.",
        )