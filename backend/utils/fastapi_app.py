from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.utils.errors import AppError


def register_exception_handlers(app: FastAPI) -> None:
    logger = logging.getLogger("backend.errors")

    @app.exception_handler(AppError)
    async def _handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        logger.info(
            "app_error",
            extra={
                "path": request.url.path,
                "code": exc.code,
                "status_code": exc.status_code,
            },
        )
        payload: Dict[str, Any] = {"error": {"code": exc.code, "message": exc.message}}
        if exc.details is not None:
            payload["error"]["details"] = exc.details
        return JSONResponse(status_code=exc.status_code, content=payload)

    @app.exception_handler(Exception)
    async def _handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_exception", extra={"path": request.url.path})
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "internal_error", "message": "Unexpected server error."}},
        )

