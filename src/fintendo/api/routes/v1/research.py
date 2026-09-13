from fastapi import APIRouter, HTTPException

from fintendo.api.schemas.request import ResearchRequest
from fintendo.api.schemas.response import ResearchResponse
from fintendo.api.services.research_service import APIResearchService


router = APIRouter(
    prefix="/research",
    tags=["Research"],
)


research_service = APIResearchService()


@router.post(
    "/company",
    response_model=ResearchResponse,
)
def research_company(
    request: ResearchRequest,
) -> ResearchResponse:
    try:
        return research_service.research(
            ticker=request.ticker,
            rag_query=request.rag_query,
            rag_top_k=request.rag_top_k,
            technical_period=request.technical_period,
            technical_interval=request.technical_interval,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc