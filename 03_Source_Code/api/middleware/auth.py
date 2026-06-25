"""
API key authentication middleware.
Enforces X-API-Key on /api/v1/* routes when keys are configured.
Skips: /health, /docs, /openapi.json, /api/v1/health, legacy routes.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

OPEN_PATHS = {"/health", "/docs", "/redoc", "/openapi.json", "/api/v1/health"}


class ApiKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, valid_keys: set):
        super().__init__(app)
        self.valid_keys = valid_keys

    async def dispatch(self, request: Request, call_next):
        # Only enforce on /api/v1/* when keys are configured
        if self.valid_keys and request.url.path.startswith("/api/v1"):
            if request.url.path not in OPEN_PATHS:
                key = request.headers.get("X-API-Key", "")
                if key not in self.valid_keys:
                    return JSONResponse(
                        status_code=401,
                        content={"error": "Invalid or missing API key",
                                 "hint": "Pass X-API-Key header"},
                    )
        return await call_next(request)
