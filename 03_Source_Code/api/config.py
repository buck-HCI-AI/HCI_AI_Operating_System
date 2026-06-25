"""
HCI AI API — Configuration
All settings loaded from environment variables / .env file.
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # ── Application ──────────────────────────────────────────────────────────
    app_name:    str = "HCI AI Operating System API"
    app_version: str = "1.0.0"
    debug:       bool = False

    # ── API Authentication ────────────────────────────────────────────────────
    # Comma-separated list of valid API keys.
    # Leave blank during development — all requests allowed.
    api_keys: str = ""

    # ── PostgreSQL ────────────────────────────────────────────────────────────
    postgres_host:     str = "localhost"
    postgres_port:     int = 5432
    postgres_db:       str = "hci_os"
    postgres_user:     str = "hci_admin"
    postgres_password: str = ""

    # ── Redis ─────────────────────────────────────────────────────────────────
    redis_host:     str = "localhost"
    redis_port:     int = 6379
    redis_password: str = ""

    # ── MinIO ─────────────────────────────────────────────────────────────────
    minio_endpoint: str = "localhost:9000"
    minio_root_user:     str = "hci_admin"
    minio_root_password: str = ""
    minio_secure:        bool = False

    # ── Qdrant ────────────────────────────────────────────────────────────────
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    # ── Storage ───────────────────────────────────────────────────────────────
    hci_storage_root: str = ""

    # ── Anthropic ─────────────────────────────────────────────────────────────
    anthropic_api_key: Optional[str] = None

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def valid_api_keys(self) -> set:
        if not self.api_keys:
            return set()
        return {k.strip() for k in self.api_keys.split(",") if k.strip()}

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
