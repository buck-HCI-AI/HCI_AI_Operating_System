"""Shared Pydantic response models used across routers."""
from pydantic import BaseModel
from typing import Any, Optional, List
from datetime import datetime


class SuccessResponse(BaseModel):
    status: str = "ok"
    message: Optional[str] = None
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    status: str = "error"
    error: str
    detail: Optional[Any] = None


class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[Any]


class ServiceStatus(BaseModel):
    name: str
    status: str          # ok | degraded | down
    detail: Optional[str] = None
    latency_ms: Optional[float] = None


class SystemStatusResponse(BaseModel):
    status: str          # healthy | degraded | down
    version: str
    timestamp: datetime
    services: List[ServiceStatus]
