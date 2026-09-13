from fastapi import APIRouter, HTTPException, Query

from fintendo.api.schemas.company import CompanySearchResult
from fintendo.api.services.company_service import CompanyService


router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


company_service = CompanyService()


@router.get(
    "/search",
    response_model=list[CompanySearchResult],
)
def search_companies(
    q: str = Query(
        min_length=1,
        description="Company name or ticker.",
    ),
) -> list[CompanySearchResult]:
    try:
        return company_service.search(q)

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