"""
API Key authentication endpoints.
Scaffold — no persistent key store yet (keys live in .env API_KEYS).
"""
from fastapi import APIRouter, Depends
from dependencies import require_api_key
from config import settings

router = APIRouter()


@router.get("/status")
def auth_status(key: str = Depends(require_api_key)):
    """Check whether the current API key is valid."""
    mode = "development (open)" if not settings.valid_api_keys else "production (key required)"
    return {
        "authenticated": True,
        "mode": mode,
        "key_hint": f"{key[:8]}..." if key else None,
    }


@router.get("/mode")
def auth_mode():
    """Return current auth mode without requiring a key."""
    if settings.valid_api_keys:
        return {
            "mode": "production",
            "keys_configured": len(settings.valid_api_keys),
            "header": "X-API-Key",
        }
    return {
        "mode": "development",
        "keys_configured": 0,
        "note": "All requests permitted — set API_KEYS in .env to enforce authentication",
    }
