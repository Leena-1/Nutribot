from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class AppError(Exception):
    message: str
    code: str = "app_error"
    status_code: int = 400
    details: Optional[Any] = None


class NotFoundError(AppError):
    def __init__(self, message: str = "Not found", *, details: Optional[Any] = None):
        super().__init__(message=message, code="not_found", status_code=404, details=details)


class ServiceUnavailableError(AppError):
    def __init__(self, message: str = "Service unavailable", *, details: Optional[Any] = None):
        super().__init__(message=message, code="service_unavailable", status_code=503, details=details)


class ModelNotLoadedError(AppError):
    def __init__(self, message: str = "Model not available", *, details: Optional[Any] = None):
        super().__init__(message=message, code="model_not_available", status_code=503, details=details)

