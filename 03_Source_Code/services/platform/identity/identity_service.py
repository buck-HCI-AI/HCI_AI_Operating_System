"""Platform Identity & Permissions Service.

Resolves actor names → roles → permissions.
Single source of truth for who can do what in the HCI AI system.
"""
from __future__ import annotations
import os, sys

_here = os.path.dirname(os.path.abspath(__file__))
_src = os.path.abspath(os.path.join(_here, "..", "..", ".."))
sys.path.insert(0, _src)
sys.path.insert(0, os.path.join(_src, "api"))

import services.db as db


ROLE_HIERARCHY = {
    "owner":          5,
    "pm":             3,
    "superintendent": 3,
    "contracts":      2,
    "ai_agent":       1,
    "system":         1,
}

# Hardcoded fallback — DB is authoritative when online
_DEFAULT_ROLES: dict[str, str] = {
    "Buck Adams":    "owner",
    "buck":          "owner",
    "pm":            "pm",
    "super":         "superintendent",
    "AI":            "ai_agent",
    "contracts_team":"contracts",
    "system":        "system",
}


class IdentityService:
    """Resolve actor → role → permissions."""

    @staticmethod
    def get_actor(actor_name: str) -> dict | None:
        try:
            row = db.query_one(
                "SELECT * FROM platform_users WHERE actor_name = %s AND active = TRUE",
                (actor_name,)
            )
            return dict(row) if row else None
        except Exception:
            return None

    @staticmethod
    def get_role(actor_name: str) -> str:
        """Return the role for an actor. Falls back to hardcoded defaults."""
        try:
            row = db.query_one(
                "SELECT role FROM platform_users WHERE actor_name = %s AND active = TRUE",
                (actor_name,)
            )
            if row:
                return row["role"]
        except Exception:
            pass
        return _DEFAULT_ROLES.get(actor_name, "pm")

    @staticmethod
    def get_permissions(actor_name: str) -> list[str]:
        role = IdentityService.get_role(actor_name)
        try:
            rows = db.query(
                "SELECT permission FROM platform_permissions WHERE role = %s",
                (role,)
            )
            return [r["permission"] for r in rows]
        except Exception:
            return []

    @staticmethod
    def can(actor_name: str, permission: str) -> bool:
        """Check whether actor_name has a given permission."""
        return permission in IdentityService.get_permissions(actor_name)

    @staticmethod
    def require(actor_name: str, permission: str) -> None:
        """Raise if actor lacks permission."""
        if not IdentityService.can(actor_name, permission):
            role = IdentityService.get_role(actor_name)
            raise PermissionError(
                f"Actor '{actor_name}' (role: {role}) lacks permission '{permission}'"
            )

    @staticmethod
    def list_users(role: str | None = None) -> list[dict]:
        try:
            if role:
                rows = db.query(
                    "SELECT * FROM platform_users WHERE role = %s AND active = TRUE ORDER BY actor_name",
                    (role,)
                )
            else:
                rows = db.query(
                    "SELECT * FROM platform_users WHERE active = TRUE ORDER BY role, actor_name"
                )
            return [dict(r) for r in rows]
        except Exception:
            return []

    @staticmethod
    def upsert_user(actor_name: str, role: str, email: str | None = None) -> dict:
        try:
            existing = db.query_one(
                "SELECT id FROM platform_users WHERE actor_name = %s", (actor_name,)
            )
            if existing:
                db.execute("""
                    UPDATE platform_users
                    SET role = %s, email = COALESCE(%s, email), updated_at = NOW()
                    WHERE actor_name = %s
                """, (role, email, actor_name))
            else:
                db.execute("""
                    INSERT INTO platform_users (actor_name, role, email)
                    VALUES (%s, %s, %s)
                """, (actor_name, role, email))
            return {"actor_name": actor_name, "role": role}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def list_roles() -> list[dict]:
        try:
            rows = db.query("""
                SELECT role, COUNT(*) AS permission_count
                FROM platform_permissions
                GROUP BY role ORDER BY role
            """)
            return [dict(r) for r in rows]
        except Exception:
            return [{"role": r, "permission_count": 0} for r in ROLE_HIERARCHY]

    @staticmethod
    def role_level(actor_name: str) -> int:
        """Numeric authority level — higher = more authority."""
        role = IdentityService.get_role(actor_name)
        return ROLE_HIERARCHY.get(role, 0)
