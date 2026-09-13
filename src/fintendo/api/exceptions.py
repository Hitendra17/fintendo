from fastapi import Request
from fastapi.responses import JSONResponse


async def value_error_handler(
    request: Request,
    exc: ValueError,
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "error": "validation_error",
            "detail": str(exc),
        },
    )


async def runtime_error_handler(
    request: Request,
    exc: RuntimeError,
) -> JSONResponse:
    return JSONResponse(
        status_code=502,
        content={
            "error": "upstream_error",
            "detail": str(exc),
        },
    )