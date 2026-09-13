from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl


class DocumentType(StrEnum):
    ANNUAL_REPORT = "annual_report"
    QUARTERLY_RESULT = "quarterly_result"
    INVESTOR_PRESENTATION = "investor_presentation"
    CORPORATE_FILING = "corporate_filing"
    SUSTAINABILITY_REPORT = "sustainability_report"
    TRANSCRIPT = "transcript"
    PRESS_RELEASE = "press_release"
    OTHER = "other"


class DiscoveredDocument(BaseModel):
    url: HttpUrl
    title: str = Field(min_length=1)
    source: str = Field(min_length=1)
    document_type: DocumentType
    ticker: str = Field(min_length=1)
    published_at: datetime | None = None