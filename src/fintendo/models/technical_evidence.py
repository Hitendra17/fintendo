from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class TechnicalEvidenceType(StrEnum):
    OBSERVED = "observed"
    DERIVED = "derived"
    LEVEL = "level"


class TechnicalEvidence(BaseModel):
    source: str = Field(min_length=1)
    field: str = Field(min_length=1)
    evidence_type: TechnicalEvidenceType
    value: float | int
    period: datetime
    description: str = Field(min_length=1)