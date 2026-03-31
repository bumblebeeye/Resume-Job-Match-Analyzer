import logging
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

REQUEST_ID_HEADER = "X-Request-ID"

logger = logging.getLogger(__name__)


def register_error_handling(app: FastAPI) -> None:
    @app.middleware("http")
    async def attach_request_id(request: Request, call_next):
        request_id = request.headers.get(REQUEST_ID_HEADER) or uuid4().hex
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        return response

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        detail = exc.detail if isinstance(exc.detail, str) else "Request failed."
        request_id = _get_request_id(request)
        return _build_error_response(
            status_code=exc.status_code,
            detail=detail,
            error_code=_http_error_code(exc.status_code),
            request_id=request_id,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        _exc: RequestValidationError,
    ) -> JSONResponse:
        return _build_error_response(
            status_code=422,
            detail="Request validation failed.",
            error_code="validation_error",
            request_id=_get_request_id(request),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = _get_request_id(request)
        logger.error("Unhandled server error for request_id=%s: %s", request_id, exc)
        return _build_error_response(
            status_code=500,
            detail="Internal server error.",
            error_code="internal_server_error",
            request_id=request_id,
        )


def _build_error_response(
    *,
    status_code: int,
    detail: str,
    error_code: str,
    request_id: str,
) -> JSONResponse:
    response = JSONResponse(
        status_code=status_code,
        content={
            "detail": detail,
            "error_code": error_code,
            "request_id": request_id,
        },
    )
    response.headers[REQUEST_ID_HEADER] = request_id
    return response


def _get_request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


def _http_error_code(status_code: int) -> str:
    if status_code == 400:
        return "bad_request"
    if status_code == 404:
        return "not_found"
    if status_code == 429:
        return "rate_limit_exceeded"
    return "http_error"
