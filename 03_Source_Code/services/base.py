"""
Base class for all Construction Intelligence Services.
Provides shared access to Postgres, Redis, Qdrant, and Anthropic.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "integrations"))

import services.db    as db
import services.cache as cache
import services.vector as vector
from config import settings


class BaseIntelligenceService:
    SERVICE_NAME: str = "base"
    STATUS: str = "planned"       # planned | partial | active
    VERSION: str = "1.0.0"

    @classmethod
    def info(cls) -> dict:
        return {
            "service": cls.SERVICE_NAME,
            "status":  cls.STATUS,
            "version": cls.VERSION,
        }

    @staticmethod
    def pg_query(sql: str, params=None):
        return db.query(sql, params)

    @staticmethod
    def pg_one(sql: str, params=None):
        return db.query_one(sql, params)

    @staticmethod
    def resolve_project_id(project_number: str) -> int | None:
        """Convert a short project code (e.g. '64EW') to the projects.id.
        Matches by leading digit prefix against projects.name / projects.address."""
        import re
        m = re.match(r'^(\d+)', project_number.upper())
        prefix = m.group(1) if m else project_number
        row = db.query_one(
            "SELECT id FROM projects WHERE name ILIKE %s OR address ILIKE %s LIMIT 1",
            (f"{prefix}%", f"{prefix}%")
        )
        return int(row["id"]) if row else None

    @staticmethod
    def cache_get(key: str):
        return cache.get(key)

    @staticmethod
    def cache_set(key: str, value, ttl: int = 300):
        cache.set(key, value, ttl)

    @staticmethod
    def search(query: str, collection: str = None, limit: int = 8,
               project_filter: str = None) -> list:
        filters = {}
        if project_filter:
            filters["project_number"] = project_filter
        try:
            return vector.search(
                query=query, collection=collection,
                limit=limit, filters=filters or None,
            )
        except Exception:
            return []

    @staticmethod
    def pg_execute(sql: str, params=None) -> None:
        db.execute(sql, params)

    @staticmethod
    def pg_execute_returning(sql: str, params=None):
        return db.execute_returning(sql, params)

    @staticmethod
    def ask_claude(prompt: str, system: str = "", max_tokens: int = 1024) -> str:
        """Call Claude Haiku for fast, cheap intelligence synthesis."""
        import anthropic
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        messages = [{"role": "user", "content": prompt}]
        kwargs = {"model": "claude-haiku-4-5-20251001",
                  "max_tokens": max_tokens, "messages": messages}
        if system:
            kwargs["system"] = system
        response = client.messages.create(**kwargs)
        return response.content[0].text

    @staticmethod
    def parse_json_response(raw: str) -> dict:
        """Parse Claude response as JSON, stripping markdown code fences if present."""
        import json, re
        text = raw.strip()
        if text.startswith("```"):
            text = re.sub(r'^```(?:json)?\s*\n?', '', text)
            text = re.sub(r'\n?```\s*$', '', text)
        return json.loads(text.strip())
