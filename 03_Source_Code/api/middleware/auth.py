"""
API key authentication middleware.
Enforces X-API-Key on /api/v1/* routes when keys are configured.
Skips: /health, /docs, /openapi.json, /api/v1/health, legacy routes.
Token-auth exception: executive approve/reject/defer paths bypass key check
when a ?token= query param is present (one-tap mobile approvals).
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

OPEN_PATHS = {"/health", "/docs", "/redoc", "/openapi.json", "/api/v1/health"}

# Paths that require API key (in addition to /api/v1/*)
# /mcp deliberately excluded 2026-07-07: it now has its own real OAuth 2.0 flow
# (dynamic client registration + bearer tokens via mcp_server/oauth_provider.py).
# Requiring our internal X-API-Key on /mcp/register etc defeated the entire point
# of OAuth - a new client can't have a pre-shared secret before it even registers.
# The /mcp protocol endpoint itself still enforces its own auth via FastMCP's
# bearer-token verification, so this isn't leaving it open.
PROTECTED_PREFIXES = ("/api/v1",)

# These prefixes skip key check when ?token= is present (mobile one-tap approvals)
TOKEN_AUTH_PREFIXES = (
    "/api/v1/executive/approve/",
    "/api/v1/executive/reject/",
    "/api/v1/executive/defer/",
)


class ApiKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, valid_keys: set):
        super().__init__(app)
        self.valid_keys = valid_keys

    async def dispatch(self, request: Request, call_next):
        if self.valid_keys and any(request.url.path.startswith(p) for p in PROTECTED_PREFIXES):
            if request.url.path not in OPEN_PATHS:
                # Allow token-authenticated one-tap approvals without API key
                is_token_path = any(request.url.path.startswith(p) for p in TOKEN_AUTH_PREFIXES)
                has_token = bool(request.query_params.get("token"))
                if is_token_path and has_token:
                    return await call_next(request)

                key = request.headers.get("X-API-Key", "")
                if key not in self.valid_keys:
                    return JSONResponse(
                        status_code=401,
                        content={"error": "Invalid or missing API key",
                                 "hint": "Pass X-API-Key header"},
                    )
        return await call_next(request)
